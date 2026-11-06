# AI Group Assignment 2 – submission contents

- `REPORT.md` – analysis for all three problems (add group names and roll numbers at the top)
- `problem1/` – `smart_home_bn.py` (Parts A–E), `multi_seed_check.py`, `output_log.txt`, `multi_seed_log.txt`, `bn_structure.png`, `error_vs_size.png`
- `problem2/` – `Domain.pddl`, `Problem.pddl`, `Problem_extended.pddl`, `strips_planner.py`, `planner_output.txt`
- `problem3/` – `royal_archive_access.pl` (add your screenshot of the final proof output)

## How to run

    cd problem1 && python3 smart_home_bn.py        # needs numpy, networkx, matplotlib
    cd problem1 && python3 multi_seed_check.py
    cd problem2 && python3 strips_planner.py       # ~5 min (the h_max A* run is slow)
    swipl royal_archive_access.pl   then   ?- run.
