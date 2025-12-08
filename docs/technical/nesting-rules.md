# Technical Guide: Nesting Rules & Logic

## The "Pipe-in-Pipe" Problem
Nesting (Telescoping) is the insertion of smaller diameter pipes into larger ones to maximize volume utilization.

## 1. Compatibility Formula
Determines if Pipe B (Guest) fits into Pipe A (Host).

### Inputs
- $ID_A$: Inner Diameter of Host (mm).
- $OD_B$: Outer Diameter of Guest (mm).
- $\epsilon$: Ovality Error (deformation from perfect circle).
- $C_{base}$: Base Clearance (handling room).

### The Logic (`gap_clearance.py`)
1.  **Calculate Effective ID**:
    $$ID_{eff} = ID_A \times (1 - Ovality\%)$$
    *Default Ovality: 4% (0.04)*
2.  **Calculate Required Gap**:
    $$G_{req} = 15mm + (1.5\% \times OD_A)$$
    *Larger pipes need larger gaps.*
3.  **Check Fit**:
    $$ID_{eff} - OD_B \ge G_{req}$$

## 2. Nesting Depth Limits
Recursive nesting creates "Bundles".
$$Bundle = \{A, \{B, \{C\}\}\}$$

**Limit**: `MAX_NESTING_LEVELS = 4`
- **Level 1**: Host Only.
- **Level 2**: Host + Guest.
- **Level 3**: Host + Guest + SubGuest.
- **Level 4**: Host + Guest + SubGuest + Core.

## 3. Extraction Constraint
Ideally, we pack as much as possible.
**Constraint**: Can the customer unload it?
- If the inner bundle weight > **2000 kg**, the application flags an **Extraction Warning**.
- Reason: Standard forklifts or site equipment may struggle to pull a 3-ton core out of a pipe without damaging it due to friction.

## 4. Multi-Pipe Nesting (Interstices)
*Not fully implemented in v1 algorithms.*
Current v1 logic places **one** guest type centrally.
Future v2 logic: Placing multiple small pipes (e.g., 3x DN110) in a triangular pattern inside a large host (DN630).
Formula: Circle Packing in Circle.
