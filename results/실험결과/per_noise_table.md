# Phase 1 — per-noise F1 결과표

Baseline (FP32 software, 3-seed mean): macro F1 = **0.9812**


각 셀: realistic 평가 macro F1 (baseline seed × noise sample n).


| Material | R_off/R_on | Ideal F1 | seed42-n1 | seed42-n2 | seed42-n3 | seed123-n1 | seed123-n2 | seed123-n3 | seed456-n1 | seed456-n2 | seed456-n3 | Mean | Std |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Pt/HfO$_x$/Ti | 25.00x | 0.9826 | 0.9603 | 0.6470 | 0.9180 | 0.9600 | 0.6624 | 0.0491 | 0.9545 | 0.7924 | 0.8763 | **0.7578** | 0.2759 |
| Ferroelectric | 333.33x | 0.9805 | 0.9781 | 0.7977 | 0.9691 | 0.9700 | 0.7834 | 0.4455 | 0.9628 | 0.8481 | 0.9579 | **0.8570** | 0.1632 |
| Metallic Nanowire | 1.97x | 0.3847 | 0.5170 | 0.3981 | 0.3929 | 0.1286 | 0.2888 | 0.1186 | 0.2781 | 0.4182 | 0.4189 | **0.3288** | 0.1286 |
| TaO$_x$/Ta | 145.83x | 0.9770 | 0.9771 | 0.8271 | 0.9756 | 0.9683 | 0.7600 | 0.5513 | 0.9628 | 0.8561 | 0.9746 | **0.8726** | 0.1364 |

## Bimodal 분포 분석

각 소재의 realistic per-noise F1 중 baseline의 90% 이상을 유지한 비율 (good)과 60% 미만으로 떨어진 비율 (catastrophic) 정량화.


| Material | Good (F1 ≥ 0.88) | Catastrophic (F1 < 0.60) | Total samples |
|---|---:|---:|---:|
| Pt/HfO$_x$/Ti | 4/9 (44%) | 1/9 (11%) | 9 |
| Ferroelectric | 5/9 (56%) | 1/9 (11%) | 9 |
| Metallic Nanowire | 0/9 (0%) | 9/9 (100%) | 9 |
| TaO$_x$/Ta | 5/9 (56%) | 1/9 (11%) | 9 |