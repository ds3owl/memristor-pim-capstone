"""
data.py — MixedWM38 데이터셋 로딩 및 전처리

- 원본: ~/Downloads/Wafer_Map_Datasets.npz (Wang et al., MixedWM38)
- 38,015장 웨이퍼 맵, 52x52 픽셀, 8 클래스 multi-hot 라벨
- multi-label 분류 (multi-hot 그대로 유지, argmax 변환 X)
- Train / Val / Test = 7 / 1 / 2 (seed=42 고정)
"""
import os
import json
import numpy as np
import torch
from torch.utils.data import TensorDataset, DataLoader
from sklearn.model_selection import train_test_split


CLASSES = ['Center', 'Donut', 'Edge-Loc', 'Edge-Ring',
           'Loc', 'Near-Full', 'Random', 'Scratch']
NUM_CLASSES = len(CLASSES)
RAW_PATH = os.path.join(os.path.expanduser('~'), 'Downloads', 'Wafer_Map_Datasets.npz')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')


def preprocess(seed: int = 42, save: bool = True):
    """원본 npz 파일을 로딩하고 7:1:2 split으로 분할."""
    print("=" * 60)
    print("[data.py] MixedWM38 전처리 시작")
    print("=" * 60)

    if not os.path.exists(RAW_PATH):
        raise FileNotFoundError(f"원본 데이터가 없습니다: {RAW_PATH}")

    raw = np.load(RAW_PATH, allow_pickle=True)
    X = raw['arr_0']  # (38015, 52, 52) int
    Y = raw['arr_1']  # (38015, 8) int (multi-hot)
    print(f"  원본: X={X.shape}, Y={Y.shape}")

    # 라벨 합이 0인(=라벨 없음) 샘플 제외
    mask = Y.sum(axis=1) > 0
    X, Y = X[mask], Y[mask]
    removed = int((~mask).sum())
    print(f"  라벨 없음 제외: {removed}장")
    print(f"  유효 샘플: {len(X)}장")

    # 단일 결함 vs 복합 결함 분포
    label_count = Y.sum(axis=1)
    n_single = int((label_count == 1).sum())
    n_multi = int((label_count > 1).sum())
    print(f"  단일 결함: {n_single}장 / 복합 결함: {n_multi}장")

    # 클래스별 분포
    print("  클래스 분포 (multi-hot 합계):")
    class_counts = {}
    for i, c in enumerate(CLASSES):
        n = int(Y[:, i].sum())
        class_counts[c] = n
        print(f"    {c:12s}: {n:6d}장 ({n / len(Y) * 100:5.1f}%)")

    # 텐서 변환 (픽셀 0/1/2 -> 0.0/0.5/1.0 정규화)
    X_t = torch.tensor(X, dtype=torch.float32).unsqueeze(1) / 2.0   # (N, 1, 52, 52)
    Y_t = torch.tensor(Y, dtype=torch.float32)                       # (N, 8) multi-hot

    # 7:1:2 split (seed=42 고정)
    idx = np.arange(len(X_t))
    idx_trainval, idx_test = train_test_split(idx, test_size=0.2, random_state=seed)
    idx_train, idx_val = train_test_split(idx_trainval, test_size=0.125, random_state=seed)

    splits = {
        'X_train': X_t[idx_train], 'Y_train': Y_t[idx_train],
        'X_val':   X_t[idx_val],   'Y_val':   Y_t[idx_val],
        'X_test':  X_t[idx_test],  'Y_test':  Y_t[idx_test],
        'classes': np.array(CLASSES),
    }
    print(f"  Train/Val/Test = {len(idx_train)}/{len(idx_val)}/{len(idx_test)} "
          f"({len(idx_train)/len(X_t)*100:.0f}/{len(idx_val)/len(X_t)*100:.0f}/{len(idx_test)/len(X_t)*100:.0f})")

    if save:
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(RESULTS_DIR, exist_ok=True)
        out = os.path.join(DATA_DIR, 'mixedwm38_processed.pth')
        torch.save(splits, out)
        print(f"  저장: {out}")

        summary = {
            'dataset': 'MixedWM38 (Wang et al., 2020)',
            'raw_samples': int(raw['arr_0'].shape[0]),
            'removed_unlabeled': removed,
            'final_samples': int(len(X)),
            'image_size': [52, 52],
            'num_classes': NUM_CLASSES,
            'classes': CLASSES,
            'paradigm': 'multi-label (multi-hot)',
            'single_defect': n_single,
            'multi_defect': n_multi,
            'class_counts': class_counts,
            'split_seed': seed,
            'split_ratio': '70/10/20',
            'normalization': 'pixel /2.0 (0,1,2 -> 0.0, 0.5, 1.0)',
            'train_size': int(len(idx_train)),
            'val_size': int(len(idx_val)),
            'test_size': int(len(idx_test)),
        }
        sum_path = os.path.join(RESULTS_DIR, 'dataset_summary.json')
        with open(sum_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"  요약: {sum_path}")

    return splits


def get_dataloaders(batch_size: int = 128):
    """저장된 split을 불러와 DataLoader 반환."""
    path = os.path.join(DATA_DIR, 'mixedwm38_processed.pth')
    if not os.path.exists(path):
        print(f"전처리 파일 없음. preprocess() 먼저 실행합니다.")
        preprocess()
    splits = torch.load(path, weights_only=False)

    train = DataLoader(TensorDataset(splits['X_train'], splits['Y_train']),
                       batch_size=batch_size, shuffle=True)
    val = DataLoader(TensorDataset(splits['X_val'], splits['Y_val']),
                     batch_size=batch_size, shuffle=False)
    test = DataLoader(TensorDataset(splits['X_test'], splits['Y_test']),
                      batch_size=batch_size, shuffle=False)
    return train, val, test


if __name__ == "__main__":
    preprocess()
    print("\n[data.py] 정상 동작 확인")
