# Mars Rover Sample Collection Planning — Analysis Report

## 1. Scope and approach

The supplied `Domain.pddl`, `Problem.pddl`, and `Problem_extended.pddl` were evaluated using Fast Downward 24.06.1. Two search configurations were run for each scenario:

- **Satisficing:** Lazy Greedy Best-First Search with the FF heuristic: `lazy_greedy([ff()])`.
- **Optimal:** A* with the LM-cut heuristic: `astar(lmcut())`.

Every action has unit cost, so the reported plan cost equals the number of actions. LM-cut is admissible; therefore A* with this heuristic returns an optimal-cost plan for these unit-cost tasks. Greedy Best-First Search is satisficing and does not guarantee optimality.

The four complete action sequences are retained in the accompanying `.plan` files. The summary below explains their structure and compares the measured search statistics.

## 2. Model review

The domain uses only `:strips` and `:typing`. It declares the object types `location`, `rover`, `bay`, `rock`, and `drill`. Softness and hardness are represented by the static predicates `soft` and `hard`, rather than by separate rock subtypes.

The predicates describe rover position, directed connectivity, rock and drill locations, drill possession, bay ownership, bay occupancy, and rock storage. The five action schemas are `move`, `pick-drill`, `collect-soft`, `collect-hard`, and `deposit`.

The model represents two-way routes by listing both directed `connected` facts. The steep route is represented only by `(connected sitec sited)`, so movement from SiteD directly to SiteC is not permitted. The extended problem correctly removes both Base–SiteB connectivity facts while retaining SiteB's connection to SiteD.

The goal in each problem requires every relevant rock to be at Base, both bays to be empty, and Curiosity to be at Base. The initial states also correctly specify each rock's `soft` or `hard` property and the ownership and initial emptiness of both bays.

## 3. Planner results

| Scenario | Search configuration | Plan length / cost | Expanded states | Generated states | Search time | End-to-end planner time |
|---|---|---:|---:|---:|---:|---:|
| Original | Greedy Best-First (FF) | 33 | 122 | 458 | 0.002137 s | 0.22 s |
| Original | A* (LM-cut) | **25** | 6,828 | 27,840 | 0.547081 s | 0.73 s |
| Extended | Greedy Best-First (FF) | 46 | 241 | 982 | 0.003460 s | 0.19 s |
| Extended | A* (LM-cut) | **40** | 2,553,762 | 10,392,770 | 260.416245 s | 260.63 s |

*Timing note:* “Search time” is Fast Downward's internal search statistic. “End-to-end planner time” is the `INFO Planner time` reported by the surrounding Fast Downward script, and includes additional run overhead. Small times can vary with machine load and process startup.

### 3.1 Plan-length comparison

In the original scenario, A* finds a 25-action plan compared with the greedy plan's 33 actions. This is 8 fewer actions, or approximately **24.2% shorter** than the greedy plan.

In the extended scenario, A* finds a 40-action plan compared with the greedy plan's 46 actions. This is 6 fewer actions, or approximately **13.0% shorter**.

These results illustrate the trade-off between the configurations. Greedy Best-First Search finds valid plans quickly and expands relatively few states, but it does not optimise plan length. A* with LM-cut finds the shorter, optimal plans, but the search can be much more expensive. This is particularly visible in the extended scenario: A* expands 2,553,762 states, compared with 241 for greedy search, and takes about 260.4 seconds of internal search time.

### 3.2 Action counts

| Scenario | Configuration | Move | Collect | Pick drill | Deposit | Total |
|---|---|---:|---:|---:|---:|---:|
| Original | Greedy | 22 | 5 | 1 | 5 | 33 |
| Original | A* | 14 | 5 | 1 | 5 | 25 |
| Extended | Greedy | 31 | 7 | 1 | 7 | 46 |
| Extended | A* | 25 | 7 | 1 | 7 | 40 |

The plan-length differences are primarily due to movement. Both configurations must collect and deposit every rock and pick up the drill once; A* reduces unnecessary travel and uses the two bays to combine deliveries.

## 4. Plan structure and storage-bay use

The full ordered action sequences are in `original_greedy.plan`, `original_astar.plan`, `extended_greedy.plan`, and `extended_astar.plan`. The following is a trip-level summary of those sequences.

### 4.1 Original scenario

- **Greedy:** Makes five separate delivery trips: Rock1; Rock4; Rock2; Rock3; and Rock5. It uses Bay1 for all five collections and does not use Bay2. The drill is picked up at action 8, before collecting Rock4 and the two hard rocks.
- **A*:** Uses three delivery trips. First it collects Rock2 into Bay1 and Rock4 into Bay2, then returns to Base and deposits both. It next collects hard Rock5 into Bay1 and hard Rock3 into Bay2 after obtaining the drill, and delivers them together. Rock1 is collected and delivered on the final trip. The drill is picked up at **action 12**, at SiteE, after the first two soft samples have been delivered and before either hard sample is collected.

This is a clear example of A* exploiting the two-bay capacity: it carries two rocks at once on two of its three delivery trips, reducing the number of movements and total actions.

### 4.2 Extended scenario

- **Greedy:** Makes five delivery trips: Rock1; Rock3; Rock2 and Rock4 together; Rock5 and Rock7 together; and Rock6. It picks up the drill at **action 8**, at SiteE. It uses Bay2 for the Rock4 and Rock7 collections, but otherwise relies on Bay1.
- **A*:** Makes four delivery trips: Rock4 and Rock2 together; Rock5 and Rock7 together; Rock3 and Rock6 together; and Rock1. It uses both bays on the first three trips, with each pair deposited at Base before the next collection run. The drill is picked up at **action 9**, at SiteE, after collecting the two soft rocks Rock4 and Rock2 on the first trip and before collecting any hard rock.

The optimal extended plan therefore uses the two bays more consistently: three paired deliveries instead of the greedy plan's two paired deliveries. This reduces the number of trips and contributes to the 6-action improvement.

## 5. Dust-storm route analysis

The extended problem removes both `(connected base siteb)` and `(connected siteb base)`, closing the direct Base–SiteB route. SiteB remains connected to SiteD in both directions. The A* plan reaches SiteB by the legal path:

**Base → SiteA → SiteC → SiteD → SiteB**

The move from SiteC to SiteD uses the one-way downhill route, which is explicitly present in the problem as `(connected sitec sited)`. The rover then moves from SiteD to SiteB using the ordinary two-way connection. On the return journey it travels SiteB → SiteD → SiteE → SiteC → SiteA → Base. It does not attempt the forbidden direct movement SiteD → SiteC.

The extended greedy plan also uses SiteC → SiteD to reach SiteB. Thus, both generated plans respect the dust-storm closure and the one-way slope constraint.

## 6. Goal verification

Each of the four `.plan` files was independently replayed in sequence against the supplied domain and corresponding problem file. For every step, the replay checked that the action exists, its arguments have the declared types, and all positive preconditions hold before applying its add and delete effects. **No invalid action or missing precondition was found in any plan.**

The final replayed states satisfy the required goals:

### Original scenario — both configurations

- `(rock-at rock1 base)`
- `(rock-at rock2 base)`
- `(rock-at rock3 base)`
- `(rock-at rock4 base)`
- `(rock-at rock5 base)`
- `(bay-empty bay1)` and `(bay-empty bay2)`
- `(rover-at curiosity base)`

### Extended scenario — both configurations

- `(rock-at rock1 base)` through `(rock-at rock7 base)`
- `(bay-empty bay1)` and `(bay-empty bay2)`
- `(rover-at curiosity base)`

The rover also retains the drill after picking it up, as intended by the domain. Goal satisfaction does not require the drill to be returned to SiteE.

## 7. Conclusion

Both search configurations solve both scenarios, and all four plans satisfy the modeled goals. Greedy Best-First Search is substantially cheaper in state expansions and runtime, but returns longer plans. A* with LM-cut returns the optimal plans: 25 actions for the original scenario and 40 for the extended scenario. Its computational cost rises sharply in the extended scenario, where it expands over 2.5 million states.

The extended A* plan handles the dust storm by taking the indirect route through SiteA, SiteC, SiteD, and SiteB. It uses the one-way SiteC → SiteD edge in the permitted direction and never traverses the closed Base–SiteB edge.

## 8. Files corresponding to the results

| File | Contents |
|---|---|
| `Domain.pddl` | STRIPS + typing domain and action schemas |
| `Problem.pddl` | Original scenario |
| `Problem_extended.pddl` | Dust-storm scenario with Rock6 and Rock7 |
| `original_greedy.txt` / `.plan` | Original scenario, greedy search log and plan |
| `original_astar.txt` / `.plan` | Original scenario, A* search log and plan |
| `extended_greedy.txt` / `.plan` | Extended scenario, greedy search log and plan |
| `extended_astar.txt` / `.plan` | Extended scenario, A* search log and plan |

