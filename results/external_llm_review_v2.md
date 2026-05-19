# 3개 외부 LLM 신규 지적 통합 (paper.html v2 대상)

## 종합 평가
- LLM-A: 75점, "학부 캡스톤 시뮬레이션 보고서로 자연스러움". 핵심 5개 수정 권고.
- LLM-B: "이전 5개 약점 중 3개 완벽 해결, 학부 캡스톤 통과 가능". 5개 보강 권고.
- LLM-C: "A+급, 표 5와 용어만 다듬으면 완벽". 3개 수정 권고.

## 신규 지적사항 통합 (중복 합치고 우선순위 매김)

### CRITICAL — 명확한 사실 오류 (3자 공통 또는 사실관계)

**N1. Table 5 합계 모순 (LLM-C 단독, 사실 오류)**
- Pt/HfOx/Ti: Good 4 + Catastrophic 1 = 5인데 Total = 9 표기
- 나머지 4회의 Moderate(0.60~0.88) 결과가 표에서 누락됨
- → Moderate 열 추가 또는 캡션에 명시

**N2. std 범위 표기 오류 (LLM-A 단독, 사실 오류)**
- 본문 IV.B에서 "표준편차가 0.13~0.24"라 했으나 Pt std=0.2759 → 실제 0.13~0.28
- → 단순 수치 정정

**N3. "binary wafer map" vs "0/0.5/1.0 정규화" 모순 (LLM-A 단독, 사실 오류)**
- II.D는 binary라 했으나 III.A는 3-level categorical (0/0.5/1.0)
- → "3-level categorical wafer map"으로 통일

**N4. "라벨 없음 1,000장" 표현 정확성 (LLM-A 단독)**
- MixedWM38의 1,000장은 normal/no-defect 클래스
- → "8개 결함 라벨이 모두 0인 normal/no-defect 1,000장 제외"로 수정

### HIGH — 주장의 통계적 근거 부족 (3자 공통)

**N5. Bimodal/10% 확률 표현 (3 LLM 모두 지적, 가장 강한 합의)**
- n=9 표본에서 1번 catastrophic = 11%는 통계적으로 약함
- 95% Wilson CI 약 [0.6%, 47%]로 매우 넓음 (LLM-B)
- "약 10% 확률" "실제 PIM 칩에서 발생" 표현이 과장
- → "본 실험 9회 중 1회 관찰" 또는 "worst-case 붕괴 현상 관찰"로 톤다운
- LLM-C는 "Bimodal" 용어 자체를 "worst-case 현상"으로 워딩 변경 권고

### MEDIUM — 방법론 정확성/근거 보강

**N6. "VTEAM 기반" 제목 vs 실제 방법론 (LLM-A 가장 강하게 지적)**
- 본 방법론은 정적 conductance mapping + 양자화 + variation/fault
- VTEAM 동역학 파라미터(v_on, k, α)는 사용 안 함
- → 제목을 "VTEAM 문헌 파라미터를 참고한..." 또는 "소재별 저항비와 비이상성 기반..."으로 완화

**N7. Differential pair 처리 명시 부재 (LLM-B 단독)**
- 멤리스터 컨덕턴스는 양수만 가능한데 부호 처리(W+ - W- 분리?) 미명시
- → 한 문장 추가

**N8. Variation σ 평균 처리 근거 (LLM-B 단독)**
- 표 2에서 σ_R_on/σ_R_off 분리하고 시뮬에선 평균
- → 한 줄 근거 ("구현 단순화" 또는 "결과 유사함") 추가

**N9. Stuck-at fault rate 가정값 근거 부재 (LLM-B 단독)**
- "왜 5%인가" 문헌 근거 없음
- → 짧은 단락 부활 (이전 paper III.C의 fault rate 근거 부분, 단 부정확 인용은 제외)

**N10. Pt/HfOx/Ti Ideal F1 > Baseline 평균 (LLM-B 단독)**
- Pt Ideal 0.9826 > Baseline 0.9812 (직관 반함)
- → 한 줄 설명 ("baseline std 0.0032 범위 내 우연 변동")

### LOW — 표현/형식

**N11. "어떤 후처리로도 회복하기 어렵다" 과함 (LLM-A)**
- → "단순 후처리만으로는 회복 어렵고 QAT/회로 보정 필요"로 완화

**N12. Table 4 "Drop" 열 부호 (LLM-C)**
- Drop과 마이너스 이중 부정
- → "Degradation"으로 열명 변경 또는 마이너스 제거

**N13. 수치 표현 통일 (LLM-B)**
- "9% 이상", "약 10%", "11%" 혼재
- → "약 11% (9회 중 1회)"로 통일

**N14. 추가 참고문헌 (LLM-A)**
- 메모리 접근 에너지 주장에 Horowitz 2014 ISSCC 또는 Eyeriss(Chen 2017 JSSC) 추가 권장

**N15. 그림 파일 embed (LLM-A)**
- 제출 시 그림 깨질 위험. PDF 변환 또는 base64 embed

## 너의 임무

각 항목 N1~N15에 대해 다음 판정:

```
[항목 코드] 동의/이견/판단보류 — 한 줄 사유
수정 방향: 수정함 / 수정 안함 / 부분 수정
우선순위: Critical / High / Medium / Low / 불필요
```

마지막에:
- **수정 필수 항목 (최소)**: 번호 나열
- **수정 권장 항목 (가능하면)**: 번호 나열
- **수정 불필요**: 번호 나열
- **종합 한 줄**: 수정 후 즉시 제출 가능 / 추가 작업 필요

분량 600자 이내. 한국어. 검토 대상 파일:
- `C:\Users\ds3owl\Desktop\memristor_pim_capstone\paper.html` (또는 Gemini는 `code\paper.html`)
