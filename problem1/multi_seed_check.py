# Supplementary check: repeat Parts C-E over many seeds so conclusions about
# MLE vs Bayesian estimation do not depend on one random draw.
# Run:  python3 multi_seed_check.py   (needs smart_home_bn.py in the same folder)

import numpy as np
from smart_home_bn import (EXPERT, QUERIES, run_queries, sample_dataset,
                           learn_mle, learn_bdeu)

N_SEEDS = 100
expert = run_queries(EXPERT)
print(f"Average over {N_SEEDS} seeds (seeds 0..{N_SEEDS - 1})")
for n in [500, 5000, 20000]:
    em, eb = [], []  # per-seed absolute errors for each query
    for s in range(N_SEEDS):
        d = sample_dataset(EXPERT, n, seed=s)
        rm, rb = run_queries(learn_mle(d)), run_queries(learn_bdeu(d, 10))
        em.append([abs(expert[q] - rm[q]) for q in QUERIES])
        eb.append([abs(expert[q] - rb[q]) for q in QUERIES])
    em, eb = np.array(em), np.array(eb)
    print(f"\nN={n}: mean |diff| over Q1-Q7  MLE={em.mean():.5f}  Bayesian={eb.mean():.5f}"
          f"  (Bayesian better in {(eb.mean(1) < em.mean(1)).mean() * 100:.0f}% of seeds)")
    print("  per-query mean |diff| MLE      :",
          {q: round(v, 4) for q, v in zip(QUERIES, em.mean(0))})
    print("  per-query mean |diff| Bayesian :",
          {q: round(v, 4) for q, v in zip(QUERIES, eb.mean(0))})
