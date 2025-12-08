# Business Requirements & Implementation Status

> **Status Reference**: Version 1.0.0 (December 2025)

## 1. Core Objective
Maximize efficient usage of standard 13.6m / 24t trucks for HDPE pipe transport using telescoping (nesting) techniques to balance volume and weight constraints.

## 2. Functional Requirements

### 2.1. Physical Validation (Physics Engine)
| Requirement | Spec | Implementation Status | Component |
|-------------|------|-----------------------|-----------|
| **Gap Clearance** | `Gap_min = 15mm + (1.5% * OD)` | ✅ **Implemented** | `app.core.calculators.gap_clearance` |
| **Ovality Check** | Assume 4% ovality deformation | ✅ **Implemented** | `app.core.calculators.gap_clearance` |
| **Weight Limit** | Max 24,000 kg per truck | ✅ **Implemented** | `app.core.algorithms.bin_packing` |
| **Nesting Depth** | Limit configurable (default 4) | ✅ **Implemented** | `app.core.algorithms.nesting` |
| **Extr. Warning** | Warn if inner bundle > 2000kg | ✅ **Implemented** | `NestedBundle.extraction_warning` |

### 2.2. Optimization Algorithms
| Requirement | Spec | Implementation Status | Component |
|-------------|------|-----------------------|-----------|
| **Strategy** | Matryoshka (Bottom-Up Nesting) | ✅ **Implemented** | `app.core.algorithms.nesting.create_nested_bundles` |
| **Packing** | First Fit Decreasing (FFD) | ✅ **Implemented** | `app.core.algorithms.bin_packing.pack_pipes_into_trucks` |
| **3D Stacking** | Hexagonal Pattern (Staggered) | ⚠️ **Simplified** | Used simplified 2D rect packing for v1; Hexagonal planned for v2. |

### 2.3. User Interface
| Requirement | Implementation Status | Component |
|-------------|-----------------------|-----------|
| **Dynamic Grid** | ✅ **Implemented** | `frontend/src/components/order/OrderForm` |
| **CSV Import** | ✅ **Implemented** | `frontend/src/components/order/FileImport` |
| **3D Visualizer** | ✅ **Implemented** | `frontend/src/components/visualization/TruckView3D` |
| **Dashboard** | ✅ **Implemented** | `frontend/src/pages/ResultsDashboard` |

### 2.4. Outputs
| Requirement | Implementation Status | Component |
|-------------|-----------------------|-----------|
| **Loading Plan** | ✅ **Implemented** | JSON API Response |
| **PDF Report** | ✅ **Implemented** | `app.api.v1.routes.reports` (ReportLab) |
| **History** | ✅ **Implemented** | PostgreSQL `orders` table |

## 3. Regulatory Constraints (Romania/EU)
- **Max Weight**: 40t Total / 24t Payload -> **Implemented**
- **Axle Distribution**: Calculation logic exists in `axle_distribution.py` but is **Prototype** only. Not enforced in v1.0 blocking.
- **Securement**: PDF Report includes generic securement advice (EN 12195).

## 4. Pending / Future Scope
- [ ] **Auth**: User accounts and RBAC.
- [ ] **Advanced Axle Logic**: Real-time CoG visualization preventing illegal axle loads.
- [ ] **Visual Drag-and-Drop**: Manual adjustment of the loading plan.
