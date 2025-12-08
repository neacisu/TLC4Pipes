# HDPE Pipe Technical Specifications

## 1. Material Characteristics (PE100)
- **Density**: ~950-960 kg/m³
- **Friction Coefficient**: 0.2 - 0.3 (HDPE on HDPE)
- **Elastic Modulus**: ~900-1100 MPa

## 2. Standard Dimension Ratio (SDR)
SDR is defined as the ratio of Nominal Outer Diameter ($DN$) to Wall Thickness ($e$).
$$SDR = \frac{DN}{e}$$

### Implemented SDR Classes
| SDR | PN (Bar) | Wall Thickness | Application | Validation Rule |
|-----|----------|----------------|-------------|-----------------|
| **26** | PN6 | Thin | Gravity Flow | High Ovality Risk (needs larger gap) |
| **21** | PN8 | Medium | Irrigation | Moderate Ovality |
| **17** | PN10 | Standard | Water Supply | Standard |
| **11** | PN16 | Thick | High Pressure | Low Ovality, Very Heavy |

## 3. Dimensions & Tolerances

### 3.1. Diameter Range
Supported DN (mm): 20, 25, 32, 40, 50, 63, 75, 90, 110, 125, 140, 160, 180, 200, 225, 250, 280, 315, 355, 400, 450, 500, 560, 630, 710, 800.

### 3.2. Inner Diameter Calculation
The application calculates Inner Diameter ($ID$) dynamically:
$$ID \approx DN - (2 \times e)$$
*Note: In v1, the specific values are pre-seeded in `pipe_catalog` table based on ISO 4427 standard values.*

### 3.3. Linear Weight
Weight is critical for transport limits.
$$Weight (kg/m) \approx \pi \times (DN - e) \times e \times Density$$
*Example: DN800 PN16 (SDR 11)*: 168.7 kg/m.

## 4. Safety Margins for Transport

### 4.1. Gap Clearance Formula
To ensure safe nesting, the application enforces:
$$Clearance = ID_{host} - OD_{guest}$$
$$Required = 15mm + (0.015 \times DN_{host})$$

### 4.2. Ovality Adjustment
Effective Inner Diameter is reduced to account for transport deformation:
$$ID_{effective} = ID_{nominal} \times (1 - 0.04)$$
Default ovality factor: **4%**.
