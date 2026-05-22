4종 멤리스터 소재 파라미터를 활용한 PIM 환경 웨이퍼 결함 분류 성능 비교 연구

  [B.S. Capstone Design Project]
  Department of System Semiconductor Engineering
  
    4종 멤리스터 소재 파라미터를 활용한
    PIM 환경 웨이퍼 결함 분류 성능 비교 연구
  
  
    A Comparative Study of Four Memristive Material Candidates for Processing-In-Memory
    Wafer Defect Classification
  
  
    임 창 우
    Department of System Semiconductor Engineering
    Sangmyung University
    
    지도교수 : 이 종 환
    
    2026
  

  
# 목차 (Contents)

  
    초록 (Abstract)
    I. 서론 (Introduction)
    A. 연구 배경
    B. 선행 연구의 한계
    C. 본 연구의 기여
    II. 이론적 배경 (Background)
    A. Processing-In-Memory (PIM)
    B. 멤리스터 크로스바 어레이
    C. VTEAM 모델
    D. 웨이퍼 결함 분류와 CNN
    III. 방법론 (Methodology)
    A. 데이터셋
    B. CNN 모델 구조
    C. 4종 소재 파라미터
    D. 매핑·양자화 및 비이상성 모델
    E. 평가 프로토콜
    IV. 결과 (Results)
    A. Baseline (FP32 software) 성능
    B. 4 소재 Ideal vs Realistic 비교
    C. Worst-case 붕괴 현상 분석
    D. 결함 유형별 (per-class) F1 분석
    V. 논의 (Discussion)
    A. 저항비(Roff/Ron)의 영향
    B. Metallic Nanowire의 본질적 한계
    C. Worst-case 붕괴 현상의 PIM 함의
    D. 한계 및 향후 과제
    VI. 결론 (Conclusion)
    참고문헌 (References)
  

  
### 초록 (Abstract)

  
  Processing-In-Memory (PIM) 아키텍처는 인공지능 가속기의 메모리-연산 병목을 해결할 차세대 기술로 주목받고 있다.
  특히 멤리스터(memristor) 기반 크로스바 어레이는 가중치 저장과 곱셈-누적 연산을 동시에 수행할 수 있어
  딥러닝 추론에 적합하다.
  그러나 멤리스터는 소재별로 저항비, 표현 가능한 상태 수, 변동(variation), 결함률(stuck-at fault) 등 물리적
  특성이 크게 다르며, 이는 분류 성능에 직접적인 영향을 미친다.
  본 연구에서는 VTEAM 모델의 문헌 파라미터를 활용하여 Pt/HfOx/Ti, Ferroelectric, Metallic Nanowire,
  TaOx/Ta의 4종 멤리스터 소재를 동일한 정적 conductance mapping 기반 시뮬레이션 환경에서 비교하였다.
  MixedWM38 웨이퍼 결함 데이터셋(8개 결함 라벨이 모두 0인 normal/no-defect 1,000장을 제외한 37,015장, 8개 결함 클래스 multi-label)으로
  학습된 경량 CNN 모델을 각 소재의 크로스바 어레이에 매핑하고, 양자화·변동·stuck-at fault의 세 비이상성을 동시에
  적용하여 9회 Monte Carlo 평가를 수행하였다.
  실험 결과, Roff/Ron 저항비가 25배 이상인 세 소재(Pt/HfOx/Ti, Ferroelectric,
  TaOx/Ta)는 평균 macro F1이 0.76~0.88 수준이었으나 noise sample에 따른 변동성이 매우 컸으며
  (std 0.13~0.28), 저항비 1.97배의
  Metallic Nanowire는 4-state 양자화의 본질적 한계로 인해 이상적 조건에서도 F1 0.38로 분류 성능이 붕괴하였다.
  또한 고저항비 세 소재(Pt/HfOx/Ti, Ferroelectric, TaOx/Ta) 각각에서 9회 Monte Carlo
  샘플 중 1회씩 치명적 성능 붕괴(catastrophic degradation, F1 &lt; 0.60)가 관찰되었으며,
  이는 stuck-at fault 위치 무작위성에 의한 worst-case 붕괴 위험의 가능성을 시사한다(다만 실제 발생 확률 추정에는
  더 많은 반복이 필요하다).
  이는 PIM 응용에서 평균 성능뿐 아니라 결함 분포에 따른 worst-case 위험까지 함께 고려해야 함을 시사한다.
  
  
  Keywords : Memristor, Processing-In-Memory (PIM), VTEAM model, Convolutional Neural Network,
  Wafer defect classification, Stuck-at fault, Quantization
  

# I. 서론 (Introduction)

## A. 연구 배경

딥러닝 모델의 규모가 급격히 커지면서 전통적인 von Neumann 구조의 메모리-연산 분리에 의한 데이터 이동 비용이
시스템 전체 성능과 전력 효율을 좌우하는 주된 병목으로 떠올랐다. 추론 단계에서 발생하는 메모리 접근은 실제 계산
자원이 소비하는 에너지보다 수십 배 이상의 전력을 요구하는 것으로 보고되며 [11], 이는 모바일·엣지 환경에서
인공지능 가속기를 구현할 때 가장 큰 걸림돌이 된다 [10, 8, 12].

Processing-In-Memory (PIM)는 가중치 저장 셀이 동시에 곱셈-누적(MAC) 연산을 수행하도록 함으로써 위의 데이터
이동 병목을 완화하는 아키텍처이다. 그중에서도 멤리스터(memristor) 기반 크로스바 어레이는 옴의 법칙과 키르히호프
전류 법칙만으로 단일 사이클 안에 행렬-벡터 곱셈을 완성할 수 있어 딥러닝 추론용 PIM 가속기의 대표 후보로
연구되어 왔다 [1, 8, 9, 10].

반도체 제조 공정에서는 웨이퍼 표면의 결함 패턴(Center, Donut, Edge-Ring 등)을 자동 분류하는 작업이 수율 관리에
필수적이다. 이 작업은 CNN(convolutional neural network)이 강점을 보이는 분야이며, 공장 라인에서 실시간으로
요구되는 만큼 저전력 엣지 추론 가속기와 결합할 수 있다면 실용적 가치가 크다.

## B. 선행 연구의 한계

멤리스터 기반 PIM에서 분류 정확도에 영향을 주는 비이상성(non-ideality)은 크게 세 가지로 정리된다.
첫째, 멤리스터가 안정적으로 구분할 수 있는 컨덕턴스 상태의 수가 유한하므로 가중치를 표현할 때 양자화 손실이
발생한다. 둘째, 동일 공정에서 제조된 셀들 간에도 저항값이 가우시안 분포로 변동(device-to-device variation)
한다. 셋째, 일부 셀은 영구적으로 저저항(LRS) 또는 고저항(HRS) 상태에 고착되는 stuck-at fault를 보인다 [1, 8].

선행 연구의 다수는 위 세 가지 비이상성 중 한두 가지만을 부분적으로 모델링하거나, 매핑 후 출력 재보정(tune)을
가정해 비이상성의 영향을 과소평가하는 경향이 있었다. 이는 실제 PIM 칩에서 발생할 수 있는 심각한 성능 저하
(catastrophic degradation)를 시뮬레이션 단계에서 사전 평가하지 못하게 만든다.

## C. 본 연구의 기여

본 연구는 다음과 같은 기여를 제시한다.

1) VTEAM 문헌 파라미터를 참고한 정적 conductance mapping 환경에서 4종 멤리스터 소재의 정량 비교.
Pt/HfOx/Ti, Ferroelectric, Metallic Nanowire, TaOx/Ta에 대해 동일한 CNN, 동일한 데이터셋,
동일한 비이상성 모델을 적용하여 소재 간 PIM 적합성을 macro F1 지표로 비교한다.

2) 세 비이상성의 동시 적용.
양자화·변동·stuck-at fault를 매핑 파이프라인에 동시에 반영함으로써 실제 멤리스터 칩의 동작에 더 가까운
보수적 평가를 수행한다. 매핑 후 출력 재보정은 가정하지 않는다.

3) Worst-case 붕괴 현상 관찰.
3개의 baseline seed와 3개의 noise sample을 결합한 9회 Monte Carlo 평가에서, 고저항비 세 소재 모두에서
9회 중 1회 비율로 catastrophic degradation이 관찰되었다. 표본이 작아 분포 형태를 단정할 수는 없으나,
stuck-at fault 위치 무작위성에 따라 동일 소재가 worst-case에 가까운 붕괴 결과를 보일 수 있음을 시사한다.
이는 PIM 응용에서 평균 성능뿐 아니라 worst-case 위험까지 고려해야 함을 정성적으로 뒷받침한다.

본 논문의 구성은 다음과 같다. II장에서는 PIM과 VTEAM 모델 등 이론적 배경을 정리한다.
III장은 데이터셋과 CNN 구조, 4 소재 파라미터 및 평가 프로토콜을 기술한다.
IV장은 실험 결과를, V장은 결과의 해석과 PIM 설계에 대한 시사점을 다룬다. VI장에서 결론을 맺는다.

# II. 이론적 배경 (Background)

## A. Processing-In-Memory (PIM)

PIM은 메모리 셀이 저장 기능과 함께 연산 기능을 수행하도록 하여 가중치 데이터를 별도 연산 유닛으로 이동시키는
비용을 제거하는 아키텍처이다. CNN 추론은 본질적으로 행렬-벡터 곱셈(MVM)의 연쇄이며, 멤리스터 크로스바
어레이는 단일 사이클의 아날로그 연산으로 MVM을 처리할 수 있어 PIM의 효과적인 물리 구현 후보로 평가된다 [10].

## B. 멤리스터 크로스바 어레이

멤리스터는 인가 전압 이력에 따라 저항 상태가 변화하고, 전원이 차단된 이후에도 마지막 저항 상태를 유지하는
2단자 비휘발성 소자이다. 행과 열이 격자형으로 교차하는 크로스바 어레이에서 각 교차점에 멤리스터를 배치하면, 행 라인에
입력 전압 Vi를 인가했을 때 열 라인에 흐르는 전류는 Ij = Σi Gij Vi
가 되어 옴의 법칙과 키르히호프 전류 법칙만으로 가중치 행렬 G와 입력 벡터의 곱이 즉시 얻어진다.

## C. VTEAM 모델

VTEAM(Voltage Threshold Adaptive Memristor) 모델은 Kvatinsky 등이 제안한 전압 임계 기반의 일반화된 멤리스터
거동 모델이다 [1]. 본 연구가 참조한 기본 방정식은 다음과 같다(단, 본 연구에서는 아래 동역학 방정식을 직접
적분하지 않고, 해당 모델 및 관련 소자 문헌에서 제시된 소재별 저항 범위와 스위칭 특성을 정적 conductance
mapping의 기준 파라미터로 활용하였다).

  dw/dt = koff·((v(t)/voff) − 1)αoff·foff(w) &nbsp;&nbsp; (v &gt; voff &gt; 0)

  dw/dt = 0 &nbsp;&nbsp; (von &lt; v &lt; voff)

  dw/dt = kon·((v(t)/von) − 1)αon·fon(w) &nbsp;&nbsp; (v &lt; von &lt; 0)

여기서 w는 0과 1 사이로 정규화된 내부 상태 변수, von, voff는 스위칭 임계 전압이며,
kon, koff, α는 소재별로 결정되는 동역학 파라미터이다.
정적 상태에서 멤리스터의 저항은 R(w) = Ron + (Roff − Ron) w
로 표현된다. VTEAM 모델의 장점은 다양한 소재의 실측 특성을 동일한 수식 형태 안에서 파라미터만 바꾸어
표현할 수 있다는 점이며, 이는 본 연구의 통일된 정적 conductance mapping 비교 환경의 기반이 된다.

## D. 웨이퍼 결함 분류와 CNN

웨이퍼 결함 패턴은 공정 이상의 1차 신호로서, 패턴 종류에 따라 원인 공정이 다르다.
CNN은 공간적 패턴을 계층적으로 추출하므로 결함 분류에 효과적이며, 본 연구에서는 3개의 합성곱 계층과 1개의
은닉 완전연결 계층, 최종 분류 계층으로 구성된 경량 CNN(약 32만 파라미터)을 사용한다. 입력은 52×52 픽셀의
3-level categorical wafer map(배경/정상 다이/결함 다이를 0/0.5/1.0으로 정규화)이고, 출력은 8개 결함 클래스 각각에
대한 multi-label sigmoid 확률이다.

# III. 방법론 (Methodology)

## A. 데이터셋

본 연구에서는 Wang 등이 공개한 MixedWM38 웨이퍼 결함 데이터셋을 사용하였다 [2].
총 38,015장의 52×52 웨이퍼 맵으로 구성되며, 픽셀 값은 배경(0), 정상 다이(1), 결함 다이(2)의 정수 categorical
값이다. 라벨은 8개 결함 클래스(Center, Donut, Edge-Loc, Edge-Ring, Loc, Near-Full, Random, Scratch)에 대한
multi-hot 벡터로, 단일 결함뿐 아니라 두 종류 이상의 결함이 동시에 존재하는 복합 결함(mixed-type) 패턴을
포함한다는 점이 특징이다.

전처리 과정에서 8개 결함 라벨이 모두 0인 1,000장의 normal/no-defect 샘플을 제외하고, 결함이 존재하는 37,015장을
사용하였다. 이 중 단일 결함은 7,015장(19.0%), 복합 결함은 30,000장(81.0%)이며, 복합 결함이 다수를 차지하는
데이터셋 특성은 multi-label 분류 패러다임 선택의 근거가 된다. 픽셀 값은 categorical 값(0,1,2)을 0/0.5/1.0으로
정규화하였고, 학습/검증/테스트는 70/10/20 비율로 seed=42로 고정 분할하였다(Train 25,910 / Val 3,702 / Test 7,403).

## B. CNN 모델 구조

모델 구조는 다음과 같이 단순하고 재현 가능한 형태로 고정하였다.

[TABLE]
  계층구성출력 크기
  Conv13×3, 16ch, BN, ReLU, MaxPool(2)26×26×16
  Conv23×3, 32ch, BN, ReLU, MaxPool(2)13×13×32
  Conv33×3, 64ch, BN, ReLU, MaxPool(2)6×6×64
  FC1Linear(2304→128), ReLU, Dropout(0.3)128
  FC2Linear(128→8)8 (logits)

Table 1. CNN 모델 구조. 총 파라미터 수 319,592.

손실 함수는 multi-label 분류 표준인 BCEWithLogitsLoss를 사용하였고, 최적화는 Adam(lr=1e-3, batch size=128)
이다. 최대 학습 epoch는 20이며, 검증 macro F1이 5 epoch 동안 갱신되지 않으면 학습을 조기 종료(early stopping)
하였다. 동일 모델 구조를 3개의 baseline seed(42, 123, 456)에 대해 독립적으로 학습하여 평가 결과가 특정 초기화
seed에만 의존하지 않는지(baseline 변동성)를 확인하였다.

## C. 4종 소재 파라미터

본 연구의 핵심 비교 대상인 4종 소재의 물리 파라미터는 표 2에 정리하였다.
Ron, Roff 등 거시 특성은 각 소재의 실측 문헌에서 가져왔으며,
device-to-device variation(σ/μ)과 stuck-at fault 비율은 문헌에서 보고된 범위에 기반한 시뮬레이션 가정값이다.

[TABLE]
  ParameterPt/HfOx/TiFerroelectricMetallic NanowireTaOx/Ta
  Ron (Ω)100150,00017.34,800
  Roff (Ω)2,50050,000,00034700,000
  Roff/Ron25.0×333.3×1.97×145.8×
  Conductance states64128432
  Variation σR_on10%8%5%8%
  Variation σR_off15%12%8%10%
  Stuck-at fault rate0.5%0.3%5.0%0.3%
  출처(Ron, Roff)[1, 3][1, 4][1, 5][6]

Table 2. 4종 멤리스터 소재의 conductance mapping 및 비이상성 파라미터. Ron/Roff는 실측 문헌, variation/fault는 가정값.

## D. 매핑·양자화 및 비이상성 모델

학습된 CNN의 가중치는 다음 4단계 파이프라인을 통해 각 소재의 멤리스터 크로스바에 매핑된다.

1) 레이어별 정규화 및 부호 분리. 각 Conv/Linear 계층의 가중치 W를 부호 비트 sign(W)와 크기 |W|로 분리한 뒤
|W|/max(|W|)로 정규화한다. 멤리스터 컨덕턴스는 양의 값만 가지므로, 실제 PIM 회로에서는 양·음 가중치를 두 개의
멤리스터 컬럼(differential pair: W+ − W−)으로 구현해야 한다. 본 시뮬레이션에서는 |W|만
컨덕턴스로 매핑하고 부호 정보는 외부에서 유지하는 방식으로 단순화하였다.

2) 선형 매핑. 정규화된 값을 Gmin=1/Roff, Gmax=1/Ron 범위로
선형 매핑한다.

3) 비이상성 주입 (Realistic 조건만 해당).
(i) Device-to-device variation: g ← g·(1 + N(0, σ)), σ = (σR_on + σR_off)/2.
LRS와 HRS의 variation은 본래 분리된 물리 메커니즘에 기인하지만, 본 연구에서는 구현 단순화를 위해 두 값의
산술 평균을 단일 가우시안 분산으로 사용하였다. 이는 4 소재 간 fault rate가 이미 상이한 본 연구 설정에서
variation 변수를 통제하여 비교 변수를 줄이기 위함이며, LRS/HRS variation을 분리 적용한 경우의 결과 변동
가능성은 V.D(한계 및 향후 과제)에 명시하였다.
(ii) Stuck-at fault: 전체 셀의 fault rate 비율 위치를 무작위로 선택하여 절반은 Gmax(LRS), 절반은
Gmin(HRS)으로 고착시킨다. 본 연구의 fault rate(0.3~5%)는 멤리스터 크로스바 yield 문헌의 보고 범위에
기반한 가정값으로, 고저항비 세 소재(Pt/HfOx/Ti, Ferroelectric, TaOx/Ta)는 안정적 공정에서
보고되는 1% 미만 수준을, Metallic Nanowire는 4-state 양자화의 본질적 한계와 함께 worst-case 시나리오를
보이기 위한 sensitivity bound로서 보수적 가정인 5%를 적용하였다. 다만 4 소재 간 fault rate가 동일하지 않으므로,
NW의 realistic 결과 자체는 다른 소재와 수평 비교하기보다는 sensitivity 시나리오로 해석해야 한다. 실제로
NW의 ideal 조건(variation=0, fault=0)에서도 F1이 0.38로 붕괴하므로, 본 연구의 설정에서는 NW의 분류 성능
저하가 fault rate보다 4-state 양자화의 본질적 한계에 더 크게 기인한 것으로 해석된다.

4) N-state 양자화. 각 셀의 컨덕턴스를 등간격 N개의 levels = linspace(Gmin, Gmax, N)
중 가장 가까운 값으로 반올림한다(nearest-state rounding). 양자화는 ideal/realistic 두 조건 모두에 적용된다.

이 파이프라인은 양자화·변동·stuck-at fault의 세 비이상성을 동시에 반영하며, 매핑 후 출력 재보정(tune)은
수행하지 않는다.

## E. 평가 프로토콜

평가는 다음 두 조건에서 수행된다.

  Ideal: 변동·고장 없이 양자화만 적용. 양자화는 결정론적이므로 noise sampling은 무의미하며,
  baseline seed당 1회 평가한다.
  Realistic: 양자화 + 변동 + stuck-at fault. noise 위치는 무작위이므로 baseline seed당 noise seed를
  분리해 3회 sampling(총 9회/소재) 후 평균과 표준편차를 보고한다.

평가 지표는 multi-label 분류 표준인 Macro F1(클래스 불균형에 강건)과 Subset Accuracy(모든 라벨이
정확히 일치한 샘플 비율)를 모두 측정한다. Threshold는 0.5로 고정하였다.

# IV. 결과 (Results)

## A. Baseline (FP32 software) 성능

3개의 baseline seed에 대해 학습된 CNN의 테스트 성능은 표 3과 같다.

[TABLE]
  SeedBest epochTest Subset AccTest Macro F1
  4290.95680.9780
  123110.94460.9800
  456130.95880.9856
  평균±std—0.9534 ± 0.00630.9812 ± 0.0032

Table 3. FP32 software baseline의 3 seed 결과. macro F1의 std=0.0032로 매우 안정적.

세 seed 모두 macro F1 0.98 수준의 안정적인 baseline을 학습하였으며, std가 0.003 수준으로 매우 작아 이후
소재 비교의 신뢰성 기반으로 사용 가능하다.

## B. 4 소재 Ideal vs Realistic 비교

각 소재별 ideal 및 realistic 조건에서의 macro F1 결과를 표 4와 그림 1에 정리하였다.

[TABLE]
  MaterialRoff/RonStatesIdealRealistic (mean ± std)ΔF1
  Subset AccMacro F1Subset AccMacro F1absoluterelative
  Pt/HfOx/Ti25.0×640.95780.98260.5601 ± 0.27790.7578 ± 0.2759−0.2248−22.88%
  Ferroelectric333.3×1280.95260.98050.6992 ± 0.26600.8570 ± 0.1632−0.1235−12.60%
  Metallic Nanowire1.97×40.08130.38470.0518 ± 0.04130.3288 ± 0.1286−0.0559−14.53%
  TaOx/Ta145.8×320.94580.97700.7258 ± 0.24310.8726 ± 0.1364−0.1044−10.69%

Table 4. 4 소재의 Ideal vs Realistic 분류 성능 (Subset Accuracy 및 Macro F1, 3 baseline seed × 3 noise sample = 9회 평균). ΔF1은 macro F1 기준의 절대 변화량과 상대 변화율을 분리하여 표기.

  
  Figure 1. 4 소재의 Ideal(파랑) vs Realistic(주황) macro F1 비교. 오차막대는 9회 표준편차. 회색 점선은 FP32 baseline.

저항비 25배 이상의 세 소재(Pt/HfOx/Ti, Ferroelectric, TaOx/Ta)는 ideal 조건에서
0.98 수준의 baseline에 거의 근접한 성능을 보였다. 즉 양자화 단독으로는 분류 성능에 큰 영향을 미치지
않는다. 또한 Pt/HfOx/Ti의 ideal F1(0.9826)이 baseline 평균(0.9812)을 미세하게 상회하는 현상이
관찰되었으나, 이는 baseline 표준편차(0.0032) 범위 내에 들어가는 우연한 변동으로 해석된다. 그러나 variation과
stuck-at fault가 더해진 realistic 조건에서는 평균 macro F1이 0.76~0.87 수준으로 하락하였으며, 표준편차가
0.13~0.28로 매우 컸다.

Subset Accuracy(8개 라벨이 모두 정확히 일치한 비율) 기준으로는 macro F1보다 더 큰 감소가 관찰되었다.
고저항비 세 소재의 realistic Subset Acc는 0.56~0.73 수준으로, multi-label 분류에서 모든 결함을 동시에 정확히
포착하는 것이 부분 일치(macro F1 0.76~0.87)보다 훨씬 어려움을 보여준다. Metallic Nanowire는 ideal Subset
Acc도 0.08에 그쳐 거의 분류가 성립하지 않았다.

이와 대조적으로 Metallic Nanowire는 ideal 조건에서도 F1 0.38로 분류 성능이 붕괴하였다. 이는 저항비 1.97배
+ 4-state 양자화의 조합이 가중치 분포의 대부분의 정보를 손실시키기 때문이며, realistic 조건이 추가된다고
하여 더 악화될 여지가 적다(realistic F1 0.33). 즉 Metallic Nanowire의 한계는 비이상성이 아니라
표현 가능한 가중치 자유도 자체에 있다.

## C. Worst-case 붕괴 현상 분석

표 4의 큰 표준편차는 단순한 noise variance가 아니라, 동일 소재의 9회 noise sampling 결과가 "정상 영역"과
"붕괴 영역"의 두 그룹으로 갈리는 양상에서 비롯된다. 그림 2는 4 소재의 per-noise F1 분포를 히스토그램으로
나타낸 것이다. 다만 표본 수가 소재당 9회로 제한되므로 통계적 의미의 bimodal 분포로 단정할 수는 없으며,
본 절에서는 "worst-case 붕괴 현상"으로 표현한다.

  
  Figure 2. 4 소재의 realistic per-noise macro F1 분포 (9 samples). 검정 점선: ideal F1, 빨강 점선: realistic mean.

F1 ≥ 0.88을 "good", F1 &lt; 0.60을 "catastrophic"으로 정의했을 때 4 소재의 분포는 표 5와 같다.

[TABLE]
  MaterialGood (F1≥0.88)Moderate (0.60≤F1&lt;0.88)Catastrophic (F1&lt;0.60)Total
  Pt/HfOx/Ti4/9 (44%)4/9 (44%)1/9 (11%)9
  Ferroelectric5/9 (56%)3/9 (33%)1/9 (11%)9
  Metallic Nanowire0/9 (0%)0/9 (0%)9/9 (100%)9
  TaOx/Ta5/9 (56%)3/9 (33%)1/9 (11%)9

Table 5. 각 소재의 per-noise 결과를 good / moderate / catastrophic 임계로 분류한 빈도.

고저항비 세 소재는 약 44~56%가 baseline의 90% 이상을 유지(good)하는 한편, 9회 중 1회 (약 11%) 비율로 F1이
0.60 미만으로 붕괴(catastrophic)하는 결과가 세 소재 모두에서 일관되게 관찰되었다. Metallic Nanowire는 9회 모두
catastrophic 구간에 존재하여, 본질적 표현 한계가 noise 종류와 무관하게 항상 성능 붕괴를 초래함을 보여준다.
또한 NW의 ideal 조건(variation=0, fault=0)에서도 이미 F1=0.38로 붕괴하므로, NW의 결과는 fault rate 차이가
아닌 4-state 양자화 효과로 해석된다(NW에 대한 4-state vs. 더 많은 상태 수의 강제 ablation은 본 연구 범위 외이며,
V.D에 향후 과제로 명시한다).

## D. 결함 유형별 (per-class) F1 분석

표 6은 4 소재 × 두 조건에서의 결함 클래스별 macro F1을 보여준다. 데이터셋의 클래스 빈도가 균일하지 않음을
유의해야 한다(Near-Full 0.4%, Scratch 2.3%로 가장 적음, Loc 48.6%, Random 51.3%로 가장 많음).

[TABLE]
  Material / ConditionCenterDonutEdge-LocEdge-RingLocNear-FullRandomScratch
  Pt/HfOx/Ti — Ideal1.001.000.980.990.990.930.990.98
  Pt/HfOx/Ti — Realistic0.860.870.740.780.760.640.820.59
  Ferroelectric — Ideal1.001.000.980.990.980.920.990.98
  Ferroelectric — Realistic0.940.900.900.940.810.790.870.69
  Metallic Nanowire — Ideal0.290.730.670.000.670.000.720.01
  Metallic Nanowire — Realistic0.190.440.380.270.570.150.460.17
  TaOx/Ta — Ideal1.001.000.980.990.980.920.990.97
  TaOx/Ta — Realistic0.980.920.920.950.830.800.890.70

Table 6. 4 소재 × Ideal/Realistic 조건에서의 결함 클래스별 F1 (Ideal은 3 seed 평균, Realistic은 9 sample 평균).

두 가지 패턴이 관찰된다. 첫째, minority class인 Near-Full(0.4%)과 Scratch(2.3%)가 모든 고저항비 소재에서
가장 낮은 F1을 보였다. 특히 realistic 조건의 Scratch는 Pt/HfOx/Ti 0.59, Ferroelectric 0.69,
TaOx/Ta 0.70으로 떨어져, 다른 다수 클래스(Loc, Random 등)와 약 0.15~0.25의 F1 격차를 보인다. 이는
multi-label 분류에서 클래스 불균형이 비이상성 조건에서 더 증폭됨을 시사한다.

둘째, Metallic Nanowire는 ideal 조건에서도 Edge-Ring, Near-Full, Scratch의 F1이 약 0으로 사실상 분류
실패이다. 이는 4-state 양자화로 인해 가중치 표현 자유도가 부족해 minority 또는 공간적으로 미세한
패턴(Edge-Ring 같은 가장자리 고리)을 식별할 수 없음을 보여준다. realistic 조건에서 일부 클래스의 F1이 살짝
증가하는 현상은 양자화로 이미 무너진 결정 경계가 random noise로 우연히 일부 정답을 맞히는 통계적 효과로
해석된다.

다만 본 결과는 소재당 9개 표본에 기반한 점추정치이므로, 11% 빈도를 실제 칩의 발생 확률로 일반화하기 위해서는
더 많은 Monte Carlo 반복이 필요하다. 9회 중 1회 사건의 binomial 95% 신뢰구간은 약 [0.3%, 48%]에 이르므로,
"11%"는 정확한 발생률 추정치가 아닌 본 표본 기준의 관찰 빈도로 해석되어야 한다.

# V. 논의 (Discussion)

## A. 저항비(Roff/Ron)의 영향

실험 결과에서 가장 명확한 경계는 Roff/Ron ≈ 25배 부근에 존재한다. 저항비가 25배 이상인 세 소재는
ideal 조건에서 baseline 대비 1% 이내의 손실로 가중치 정보를 잘 보존하지만, 저항비 1.97배의 Metallic Nanowire는
ideal에서도 baseline의 39% 수준으로 추락한다. 이 차이는 컨덕턴스 범위가 좁을수록 동일한 절대 noise/양자화
간격이 가중치 표현에 미치는 상대 오차가 커지기 때문이다.

다만 본 연구의 실험만으로 "25배가 보편적 문턱값"이라 단정하기는 어렵다. 본 연구는 4 소재의 이산적인 비교이며,
저항비 sweep(예: 5×, 10×, 20×, 50×)을 수행하지 않았기 때문이다. "본 연구의 조건에서 25배 이상이면 양자화로
인한 ideal 성능 손실이 1% 이내였다"가 정직한 결론이다.

## B. Metallic Nanowire의 본질적 한계

Metallic Nanowire의 4-state 양자화는 가중치를 4개의 칸으로 압축한다는 것을 의미한다. 32만 개의 부동소수점
가중치가 가질 수 있는 다양한 값이 4개의 이산 값으로 반올림되는 과정에서, CNN이 학습한 미세한 결정 경계가
대부분 소실된다. 이 한계는 단순 사후 보정만으로는 회복하기 어렵고, 완화를 위해서는 quantization-aware training
(QAT)이나 소재·회로 수준의 추가 보정(예: 더 많은 conductance level을 갖는 변형 nanowire 구조)이 필요할
가능성이 크다.

한편 Metallic Nanowire는 동작 전압이 매우 낮고 (voff=0.145 V) variation이 작아 (5~8%) 별도 응용
영역에서는 유리한 면이 있을 수 있다. 본 연구가 보이는 것은 "다단계 가중치 정밀도가 필요한 PIM 추론 응용에서
부적합"하다는 것이지, 소재 자체의 부정이 아니다.

## C. Worst-case 붕괴 현상의 PIM 함의

고저항비 세 소재가 평균 성능에서는 비슷한 수준을 보이지만, 본 실험에서 9회 중 1회 (약 11%) 비율로 catastrophic
degradation이 관찰된 점은 평균만으로 소재를 평가하는 관행에 대한 경고이다. 표본 수가 작아 실제 PIM 칩의
발생 확률로 단정할 수는 없으나, stuck-at fault 위치 무작위성에 따라 동일 소재가 worst-case에 가까운 결과를
보일 가능성을 시사한다. 그 원인은 stuck-at fault가 가중치 행렬 안에서 어떤 위치에 박히는지에 따라 갈린다.
핵심 가중치를 hit하면 분류기 전체가 무너지지만, 중요도가 낮은 가중치를 hit하면 거의 영향이 없다.

따라서 실제 PIM 가속기 설계에서는 (i) write-verify를 통한 stuck-at 셀의 사전 검출, (ii) row/column-shifting
같은 매핑 다양화, (iii) ECC나 redundancy 같은 fault tolerance 메커니즘이 동반되어야 한다. 본 연구는 이러한
대책이 적용되지 않은 보수적 베이스라인이며, 향후 fault tolerance 적용 후 worst-case 붕괴 빈도가 어떻게
변화하는지를 충분한 표본으로 정량화하는 후속 연구가 필요하다.

## D. 한계 및 향후 과제

  단일 데이터셋. MixedWM38만을 사용하였으며, 단일 결함 비중이 높은 WM-811K [7] 등 다른 데이터셋에서의
  소재 간 순위 보존 여부는 검증되지 않았다.
  경량 CNN. 약 32만 파라미터의 얕은 모델에 한정된 결과이며, ResNet 계열의 대규모 모델에서는
  비이상성의 누적 효과가 더 클 수 있다.
  저항비 sweep 미수행. 4 소재의 이산적인 비교만 수행하여 저항비-성능 관계의 연속적 함수 형태는
  본 연구에서 결정할 수 없다.
  회로 수준 비이상성 미반영. sneak path, IR drop, ADC 양자화 등 어레이 수준의 비이상성은
  본 연구의 가중치 수준 모델에서 다루지 않았다.
  시간적 비이상성 미반영. drift와 endurance 같은 장기 변화는 inference-only 평가 범위에서 제외하였다.
  3 seed × 3 noise. 학회 수준의 통계 분석(예: paired t-test, effect size)은 본 학부 캡스톤의
  범위에서 보류하였으며, mean과 std를 통해 대략적인 경향만 확인하였다. 정량적 확률 추정이나 통계적 유의성
  검정에는 더 많은 Monte Carlo 반복이 필요하다.

# VI. 결론 (Conclusion)

본 연구는 VTEAM 모델 문헌의 소재별 파라미터를 활용한 정적 conductance mapping 환경에서 4종 멤리스터 소재
(Pt/HfOx/Ti, Ferroelectric, Metallic Nanowire, TaOx/Ta)의 PIM 환경 웨이퍼 결함 분류 성능을
정량 비교하였다. 양자화, device-to-device variation, stuck-at fault의 세 비이상성을 동시에 적용한 9회
Monte Carlo 평가에서 다음 세 가지를 확인하였다.

첫째, Roff/Ron 25배 이상의 세 소재는 ideal 조건에서 baseline의 99% 이상의 분류 성능을 유지하였으나,
realistic 조건에서는 평균 macro F1이 0.76~0.87로 하락하였다. 둘째, 저항비 1.97배의 Metallic Nanowire는
4-state 양자화의 본질적 한계로 ideal 조건에서도 분류 성능이 붕괴(F1 0.38)하여, 다단계 가중치 정밀도가
필요한 PIM 추론 응용에는 부적합함을 확인하였다. 셋째, 동일 소재 내에서도 stuck-at fault의 위치 무작위성에
의해 9회 중 1회 (약 11%) 비율로 catastrophic degradation이 관찰되었으며, 이는 worst-case 붕괴 위험을 정성적으로
시사한다(표본 9개 한계상 통계적 분포 형태로는 단정하지 않는다).

본 연구의 결과는 PIM용 멤리스터 소재 선정에서 (i) Roff/Ron 충분한 동적 범위 확보,
(ii) 평균 성능과 함께 worst-case 위험에 대한 평가, (iii) fault tolerance 메커니즘 병행의 필요성을 제안한다.
본 연구의 보수적 평가 프로토콜은 향후 PIM 기반 결함 분류 시스템을 설계할 때 평균 성능과 worst-case 위험을
함께 검토하는 기초 검증 절차로 활용될 수 있다.

# 참고문헌 (References)

S. Kvatinsky, M. Ramadan, E. G. Friedman, and A. Kolodny, "VTEAM: A General Model for Voltage-Controlled Memristors," IEEE Transactions on Circuits and Systems II: Express Briefs, vol. 62, no. 8, pp. 786-790, Aug. 2015.
J. Wang, C. Xu, Z. Yang, J. Zhang, and X. Li, "Deformable Convolutional Networks for Efficient Mixed-type Wafer Defect Pattern Recognition," IEEE Transactions on Semiconductor Manufacturing, vol. 33, no. 4, pp. 587-596, Nov. 2020. DOI: 10.1109/TSM.2020.3020985
E. Yalon, A. Gavrilov, S. Cohen, D. Mistele, B. Meyler, J. Salzman, and D. Ritter, "Resistive Switching in HfO2 Probed by a Metal-Insulator-Semiconductor Bipolar Transistor," IEEE Electron Device Letters, vol. 33, no. 1, pp. 11-13, Jan. 2012.
A. Chanthbouala, V. Garcia, R. O. Cherifi, K. Bouzehouane, S. Fusil, X. Moya, S. Xavier, H. Yamada, C. Deranlot, N. D. Mathur, M. Bibes, A. Barthélémy, and J. Grollier, "A Ferroelectric Memristor," Nature Materials, vol. 11, no. 10, pp. 860-864, Oct. 2012.
S. L. Johnson, A. Sundararajan, D. P. Hunley, and D. R. Strachan, "Memristive Switching of Single-Component Metallic Nanowires," Nanotechnology, vol. 21, no. 12, Art. no. 125204, Mar. 2010.
C. Yakopcic, T. M. Taha, D. J. Mountain, T. Salter, M. J. Marinella, and M. McLean, "Memristor Model Optimization Based on Parameter Extraction from Device Characterization Data," IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems, vol. 39, no. 5, pp. 1084-1095, May 2020.
M.-J. Wu, J.-S. R. Jang, and J.-L. Chen, "Wafer Map Failure Pattern Recognition and Similarity Ranking for Large-Scale Data Sets," IEEE Transactions on Semiconductor Manufacturing, vol. 28, no. 1, pp. 1-12, Feb. 2015.
C. Lammie, W. Xiang, B. Linares-Barranco, and M. R. Azghadi, "MemTorch: An Open-Source Simulation Framework for Memristive Deep Learning Systems," Neurocomputing, vol. 485, pp. 124-133, May 2022.
S. Yu and P.-Y. Chen, "Emerging Memory Technologies: Recent Trends and Prospects," IEEE Solid-State Circuits Magazine, vol. 8, no. 2, pp. 43-56, Spring 2016.
M. A. Zidan, J. P. Strachan, and W. D. Lu, "The Future of Electronics Based on Memristive Systems," Nature Electronics, vol. 1, no. 1, pp. 22-29, Jan. 2018.
M. Horowitz, "Computing's Energy Problem (and what we can do about it)," in Proc. IEEE International Solid-State Circuits Conference (ISSCC), Feb. 2014, pp. 10-14.
Y.-H. Chen, T. Krishna, J. S. Emer, and V. Sze, "Eyeriss: An Energy-Efficient Reconfigurable Accelerator for Deep Convolutional Neural Networks," IEEE Journal of Solid-State Circuits, vol. 52, no. 1, pp. 127-138, Jan. 2017.

— Manuscript draft, Sangmyung University Capstone Project, 2026 —