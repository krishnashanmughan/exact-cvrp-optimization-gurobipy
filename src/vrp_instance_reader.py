import numpy as np
import pandas as pd
import math
import re


def read_vrp_instance(file_path):
    """
    Universal VRP reader supporting multiple formats:

    Supported formats:
        - EXPLICIT (LOWER_ROW distance matrix given)
        - SOLOMON (VRPTW format with time windows)
        - COORDINATE-BASED (NODE_COORD_SECTION)

    Args:
        file_path (str): Path to VRP instance file

    Returns:
        dist_matrix : np.ndarray - Distance/cost matrix (n x n)
        df          : pd.DataFrame - Customer data with columns:
                        - customer_id
                        - x_coord, y_coord (if applicable)
                        - demand
                        - ready_time, due_date, service_time (if VRPTW)
        K           : int or None - Number of vehicles
        Q           : int or None - Vehicle capacity
    """

    # Read file content
    with open(file_path, 'r') as f:
        content = f.read()

    # =========================
    # 🔹 STEP 1: Detect Format
    # =========================
    if "EDGE_WEIGHT_FORMAT" in content:
        fmt = "explicit"
    elif "CUSTOMER" in content:
        fmt = "solomon"
    else:
        fmt = "coord"

    # =========================
    # 🔹 STEP 2: Extract Common Parameters
    # =========================
    # Extract capacity
    q_match = re.search(r"CAPACITY\s*:\s*(\d+)", content)
    Q = int(q_match.group(1)) if q_match else None

    # Extract number of vehicles
    # Only Solomon-style VEHICLE NUMBER is a true fleet size
    k_match = re.search(r"VEHICLE\s+NUMBER\s+(\d+)", content)
    # Default to None
    K = int(k_match.group(1)) if k_match else None

    # =========================
    # 🟢 CASE 1: EXPLICIT DISTANCE MATRIX
    # =========================
    if fmt == "explicit":
        return _parse_explicit_format(content, K, Q)

    # =========================
    # 🔵 CASE 2: SOLOMON FORMAT (VRPTW)
    # =========================
    elif fmt == "solomon":
        return _parse_solomon_format(content, K, Q)

    # =========================
    # 🟡 CASE 3: COORDINATE-BASED FORMAT
    # =========================
    else:
        return _parse_coordinate_format(content, K, Q)


def _parse_explicit_format(content, K, Q):
    """Parse EXPLICIT (distance matrix) format."""

    # Extract dimension
    n_match = re.search(r"DIMENSION\s*:\s*(\d+)", content)
    if not n_match:
        raise ValueError("Missing DIMENSION field in EXPLICIT format")
    n = int(n_match.group(1))

    # Extract edge weight section
    try:
        edge_section = content.split("EDGE_WEIGHT_SECTION")[1]
        edge_section = edge_section.split("DEMAND_SECTION")[0]
    except IndexError:
        raise ValueError("Missing EDGE_WEIGHT_SECTION or DEMAND_SECTION")

    # Parse numbers
    numbers = list(map(int, edge_section.split()))

    # Build symmetric distance matrix from lower triangle
    dist_matrix = np.zeros((n, n), dtype=float)
    idx = 0
    for i in range(1, n):
        for j in range(i):
            dist_matrix[i][j] = numbers[idx]  # lower triangle
            dist_matrix[j][i] = numbers[idx]  # mirror upper triangle
            idx += 1
    '''
    ### Example Result (13×13)
       0    1   2   3  ...
    0 [0,   9, 14, 21, ...]
    1 [9,   0, 21, 23, ...]
    2 [14, 21,  0, 22, ...]
    3 [21, 23, 22,  0, ...]
    '''
    # Parse demand section
    try:
        demand_section = content.split("DEMAND_SECTION")[1]
        demand_section = demand_section.split("DEPOT_SECTION")[0]
    except IndexError:
        raise ValueError("Missing DEMAND_SECTION")

    nodes = []
    demands = []
    for line in demand_section.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 2:
            node_id = int(parts[0]) - 1  # ← shift to 0-indexed (1→0, 2→1...)
            demand = int(parts[1])
            nodes.append(node_id)
            demands.append(demand)

    df = pd.DataFrame({
        "customer_id": nodes,
        "demand": demands
    })

    # Compute K here using len(df)
    k_match = re.search(r"VEHICLE\s+NUMBER\s+(\d+)", content)
    K = int(k_match.group(1)) if k_match else (math.ceil(df['demand'].sum() / Q))

    return dist_matrix, df, K, Q


def _parse_solomon_format(content, K, Q):
    """Parse SOLOMON format (VRPTW with time windows)."""

    lines = content.split("\n")

    # Extract K and Q from VEHICLE section
    if not K or not Q:
        for i, line in enumerate(lines):
            if "VEHICLE" in line.upper():
                try:
                    values = lines[i + 2].split()
                    K = int(values[0])
                    Q = int(values[1])
                    break
                except (IndexError, ValueError):
                    pass

    # Find CUSTOMER section start
    start_idx = None
    for i, line in enumerate(lines):
        if "CUSTOMER" in line.upper():
            start_idx = i + 3
            break

    if start_idx is None:
        raise ValueError("CUSTOMER section not found in SOLOMON format")

    # Parse customer data
    data = []
    for line in lines[start_idx:]:
        parts = line.split()
        if len(parts) == 7:
            try:
                data.append([
                    int(parts[0]),  # customer_id
                    float(parts[1]),  # x_coord
                    float(parts[2]),  # y_coord
                    int(parts[3]),  # demand
                    int(parts[4]),  # ready_time
                    int(parts[5]),  # due_date
                    int(parts[6])  # service_time
                ])
            except ValueError:
                continue

    if not data:
        raise ValueError("No customer data parsed from SOLOMON format")

    df = pd.DataFrame(data, columns=[
        "customer_id", "x_coord", "y_coord",
        "demand", "ready_time", "due_date", "service_time"
    ])

    # Compute Euclidean distance matrix
    coords = df[["x_coord", "y_coord"]].values
    diff = coords[:, None, :] - coords[None, :, :]
    dist_matrix = np.sqrt((diff ** 2).sum(axis=2))

    return dist_matrix, df, K, Q


def _parse_coordinate_format(content, K, Q):
    """Parse COORDINATE format (NODE_COORD_SECTION + DEMAND_SECTION)."""

    lines = content.split("\n")

    coords = {}
    demands = {}

    in_coord = False
    in_demand = False

    for line in lines:
        line = line.strip()

        # Section detection
        if line.upper() == "NODE_COORD_SECTION":
            in_coord = True
            in_demand = False
            continue
        elif line.upper() == "DEMAND_SECTION":
            in_coord = False
            in_demand = True
            continue
        elif line.upper() == "DEPOT_SECTION":
            in_coord = False
            in_demand = False
            break

        if not line or line.startswith("EOF"):
            continue

        # Parse coordinates
        if in_coord:
            parts = line.split()
            if len(parts) >= 3:
                try:
                    coords[int(parts[0])] = (float(parts[1]), float(parts[2]))
                except ValueError:
                    continue

        # Parse demands
        if in_demand:
            parts = line.split()
            if len(parts) >= 2:
                try:
                    demands[int(parts[0])] = int(parts[1])
                except ValueError:
                    continue

    if not coords:
        raise ValueError("No coordinates found in NODE_COORD_SECTION")

    # Build dataframe
    data = []
    for node in sorted(coords.keys()):
        x, y = coords[node]
        d = demands.get(node, 0)
        data.append([node, x, y, d, 0, 99999, 0])

    df = pd.DataFrame(data, columns=[
        "customer_id", "x_coord", "y_coord",
        "demand", "ready_time", "due_date", "service_time"
    ])

    if K is None:
        K = math.ceil(df['demand'].sum() / Q)

    # Compute Euclidean distance matrix
    coords_arr = df[["x_coord", "y_coord"]].values
    diff = coords_arr[:, None, :] - coords_arr[None, :, :]
    dist_matrix = np.sqrt((diff ** 2).sum(axis=2))

    return dist_matrix, df, K, Q