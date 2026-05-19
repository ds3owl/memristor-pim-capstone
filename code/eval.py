"""
eval.py — VTEAM 기반 4 소재 매핑 후 ideal / realistic 평가

- 학습된 baseline 모델(3 seed)을 사용
- 각 소재에 대해:
    1. ideal: 컨덕턴스 매핑 + N_states 양자화만 (variation/fault 없음)
    2. realistic: variation(Gaussian noise) + stuck-at fault + 양자화
- accuracy(subset) + macro F1 둘 다 측정
- 결과: results/material_results.json
"""
import os
import json
import copy
import numpy as np
import torch
import torch.nn as nn

from data import get_dataloaders
from model import WaferCNN, multi_label_metrics


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CKPT_DIR = os.path.join(BASE_DIR, 'checkpoints')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
SEEDS = [42, 123, 456]          # baseline 학습 seed
NOISE_REPEATS = 3                # realistic 평가에서 noise sampling 반복 횟수 (Monte Carlo)
NOISE_SEED_BASE = 10_000         # noise seed offset (baseline seed와 분리)


# ============================================================
# VTEAM 4 소재 파라미터 (문헌 기반)
#   R_ON, R_OFF: 문헌 실측값 (Kvatinsky 2015 VTEAM Table II 등)
#   states: 안정적으로 구분 가능한 컨덕턴스 상태 수
#   var_on, var_off: device-to-device 변동 계수 (σ/μ)
#   fault_rate: stuck-at fault 비율 (LRS+HRS, 본 연구 가정값)
# ============================================================
MATERIALS = {
    'Pt_HfOx_Ti': {
        'R_on':  100.0,      'R_off':  2_500.0,
        'states': 64,
        'var_on': 0.10,      'var_off': 0.15,
        'fault_rate': 0.005,
        'reference': 'Kvatinsky 2015; Yalon 2012',
    },
    'Ferroelectric': {
        'R_on':  150_000.0,  'R_off': 50_000_000.0,
        'states': 128,
        'var_on': 0.08,      'var_off': 0.12,
        'fault_rate': 0.003,
        'reference': 'Kvatinsky 2015; Chanthbouala 2012',
    },
    'Metallic_Nanowire': {
        'R_on':  17.3,       'R_off': 34.0,
        'states': 4,
        'var_on': 0.05,      'var_off': 0.08,
        'fault_rate': 0.05,
        'reference': 'Kvatinsky 2015; Johnson 2010',
    },
    'TaOx_Ta': {
        'R_on':  4_800.0,    'R_off': 700_000.0,
        'states': 32,
        'var_on': 0.08,      'var_off': 0.10,
        'fault_rate': 0.003,
        'reference': 'Yakopcic 2020',
    },
}


def map_and_perturb(weight: torch.Tensor, params: dict, realistic: bool, rng: np.random.Generator):
    """가중치 행렬을 소재 컨덕턴스로 매핑 + 양자화 (+ realistic 시 variation/fault)."""
    w = weight.detach().clone()
    sign = torch.sign(w)
    w_abs = w.abs()

    if w_abs.max().item() < 1e-12:
        return w  # all zero

    # 1) [G_min, G_max]로 선형 매핑
    g_min = 1.0 / params['R_off']
    g_max = 1.0 / params['R_on']
    w_norm = w_abs / w_abs.max()
    g = g_min + (g_max - g_min) * w_norm

    if realistic:
        # 2-a) device-to-device variation (Gaussian multiplicative)
        sigma = (params['var_on'] + params['var_off']) / 2.0
        noise = torch.tensor(
            rng.normal(loc=1.0, scale=sigma, size=g.shape),
            dtype=g.dtype,
        )
        g = g * noise
        g = torch.clamp(g, min=g_min * 0.5, max=g_max * 1.5)

        # 2-b) stuck-at fault (절반 LRS, 절반 HRS)
        n = g.numel()
        n_fault = int(n * params['fault_rate'])
        if n_fault > 0:
            idx = rng.choice(n, size=n_fault, replace=False)
            flat = g.flatten()
            half = n_fault // 2
            flat[idx[:half]] = g_max         # stuck-LRS (저저항)
            flat[idx[half:]] = g_min         # stuck-HRS (고저항)
            g = flat.reshape(g.shape)

    # 3) N_states 양자화 (등간격)
    levels = torch.linspace(g_min, g_max, params['states'])
    diff = (g.unsqueeze(-1) - levels).abs()
    g_quant = levels[diff.argmin(dim=-1)]

    # 4) 컨덕턴스 → 가중치 역매핑
    w_back = (g_quant - g_min) / (g_max - g_min) * w_abs.max()
    return sign * w_back


@torch.no_grad()
def apply_material_to_model(model: nn.Module, params: dict, realistic: bool, seed: int):
    """모델의 모든 nn.Conv2d / nn.Linear 가중치에 매핑 적용 (사본 반환)."""
    new_model = copy.deepcopy(model)
    rng = np.random.default_rng(seed)
    for m in new_model.modules():
        if isinstance(m, (nn.Conv2d, nn.Linear)):
            m.weight.data = map_and_perturb(m.weight.data, params, realistic, rng)
    return new_model


def evaluate(model, loader, device, threshold: float = 0.5):
    model.eval()
    all_logits, all_targets = [], []
    with torch.no_grad():
        for x, y in loader:
            logits = model(x.to(device))
            all_logits.append(logits.cpu())
            all_targets.append(y.cpu())
    return multi_label_metrics(torch.cat(all_logits), torch.cat(all_targets), threshold)


def main():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"[eval.py] device = {device}")

    _, _, test_loader = get_dataloaders(batch_size=128)

    results = {'materials': {}, 'config': {
        'baseline_seeds': SEEDS,
        'noise_repeats_per_baseline_seed': NOISE_REPEATS,
        'noise_seed_strategy': 'NOISE_SEED_BASE * (baseline_seed+1) + r (baseline과 완전 분리)',
        'threshold': 0.5,
    }}

    for mat_name, params in MATERIALS.items():
        print("\n" + "=" * 60)
        print(f"[{mat_name}] R_off/R_on = {params['R_off']/params['R_on']:.2f}x  "
              f"| states = {params['states']}  | fault = {params['fault_rate']*100:.1f}%")
        print("=" * 60)

        per_seed = {'ideal': [], 'realistic': []}
        for seed in SEEDS:
            base = WaferCNN().to(device)
            base.load_state_dict(torch.load(
                os.path.join(CKPT_DIR, f'baseline_seed{seed}.pt'),
                map_location=device, weights_only=True))

            # ideal: variation/fault 없음, 양자화만 (deterministic → 1회만)
            #   ideal에서도 양자화 자체는 stochastic 아님. seed는 그래도 분리(이전과 다른 값) 사용.
            mi = apply_material_to_model(base, params, realistic=False,
                                          seed=NOISE_SEED_BASE + seed)
            acc_i, f1_i, pc_i = evaluate(mi, test_loader, device)
            per_seed['ideal'].append({'seed': seed, 'subset_acc': acc_i,
                                       'macro_f1': f1_i, 'per_class_f1': pc_i})
            print(f"  seed={seed:3d} | ideal: acc={acc_i:.4f} f1={f1_i:.4f}")

            # realistic: variation + fault + 양자화. noise sampling NOISE_REPEATS 회 반복 (Monte Carlo)
            #   noise seed는 baseline seed와 완전 분리 → realistic 평가의 분산이
            #   "baseline 학습 운"이 아닌 "noise sample 운"만 반영하도록 함.
            for r in range(NOISE_REPEATS):
                noise_seed = NOISE_SEED_BASE * (seed + 1) + r
                mr = apply_material_to_model(base, params, realistic=True, seed=noise_seed)
                acc_r, f1_r, pc_r = evaluate(mr, test_loader, device)
                per_seed['realistic'].append({
                    'baseline_seed': seed, 'noise_seed': noise_seed,
                    'subset_acc': acc_r, 'macro_f1': f1_r, 'per_class_f1': pc_r,
                })
                print(f"  seed={seed:3d}/n{r+1} | realistic: acc={acc_r:.4f} f1={f1_r:.4f}")

        ideal_acc = np.array([r['subset_acc'] for r in per_seed['ideal']])
        ideal_f1 = np.array([r['macro_f1'] for r in per_seed['ideal']])
        real_acc = np.array([r['subset_acc'] for r in per_seed['realistic']])
        real_f1 = np.array([r['macro_f1'] for r in per_seed['realistic']])

        results['materials'][mat_name] = {
            'parameters': params,
            'ratio': params['R_off'] / params['R_on'],
            'ideal':     {'acc_mean': float(ideal_acc.mean()), 'acc_std': float(ideal_acc.std()),
                          'f1_mean':  float(ideal_f1.mean()),  'f1_std':  float(ideal_f1.std())},
            'realistic': {'acc_mean': float(real_acc.mean()),  'acc_std': float(real_acc.std()),
                          'f1_mean':  float(real_f1.mean()),   'f1_std':  float(real_f1.std())},
            'f1_drop_pct': float((real_f1.mean() - ideal_f1.mean()) / ideal_f1.mean() * 100),
            'per_seed': per_seed,
        }
        print(f"  3-seed 평균 | ideal F1 = {ideal_f1.mean():.4f}±{ideal_f1.std():.4f} "
              f"| realistic F1 = {real_f1.mean():.4f}±{real_f1.std():.4f} "
              f"| Drop = {results['materials'][mat_name]['f1_drop_pct']:+.2f}%")

    out = os.path.join(RESULTS_DIR, 'material_results.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("[eval.py] 최종 요약 (3-seed 평균)")
    print("=" * 60)
    print(f"{'Material':22s} {'Ratio':>8s} {'Ideal F1':>10s} {'Real F1':>10s} {'Drop':>10s}")
    for n, d in results['materials'].items():
        print(f"{n:22s} {d['ratio']:>7.2f}x {d['ideal']['f1_mean']:>10.4f} "
              f"{d['realistic']['f1_mean']:>10.4f} {d['f1_drop_pct']:>+9.2f}%")
    print(f"\n저장: {out}")


if __name__ == "__main__":
    main()
