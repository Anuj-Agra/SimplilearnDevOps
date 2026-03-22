# Integration Analysis: [SERVICE NAME]

> **ID**: INT-XXX
> **Layer**: [layer]
> **Analyzed**: [date]
> **Agent**: 03-Integration Scanner
> **Status**: [Complete / Partial]

---

## Metadata

| Field | Value |
|-------|-------|
| Service Name | [name] |
| Type | [REST / SOAP / SQL / File / JMS] |
| Layer | [layer] |
| Method | [GET / POST / PUT / DELETE] |
| Endpoint | [URL or resource] |
| Authentication | [API Key / OAuth2 / Basic / None] |

## Business Purpose

[2-3 sentences: Why does the application call this external system? What business need does it serve?]

## Endpoint Specification

```
URL:             [full endpoint URL]
Method:          [HTTP method]
Content-Type:    [application/json / application/xml]
Authentication:  [type and location — header, query, body]
Timeout:         [seconds]
```

## Request Schema

| PEGA Property | Maps To (External) | Type | Required | Notes |
|---------------|---------------------|------|----------|-------|
| [.path] | [field name] | [type] | [Y/N] | |

Data Transform used: [name of request mapping]

## Response Schema

| External Field | Maps To (PEGA Property) | Type | Notes |
|----------------|-------------------------|------|-------|
| [field name] | [.path] | [type] | |

Data Transform used: [name of response mapping]

## Error Handling

| Error Scenario | HTTP Status | PEGA Response | Fallback Action |
|----------------|-------------|---------------|-----------------|
| Timeout | — | [action] | [fallback] |
| Bad Request | 400 | [action] | [fallback] |
| Unauthorized | 401 | [action] | [fallback] |
| Server Error | 500 | [action] | [fallback] |

Retry logic: [count] retries, [interval] interval, [strategy] backoff

## Data Page (if applicable)

| Field | Value |
|-------|-------|
| Data Page Name | [D_PageName] |
| Scope | [Thread / Requestor / Node] |
| Refresh Strategy | [Always / Timer / Manual] |
| Cache Duration | [minutes, if cached] |
| Parameters | [list] |

## Cross-References

| Used By Flow | At Step | Purpose |
|-------------|---------|---------|
| [FL-XXX] | [step name] | [what data is needed] |

## Open Questions

- [anything unclear]
