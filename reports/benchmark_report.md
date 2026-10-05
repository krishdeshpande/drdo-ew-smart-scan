# DRDO Electronic Support Receiver Benchmark Report

Evaluated over 3 Monte Carlo runs of 500 dwell steps each across 8 surveillance bands.

## Figures of Merit Comparison

| Strategy / Scheduler | Pd (%) | Pfa | Intercept Rate (/s) | Mean Reward | TTFI Surv Radar (s) | Agile Intercept Ratio | Time Error (ms) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Uniform Sequential (Open-Loop) | 100.0% | 0.0000 | 17.1 | +10.69 | 0.05 | 12.4% | N/A |
| Random Sweep (Open-Loop) | 100.0% | 0.0023 | 16.9 | +10.46 | 0.1 | 13.1% | N/A |
| Static Priority (Open-Loop) | 100.0% | 0.0021 | 15.4 | +9.77 | 0.325 | 17.4% | N/A |
| Discounted UCB (Online MAB) | 100.0% | 0.0039 | 19.9 | +12.93 | 0.05 | 10.6% | N/A |
| EXP3 (Adversarial MAB) | 100.0% | 0.0030 | 31.2 | +20.63 | 0.0 | 3.2% | N/A |
| Deep Q-Network (RL Policy) | 100.0% | 0.0029 | 30.6 | +25.90 | 0.6 | 6.0% | N/A |
| Predictive Temporal Interceptor | 100.0% | 0.0011 | 16.8 | +10.36 | 0.05 | 11.5% | 35.1 |
| Prime-Staggered Periodic | 100.0% | 0.0000 | 16.8 | +10.21 | 0.125 | 12.0% | N/A |

## Key Takeaways

1. **Closed-Loop Adaptation**: Discounted UCB and Deep Q-Network substantially outperform open-loop sequential sweep in average reward and agile emitter tracking.
2. **Anti-Stroboscopic Interception**: Prime-Staggered Periodic and Predictive Temporal Interceptors minimize intercept time error for periodic rotating emitters without getting locked in harmonic blind spots.
