# API Contract Spec

This is the shared source of truth for the API boundary between the Java service (backend) and Angular app (frontend).

## How This Works

Each repo has its own `openspec/` with independent specs, changes, and archive. This contract spec defines what both repos must agree on: endpoints, request/response shapes, and error contracts.

## Endpoints

<!-- Run /xspec-sync-contract to populate from your actual code -->

### GET /api/health
- **Response**: `{ status: string, timestamp: string }`
- **Java**: `HealthController.getHealth()`
- **Angular**: `HealthService.getHealth(): Observable<HealthResponse>`

## Schemas

### HealthResponse
| Field     | Type   | Required | Notes          |
|-----------|--------|----------|----------------|
| status    | string | yes      | "UP" or "DOWN" |
| timestamp | string | yes      | ISO 8601       |

## Error Contract

All error responses follow:
- `error`: string (machine-readable code)
- `message`: string (human-readable)
- `status`: number (HTTP status code)
- `timestamp`: string (ISO 8601)
