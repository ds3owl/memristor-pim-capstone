# Phase 1 자체 체크리스트

## 목적
**"멤리스터를 소재별로 CNN에 돌려서 웨이퍼 defect를 찾는다"** — 본질에 부합하는 코드·실험·결과가 깨끗하게 나왔는가.

## 산출물
- `code/data.py`, `model.py`, `train.py`, `eval.py` (4 파일, 친구 구조와 비슷한 단순함)
- `data/mixedwm38_processed.pth` (전처리 텐서)
- `checkpoints/baseline_seed{42,123,456}.pt` (3 baseline 체크포인트)
- `results/dataset_summary.json` (데이터 통계)
- `results/baseline_results.json` (3 seed 학습 결과)
- `results/material_results.json` (4 소재 × ideal/realistic 결과 — 평가 완료 후)

## 자체 체크리스트

### A. 코드 vs 본문 일관성 (이전 논문 최대 약점)
- [x] 분류 패러다임 명확 (multi-label sigmoid + threshold 0.5)
- [x] 라벨 처리 명확 (multi-hot 그대로, argmax 변환 X)
- [x] Split 명확 (7:1:2, seed=42 고정)
- [x] CNN 구조와 파라미터 수 일치 (319,592, 본문에 "약 32만"으로 명시)
- [x] 손실 명확 (BCEWithLogitsLoss)

### B. 본질 부합
- [x] 4 소재 비교 유지
- [x] VTEAM 모델 적용 (Kvatinsky 2015 Table II 파라미터)
- [x] ideal/realistic 분리 평가
- [x] 본 실험 1 데이터셋(MixedWM38)으로 단순화

### C. 데이터 정직성
- [x] 데이터셋 정체 명시 (MixedWM38, Wang et al.)
- [x] 라벨 없음 1000장 제외 후 37,015 유효 (코드와 통계 일치)
- [x] 클래스 불균형 명시 (Near-Full 0.4%, Scratch 2.3% 등)
- [x] 단일 결함 7K / 복합 결함 30K 명시 (multi-label 정당성)

### D. 신뢰성
- [x] 3 seed (42, 123, 456) 반복
- [x] Early Stopping (val macro-F1 기준)
- [x] Subset Acc + Macro F1 둘 다 측정 (친구 약점 보강)
- [x] 결과 통계 (mean ± std) 자동 계산

### E. 친구 약점 보강
- [x] multi-label argmax 변환 X (친구 step1 vs 본 코드 차이)
- [x] memtorch 의존 X — 가중치 매핑·양자화·variation·fault 자체 구현
- [x] 노이즈 + 매핑 분리 (ideal=양자화만 / realistic=양자화+variation+fault)
- [x] 평가 지표 2개 (accuracy + F1)
- [x] Seed 1회 → 3회

### F. Phase 2 진입 가능 여부
- [ ] 평가 결과(material_results.json) 정상 생성
- [ ] 4 소재 간 차이가 본질에 부합 (R_off/R_on 큰 소재 vs Metallic Nanowire)
- [ ] Phase 2 본문 작성에 필요한 모든 수치·표·통계 확보

## Phase 2 진입 판정 기준
1. baseline 3 seed F1 std < 0.01 (안정적) — **확인: 0.0032 ✓**
2. 4 소재 평가가 에러 없이 완료
3. 4 소재 F1 평균에 의미 있는 차이 (Metallic Nanowire와 나머지 간 명확한 갭) — eval 결과 보고 판정

## 알려진 제한 (limitations로 명시 예정)
- 단일 데이터셋(MixedWM38). WM-811K 미포함.
- 사이드 sweep(ratio/states/fault/variation) 제외.
- 통계는 mean±std + paired diff. ANOVA/effect size 제외.
- 3 seed (학회 표준 5 seed보다 적음).
