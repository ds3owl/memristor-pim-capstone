# Memristor PIM 웨이퍼 결함 분류 — 학부 캡스톤 디자인

> **4종 멤리스터 소재 파라미터를 활용한 PIM 환경 웨이퍼 결함 분류 성능 비교 연구**
> 상명대학교 시스템반도체공학과 · 임창우 · 지도교수 이종환 · 2026

## 한 줄 요약
VTEAM 문헌 파라미터를 정적 conductance mapping에 활용하여 4종 멤리스터 소재
(Pt/HfO<sub>x</sub>/Ti, Ferroelectric, Metallic Nanowire, TaO<sub>x</sub>/Ta)의 PIM 환경 웨이퍼 결함 분류
성능을 정량 비교하고, R<sub>off</sub>/R<sub>on</sub> 25배 이상이면 평균 성능은 보존되나 stuck-at fault
위치 무작위성에 의한 worst-case 붕괴가 관찰됨을 보였습니다.

## 핵심 결과 (3 baseline seed × 3 noise sample = 9회 평균)

| Material | R<sub>off</sub>/R<sub>on</sub> | States | Ideal F1 | Realistic F1 | ΔF1 |
|---|---|---|---|---|---|
| Pt/HfO<sub>x</sub>/Ti | 25.0× | 64 | 0.9826 | 0.7578 ± 0.2759 | −22.88% |
| Ferroelectric | 333.3× | 128 | 0.9805 | 0.8570 ± 0.1632 | −12.60% |
| Metallic Nanowire | **1.97×** | **4** | **0.3847** | 0.3288 ± 0.1286 | −14.53% |
| TaO<sub>x</sub>/Ta | 145.8× | 32 | 0.9770 | 0.8726 ± 0.1364 | −10.69% |

- **FP32 software baseline**: macro F1 = 0.9812 ± 0.0032
- **NW는 ideal 조건(fault=0)에서도 F1=0.38로 붕괴** → 4-state 양자화의 본질적 한계
- **고저항비 세 소재에서 각각 9회 중 1회 worst-case 붕괴(F1<0.60) 관찰**

## 폴더 구조
```
memristor_pim_capstone/
├── paper.html                  ← 최종 논문 (그림 base64 embed, 단독 표시 가능)
├── 교수님_보고용.html           ← 학술 요약 (4~5p)
├── 내가_이해하는용.html         ← 본인 학습용 가이드 + 디펜스 Q&A
├── code/                       ← Python 코드
│   ├── data.py                 (MixedWM38 전처리)
│   ├── model.py                (WaferCNN)
│   ├── train.py                (3 seed baseline 학습)
│   ├── eval.py                 (4 소재 × ideal/realistic 평가)
│   ├── analyze.py              (Worst-case 분포 분석)
│   └── embed_figures.py        (그림 base64 embed)
├── checkpoints/                ← 학습된 baseline 모델 3개 (.pt)
├── figures/                    ← 결과 그림 (paper.html에 이미 embed)
├── data/                       ← (전처리 데이터는 .gitignore. data.py로 재생성)
└── results/                    ← JSON 결과, 분석 markdown, 토론 기록
```

## 실행 방법

### 1. 데이터 준비
[MixedWM38 데이터셋](https://github.com/Junliangwangdhu/WaferMap)을 다운로드 후
`~/Downloads/Wafer_Map_Datasets.npz` 위치에 배치.

### 2. 학습 & 평가
```bash
cd code
python data.py     # 전처리 (data/mixedwm38_processed.pth 생성, 약 383MB)
python train.py    # baseline 3 seed 학습 (~15분 CPU)
python eval.py     # 4 소재 × ideal/realistic 평가 (~30분 CPU)
python analyze.py  # Worst-case 분포 분석 + 그림 생성
```

### 환경
- Python 3.11, PyTorch 2.11 (CPU 또는 CUDA)
- 의존성: `torch`, `numpy`, `sklearn`, `matplotlib`

## 방법론 요약

### 데이터셋
- **MixedWM38** (Wang et al., IEEE TSM 2020): 52×52 binary wafer map, 8개 결함 클래스 multi-label
- 38,015장 중 normal/no-defect 1,000장 제외 → 37,015장 사용
- Train/Val/Test = 7:1:2 (seed=42 고정)

### CNN 모델 (고정 기준)
- 3 Conv (16→32→64, BN+ReLU+MaxPool) + FC(128, Dropout 0.3) + FC(8)
- 총 파라미터: 319,592
- 손실: BCEWithLogitsLoss · 최적화: Adam (lr=1e-3, batch=128)
- Max 20 epoch + Early Stopping (patience=5, val macro-F1)

### 매핑 파이프라인 (4단계)
1. **레이어별 정규화 + 부호 분리**: W = sign(W)·|W|, |W|/max(|W|)
2. **선형 매핑**: [G<sub>min</sub>, G<sub>max</sub>] = [1/R<sub>off</sub>, 1/R<sub>on</sub>]
3. **비이상성 주입 (Realistic)**: variation (Gaussian) + stuck-at fault (LRS/HRS 절반씩 고정)
4. **N-state 양자화**: 등간격 nearest-state rounding

## 핵심 발견 3가지
1. **저항비 임계 부근의 분기** — R<sub>off</sub>/R<sub>on</sub> 25× 이상은 ideal 보존, NW는 ideal부터 붕괴
2. **NW의 본질적 한계** — 4-state 양자화로 fault rate 무관하게 분류 성능 성립 불가
3. **Worst-case 붕괴** — 고저항비 소재도 stuck-at fault 위치에 따라 약 11% 빈도 catastrophic 위험

## 한계 (정직히 명시)
- 단일 데이터셋 (MixedWM38만), 경량 CNN, 저항비 sweep 미수행
- 회로 수준 비이상성(IR drop, sneak path, ADC) 미반영
- 표본 한계(9회/소재) — 통계적 유의성 검정 미수행
- VTEAM 동역학 방정식 직접 적분 미수행 (정적 mapping에만 활용)

자세한 내용은 [`paper.html`](paper.html) 참고.

## 참고문헌 (핵심)
- [1] S. Kvatinsky et al., "VTEAM: A General Model for Voltage-Controlled Memristors," IEEE TCAS-II, 2015.
- [2] J. Wang et al., "Deformable Convolutional Networks for Efficient Mixed-type Wafer Defect Pattern Recognition," IEEE TSM, 2020.
- 전체 12개 인용은 `paper.html` References 절 참고.

## 라이선스
학부 캡스톤 디자인 결과물. 학술·교육 목적 자유 사용.
