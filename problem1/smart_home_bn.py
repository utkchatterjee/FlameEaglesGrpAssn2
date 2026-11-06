# Problem 1: Smart Home Energy Consumption using a Bayesian Network.
# Covers Parts A-E. Run:  python3 smart_home_bn.py
# Everything (CPTs, exact inference, d-separation, sampling, MLE, BDeu) is
# implemented from scratch with numpy, so no extra libraries are required.

import itertools
import random
import numpy as np
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SEED = 42  # fixed seed -> reproducible sampling

# ---------------------------------------------------------------
# Network definition
# ---------------------------------------------------------------
# State space of every variable
STATES = {
    "Weather": ["Hot", "Mild", "Cold"],
    "DayType": ["Weekday", "Weekend"],
    "Occupancy": ["High", "Low"],
    "AC": ["On", "Off"],
    "ApplianceLoad": ["Heavy", "Light"],
    "Energy": ["High", "Low"],
}
# Parents of every variable; the dict order is also a topological order
PARENTS = {
    "Weather": [],
    "DayType": [],
    "Occupancy": ["DayType"],
    "AC": ["Weather", "Occupancy"],
    "ApplianceLoad": ["Occupancy"],
    "Energy": ["AC", "ApplianceLoad"],
}
ORDER = list(PARENTS)  # topological order used for sampling
EDGES = [(p, c) for c, ps in PARENTS.items() for p in ps]


def make_cpt(var, p_first):
    """Build a full CPT from P(first state) per parent configuration.
    p_first maps parent-config tuple -> P(first state of var)."""
    first, second = STATES[var][0], STATES[var][1]
    return {cfg: {first: p, second: 1 - p} for cfg, p in p_first.items()}


# Expert CPTs: cpt[var][parent_config][value] = probability
EXPERT = {
    "Weather": {(): {"Hot": 0.50, "Mild": 0.30, "Cold": 0.20}},
    "DayType": {(): {"Weekday": 0.70, "Weekend": 0.30}},
    "Occupancy": make_cpt("Occupancy", {("Weekday",): 0.45, ("Weekend",): 0.80}),
    "AC": make_cpt("AC", {
        ("Hot", "High"): 0.90, ("Hot", "Low"): 0.60,
        ("Mild", "High"): 0.40, ("Mild", "Low"): 0.15,
        ("Cold", "High"): 0.10, ("Cold", "Low"): 0.05}),
    "ApplianceLoad": make_cpt("ApplianceLoad", {("High",): 0.75, ("Low",): 0.35}),
    "Energy": make_cpt("Energy", {
        ("On", "Heavy"): 0.92, ("On", "Light"): 0.68,
        ("Off", "Heavy"): 0.55, ("Off", "Light"): 0.12}),
}


def parent_configs(var):
    """All combinations of parent values for a variable."""
    return list(itertools.product(*[STATES[p] for p in PARENTS[var]]))


def check_cpts(cpt):
    """Part A.2: every CPT row must sum to 1 and every parent config must exist."""
    ok = True
    for var in ORDER:
        for cfg in parent_configs(var):
            row = cpt[var][cfg]
            s = sum(row.values())
            if abs(s - 1) > 1e-9 or set(row) != set(STATES[var]):
                ok = False
                print(f"  BAD row {var}{cfg}: sum={s}")
    return ok


# ---------------------------------------------------------------
# Exact inference by enumerating the full joint distribution
# ---------------------------------------------------------------
def joint_table(cpt):
    """P(w,d,o,a,l,e) = product of P(var | parents) for all 96 assignments."""
    table = {}
    for vals in itertools.product(*[STATES[v] for v in ORDER]):
        a = dict(zip(ORDER, vals))
        p = 1.0
        for v in ORDER:
            cfg = tuple(a[q] for q in PARENTS[v])
            p *= cpt[v][cfg][a[v]]
        table[vals] = p
    return table


def prob(cpt, query, evidence=None):
    """P(query | evidence); query and evidence are dicts {var: value}.
    = sum of joint rows matching both / sum of joint rows matching evidence."""
    evidence = evidence or {}
    idx = {v: i for i, v in enumerate(ORDER)}
    num = den = 0.0
    for vals, p in joint_table(cpt).items():
        if all(vals[idx[k]] == x for k, x in evidence.items()):
            den += p
            if all(vals[idx[k]] == x for k, x in query.items()):
                num += p
    return num / den if den > 0 else float("nan")


# The seven required queries as (query, evidence)
QUERIES = {
    "Q1": ({"Energy": "High"}, {}),
    "Q2": ({"Energy": "High"}, {"Weather": "Hot"}),
    "Q3": ({"Energy": "High"}, {"DayType": "Weekend"}),
    "Q4": ({"Energy": "High"}, {"Weather": "Cold", "Occupancy": "High"}),
    "Q5": ({"Weather": "Hot"}, {"Energy": "High"}),
    "Q6": ({"AC": "On"}, {"Energy": "High"}),
    "Q7": ({"AC": "On"}, {"Energy": "High", "ApplianceLoad": "Heavy"}),
}


def run_queries(cpt):
    return {q: prob(cpt, qq, ev) for q, (qq, ev) in QUERIES.items()}


# ---------------------------------------------------------------
# d-separation (moralised ancestral graph method)
# ---------------------------------------------------------------
def d_separated(x, y, z):
    """True if x and y are d-separated given set z.
    Steps: keep ancestors of {x,y,z}, marry parents, drop directions,
    remove z, then check whether x and y are still connected."""
    g = nx.DiGraph(EDGES)
    g.add_nodes_from(ORDER)
    keep = {x, y} | set(z)
    for n in list(keep):
        keep |= nx.ancestors(g, n)
    sub = g.subgraph(keep)
    moral = nx.Graph(sub.to_undirected())
    for n in sub.nodes:
        ps = list(sub.predecessors(n))
        moral.add_edges_from(itertools.combinations(ps, 2))
    moral.remove_nodes_from(z)
    return not nx.has_path(moral, x, y)


# ---------------------------------------------------------------
# Ancestral sampling (Part C)
# ---------------------------------------------------------------
def sample_dataset(cpt, n, seed=SEED):
    """Visit nodes in topological order; sample each from P(var | sampled parents)."""
    rng = random.Random(seed)
    data = []
    for _ in range(n):
        row = {}
        for v in ORDER:
            cfg = tuple(row[q] for q in PARENTS[v])
            dist = cpt[v][cfg]
            u, cum = rng.random(), 0.0
            for val in STATES[v]:
                cum += dist[val]
                if u < cum:
                    row[v] = val
                    break
            else:  # guards against floating point round-off
                row[v] = STATES[v][-1]
        data.append(row)
    return data


# ---------------------------------------------------------------
# Parameter learning (Part D)
# ---------------------------------------------------------------
def count_table(data, var):
    """N[parent_config][value] = how often it appears in the data."""
    cnt = {cfg: {s: 0 for s in STATES[var]} for cfg in parent_configs(var)}
    for r in data:
        cnt[tuple(r[q] for q in PARENTS[var])][r[var]] += 1
    return cnt


def learn_mle(data):
    """MLE: P(x | cfg) = N(x, cfg) / N(cfg). Unseen cfg -> uniform fallback."""
    cpt = {}
    for v in ORDER:
        cpt[v] = {}
        for cfg, c in count_table(data, v).items():
            tot = sum(c.values())
            cpt[v][cfg] = {s: (c[s] / tot if tot else 1 / len(c)) for s in c}
    return cpt


def learn_bdeu(data, ess=10):
    """BDeu: each cell gets pseudo-count ess/(#states * #parent configs),
    so P(x | cfg) = (N(x,cfg) + a) / (N(cfg) + a * #states)."""
    cpt = {}
    for v in ORDER:
        r = len(STATES[v])
        q = len(parent_configs(v))
        a = ess / (r * q)
        cpt[v] = {}
        for cfg, c in count_table(data, v).items():
            tot = sum(c.values()) + a * r
            cpt[v][cfg] = {s: (c[s] + a) / tot for s in c}
    return cpt


# ---------------------------------------------------------------
# Helpers for printing
# ---------------------------------------------------------------
def ac_table(models):
    """Print the AC CPT: P(AC=On | Weather, Occupancy) for several models."""
    names = list(models)
    print(f"  {'Weather':<8}{'Occ':<6}" + "".join(f"{n:>10}" for n in names))
    for cfg in parent_configs("AC"):
        vals = "".join(f"{models[n]['AC'][cfg]['On']:>10.4f}" for n in names)
        print(f"  {cfg[0]:<8}{cfg[1]:<6}{vals}")


def main():
    # ===================== PART A =====================
    print("=" * 70, "\nPART A: EXPERT BAYESIAN NETWORK\n", "=" * 70, sep="")
    print("A.2 CPT validity (all rows sum to 1):", check_cpts(EXPERT))

    # A.3 draw the network
    g = nx.DiGraph(EDGES)
    pos = {"Weather": (0, 2), "DayType": (3, 2), "Occupancy": (3, 1),
           "AC": (1, 0), "ApplianceLoad": (4.5, 0), "Energy": (2.7, -1)}
    plt.figure(figsize=(8, 5.5))
    nx.draw(g, pos, with_labels=True, node_size=3600, node_color="#cfe3ff",
            font_size=9, arrowsize=22, edge_color="#444")
    plt.title("Smart Home Energy Bayesian Network")
    plt.savefig("bn_structure.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("A.3 Network drawing saved to bn_structure.png")

    # A.4 queries
    expert_res = run_queries(EXPERT)
    print("\nA.4 Expert-model query results")
    for q, (qq, ev) in QUERIES.items():
        print(f"  {q}: P({qq} | {ev}) = {expert_res[q]:.6f}")

    # A.5 explaining away
    q6, q7 = expert_res["Q6"], expert_res["Q7"]
    print(f"\nA.5 Q6 = {q6:.4f}  vs  Q7 = {q7:.4f}  (change {q7 - q6:+.4f})")
    print("  Heavy appliance load is itself a likely cause of High energy, so once")
    print("  it is known, High energy needs less 'help' from the AC -> AC=On drops.")

    # A.6 hand calculation of Q1 using the factorisation
    print("\nA.6 Q1 by summation (code check of the hand calculation)")
    pO = {o: sum(EXPERT["DayType"][()][d] * EXPERT["Occupancy"][(d,)][o]
                 for d in STATES["DayType"]) for o in STATES["Occupancy"]}
    pAOn_O = {o: sum(EXPERT["Weather"][()][w] * EXPERT["AC"][(w, o)]["On"]
                     for w in STATES["Weather"]) for o in STATES["Occupancy"]}
    print("  P(O=High) =", round(pO["High"], 6), " P(O=Low) =", round(pO["Low"], 6))
    print("  P(AC=On|O=High) =", round(pAOn_O["High"], 6),
          " P(AC=On|O=Low) =", round(pAOn_O["Low"], 6))
    q1_hand = 0.0
    for a in STATES["AC"]:
        for l in STATES["ApplianceLoad"]:
            p_al = 0.0
            for o in STATES["Occupancy"]:
                pa = pAOn_O[o] if a == "On" else 1 - pAOn_O[o]
                p_al += pO[o] * EXPERT["ApplianceLoad"][(o,)][l] * pa
            pe = EXPERT["Energy"][(a, l)]["High"]
            print(f"  P(A={a:<3},L={l:<5}) = {p_al:.8f}  x P(E=High|..)={pe:.2f}"
                  f"  -> {p_al * pe:.8f}")
            q1_hand += p_al * pe
    print(f"  Q1 by hand-sum = {q1_hand:.8f} ; Q1 by code = {expert_res['Q1']:.8f}"
          f" ; match = {abs(q1_hand - expert_res['Q1']) < 1e-12}")

    # ===================== PART B =====================
    print("\n" + "=" * 70, "\nPART B: CONDITIONAL INDEPENDENCE\n", "=" * 70, sep="")
    tests = [
        ("Weather", "DayType", [],
         ("P(W=Hot)", {"Weather": "Hot"}, {}),
         ("P(W=Hot | D=Weekend)", {"Weather": "Hot"}, {"DayType": "Weekend"})),
        ("Weather", "DayType", ["Energy"],
         ("P(W=Hot | E=High)", {"Weather": "Hot"}, {"Energy": "High"}),
         ("P(W=Hot | E=High, D=Weekend)", {"Weather": "Hot"},
          {"Energy": "High", "DayType": "Weekend"})),
        ("Weather", "ApplianceLoad", ["Occupancy"],
         ("P(W=Hot | O=High)", {"Weather": "Hot"}, {"Occupancy": "High"}),
         ("P(W=Hot | O=High, L=Heavy)", {"Weather": "Hot"},
          {"Occupancy": "High", "ApplianceLoad": "Heavy"})),
    ]
    for i, (x, y, z, (n1, q1_, e1), (n2, q2_, e2)) in enumerate(tests, 1):
        ds = d_separated(x, y, z)
        a, b = prob(EXPERT, q1_, e1), prob(EXPERT, q2_, e2)
        print(f"B.{i} {x} _||_ {y} | {z}: d-separated = {ds}")
        print(f"     {n1} = {a:.6f}   {n2} = {b:.6f}   equal = {abs(a - b) < 1e-9}")

    # ===================== PART C =====================
    print("\n" + "=" * 70, "\nPART C: SYNTHETIC DATA (seed =", SEED, ")\n", "=" * 70, sep="")
    sizes = [500, 5000, 20000]
    datasets = {n: sample_dataset(EXPERT, n) for n in sizes}
    for n, d in datasets.items():
        print(f"\nN = {n}")
        print("  Weather empirical frequency:",
              {w: round(sum(r["Weather"] == w for r in d) / n, 4)
               for w in STATES["Weather"]})
        print("  (Weather, Occupancy) counts:")
        for w in STATES["Weather"]:
            print("   ", w, {o: sum(r["Weather"] == w and r["Occupancy"] == o
                                    for r in d) for o in STATES["Occupancy"]})

    # ===================== PART D & E =====================
    print("\n" + "=" * 70, "\nPART D/E: LEARNING AND COMPARISON\n", "=" * 70, sep="")
    mean_err = {"MLE": [], "Bayesian": []}
    for n in sizes:
        mle, bde = learn_mle(datasets[n]), learn_bdeu(datasets[n], ess=10)
        print(f"\n--- Dataset size {n} ---")
        print("D.3 AC CPT  P(AC=On | Weather, Occupancy):")
        ac_table({"Expert": EXPERT, "MLE": mle, "BDeu": bde})
        rm, rb = run_queries(mle), run_queries(bde)
        print(f"\n  {'Query':<6}{'Expert':>9}{'MLE':>9}{'Bayes':>9}"
              f"{'|Diff|MLE':>11}{'|Diff|Bayes':>13}")
        dm, db = [], []
        for q in QUERIES:
            e, m, b = expert_res[q], rm[q], rb[q]
            dm.append(abs(e - m))
            db.append(abs(e - b))
            print(f"  {q:<6}{e:>9.4f}{m:>9.4f}{b:>9.4f}{dm[-1]:>11.4f}{db[-1]:>13.4f}")
        mean_err["MLE"].append(np.mean(dm))
        mean_err["Bayesian"].append(np.mean(db))
        worst = max(zip(QUERIES, dm), key=lambda t: t[1])
        print(f"  Mean |Diff|: MLE={np.mean(dm):.5f}  Bayesian={np.mean(db):.5f}")
        print(f"  Largest MLE error: {worst[0]} ({worst[1]:.4f})")
        if n == 500:
            # how many rows contain the evidence of each query
            print("  Evidence counts in the 500-sample data:")
            for q, (_, ev) in QUERIES.items():
                c = sum(all(r[k] == v for k, v in ev.items()) for r in datasets[n])
                print(f"    {q}: evidence {ev or '(none)'} occurs {c} times")

    # E.1 plot of mean absolute difference vs dataset size
    plt.figure(figsize=(6.5, 4.2))
    plt.plot(sizes, mean_err["MLE"], "o-", label="MLE")
    plt.plot(sizes, mean_err["Bayesian"], "s-", label="Bayesian (BDeu, ESS=10)")
    plt.xscale("log")
    plt.xlabel("Dataset size (log scale)")
    plt.ylabel("Mean |Expert - Learned| over Q1-Q7")
    plt.title("Learning error vs dataset size")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.savefig("error_vs_size.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("\nE.1 Plot saved to error_vs_size.png")
    print("Mean errors:", {k: [round(x, 5) for x in v] for k, v in mean_err.items()})


if __name__ == "__main__":
    main()