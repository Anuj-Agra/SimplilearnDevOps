---
name: api-contract-generator
description: >
  Extract OpenAPI 3.0 specifications from Spring REST controllers automatically.
  Produces a versioned openapi.yaml that becomes the contract between Java backend
  and Angular frontend. Use when asked: 'generate OpenAPI', 'swagger spec', 'API
  contract', 'openapi.yaml', 'API documentation', 'REST spec', 'API schema',
  'mock server', 'contract testing', 'API first'. Enables parallel development —
  frontend can mock against the spec while backend implements.
---
# API Contract Generator

Extract a complete OpenAPI 3.0 specification from Spring controllers.

## Step 1 — Scan Controllers
```bash
grep -rn "@RestController\|@Controller" <java_path> --include="*.java" -l
grep -rn "@GetMapping\|@PostMapping\|@PutMapping\|@DeleteMapping\|@PatchMapping\|@RequestMapping" \
  <java_path> --include="*.java" | grep -v "//\|test"
grep -rn "@RequestBody\|@PathVariable\|@RequestParam\|@RequestHeader" \
  <java_path> --include="*.java" | head -100
grep -rn "@ResponseStatus\|ResponseEntity\|HttpStatus\." <java_path> --include="*.java" | head -60
find <java_path> -name "*Request*.java" -o -name "*Response*.java" -o -name "*Dto.java" | head -30
grep -rn "@PreAuthorize\|@Secured\|ROLE_" <java_path> --include="*.java" | head -40
```

## Step 2 — Extract Per Endpoint
For each controller method, extract:
- HTTP method + path → `operationId`
- Path/query/body parameters → `parameters` + `requestBody`
- Response types → `responses` (200, 201, 400, 401, 403, 404, 422, 500)
- Security requirements → `security`
- DTO fields → `components/schemas`

## Step 3 — Emit openapi.yaml

```yaml
openapi: "3.0.3"
info:
  title: "[System Name] API"
  version: "1.0.0"
  description: "Auto-generated from source — review before publishing"

servers:
  - url: http://localhost:8080
    description: Local development
  - url: https://api.yourorg.com
    description: Production

security:
  - bearerAuth: []

paths:
  /api/[resource]:
    get:
      operationId: list[Resource]
      summary: "[Plain English description]"
      tags: ["[Module]"]
      parameters:
        - name: page
          in: query
          schema: { type: integer, default: 0 }
        - name: size
          in: query
          schema: { type: integer, default: 20, maximum: 100 }
      responses:
        "200":
          description: "[Resources] retrieved successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/[Resource]Page'
        "401": { $ref: '#/components/responses/Unauthorized' }
        "403": { $ref: '#/components/responses/Forbidden' }

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
  schemas:
    [Resource]:
      type: object
      required: [field1, field2]
      properties:
        [field1]: { type: string, maxLength: 100, example: "..." }
  responses:
    Unauthorized:
      description: Authentication required
    Forbidden:
      description: Insufficient permissions
```

## Step 4 — Validation Checklist
- [ ] Every controller method has an entry
- [ ] Every DTO field is in components/schemas
- [ ] Every validation annotation maps to a schema constraint (maxLength, minimum, pattern)
- [ ] Every @ResponseStatus maps to a response code
- [ ] Every @PreAuthorize maps to a security requirement
- [ ] Pagination parameters on all list endpoints
