# SDR Calculations & Formulas

## Standard Dimension Ratio
$$SDR = \frac{DN}{e_n}$$

Where:
- $DN$: Nominal Outer Diameter (mm).
- $e_n$: Nominal Wall Thickness (mm).

### Common Values
| SDR | Pressure (Water) | Application |
|-----|------------------|-------------|
| 41 | PN 4 | Drainage |
| 26 | PN 6 | Low Pressure |
| 21 | PN 8 | Irrigation |
| 17 | PN 10 | Potable Water |
| 13.6| PN 12.5 | Ind/Mining |
| 11 | PN 16 | Gas/Fire |

## Theoretical Weight Calculation
Used when catalog data is missing.

$$Mass = \pi \times \rho \times e_n \times (DN - e_n)$$

- $\rho$ (Density of HDPE): $0.955 g/cm^3$ or $955 kg/m^3$.

**Example**: DN 110 SDR 17 (Wall 6.6mm)
- Mean Diameter: $110 - 6.6 = 103.4 mm = 0.1034 m$
- Circumference: $\pi \times 0.1034 = 0.3248 m$
- Cross Section Area of Wall: $0.3248 \times 0.0066 = 0.00214 m^2$
- Volume per meter: $0.00214 m^3$
- Weight: $0.00214 \times 955 = 2.04 kg/m$

*(Note: Catalog values may vary slightly due to resin blend and manufacturing tolerances)*.
