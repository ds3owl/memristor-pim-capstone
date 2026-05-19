"""
analyze.py — Phase 1 결과 통계 분석 + bimodal histogram 생성

생성물:
- figures/bimodal_distribution.png        : per-noise F1 분포 (4 소재 동시 비교)
- figures/material_comparison.png          : ideal vs realistic mean±std 막대 그래프
- results/per_noise_table.md               : per-noise F1 표 (markdown)
- results/phase1_statistics.json           : 추가 통계 (paired diff, bimodal 임계)
"""
import os
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')  # non-interactive
import matplotlib.pyplot as plt


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
FIG_DIR = os.path.join(BASE_DIR, 'figures')
os.makedirs(FIG_DIR, exist_ok=True)

PRETTY = {
    'Pt_HfOx_Ti':       'Pt/HfO$_x$/Ti',
    'Ferroelectric':    'Ferroelectric',
    'Metallic_Nanowire':'Metallic Nanowire',
    'TaOx_Ta':          'TaO$_x$/Ta',
}
COLORS = {
    'Pt_HfOx_Ti':       '#4C72B0',
    'Ferroelectric':    '#55A868',
    'Metallic_Nanowire':'#C44E52',
    'TaOx_Ta':          '#8172B2',
}


def main():
    with open(os.path.join(RESULTS_DIR, 'material_results.json'), encoding='utf-8') as f:
        results = json.load(f)
    with open(os.path.join(RESULTS_DIR, 'baseline_results.json'), encoding='utf-8') as f:
        baseline = json.load(f)
    baseline_f1 = baseline['test_macro_f1_mean']

    # ---------- per-noise 표 (markdown) ----------
    md_lines = []
    md_lines.append("# Phase 1 — per-noise F1 결과표\n")
    md_lines.append(f"Baseline (FP32 software, 3-seed mean): macro F1 = **{baseline_f1:.4f}**\n")
    md_lines.append("\n각 셀: realistic 평가 macro F1 (baseline seed × noise sample n).\n")

    md_lines.append("\n| Material | R_off/R_on | Ideal F1 | seed42-n1 | seed42-n2 | seed42-n3 | "
                    "seed123-n1 | seed123-n2 | seed123-n3 | seed456-n1 | seed456-n2 | seed456-n3 | "
                    "Mean | Std |")
    md_lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for mat_name, d in results['materials'].items():
        ideal_f1 = d['ideal']['f1_mean']
        per_noise = [r['macro_f1'] for r in d['per_seed']['realistic']]
        row = [PRETTY[mat_name], f"{d['ratio']:.2f}x", f"{ideal_f1:.4f}"]
        row += [f"{v:.4f}" for v in per_noise]
        row += [f"**{d['realistic']['f1_mean']:.4f}**",
                f"{d['realistic']['f1_std']:.4f}"]
        md_lines.append("| " + " | ".join(row) + " |")

    # ---------- bimodal 임계 분석 ----------
    md_lines.append("\n## Bimodal 분포 분석\n")
    md_lines.append(
        "각 소재의 realistic per-noise F1 중 baseline의 90% 이상을 유지한 비율 (good)과 "
        "60% 미만으로 떨어진 비율 (catastrophic) 정량화.\n"
    )
    md_lines.append("\n| Material | Good (F1 ≥ 0.88) | Catastrophic (F1 < 0.60) | Total samples |")
    md_lines.append("|---|---:|---:|---:|")
    stats_summary = {}
    for mat_name, d in results['materials'].items():
        per_noise = np.array([r['macro_f1'] for r in d['per_seed']['realistic']])
        n = len(per_noise)
        good = int((per_noise >= 0.88).sum())
        cat = int((per_noise < 0.60).sum())
        md_lines.append(f"| {PRETTY[mat_name]} | {good}/{n} ({good/n*100:.0f}%) | "
                        f"{cat}/{n} ({cat/n*100:.0f}%) | {n} |")
        stats_summary[mat_name] = {
            'good_count': good, 'catastrophic_count': cat, 'total': n,
            'good_ratio': good / n, 'catastrophic_ratio': cat / n,
            'per_noise_f1': per_noise.tolist(),
        }

    with open(os.path.join(RESULTS_DIR, 'per_noise_table.md'), 'w', encoding='utf-8') as f:
        f.write("\n".join(md_lines))
    print("저장: results/per_noise_table.md")

    # ---------- bimodal histogram ----------
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    axes = axes.flatten()
    bins = np.linspace(0, 1, 21)
    for ax, (mat_name, d) in zip(axes, results['materials'].items()):
        per_noise = np.array([r['macro_f1'] for r in d['per_seed']['realistic']])
        ax.hist(per_noise, bins=bins, color=COLORS[mat_name], edgecolor='black', alpha=0.85)
        ax.axvline(d['ideal']['f1_mean'], color='black', linestyle='--', linewidth=1.5,
                   label=f"Ideal F1 = {d['ideal']['f1_mean']:.3f}")
        ax.axvline(d['realistic']['f1_mean'], color='red', linestyle=':', linewidth=1.5,
                   label=f"Realistic mean = {d['realistic']['f1_mean']:.3f}")
        ax.set_xlim(0, 1)
        ax.set_xlabel("Realistic macro F1")
        ax.set_ylabel("Count (per-noise samples)")
        ax.set_title(f"{PRETTY[mat_name]} (R_off/R_on = {d['ratio']:.2f}x)")
        ax.legend(fontsize=9, loc='upper left')
        ax.grid(True, linestyle='--', alpha=0.4)
    fig.suptitle("Bimodal Distribution of Realistic F1 — Stuck-at Fault Position Sensitivity",
                 fontsize=13, fontweight='bold')
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'bimodal_distribution.png'), dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("저장: figures/bimodal_distribution.png")

    # ---------- 막대 비교 ----------
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(results['materials']))
    width = 0.35
    ideal_means = [d['ideal']['f1_mean'] for d in results['materials'].values()]
    ideal_stds = [d['ideal']['f1_std'] for d in results['materials'].values()]
    real_means = [d['realistic']['f1_mean'] for d in results['materials'].values()]
    real_stds = [d['realistic']['f1_std'] for d in results['materials'].values()]
    labels = [PRETTY[k] for k in results['materials'].keys()]

    ax.bar(x - width / 2, ideal_means, width, yerr=ideal_stds, capsize=4,
           label='Ideal (quantization only)', color='#7FB3D5', edgecolor='black')
    ax.bar(x + width / 2, real_means, width, yerr=real_stds, capsize=4,
           label='Realistic (var + fault)', color='#E59866', edgecolor='black')
    ax.axhline(baseline_f1, color='gray', linestyle='--', linewidth=1,
               label=f'FP32 baseline = {baseline_f1:.4f}')
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=15)
    ax.set_ylabel('Macro F1 (mean ± std)')
    ax.set_title('Material Comparison — Ideal vs Realistic')
    ax.legend(loc='lower left', fontsize=9)
    ax.grid(True, axis='y', linestyle='--', alpha=0.4)
    ax.set_ylim(0, 1.05)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'material_comparison.png'), dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("저장: figures/material_comparison.png")

    # ---------- paired diff (ideal vs realistic) ----------
    paired_stats = {}
    for mat_name, d in results['materials'].items():
        ideal_per = [r['macro_f1'] for r in d['per_seed']['ideal']]  # 3
        real_per = [r['macro_f1'] for r in d['per_seed']['realistic']]  # 9
        ideal_arr = np.array(ideal_per)
        real_arr = np.array(real_per)
        paired_stats[mat_name] = {
            'ideal_mean': float(ideal_arr.mean()),
            'realistic_mean': float(real_arr.mean()),
            'mean_diff': float(real_arr.mean() - ideal_arr.mean()),
            'relative_drop_pct': float(
                (real_arr.mean() - ideal_arr.mean()) / ideal_arr.mean() * 100),
        }

    out_stats = {
        'baseline_macro_f1': baseline_f1,
        'bimodal_threshold': {'good': 0.88, 'catastrophic': 0.60},
        'bimodal_counts': stats_summary,
        'paired_stats': paired_stats,
    }
    with open(os.path.join(RESULTS_DIR, 'phase1_statistics.json'), 'w', encoding='utf-8') as f:
        json.dump(out_stats, f, indent=2, ensure_ascii=False)
    print("저장: results/phase1_statistics.json")

    # ---------- 콘솔 요약 ----------
    print("\n" + "=" * 60)
    print("Phase 1 통계 요약")
    print("=" * 60)
    for n, s in stats_summary.items():
        print(f"  {PRETTY[n]:20s}  good={s['good_ratio']*100:5.1f}%  "
              f"catastrophic={s['catastrophic_ratio']*100:5.1f}%  (n={s['total']})")


if __name__ == "__main__":
    main()
