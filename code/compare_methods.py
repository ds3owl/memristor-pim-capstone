"""
compare_methods.py — 친구 방식 vs 우리 방식 직접 비교

생성물:
- figures/method_comparison.png   : 4 소재 × 2 방식 막대 비교
- results/method_comparison.md    : 비교표 (markdown)
"""
import os
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
FIG_DIR = os.path.join(BASE_DIR, 'figures')

PRETTY = {
    'Pt_HfOx_Ti':       'Pt/HfO$_x$/Ti',
    'Ferroelectric':    'Ferroelectric',
    'Metallic_Nanowire':'Metallic Nanowire',
    'TaOx_Ta':          'TaO$_x$/Ta',
}


def main():
    with open(os.path.join(RESULTS_DIR, 'material_results.json'), encoding='utf-8') as f:
        ours = json.load(f)['materials']
    with open(os.path.join(RESULTS_DIR, 'gaussian_only_results.json'), encoding='utf-8') as f:
        friend = json.load(f)['materials']

    materials = list(ours.keys())
    x = np.arange(len(materials))
    width = 0.4

    friend_mean = [friend[m]['f1_mean'] for m in materials]
    friend_std  = [friend[m]['f1_std']  for m in materials]
    ours_mean   = [ours[m]['realistic']['f1_mean'] for m in materials]
    ours_std    = [ours[m]['realistic']['f1_std']  for m in materials]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.bar(x - width/2, friend_mean, width, yerr=friend_std, capsize=4,
           color='#7FB3D5', edgecolor='black',
           label="Friend's method (Gaussian noise only)")
    ax.bar(x + width/2, ours_mean, width, yerr=ours_std, capsize=4,
           color='#E59866', edgecolor='black',
           label="Our method (Gaussian + stuck-at fault + N-states)")
    ax.axhline(0.9812, color='gray', linestyle='--', linewidth=1,
               label='FP32 baseline = 0.9812')
    ax.set_xticks(x)
    ax.set_xticklabels([PRETTY[m] for m in materials], fontsize=10)
    ax.set_ylabel('Macro F1 (mean ± std)')
    ax.set_title("Method Comparison — Realistic F1 across 4 Materials\n"
                 "(Same baseline models, same 9 noise samples per material)",
                 fontsize=12)
    ax.legend(loc='lower left', fontsize=9)
    ax.set_ylim(0, 1.05)
    ax.grid(True, axis='y', linestyle='--', alpha=0.4)

    # 값 라벨
    for i, (fm, om) in enumerate(zip(friend_mean, ours_mean)):
        ax.text(i - width/2, fm + 0.02, f'{fm:.3f}', ha='center', fontsize=8, fontweight='bold')
        ax.text(i + width/2, om + 0.02, f'{om:.3f}', ha='center', fontsize=8, fontweight='bold')

    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'method_comparison.png'), dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("저장: figures/method_comparison.png")

    # 비교 표 markdown
    lines = []
    lines.append("# 친구 방식 vs 우리 방식 직접 비교\n")
    lines.append("Baseline: 동일한 3 seed (42, 123, 456) × 3 noise sample = 9 측정값/소재.\n")
    lines.append("\n| Material | R_off/R_on | 친구 방식 F1 | 우리 방식 F1 | 차이 | 결론 |")
    lines.append("|---|---:|---:|---:|---:|---|")
    for m in materials:
        ratio = ours[m]['ratio']
        f = friend[m]['f1_mean']
        o = ours[m]['realistic']['f1_mean']
        diff = f - o
        if m == 'Metallic_Nanowire':
            verdict = '**친구 방식 = 가장 좋게 보임** vs 우리 방식 = 100% catastrophic'
        elif diff > 0.05:
            verdict = '친구 방식이 더 관대'
        else:
            verdict = '비슷'
        lines.append(f"| {PRETTY[m]} | {ratio:.1f}x | {f:.4f} ± {friend[m]['f1_std']:.4f} | "
                     f"{o:.4f} ± {ours[m]['realistic']['f1_std']:.4f} | "
                     f"{diff:+.4f} | {verdict} |")

    lines.append("\n## 핵심 발견\n")
    lines.append(
        "1. **NW(Metallic Nanowire)에서 결론이 완전히 뒤집힘**: 친구 방식에선 "
        f"F1 = {friend['Metallic_Nanowire']['f1_mean']:.3f}로 4 소재 중 가장 안정. "
        f"우리 방식에선 F1 = {ours['Metallic_Nanowire']['realistic']['f1_mean']:.3f}로 100% catastrophic. "
        "→ **노이즈 모델링 방식이 소재 추천 결론을 완전히 뒤집을 수 있다.**\n"
    )
    lines.append(
        "2. **친구 방식이 NW를 '안정'으로 본 이유**: 양자화(4 state)와 fault(5%)를 적용하지 않았고, "
        "NW의 variation 값(σ=0.065)이 다른 소재 대비 가장 작아 Gaussian noise의 영향이 가장 적게 보였기 때문. "
        "그러나 PIM의 본질적 한계인 4-state 양자화와 stuck-at fault를 적용하면 NW의 한계가 드러남.\n"
    )
    lines.append(
        "3. **고저항비 3 소재(Pt/Ferro/TaOx)는 양쪽 방식에서 비슷한 평균**: ±0.05 이내. "
        "다만 std는 둘 다 큼(0.13~0.24) → bimodal 분포가 노이즈 종류와 무관하게 본질적.\n"
    )
    lines.append(
        "4. **본 연구의 노이즈 모델(Gaussian + stuck-at fault + N-states)이 더 현실적 결론을 줌**: "
        "실제 멤리스터 제조 결함은 stuck-at fault에 가깝고, 매핑 시 양자화는 피할 수 없는 손실. "
        "친구 방식은 한 측면만 본 셈.\n"
    )

    out = os.path.join(RESULTS_DIR, 'method_comparison.md')
    with open(out, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    print("저장: results/method_comparison.md")

    print("\n" + "=" * 60)
    print("비교 요약")
    print("=" * 60)
    print(f"{'Material':22s} {'Friend F1':>12s} {'Ours F1':>12s} {'Diff':>10s}")
    for m in materials:
        f = friend[m]['f1_mean']
        o = ours[m]['realistic']['f1_mean']
        print(f"{PRETTY[m]:22s} {f:>12.4f} {o:>12.4f} {f-o:>+10.4f}")


if __name__ == "__main__":
    main()
