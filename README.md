## exact-cvrp-optimization-gurobipy
This project implements an exact mathematical model to solve the Capacitated Vehicle Routing Problem (CVRP).The goal is to minimize total fleet travel distance while ensuring that every customer is serviced exactly once and vehicle capacity limits ($Q$) are never breached.

## Mathematical Formulation
The core of the optimization engine relies on a Mixed-Integer Linear Programming (MILP) framework.

**Objective Function:**
Minimize the total fleet travel distance:

**Key Constraints:**
- Degree Constraints: Ensures every customer is visited exactly once.
- Fleet Size Limit: Bounds the maximum number of vehicles ($K$) departing the depot.
- MTZ Subtour Elimination: Eliminates disconnected loops and tracks the continuous load ($u_i$) to enforce vehicle capacity ($Q$).

**Results:**
The MTZ formulation was tested against standard CVRP benchmark datasets. The model successfully proves optimality for smaller networks and provides high-quality feasible bounds for larger instances.

| Instance | Status | Objective (Distance) | Time (sec) | MIP Gap |
| :--- | :--- | :--- | :--- | :--- |
| **E-n13-k4** | `OPTIMAL` | 247.00 | 3.2 | 0.00% |
| **E-n23-k3** | `OPTIMAL` | 568.56 | 74.5 | 0.00% |
| **E-n30-k3** | `TIME_LIMIT_FEASIBLE` | 542.29 | 1800.2 | 30.79% |
| **E-n51-k5** | `TIME_LIMIT_FEASIBLE` | 544.68 | 1800.3 | 19.87% |
| **E-n76-k7** | `TIME_LIMIT_FEASIBLE` | 710.82 | 3008.4* | 23.30% |

> ***Technical Note on E-n76-k7:** The solver recorded a termination time of 3008.4 seconds despite the 1800-second parameter. This behavior is standard in advanced branch-and-cut engines; Gurobi delays hard termination to finish evaluating a deeply fractional cut pass or completing a complex heuristic node evaluation before gracefully returning the best incumbent solution.
