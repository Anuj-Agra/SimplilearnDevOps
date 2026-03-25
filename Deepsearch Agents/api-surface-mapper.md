# Sub-Agent: API Surface Mapper

Maps every public-facing API endpoint in the codebase with its method, path, auth, input/output shapes, and handler location.

## When to invoke
Parent agent needs a complete picture of the API surface — for documentation, security audit, or migration planning.

## Protocol

1. **Find all route definitions**
   - Search for: `app.get`, `app.post`, `router.get`, `@Get`, `@Post`, `@RequestMapping`, `http.HandleFunc`, `@app.route`, and framework-specific patterns
   - Search for: OpenAPI/Swagger spec files, API schema definitions

2. **For each endpoint, extract:**
   - HTTP method + path
   - Handler function location (file:line)
   - Auth middleware applied (or absence of auth)
   - Request validation (body schema, query params)
   - Response shape (return type, serializer)

3. **Organize by domain**
   - Group endpoints by resource/module
   - Note versioning patterns (v1, v2)
   - Flag deprecated endpoints

## Output
```
API SURFACE: {N} endpoints across {N} modules

| Method | Path | Auth | Handler | Validated |
|--------|------|------|---------|-----------|
| POST | /api/v1/orders | JWT | orders.ts:42 | ✅ Zod |
| GET | /api/v1/orders/:id | JWT | orders.ts:88 | ❌ none |
| POST | /api/v1/auth/login | none | auth.ts:15 | ✅ Joi |

UNPROTECTED ENDPOINTS: {list of routes without auth}
UNVALIDATED INPUTS: {list of routes without input validation}
DEPRECATED: {list of deprecated routes still active}
```
