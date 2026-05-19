"""
eval_gaussian.py — 친구 방식 비교 실험

친구 코드 (https://github.com/ymc0315/capstone_comparison) 의 핵심:
    weight = weight * (1 + Gaussian(0, sigma))
즉, **multiplicative Gaussian noise만** (양자화 X, stuck-at fault X).

본 스크립트는 우리 4 소재 파라미터의 variation 값(σ/μ)을 그대로 사용하되,
양자화와 fault를 빼고 Gaussian noise만 줌. 우리 방식(eval.py)과의 직접 비교용.
"""
import os
import json
import copy
import numpy as np
import torch
import torch.nn as nn

from data import get_dataloaders
from model import WaferCNN, multi_label_metrics
from eval import MATERIALS, SEEDS, NOISE_REPEATS, NOISE_SEED_BASE


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CKPT_DIR = os.path.join(BASE_DIR, 'checkpoints')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')


@torch.no_grad()
def inject_gaussian(model: nn.Module, sigma: float, seed: int) -> nn.Module:
    """친구 방식: 모든 Conv/Linear 가중치에 multiplicative Gaussian noise만 주입."""
    new_model = copy.deepcopy(model)
    rng = np.random.default_rng(seed)
    for m in new_model.modules():
        if isinstance(m, (nn.Conv2d, nn.Linear)):
            noise = torch.tensor(
                rng.normal(loc=1.0, scale=sigma, size=tuple(m.weight.shape)),
                dtype=m.weight.dtype,
            )
            m.weight.data = m.weight.data * noise
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
    print(f"[eval_gaussian.py] device = {device}")
    print("(친구 방식: Gaussian multiplicative noise만, 양자화/fault 없음)\n")

    _, _, test_loader = get_dataloaders(batch_size=128)

    results = {
        'method': 'gaussian_only (multiplicative noise, no quantization, no fault)',
        'comparison_to': 'eval.py (ours: gaussian + stuck-at fault + N-states quantization)',
        'config': {
            'baseline_seeds': SEEDS,
            'noise_repeats': NOISE_REPEATS,
            'sigma_formula': '(var_on + var_off) / 2',
        },
        'materials': {},
    }

    for mat_name, params in MATERIALS.items():
        sigma = (params['var_on'] + params['var_off']) / 2.0
        print("=" * 60)
        print(f"[{mat_name}] sigma = {sigma:.4f} (= (var_on + var_off)/2)")
        print("=" * 60)

        per_run = []
        for seed in SEEDS:
            base = WaferCNN().to(device)
            base.load_state_dict(torch.load(
                os.path.join(CKPT_DIR, f'baseline_seed{seed}.pt'),
                map_location=device, weights_only=True))

            for r in range(NOISE_REPEATS):
                noise_seed = NOISE_SEED_BASE * (seed + 1) + r
                noisy = inject_gaussian(base, sigma, noise_seed)
                acc, f1, _ = evaluate(noisy, test_loader, device)
                per_run.append({
                    'baseline_seed': seed, 'noise_seed': noise_seed,
                    'subset_acc': acc, 'macro_f1': f1,
                })
                print(f"  seed={seed:3d}/n{r+1} | acc={acc:.4f} f1={f1:.4f}")

        f1s = np.array([r['macro_f1'] for r in per_run])
        accs = np.array([r['subset_acc'] for r in per_run])
        results['materials'][mat_name] = {
            'sigma': float(sigma),
            'ratio': params['R_off'] / params['R_on'],
            'acc_mean': float(accs.mean()), 'acc_std': float(accs.std()),
            'f1_mean': float(f1s.mean()), 'f1_std': float(f1s.std()),
            'per_run': per_run,
        }
        print(f"  >> 평균 | F1 = {f1s.mean():.4f} ± {f1s.std():.4f}")

    out = os.path.join(RESULTS_DIR, 'gaussian_only_results.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("[eval_gaussian.py] 친구 방식 결과 요약")
    print("=" * 60)
    print(f"{'Material':22s} {'Sigma':>8s} {'F1 mean':>10s} {'F1 std':>10s}")
    for n, d in results['materials'].items():
        print(f"{n:22s} {d['sigma']:>7.4f} {d['f1_mean']:>10.4f} {d['f1_std']:>10.4f}")
    print(f"\n저장: {out}")


if __name__ == "__main__":
    main()
