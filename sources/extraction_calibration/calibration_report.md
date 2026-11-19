# Calibration report

Program status: PARTIAL_USER_STOP_REMOTE_TAIL_UNVERIFIED. Calibration all three passed: True. HiFWB converged: 0/13.

| target | target_type | raw_pairs | qualifying_pairs | qualifying_rate | stopping_n | converged | bootstrap_p05 | sequential_cosine | split_half_median | split_half_p05 | gpu_operation_seconds | estimated_cost_contribution | reference_cosine | angular_error | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| flippant | calibration | 20 | 19 | 0.95 | 16 | True | 0.973319 | 0.994541 | 0.93756 | 0.911021 | 1524.983106 | 0.686242 | 0.980466 | 11.34328 | PASS |
| pensive | calibration | 40 | 33 | 0.825 | 32 | True | 0.954332 | 0.99411 | 0.901121 | 0.838512 | 2687.042222 | 1.209169 | 0.965569 | 15.078838 | PASS |
| accessible | calibration | 20 | 16 | 0.8 | 16 | True | 0.954838 | 0.993657 | 0.900841 | 0.855331 | 1644.18136 | 0.739882 | 0.969196 | 14.258021 | PASS |
| q_2765 | hifwb | 180 | 64 | 0.355556 | — | False | 0.948516 | 0.986692 | 0.867514 | 0.820246 | 8823.059843 | 3.970377 | — | — | PARTIAL_USER_STOP_REMOTE_TAIL_UNVERIFIED |
| q_1371 | hifwb | 0 | 0 | — | — | False | — | — | — | — | 0 | 0.0 | — | — | NOT_RUN |
| q_1043 | hifwb | 0 | 0 | — | — | False | — | — | — | — | 0 | 0.0 | — | — | NOT_RUN |
| q_208 | hifwb | 0 | 0 | — | — | False | — | — | — | — | 0 | 0.0 | — | — | NOT_RUN |
| q_206 | hifwb | 0 | 0 | — | — | False | — | — | — | — | 0 | 0.0 | — | — | NOT_RUN |
| q_1578 | hifwb | 0 | 0 | — | — | False | — | — | — | — | 0 | 0.0 | — | — | NOT_RUN |
| q_875 | hifwb | 0 | 0 | — | — | False | — | — | — | — | 0 | 0.0 | — | — | NOT_RUN |
| q_285 | hifwb | 0 | 0 | — | — | False | — | — | — | — | 0 | 0.0 | — | — | NOT_RUN |
| q_820 | hifwb | 0 | 0 | — | — | False | — | — | — | — | 0 | 0.0 | — | — | NOT_RUN |
| q_1044 | hifwb | 0 | 0 | — | — | False | — | — | — | — | 0 | 0.0 | — | — | NOT_RUN |
| q_867 | hifwb | 0 | 0 | — | — | False | — | — | — | — | 0 | 0.0 | — | — | NOT_RUN |
| q_4288 | hifwb | 0 | 0 | — | — | False | — | — | — | — | 0 | 0.0 | — | — | NOT_RUN |
| q_832 | hifwb | 0 | 0 | — | — | False | — | — | — | — | 0 | 0.0 | — | — | NOT_RUN |

No sign/layer/threshold tuning; HiFWB is gated on all three calibration passes.

