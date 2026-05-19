"""
model.py — WaferCNN 정의 및 평가 지표

- 입력: (N, 1, 52, 52) 회색조 웨이퍼 맵
- 출력: (N, 8) logits (multi-label sigmoid → 임계 0.5)
- 구조: 3 Conv + BN + ReLU + MaxPool → FC(128) + Dropout(0.3) → FC(8)
- 손실: BCEWithLogitsLoss (multi-label 표준)
"""
import torch
import torch.nn as nn


class WaferCNN(nn.Module):
    """3층 CNN + 2층 FC. multi-label 분류용 logits 출력."""

    def __init__(self, num_classes: int = 8, dropout: float = 0.3):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, padding=1),
            nn.BatchNorm2d(16), nn.ReLU(inplace=True),
            nn.MaxPool2d(2),                              # 52 -> 26
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32), nn.ReLU(inplace=True),
            nn.MaxPool2d(2),                              # 26 -> 13
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64), nn.ReLU(inplace=True),
            nn.MaxPool2d(2),                              # 13 -> 6
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 6 * 6, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(128, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.features(x))


def count_parameters(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def multi_label_metrics(logits: torch.Tensor, targets: torch.Tensor, threshold: float = 0.5):
    """multi-label 분류 평가 지표.

    반환:
        subset_acc: 모든 라벨이 정확히 일치한 샘플 비율
        macro_f1:   클래스별 F1의 단순 평균 (클래스 불균형 강건)
        per_class_f1: 각 클래스의 F1
    """
    probs = torch.sigmoid(logits)
    preds = (probs >= threshold).float()
    t = targets.float()

    # subset accuracy (exact match)
    subset_acc = (preds == t).all(dim=1).float().mean().item()

    # per-class F1
    eps = 1e-9
    tp = (preds * t).sum(dim=0)
    fp = (preds * (1 - t)).sum(dim=0)
    fn = ((1 - preds) * t).sum(dim=0)
    precision = tp / (tp + fp + eps)
    recall = tp / (tp + fn + eps)
    f1 = 2 * precision * recall / (precision + recall + eps)
    macro_f1 = f1.mean().item()
    per_class_f1 = f1.cpu().numpy().tolist()

    return subset_acc, macro_f1, per_class_f1


if __name__ == "__main__":
    m = WaferCNN()
    n = count_parameters(m)
    x = torch.zeros(2, 1, 52, 52)
    y = m(x)
    print(f"파라미터 수: {n:,}")
    print(f"입력 {tuple(x.shape)} -> 출력 {tuple(y.shape)}")
