# 2개 외부 LLM 신규 지적 통합 — paper.html v4 대상

## 종합 평가
- LLM-A: 88점, "치명적 거짓 거의 없음". 4개 표현 톤다운만.
- LLM-B: "1차 수정에서 방어력 비약 상승. 2차 취약점 4개". cherry-picking 우려가 가장 큼.

## 신규 통합 지적

### CRITICAL — 사실관계 또는 cherry-picking 의심

**Q5. 제목 "VTEAM 문헌 파라미터 활용" 아직 과한지 (LLM-B)**
- 실제 동역학·임계전압 미사용. VTEAM 모델 자체를 거의 안 씀
- B는 "4종 멤리스터 소재 파라미터를 활용한..."으로 VTEAM 완전 제거 권장
- 본문은 VTEAM 모델을 II.C에서 다루기는 함

**Q6. Table 4 Subset Acc 누락 (LLM-B) — Cherry-picking 의심 가장 강한 지적**
- Table 3 baseline에는 Subset Acc + Macro F1 둘 다 있음
- Table 4(4 소재 비교)에는 Macro F1만, Subset Acc 누락
- B: "유리한 지표만 남기고 불리한 지표 숨김 의심" 강력 지적
- 데이터 확보됨: ideal Pt 0.96, Ferro 0.95, NW 0.08, TaOx 0.95
- realistic Pt 0.56, Ferro 0.70, NW 0.05, TaOx 0.73

### HIGH — 표현·정합성 보강

**Q1. 초록 "동일한 시뮬레이션 환경" → "동일한 정적 conductance mapping 기반 시뮬레이션 환경" (LLM-A)**
- 초록과 본문 일치도 ↑

**Q2. Table 2 caption "VTEAM 파라미터" → "conductance mapping 및 비이상성 파라미터" (LLM-A)**
- 엄밀히 표는 VTEAM 동역학 파라미터(v_on/k/α) 없음

**Q7. σ_R_on과 σ_R_off 분리 적용 (LLM-B)**
- "구현 단순화" 핑계 약함. B: "코딩 어려운 일 아님"
- (a) 텍스트만 — 사유 더 정밀하게: "다른 소재간 fault rate가 이미 다르므로 variation도 평균화하여 비교 변수 축소"
- (b) 실제 분리 적용 재실험 — 30~60분 추가

### MEDIUM — 표현 톤다운

**Q3. III.D "자명하다" → "해석된다" (LLM-A)**

**Q4. 결론 "표준 검증 도구로 채택될 필요" → "기초 검증 절차로 활용될 수 있다" (LLM-A)**

### LOW

**Q8. "병목을 근본적으로 우회" → "병목을 완화/해결하는 아키텍처" (LLM-B)**

## 너의 임무

각 항목 Q1~Q8:
```
[Q코드] 동의/이견 — 한 줄 사유
방향: 텍스트수정 / 실험추가 / 수정안함
```

특히:
- **Q5** (제목 VTEAM 완전 제거 여부): 학부 캡스톤에 적절한 강도는?
- **Q6** (Subset Acc 추가): 추가가 정직한가? Table 너무 비대해지는 것은 아닌가?
- **Q7** (σ 분리): (a) 텍스트 사유 강화 vs (b) 실제 분리 실험 추가 중 어느 게 학부 수준?

마지막에:
- **꼭 수정**: 번호
- **수정 권장**: 번호
- **선택**: 번호
- **종합 한 줄**: 수정 후 즉시 제출 / 부분 수정 / 재작업

분량 500자 이내. 한국어. 검토 파일: `paper.html` (Gemini: `code\paper.html`)
