"""
make_explain_figures.py — 입문자용 설명 그림 3종 생성 (교수님 요구 반영)

1) wafer_defect_examples.png : MixedWM38 8종 결함 패턴 실제 예시 (어떤 defect를 잡는가)
2) cnn_architecture.png      : WaferCNN 구조도 + conv 동작 개념 (CNN이 어떻게 동작하는가)
3) pipeline_overview.png     : 전체 연구 파이프라인 한눈에 보기

출력: ../figures/
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

# 한글 폰트 (Windows)
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(BASE, "figures")
os.makedirs(FIG, exist_ok=True)
RAW = os.path.join(os.path.expanduser("~"), "Downloads", "Wafer_Map_Datasets.npz")

CLASSES = ["Center", "Donut", "Edge-Loc", "Edge-Ring", "Loc", "Near-Full", "Random", "Scratch"]
KOR = {  # 입문자용 짧은 한국어 설명
    "Center": "중심부 결함",
    "Donut": "도넛형(고리 내부)",
    "Edge-Loc": "가장자리 국소",
    "Edge-Ring": "가장자리 고리",
    "Loc": "국소 군집",
    "Near-Full": "거의 전면",
    "Random": "무작위 산재",
    "Scratch": "선형 스크래치",
}

# 웨이퍼맵 색: 0=웨이퍼 밖(흰), 1=정상 die(연회색), 2=결함 die(빨강)
WAFER_CMAP = ListedColormap(["#ffffff", "#cfd8dc", "#d32f2f"])


# ---------------------------------------------------------------------------
# 1) 웨이퍼 결함 8종 예시
# ---------------------------------------------------------------------------
def _pick_representative(X, Y, ci, cls_name):
    """클래스별 '전형적인' 단일결함 샘플 1개 선택.
    - 일반 클래스: 클래스 평균 결함분포(템플릿)에 가장 잘 정렬되는 샘플
    - Scratch: 결함 화소가 선형으로 길게 뻗은(elongation 큰) 샘플
    과도/과소 결함 샘플은 화소 수 20~80 백분위로 제한해 배제."""
    cand = np.where((Y.sum(axis=1) == 1) & (Y[:, ci] == 1))[0]
    masks = (X[cand] == 2)                          # (n, 52, 52) bool
    flat = masks.reshape(len(cand), -1).astype(float)
    counts = flat.sum(axis=1)
    template = masks.mean(axis=0).reshape(-1)        # 평균 결함 밀도
    align = (flat * template).sum(axis=1) / (counts + 1e-9)

    if cls_name == "Scratch":
        score = np.zeros(len(cand))
        for k, m in enumerate(masks):
            ys, xs = np.nonzero(m)
            if len(xs) < 5:
                continue
            pts = np.stack([xs, ys]).astype(float)
            pts -= pts.mean(axis=1, keepdims=True)
            ev = np.linalg.eigvalsh(pts @ pts.T / len(xs))
            score[k] = ev[-1] / (ev[0] + 1e-9)       # 장축/단축 비 → 선형성
    else:
        score = align

    lo, hi = np.percentile(counts, [20, 80])
    band = np.where((counts >= lo) & (counts <= hi))[0]
    pool = band if len(band) else np.arange(len(cand))
    return cand[pool[np.argmax(score[pool])]]


def fig_defect_examples():
    raw = np.load(RAW, allow_pickle=True)
    X, Y = raw["arr_0"], raw["arr_1"]

    fig, axes = plt.subplots(2, 4, figsize=(11, 7.4))
    for i, cls in enumerate(CLASSES):
        ax = axes[i // 4][i % 4]
        idx = _pick_representative(X, Y, i, cls)
        ax.imshow(X[idx], cmap=WAFER_CMAP, vmin=0, vmax=2, interpolation="nearest")
        ax.set_title(f"{cls}\n({KOR[cls]})", fontsize=11, pad=6)
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_edgecolor("#90a4ae")
    fig.suptitle("MixedWM38 웨이퍼 결함 8종 — 본 연구가 분류 대상으로 삼는 패턴",
                 fontsize=13, y=0.99)
    # 범례
    from matplotlib.patches import Patch
    handles = [Patch(facecolor="#ffffff", edgecolor="#90a4ae", label="웨이퍼 밖"),
               Patch(facecolor="#cfd8dc", edgecolor="#90a4ae", label="정상 die"),
               Patch(facecolor="#d32f2f", edgecolor="#90a4ae", label="결함 die")]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False,
               fontsize=10, bbox_to_anchor=(0.5, 0.075))
    fig.text(0.5, 0.025,
             "※ 각 칸은 단일 결함 대표 예시. 실제 학습·평가 데이터는 복합(multi-label) 결함을 포함한다.",
             ha="center", fontsize=9, color="#546e7a")
    fig.subplots_adjust(top=0.90, bottom=0.13, hspace=0.45, wspace=0.15)
    out = os.path.join(FIG, "wafer_defect_examples.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("saved:", out)


# ---------------------------------------------------------------------------
# 2) CNN 구조도 + conv 동작 개념
# ---------------------------------------------------------------------------
def _block(ax, x, y, w, h, depth_n, color, label):
    """3D 느낌 feature-map 블록(겹친 사각형)."""
    off = 0.06
    for k in range(depth_n - 1, -1, -1):
        c = color if k == 0 else color
        a = 1.0 if k == 0 else 0.25
        ax.add_patch(Rectangle((x + k * off, y + k * off), w, h,
                               facecolor=c, edgecolor="#37474f", lw=1.0, alpha=a, zorder=10 - k))
    ax.text(x + w / 2, y - 0.20, label, ha="center", va="top", fontsize=13)


def fig_cnn_architecture():
    fig, ax = plt.subplots(figsize=(12, 5.2))
    ax.set_xlim(0, 13); ax.set_ylim(0, 6); ax.axis("off")

    # 입력
    _block(ax, 0.3, 2.4, 1.0, 1.0, 1, "#cfd8dc", "입력\n52×52×1")
    # 3 conv 스테이지 (공간↓, 채널↑)
    stages = [
        (2.2, "16채널\n26×26", 0.9, 4, "#90caf9"),
        (4.6, "32채널\n13×13", 0.7, 6, "#64b5f6"),
        (7.0, "64채널\n6×6", 0.5, 8, "#1e88e5"),
    ]
    prev_x = 1.3
    for x, lab, sz, dep, col in stages:
        y = 3 - sz / 2
        _block(ax, x, y, sz, sz, dep, col, lab)
        arr = FancyArrowPatch((prev_x + 0.05, 2.9), (x - 0.15, 2.9),
                              arrowstyle="-|>", mutation_scale=16, color="#455a64", lw=1.6)
        ax.add_patch(arr)
        # 반복되는 Conv 동작은 화살표마다 짧게만 표기(상세는 하단 캡션)
        ax.text((prev_x + x) / 2 - 0.05, 3.35,
                "Conv 3×3\n+Pool ½", ha="center",
                va="bottom", fontsize=12, color="#37474f")
        prev_x = x + sz + dep * 0.06

    # FC 부분
    fcx = 9.2
    arr = FancyArrowPatch((prev_x, 2.9), (fcx - 0.1, 2.9), arrowstyle="-|>",
                          mutation_scale=16, color="#455a64", lw=1.6)
    ax.add_patch(arr)
    ax.text((prev_x + fcx) / 2, 3.35, "Flatten\n(2304)", ha="center", va="bottom", fontsize=12)
    # FC128
    ax.add_patch(Rectangle((fcx, 1.6), 0.35, 2.6, facecolor="#ffb74d", edgecolor="#37474f"))
    ax.text(fcx + 0.17, 1.42, "FC 128\n+Dropout", ha="center", va="top", fontsize=12)
    # FC8 (출력)
    out_x = 10.6
    arr = FancyArrowPatch((fcx + 0.4, 2.9), (out_x - 0.1, 2.9), arrowstyle="-|>",
                          mutation_scale=16, color="#455a64", lw=1.6)
    ax.add_patch(arr)
    labels = CLASSES
    for j, cl in enumerate(labels):
        yy = 4.7 - j * 0.46
        ax.add_patch(Rectangle((out_x, yy), 0.32, 0.34, facecolor="#a5d6a7", edgecolor="#37474f"))
        ax.text(out_x + 0.45, yy + 0.17, cl, ha="left", va="center", fontsize=12)
    ax.text(out_x + 0.15, 5.25, "8 logits → Sigmoid 확률\n(threshold 0.5)", ha="center", va="bottom", fontsize=12)

    ax.text(6.5, 5.78, "WaferCNN 구조 — 3 Conv + 2 FC (총 319,592 파라미터)",
            ha="center", fontsize=17, weight="bold")
    # conv 개념 캡션
    ax.text(6.5, 0.28,
            "Conv 층은 작은 3×3 필터(pad=1, 크기 유지)를 이미지 전체에 미끄러뜨리며 국소 패턴(가장자리·고리·선)을 검출하고,\n"
            "MaxPool 2×2가 해상도를 절반으로 줄여(52→26→13→6) 점점 더 넓은 범위의 패턴을 본다.\n"
            "마지막 FC 층은 8개 logit을 내고, Sigmoid가 클래스별 확률로 변환 — 여러 결함이 동시에 1이 될 수 있다(multi-label).",
            ha="center", va="bottom", fontsize=11.5, color="#37474f")
    fig.tight_layout()
    out = os.path.join(FIG, "cnn_architecture.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("saved:", out)


# ---------------------------------------------------------------------------
# 3) 전체 파이프라인
# ---------------------------------------------------------------------------
def fig_pipeline():
    fig, ax = plt.subplots(figsize=(12, 4.6))
    ax.set_xlim(0, 12); ax.set_ylim(0, 4.6); ax.axis("off")

    boxes = [
        (0.2, "① 웨이퍼 결함 맵\nMixedWM38\n52×52, 8클래스", "#e3f2fd"),
        (2.5, "② CNN 학습\n(소프트웨어 FP32)\nmacro-F1 0.98", "#bbdefb"),
        (4.8, "③ 학습된 가중치 W\n→ 컨덕턴스 G\n선형 매핑", "#fff9c4"),
        (7.1, "④ 멤리스터 크로스바\n4종 소재 + 양자화\n+ 비이상성(노이즈·고착)", "#ffe0b2"),
        (9.4, "⑤ PIM 추론 평가\n(추론만 하드웨어)\nIdeal vs Realistic", "#c8e6c9"),
    ]
    w, h, y = 2.0, 2.2, 1.45
    centers = []
    for x, txt, col in boxes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.12",
                                    facecolor=col, edgecolor="#37474f", lw=1.2))
        ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=12.5)
        centers.append(x + w)
    for i in range(len(boxes) - 1):
        x0 = boxes[i][0] + w
        x1 = boxes[i + 1][0]
        arr = FancyArrowPatch((x0 - 0.02, y + h / 2), (x1 + 0.02, y + h / 2),
                              arrowstyle="-|>", mutation_scale=20, color="#455a64", lw=1.8)
        ax.add_patch(arr)
    ax.text(6.0, 4.30, "연구 전체 흐름: 웨이퍼 결함 분류 CNN을 멤리스터 PIM 하드웨어로 옮길 때 소재별 성능 비교",
            ha="center", fontsize=15, weight="bold")
    ax.text(6.0, 0.78,
            "학습은 소프트웨어(FP32)에서 수행하고, 학습된 가중치를 멤리스터로 매핑해 추론 단계만 PIM 환경에서 평가한다.",
            ha="center", va="center", fontsize=12, color="#546e7a")
    ax.text(6.0, 0.34,
            "핵심 질문: 4종 멤리스터 소재(Pt/HfOx/Ti, Ferroelectric, Metallic Nanowire, TaOx/Ta) 중\n"
            "어떤 것이 PIM 환경에서 분류 성능을 가장 잘 보존하는가?",
            ha="center", va="center", fontsize=12.5, color="#37474f")
    fig.tight_layout()
    out = os.path.join(FIG, "pipeline_overview.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("saved:", out)


if __name__ == "__main__":
    fig_defect_examples()
    fig_cnn_architecture()
    fig_pipeline()
    print("\n[완료] figures/ 에 3종 생성")
