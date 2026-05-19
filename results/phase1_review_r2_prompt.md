# Phase 1 검토 토론 2라운드 — bimodal 분포 처리 결정

## 1라운드 합의
"realistic std 0.12 너무 큼, noise seed 분리 + Monte Carlo 3회 평균"으로 재실행. 너희 둘 모두 옵션 1 선택.

## 재실행 결과 — 그러나 std가 더 커짐

| Material | Ratio | Ideal F1 | Realistic F1 | Drop |
|---|---|---|---|---|
| Pt_HfOx_Ti | 25.0x | 0.9826 | **0.7578 ± 0.1700** | **-22.88%** |
| Ferroelectric | 333.3x | 0.9805 | 0.8570 ± 0.1632 | -12.60% |
| Metallic_Nanowire | 1.97x | 0.3847 | 0.3288 ± 0.1286 | -14.53% |
| TaOx_Ta | 145.8x | 0.9770 | 0.8726 ± 0.1364 | -10.69% |

## 원인 분석 — Bimodal 분포

per-noise 결과를 보면 noise sample이 **good (F1 0.95+) 또는 bad (F1 0.45~0.55)로 양분**되는 패턴:

- Pt seed 42: 0.97 / 0.83 / 0.97
- Pt seed 123: 0.97 / 0.78 / **0.45**
- Ferro seed 123: 0.97 / 0.78 / **0.45**
- TaOx seed 123: 0.97 / 0.76 / **0.55**

즉 stuck-at fault가 **critical weight를 hit하면 catastrophic 망함, 아니면 거의 영향 없음**. 이건 noise variance가 아닌 **fault 위치의 random성** 자체에 기인한 PIM의 본질적 특성.

(친구 코드 https://github.com/ymc0315/capstone_comparison 는 multiplicative Gaussian noise만 있어 이 bimodal을 발견 못 함.)

## 3 옵션

**A. noise 5~10회로 더 늘림** (+60~90분)
- 평균값 안정. 하지만 bimodal 본질은 그대로.

**B. 현 결과 + 정직 서술** (즉시)
- "Stuck-at fault의 random 위치 영향" 발견사항으로 보고.
- per-noise 표 부록 + bimodal histogram 1개.
- 학부 수준 적합.

**C. fault rate 낮춤** (+30분, 예: 0.5% → 0.1%)
- bimodal 약해질 가능성.
- "왜 낮췄나" 정당화 필요. 친구 자료와 비교 가능성 약화.

**Claude 추천: B** — bimodal 패턴 자체가 본 연구의 발견이고 친구 작업물보다 한 단계 위로 만들 수 있음. 학부 캡스톤 + 정직성 둘 다 만족.

## 너의 응답 형식

```
판정: A / B / C
이유: 한 문장
추가 작업: 옵션 선택 시 본문에 추가로 들어가야 할 항목 1~2개
Claude 의견(B 추천)에 동의?: O / X / 부분
```

분량 400자 이내. 한국어.

## 핵심 컨텍스트 재확인
- 상명대학교 학부 캡스톤 (지방대 학부 수준)
- 친구 수준 단순화 + 친구 약점 보강 방향
- "제출 통과" 수준 목표
- 본질: 멤리스터 소재별 PIM 웨이퍼 결함 분류
