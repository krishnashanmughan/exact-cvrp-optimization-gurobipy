# exact-cvrp-optimization-gurobipy
This project implements an exact mathematical model to solve the Capacitated Vehicle Routing Problem (CVRP).The goal is to minimize total fleet travel distance while ensuring that every customer is serviced exactly once and vehicle capacity limits ($Q$) are never breached.

# Mathematical Formulation
The core of the optimization engine relies on a Mixed-Integer Linear Programming (MILP) framework.

**Objective Function:**
Minimize the total fleet travel distance:

**Key Constraints:**
- Degree Constraints: Ensures every customer is visited exactly once.
- Fleet Size Limit: Bounds the maximum number of vehicles ($K$) departing the depot.
- MTZ Subtour Elimination: Eliminates disconnected loops and tracks the continuous load ($u_i$) to enforce vehicle capacity ($Q$).

Results
The MTZ formulation was tested against standard CVRP benchmark datasets. The model successfully proves optimality for smaller networks and provides high-quality feasible bounds for larger instances.

| Instance | Status | Objective (Distance) | MIP Gap | Time (sec) | Nodes Explored |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **E-n13-k4** | `OPTIMAL` | 247.00 | 0.00% | 3.5 | 71,048 |
| **E-n23-k3** | `OPTIMAL` | 568.56 | 0.00% | 33.2 | 234,444 |
| **E-n30-k3** | `FEASIBLE` | 547.27 | 34.95% | 70.1 | 385,441 |
