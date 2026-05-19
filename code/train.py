"""
train.py — 3 seed Baseline 학습 (FP32 소프트웨어 기준선)

- Adam (lr=1e-3), BCEWithLogits, batch=128
- Early Stopping (val macro-F1 기준, patience=5)
- 3 seed (42, 123, 456) → 각 best 체크포인트 + 학습 로그 저장
- 최종: results/baseline_results.json
"""
import os
import json
import time
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from data import get_dataloaders
from model import WaferCNN, count_parameters, multi_label_metrics


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CKPT_DIR = os.path.join(BASE_DIR, 'checkpoints')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
SEEDS = [42, 123, 456]
MAX_EPOCH = 20
PATIENCE = 5
LR = 1e-3
BATCH = 128


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def evaluate(model, loader, device, threshold: float = 0.5):
    model.eval()
    all_logits, all_targets = [], []
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            logits = model(x)
            all_logits.append(logits.cpu())
            all_targets.append(y.cpu())
    logits = torch.cat(all_logits)
    targets = torch.cat(all_targets)
    return multi_label_metrics(logits, targets, threshold=threshold)


def train_one_seed(seed: int, device: torch.device):
    print("\n" + "=" * 60)
    print(f"[train.py] Seed = {seed}")
    print("=" * 60)
    set_seed(seed)

    train_loader, val_loader, test_loader = get_dataloaders(batch_size=BATCH)
    model = WaferCNN().to(device)
    n_params = count_parameters(model)
    print(f"  파라미터 수: {n_params:,}")

    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(model.parameters(), lr=LR)

    best_val_f1 = -1.0
    best_epoch = -1
    bad_epochs = 0
    history = []

    t0 = time.time()
    for epoch in range(1, MAX_EPOCH + 1):
        model.train()
        running = 0.0
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            loss = criterion(model(x), y)
            loss.backward()
            optimizer.step()
            running += loss.item()
        train_loss = running / len(train_loader)

        val_acc, val_f1, _ = evaluate(model, val_loader, device)
        history.append({
            'epoch': epoch, 'train_loss': train_loss,
            'val_subset_acc': val_acc, 'val_macro_f1': val_f1,
        })
        print(f"  Epoch {epoch:2d}/{MAX_EPOCH} | loss={train_loss:.4f} | "
              f"val_acc={val_acc:.4f} | val_f1={val_f1:.4f}")

        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            best_epoch = epoch
            bad_epochs = 0
            os.makedirs(CKPT_DIR, exist_ok=True)
            torch.save(model.state_dict(),
                       os.path.join(CKPT_DIR, f'baseline_seed{seed}.pt'))
        else:
            bad_epochs += 1
            if bad_epochs >= PATIENCE:
                print(f"  Early stopping (best epoch={best_epoch}, val_f1={best_val_f1:.4f})")
                break
    elapsed = time.time() - t0

    # best 체크포인트로 test 평가
    model.load_state_dict(torch.load(
        os.path.join(CKPT_DIR, f'baseline_seed{seed}.pt'),
        map_location=device, weights_only=True))
    test_acc, test_f1, per_class_f1 = evaluate(model, test_loader, device)
    print(f"  Test  : acc={test_acc:.4f} | macro_f1={test_f1:.4f}")
    print(f"  소요  : {elapsed:.1f}s")

    return {
        'seed': seed,
        'n_params': n_params,
        'best_epoch': best_epoch,
        'best_val_f1': best_val_f1,
        'test_subset_acc': test_acc,
        'test_macro_f1': test_f1,
        'test_per_class_f1': per_class_f1,
        'elapsed_sec': elapsed,
        'history': history,
    }


def main():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"[train.py] device = {device}")

    all_results = []
    for s in SEEDS:
        all_results.append(train_one_seed(s, device))

    # 통계
    accs = [r['test_subset_acc'] for r in all_results]
    f1s = [r['test_macro_f1'] for r in all_results]
    summary = {
        'seeds': SEEDS,
        'n_seeds': len(SEEDS),
        'test_subset_acc_mean': float(np.mean(accs)),
        'test_subset_acc_std': float(np.std(accs)),
        'test_macro_f1_mean': float(np.mean(f1s)),
        'test_macro_f1_std': float(np.std(f1s)),
        'per_seed': all_results,
    }
    os.makedirs(RESULTS_DIR, exist_ok=True)
    out = os.path.join(RESULTS_DIR, 'baseline_results.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print("\n" + "=" * 60)
    print(f"[train.py] 완료. 3 seed 평균:")
    print(f"  Subset Accuracy = {summary['test_subset_acc_mean']:.4f} "
          f"± {summary['test_subset_acc_std']:.4f}")
    print(f"  Macro F1        = {summary['test_macro_f1_mean']:.4f} "
          f"± {summary['test_macro_f1_std']:.4f}")
    print(f"  저장: {out}")


if __name__ == "__main__":
    main()
