# Algorithmic Architecture

## 1. Overview
The solution solves a **Nested Bin Packing Problem**.
- **Objective**: Minimize number of trucks.
- **Constraints**: Max Weight (24t), Max Volume, Nesting Compatibility.

## 2. Algorithms Implemented

### 2.1. The "Matryoshka" Nester (`nesting.py`)
**Goal**: Reduce volume by placing smaller pipes inside larger ones.

**Logic**:
1.  **Sort** all pipe quantities by Diameter Descending.
2.  **Iterate** through largest pipes (Potential Hosts).
3.  For each Host:
    *   Find best fitting Guest pipe (Largest diameter that fits `validate_nesting_compatibility`).
    *   If fit found:
        *   "Consume" one Guest.
        *   Recursively try to fill the Guest (Depth First Search).
        *   Create `NestedBundle`.
    *   If no fit:
        *   Pipe remains a single item (or base of empty bundle).
4.  **Result**: List of `NestedBundle` objects (some may contain 1 pipe, others a tree of pipes).

**Complexity**: Greedy Heuristic. $O(N^2)$ optimized by grouping (Quantity based).

### 2.2. The Truck Packer (`bin_packing.py`)
**Goal**: Pack bundles into trucks respecting weight limits.

**Algorithm**: **First Fit Decreasing (FFD)** for Bin Packing.
1.  **Input**: List of `NestedBundle` objects from Step 2.1.
2.  **Sort**: Bundles by **Weight** Descending.
3.  **Process**:
    *   Initialize `Trucks = []`.
    *   For each Bundle:
        *   Try to fit into `Trucks[0]`.
        *   If fit (Weight + Bundle < 24000kg AND Vol + Bundle < MaxVol):
            *   Add to Truck.
        *   Else, try `Trucks[1]`, etc.
        *   If no fit in existing trucks, open `New Truck`.
4.  **Result**: List of Trucks with assigned bundles.

## 3. Validation Logic

### 3.1. Nesting Compatibility
```python
def validate(host, guest):
    gap = host.inner_dia - guest.outer_dia
    required = 15 + (0.015 * host.outer_dia)
    return gap >= required
```

### 3.2. Extraction Weight
Checks if `bundle_weight > 2000kg`. Flags warning for "Heavy Lift Required".

## 4. Performance
- **Typical Runtime**: 2-6 seconds for 2500 pipes (Python).
- **Concurrency**: Wrapped in `run_in_threadpool` to avoid blocking FastAPI event loop.
