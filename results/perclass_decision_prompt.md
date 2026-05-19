# Per-class F1 본문 추가 여부 — 셋이 토론

## 상황
paper.html v6 (이미 3자 통과 + GitHub Public 푸시 완료) 본문에는 결함 유형별(per-class) F1 표/그림 없음.
다만 JSON에는 4 소재 × 2 조건(ideal/realistic) × 8 클래스 데이터가 다 저장되어 있음.

## 실측 per-class F1 (3 seed / 9 sample 평균)

### Ideal 조건
| 소재 | Center | Donut | Edge-Loc | Edge-Ring | Loc | Near-Full | Random | Scratch |
|---|---|---|---|---|---|---|---|---|
| Pt | 1.00 | 1.00 | 0.98 | 0.99 | 0.99 | 0.93 | 0.99 | 0.98 |
| Ferro | 1.00 | 1.00 | 0.98 | 0.99 | 0.98 | 0.92 | 0.99 | 0.98 |
| **NW** | 0.29 | 0.73 | 0.67 | **0.00** | 0.67 | **0.00** | 0.72 | **0.01** |
| TaOx | 1.00 | 1.00 | 0.98 | 0.99 | 0.98 | 0.92 | 0.99 | 0.97 |

### Realistic 조건
| 소재 | Center | Donut | Edge-Loc | Edge-Ring | Loc | Near-Full | Random | Scratch |
|---|---|---|---|---|---|---|---|---|
| Pt | 0.86 | 0.87 | 0.74 | 0.78 | 0.76 | 0.64 | 0.82 | **0.59** |
| Ferro | 0.94 | 0.90 | 0.90 | 0.94 | 0.81 | 0.79 | 0.87 | **0.69** |
| **NW** | 0.19 | 0.44 | 0.38 | 0.27 | 0.57 | **0.15** | 0.46 | **0.17** |
| TaOx | 0.98 | 0.92 | 0.92 | 0.95 | 0.83 | 0.80 | 0.89 | **0.70** |

## 추가 발견
- minority class (Near-Full 0.4%, Scratch 2.3%)이 가장 약함
- NW는 Edge-Ring, Near-Full, Scratch를 **ideal 조건에서도 F1≈0** (4-state 양자화로 완전 손실)

## 4 옵션
- **A**: 본문 IV.B에 per-class F1 표 1개 추가 (ideal+realistic, 15분 + GitHub 재push)
- **B**: 표 + heatmap 그림 (30분 + GitHub 재push)
- **C**: 그대로 두기 (디펜스 때 JSON으로 구두 답변)
- **D**: 내가_이해하는용.html에만 추가 (제출 논문 손 안 댐, 본인 학습용)

## 너의 임무 (짧게)
```
선택: A / B / C / D
이유: 한 줄
디펜스 시 "어떤 결함이 가장 어려운가?" 질문이 나올 가능성: 높음/중간/낮음
```

분량 200자. 한국어. 검토 파일: `paper.html` (Gemini: `code\paper.html`)
