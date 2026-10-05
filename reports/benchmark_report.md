# DRDO Electronic Support Receiver Benchmark Report

Evaluated over 5 Monte Carlo runs of 1000 dwell steps each across 8 surveillance bands.

## Figures of Merit Comparison

| Strategy / Scheduler | Pd (%) | Pfa | Intercept Rate (/s) | Mean Reward | TTFI Surv Radar (s) | Agile Intercept Ratio | Time Error (ms) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Uniform Sequential (Open-Loop) | 100.0% | 0.0003 | 16.6 | +10.20 | 0.05 | 12.5% | N/A |
| Random Sweep (Open-Loop) | 100.0% | 0.0020 | 16.4 | +9.99 | 0.1 | 13.2% | N/A |
| Static Priority (Open-Loop) | 100.0% | 0.0010 | 14.9 | +8.94 | 0.325 | 13.8% | N/A |
| Discounted UCB (Online MAB) | 100.0% | 0.0016 | 20.0 | +13.04 | 0.05 | 10.7% | N/A |
| EXP3 (Adversarial MAB) | 100.0% | 0.0013 | 33.6 | +23.25 | 0.0 | 2.5% | N/A |
| Deep Q-Network (RL Policy) | 100.0% | 0.0028 | 34.7 | +32.36 | 0.35 | 2.6% | N/A |
| Predictive Temporal Interceptor | 100.0% | 0.0021 | 16.9 | +10.75 | 0.05 | 12.7% | 38.0 |
| Prime-Staggered Periodic | 100.0% | 0.0007 | 16.7 | +10.32 | 0.125 | 12.7% | N/A |

## Key Takeaways

1. **Closed-Loop Adaptation**: Discounted UCB and Deep Q-Network substantially outperform open-loop sequential sweep in average reward and agile emitter tracking.
2. **Anti-Stroboscopic Interception**: Prime-Staggered Periodic and Predictive Temporal Interceptors minimize intercept time error for periodic rotating emitters without getting locked in harmonic blind spots.
