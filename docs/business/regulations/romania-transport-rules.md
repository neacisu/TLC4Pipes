# Romania Transport Regulations (OG 43/1997)

## Applicable Laws
- **OG 43/1997** (Republicated): Regime of roads.
- **CNAIR Norms**: Specifics for authorized vehicles.

## Weight Limits
| Category | Limit | Notes |
|----------|-------|-------|
| **Total Assembly** | **40.00 tons** | 5-axle or 6-axle articulated vehicle (40t is standard EU/RO limit). |
| **Drive Axle** | **11.50 tons** | The driving axle of the tractor unit. |
| **Trailer Axle** | **24.00 tons** | Triple axle group (Example: 8t + 8t + 8t). Spacing < 1.3m. |
| **Payload** | **~24.00 tons** | Derived (40t Total - 16t Tare Weight of Truck+Trailer). |

## Dimensional Limits
| Dimension | Limit | Notes |
|-----------|-------|-------|
| **Length** | **16.50 m** | Total articulated vehicle. |
| **Width** | **2.55 m** | Standard (Refrigerated is 2.60m). |
| **Height** | **4.00 m** | Maximum legal height from ground. |

## Implementation in TLC4Pipe
The application enforces these limits via the `TruckConfig` model:
- `max_payload_kg`: Defaults to **24,000 kg**.
- `internal_height_mm`: Defaults to **2,700 mm** to keep total height < 4.0m.

## Penalties
Exceeding axle limits by >5% constitutes a serious offense, leading to fines and immobilization of the vehicle.
**The application's "Axle Distribution Calculator" (Prototype) aims to prevent this.**
