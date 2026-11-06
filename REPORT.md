# AI Group Assignment 2 – Analysis Report

**Group members (fill in before submitting):**

| Name | Roll No. |
|------|----------|
| Moguluri Sai Siddharda | B24DS018 |
| Samarth Goyal | B24DS026 |
| Utkarsh Chatterjee | B24CS050 |
| Yash Bhardwaj | B24CS053 |
| Adarsh Satyam | B24CS002 |



---

## Problem 1 – Smart Home Bayesian Network

Files: `problem1/smart_home_bn.py` (all parts), `multi_seed_check.py` (robustness check), `output_log.txt`, `bn_structure.png`, `error_vs_size.png`.

### Part A – Expert network

Structure: Weather→AC, DayType→Occupancy, Occupancy→AC, Occupancy→ApplianceLoad, AC→Energy, ApplianceLoad→Energy (see `bn_structure.png`). The code checks that every CPT row sums to 1: **True**.

| Query | Value |
|---|---|
| Q1 P(E=High) | 0.580631 |
| Q2 P(E=High \| W=Hot) | 0.706266 |
| Q3 P(E=High \| D=Weekend) | 0.640199 |
| Q4 P(E=High \| W=Cold, O=High) | 0.484250 |
| Q5 P(W=Hot \| E=High) | 0.608188 |
| Q6 P(AC=On \| E=High) | 0.692867 |
| Q7 P(AC=On \| E=High, L=Heavy) | 0.649899 |

**A.5 Explaining away.** Q6 = 0.6929 drops to Q7 = 0.6499. AC=On and Appliance Load=Heavy are two competing causes of High energy. Once we learn the load is Heavy, that alone already explains much of the High consumption, so the evidence for the AC being on weakens. (The drop is modest because both causes share the parent Occupancy: Heavy load also hints at High occupancy, which slightly raises P(AC=On).)

**A.6 Q1 by hand.** Use P(E=High) = Σ_{A,L} P(E=High|A,L) · P(A,L), with P(A,L) = Σ_O P(O) P(L|O) P(A|O) (A and L are independent given O).

1. P(O=High) = 0.7·0.45 + 0.3·0.80 = 0.555, so P(O=Low) = 0.445.
2. P(A=On|O=High) = 0.5·0.90 + 0.3·0.40 + 0.2·0.10 = 0.59. P(A=On|O=Low) = 0.5·0.60 + 0.3·0.15 + 0.2·0.05 = 0.355.
3. P(On,Heavy) = 0.555·0.75·0.59 + 0.445·0.35·0.355 = 0.24558750 + 0.05529125 = 0.30087875
 P(On,Light) = 0.555·0.25·0.59 + 0.445·0.65·0.355 = 0.08186250 + 0.10268375 = 0.18454625
 P(Off,Heavy) = 0.555·0.75·0.41 + 0.445·0.35·0.645 = 0.17066250 + 0.10045875 = 0.27112125
 P(Off,Light) = 0.555·0.25·0.41 + 0.445·0.65·0.645 = 0.05688750 + 0.18656625 = 0.24345375 (the four add to 1)
4. Q1 = 0.92·0.30087875 + 0.68·0.18454625 + 0.55·0.27112125 + 0.12·0.24345375
 = 0.27680845 + 0.12549145 + 0.14911669 + 0.02921445 = **0.58063104**, identical to the code value.

### Part B – Conditional independence

| Statement | d-separated? | Reason | Numeric check |
|---|---|---|---|
| Weather ⊥ DayType | **Yes** | Only path is W→A←O←D. A is a collider, not observed (its descendant E is not observed either), so the path is blocked. | P(W=Hot) = 0.5000; P(W=Hot\|D=Weekend) = 0.5000 |
| Weather ⊥ DayType \| Energy | **No** | The same path W→A←O←D now has its collider A's descendant E observed, which opens the path (E is also a collider on W→A→E←L←O←D, observed). | P(W=Hot\|E=High) = 0.6082; P(W=Hot\|E=High, D=Weekend) = 0.5998 |
| Weather ⊥ ApplianceLoad \| Occupancy | **Yes** | Path W→A←O→L: O is a fork and is observed, so it blocks. Path W→A→E←L: collider E is unobserved, so it blocks. | P(W=Hot\|O=High) = 0.5000; P(W=Hot\|O=High, L=Heavy) = 0.5000 |

### Part C – Synthetic data (ancestral sampling, seed = 42 for every dataset)

| N | Hot | Mild | Cold |
|---|---|---|---|
| 500 | 0.500 | 0.278 | 0.222 |
| 5000 | 0.502 | 0.2904 | 0.2076 |
| 20000 | 0.501 | 0.2969 | 0.2021 |

(Weather, Occupancy) counts, as High / Low:

| N | Hot | Mild | Cold |
|---|---|---|---|
| 500 | 144 / 106 | 78 / 61 | 56 / 55 |
| 5000 | 1416 / 1094 | 830 / 622 | 559 / 479 |
| 20000 | 5606 / 4415 | 3327 / 2610 | 2222 / 1820 |

### Parts D and E – Learned vs expert

BDeu with equivalent sample size 10 gives each cell a pseudo-count of 10 / (#states × #parent configs). The AC CPT for each dataset is printed next to the expert CPT in `output_log.txt`; for N = 500:

| Weather, Occ | Expert | MLE | BDeu |
|---|---|---|---|
| Hot, High | 0.9000 | 0.8819 | 0.8776 |
| Hot, Low | 0.6000 | 0.6226 | 0.6207 |
| Mild, High | 0.4000 | 0.4487 | 0.4498 |
| Mild, Low | 0.1500 | 0.1803 | 0.1888 |
| Cold, High | 0.1000 | 0.0536 | 0.0665 |
| Cold, Low | 0.0500 | 0.0182 | 0.0324 |

**N = 500**

| Query | Expert | MLE | Bayesian | \|Diff\| MLE | \|Diff\| Bayes |
|---|---|---|---|---|---|
| Q1 | 0.5806 | 0.5905 | 0.5888 | 0.0099 | 0.0082 |
| Q2 | 0.7063 | 0.7003 | 0.6951 | 0.0060 | 0.0112 |
| Q3 | 0.6402 | 0.6493 | 0.6434 | 0.0091 | 0.0032 |
| Q4 | 0.4843 | 0.5073 | 0.5100 | 0.0230 | 0.0257 |
| Q5 | 0.6082 | 0.5929 | 0.5863 | 0.0153 | 0.0218 |
| Q6 | 0.6929 | 0.6619 | 0.6589 | 0.0310 | 0.0340 |
| Q7 | 0.6499 | 0.6326 | 0.6305 | 0.0173 | 0.0194 |
| **Mean** | | | | **0.01592** | **0.01765** |

**N = 5000**

| Query | Expert | MLE | Bayesian | \|Diff\| MLE | \|Diff\| Bayes |
|---|---|---|---|---|---|
| Q1 | 0.5806 | 0.5874 | 0.5872 | 0.0067 | 0.0066 |
| Q2 | 0.7063 | 0.7168 | 0.7162 | 0.0105 | 0.0099 |
| Q3 | 0.6402 | 0.6468 | 0.6462 | 0.0066 | 0.0060 |
| Q4 | 0.4843 | 0.4846 | 0.4850 | 0.0004 | 0.0007 |
| Q5 | 0.6082 | 0.6126 | 0.6119 | 0.0044 | 0.0037 |
| Q6 | 0.6929 | 0.6957 | 0.6953 | 0.0028 | 0.0024 |
| Q7 | 0.6499 | 0.6511 | 0.6508 | 0.0012 | 0.0009 |
| **Mean** | | | | **0.00466** | **0.00432** |

**N = 20000**

| Query | Expert | MLE | Bayesian | \|Diff\| MLE | \|Diff\| Bayes |
|---|---|---|---|---|---|
| Q1 | 0.5806 | 0.5866 | 0.5865 | 0.0059 | 0.0059 |
| Q2 | 0.7063 | 0.7117 | 0.7116 | 0.0055 | 0.0053 |
| Q3 | 0.6402 | 0.6452 | 0.6451 | 0.0050 | 0.0049 |
| Q4 | 0.4843 | 0.4899 | 0.4899 | 0.0056 | 0.0057 |
| Q5 | 0.6082 | 0.6080 | 0.6078 | 0.0002 | 0.0004 |
| Q6 | 0.6929 | 0.6913 | 0.6912 | 0.0016 | 0.0017 |
| Q7 | 0.6499 | 0.6492 | 0.6491 | 0.0007 | 0.0008 |
| **Mean** | | | | **0.00351** | **0.00352** |

**E.1 Plot:** `error_vs_size.png` (mean |diff| versus dataset size). Error falls for both estimators as data grows (about 0.016–0.018 at 500, 0.004–0.005 at 5000, 0.0035 at 20000).

**E.2 Largest error at 500 samples.** In our seed-42 dataset the largest error is **Q6** for both estimators (0.0310 MLE, 0.0340 Bayesian); Q4 is second (0.0230 / 0.0257). Q4 is nevertheless the query that depends on the least data: its evidence (Weather=Cold and Occupancy=High) appears in only **56 of 500 rows**, versus 250 for Q2, 146 for Q3 and 296 for Q5/Q6. Fewer rows means a noisier estimate of the AC and Energy entries it relies on, and an error in one rare CPT row is not averaged out. To check that this is not an accident of one seed, `multi_seed_check.py` repeats everything for 100 seeds: at N = 500, Q4 has the largest average error (MLE 0.0294, Bayesian 0.0282) against about 0.018–0.020 for every other query. So Q4 is the consistently hardest query, even though one particular draw can make another query look worse.

**E.3 Which estimator is better for small data?** In principle Bayesian estimation should help on small data: the BDeu pseudo-counts smooth sparse counts and prevent probabilities of exactly 0 or 1, which MLE can produce when a parent configuration is rare. In our experiment the benefit is small. In the seed-42 run, MLE is slightly better at N = 500 (0.0159 vs 0.0177) and Bayesian is slightly better at N = 5000. Averaged over 100 seeds at N = 500 the two are essentially tied (MLE 0.02065 vs Bayesian 0.02018; Bayesian wins in 55% of seeds). The reason is that every parent configuration here still has at least about 50 samples, and the prior adds only ≈1.7 pseudo-samples per AC row, so it barely moves the estimates. Where the prior does act (the rare Cold rows) it helps, e.g. Cold/Low: expert 0.05, MLE 0.018, BDeu 0.032. However, the prior shrinks every estimate toward 0.5, which slightly hurts rows whose true value is large (Hot/High). The advantage of Bayesian estimation would be much larger with sparser data or more parents. At 20000 samples the two estimators are nearly identical, but not exactly: the mean absolute errors are 0.00351 (MLE) and 0.00352 (Bayesian), and the query estimates still differ slightly.

---

## Problem 2 – Mars Rover (PDDL)

Files: `Domain.pddl`, `Problem.pddl`, `Problem_extended.pddl`, `original_greedy.txt`, `original_greedy.plan`, `original_astar.txt`, `original_astar.plan`, `extended_greedy.txt`, `extended_greedy.plan`, `extended_astar.txt`, and `extended_astar.plan`.

### Tasks 1–2 – Domain and problem modelling

The domain declares only `:strips` and `:typing`. Its object types are `location`, `rover`, `bay`, `rock`, and `drill`. All samples use the `rock` type; their properties are represented by the static predicates `soft` and `hard` rather than separate PDDL subtypes.

The main predicates represent the rover's location (`rover-at`), directed movement links (`connected`), rock and drill locations (`rock-at`, `drill-at`), rock properties (`soft`, `hard`), drill possession (`has-drill`), bay ownership (`bay-of`), bay availability (`bay-empty`), and stored samples (`in-bay`). The `bay-empty` predicate lets the collection actions require an available bay using a positive precondition. Collecting a rock removes `bay-empty` and adds `in-bay`; depositing reverses those two facts.

The five action schemas are `move`, `pick-drill`, `collect-soft`, `collect-hard`, and `deposit`. `collect-hard` has the additional `has-drill` precondition. `collect-soft` does not. The domain has no action for dropping the drill, so once picked up it remains with the rover. Negative expressions occur only in action effects (delete effects), not in preconditions, which is compatible with the STRIPS requirement.

Connectivity is represented as a directed relation. Every two-way route is entered twice, once in each direction; the steep slope is entered only as `(connected sitec sited)`. In the extended problem, both `(connected base siteb)` and `(connected siteb base)` are omitted to represent the dust-storm closure.

The original problem places Curiosity at Base, Drill1 at SiteE, and Rocks 1–5 at their specified sites. It marks Rock1, Rock2, and Rock4 as soft, and Rock3 and Rock5 as hard. Both bays initially belong to Curiosity and are empty. The goal requires all five rocks at Base, both bays empty, and Curiosity at Base. The extended problem adds soft Rock6 at SiteE and hard Rock7 at SiteF, removes the two Base–SiteB connections, and adds Rock6 and Rock7 to the goal.

### Task 3 – Plan generation and results

Fast Downward 24.06.1 was used for both scenarios. The satisficing configuration was Greedy Best-First Search with the FF heuristic (`lazy_greedy([ff()])`). The optimal configuration was A* with the admissible LM-cut heuristic (`astar(lmcut())`). Every action has unit cost, so plan cost equals the number of actions.

| Scenario | Configuration | Plan length = total actions = cost | States expanded | Search time | Total planner time |
|---|---|---:|---:|---:|---:|
| Original | Satisficing: GBFS + FF | 33 | 122 | 0.0021 s | 0.22 s |
| Original | Optimal: A* + LM-cut | 25 | 6,828 | 0.5471 s | 0.73 s |
| Extended | Satisficing: GBFS + FF | 46 | 241 | 0.0035 s | 0.19 s |
| Extended | Optimal: A* + LM-cut | 40 | 2,553,762 | 260.4162 s | 260.63 s |

Search time is the planner's reported search-only time. Total planner time includes translation and the planner's other overhead, so the two time columns are not expected to be identical. Small timings are machine-dependent. The complete action sequences are preserved in the corresponding `.plan` files, and the full Fast Downward output is preserved in the matching `.txt` files.

### Task 4 – Goal verification

Each of the four plan files was replayed from the initial state in its matching problem file. At every step, the action's positive preconditions were checked before applying its add and delete effects. All four plans passed: no action was attempted when its preconditions were false, and each resulting final state satisfied the complete goal conjunction.

In the original scenario, Rock1–Rock5 are at Base. In the extended scenario, Rock1–Rock7 are at Base. In all four final states, `bay-empty bay1`, `bay-empty bay2`, and `rover-at curiosity base` are true. The rover still has the drill, which is allowed because the goal does not require it to be returned. VAL was not used; verification was performed by step-by-step state replay.

### Task 5 – Extended scenario

The extended instance is modelled separately in `Problem_extended.pddl`; the domain file is unchanged because the same actions and predicates still describe the rover's behaviour. The following modifications are made to the original problem:

- **New samples:** Rock6 is added as a soft rock at SiteE, and Rock7 as a hard rock at SiteF. Their initial facts are `(rock-at rock6 sitee)`, `(soft rock6)`, `(rock-at rock7 sitef)`, and `(hard rock7)`.
- **Dust-storm closure:** the two directed connectivity facts for the Base↔SiteB route, `(connected base siteb)` and `(connected siteb base)`, are omitted. The SiteB↔SiteD connection remains available.
- **Goal update:** the goal now requires Rock1–Rock7 to be at Base, both bays to be empty, and Curiosity to finish at Base.

The extended problem was run with both search configurations. Greedy Best-First Search with the FF heuristic generated a 46-action plan (`extended_greedy.plan`); A* with LM-cut generated a 40-action plan (`extended_astar.plan`). Their complete Fast Downward logs are `extended_greedy.txt` and `extended_astar.txt`. The corresponding search statistics are reported in Task 3, and both plans passed the step-by-step goal verification described in Task 4.

### Task 6 – Plan analysis

**1. Plan-length comparison.** In the original scenario, GBFS returns a 33-action plan while A* returns a 25-action plan, a reduction of 8 actions. In the extended scenario, GBFS returns 46 actions and A* returns 40, a reduction of 6 actions. GBFS is satisficing: it follows heuristic guidance and finds a solution quickly, but it does not guarantee the shortest plan. A* combines the path cost already incurred with an admissible estimate of the remaining cost; with LM-cut and unit action costs, it returns an optimal plan. This advantage comes at a computational cost in the extended problem: A* expands 2,553,762 states and takes about 260.6 seconds overall, compared with 241 states and about 0.19 seconds for GBFS. The larger search is the cost of establishing an optimal solution rather than stopping at the first satisfactory one.

The two strategies also use the bays differently. The original GBFS plan uses Bay1 only and makes separate collection-and-return trips for the five rocks. Its extended plan does use both bays for the Rock2/Rock4 pair and the Rock5/Rock7 pair, but handles other rocks on separate trips. The A* plans make more systematic use of the two-bay capacity.

**2. How the optimal plans use the bays and when the drill is collected.** In the original A* plan, the rover first collects Rock2 into Bay1 at SiteB and Rock4 into Bay2 at SiteD, then returns to Base and deposits both. It next reaches SiteE and picks up the drill at **action 12**, before collecting any hard rock. It collects Rock5 into Bay1 at SiteF, then collects Rock3 into Bay2 at SiteC on the return route. Both hard rocks are brought to Base and deposited. With a bay free again, the rover makes a final trip to SiteA for Rock1.

In the extended A* plan, the first trip collects Rock4 and Rock2 into the two bays and deposits them at Base. The rover picks up the drill at **action 9**, at SiteE, before collecting the hard rocks. The next trip collects Rock5 and Rock7 together from SiteF. A later trip collects Rock3 at SiteC and Rock6 at SiteE together. Rock1 at SiteA is collected on the final trip. Thus, the optimal extended plan uses both bays on three paired trips and carries only Rock1 alone. In both optimal plans, the drill is picked up after the soft-rock collection on the first outing and before any hard-rock collection; SiteE is a useful point from which to reach the hard-rock sites.

**3. Extended scenario: access to SiteB and SiteD.** The dust storm removes the direct Base↔SiteB route. Both extended plans reach SiteB through SiteD. The A* route begins Base→SiteA→SiteC→SiteD→SiteB; the move SiteC→SiteD uses the one-way downhill connection in its permitted direction. The GBFS plan also uses SiteC→SiteD before continuing to SiteB. SiteD is also reachable from SiteE, but the slope gives a shorter route from SiteC to SiteD. On the return, the rover travels SiteB→SiteD→SiteE→SiteC→SiteA→Base; it does not attempt the forbidden SiteD→SiteC movement. Therefore, **both extended plans use the one-way route, and neither uses it in reverse**. In the original scenario, neither supplied plan needs the slope because the direct Base↔SiteB connection is still available.
---

## Problem 3 – Royal Archive (Prolog resolution refutation)

File: `problem3/royal_archive_access.pl` (follows the 8-step structure of the Aristotle example).

**Representation.** Predicates: `archivist/1, verifies/2, trusted/1, access/2, sealed/1, permitted/2, inspects/2, finds_mark/2, stored_in_archive/1`. Constants: `mira, scroll_7`. Variables: X (person), R (record). Negated goal: `¬trusted(mira)`.

**Clauses (CNF).** There are no existential quantifiers, so no Skolemization is needed.
1. `¬archivist(X) ∨ ¬verifies(X,R) ∨ trusted(X)`
2. `¬trusted(X) ∨ ¬access(X,R) ∨ ¬sealed(R) ∨ permitted(X,R)` (not needed)
3. `¬inspects(X,R) ∨ ¬finds_mark(X,R) ∨ verifies(X,R)`
4. `¬stored_in_archive(R) ∨ sealed(R)` (not needed)
5. `stored_in_archive(scroll_7)`
6. `access(mira,scroll_7)`
7. `inspects(mira,scroll_7)`
8. `finds_mark(mira,scroll_7)`
9. `archivist(mira)`
10. `¬trusted(mira)` (negated goal)

**Proof chain.** Rules 2 and 4, and the facts `stored_in_archive` and `access`, are distractors (they lead to `permitted`/`sealed`, never to `trusted`).
- (3) + `inspects(mira,scroll_7)` → `¬finds_mark(mira,scroll_7) ∨ verifies(mira,scroll_7)`
- + `finds_mark(mira,scroll_7)` → `verifies(mira,scroll_7)`
- (1) + `¬trusted(mira)` → `¬archivist(mira) ∨ ¬verifies(mira,R)`
- + `archivist(mira)` → `¬verifies(mira,R)`
- + `verifies(mira,scroll_7)` → **[]** (empty clause), so Mira is trusted.


The program searches for this itself with a given-clause resolution loop (renaming variables, using Prolog unification) and prints the clauses and resolvents actually used, in order. It may produce extra resolvents during the search, but only the ancestors of `[]` are printed.

**Executed on SWI Prolog.**
