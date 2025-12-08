# API Design Documentation

## Overview
RESTful API built with FastAPI.
- **Base URL**: `/api/v1`
- **Authentication**: None (Internal tool)
- **Content-Type**: `application/json`

## Resources

### 1. Pipes (`/pipes`)
Catalog management.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/pipes/` | List all pipes (supports pagination, filtering by PN/SDR). |
| GET | `/pipes/{id}` | Get details of a specific pipe. |
| POST | `/pipes/seed` | (Dev) Reseed catalog from template. |

### 2. Orders (`/orders`)
Order lifecycle management.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/orders/` | List all orders (History). |
| POST | `/orders/` | Create a new draft order. |
| GET | `/orders/{id}` | Get full order details (items + status). |
| DELETE | `/orders/{id}` | Delete an order. |
| PATCH | `/orders/{id}/status` | Update status (draft -> calculated). |
| POST | `/orders/{id}/items` | Add item to existing order. |
| POST | `/orders/import-csv` | Import order from CSV file. |

### 3. Calculations (`/calculations`)
Optimization engine.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/calculations/optimize` | Run loading optimization (Matryoshka + Bin Packing). |
| POST | `/calculations/validate-nesting` | Check compatibility between two specific pipes. |
| GET | `/calculations/trucks/` | List available truck configurations. |

### 4. Reports (`/reports`)
Document generation.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/reports/export-pdf/{order_id}` | Generate Loading Plan PDF. |

### 5. Settings (`/settings`)
Global application configuration.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/settings/` | Get current transport settings (margins, gaps). |
| PATCH | `/settings/` | Update settings. |

## Data Models (JSON)

### Optimize Request
```json
{
  "items": [
    { "pipe_id": 60, "quantity": 1100 }
  ],
  "pipe_length_m": 12.0,
  "enable_nesting": true,
  "max_nesting_levels": 4
}
```

### Optimize Response
```json
{
  "summary": {
    "total_pipes": 1100,
    "trucks_needed": 10
  },
  "trucks": [
    {
      "truck_number": 1,
      "bundles": [...]
    }
  ]
}
```
