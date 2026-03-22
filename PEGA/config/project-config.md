# Project Configuration

> **EDIT THIS FILE FIRST** before running any agents.
> Replace all [PLACEHOLDER] values with your actual project details.

## Application Hierarchy

```
Layer 1: [COB]              ← Top-level business application
Layer 2: [CRDFWApp]         ← Framework application
Layer 3: [MSFWApp]          ← Screen/UI framework
Layer 4: [PegaRules]        ← Base PEGA rules
```

## Manifest Versions (Latest Only)

| Layer       | Latest Manifest File         | Date Exported  |
|-------------|------------------------------|----------------|
| [COB]       | [manifest_v3.2.json]         | [YYYY-MM-DD]   |
| [CRDFWApp]  | [manifest_v2.5.json]         | [YYYY-MM-DD]   |
| [MSFWApp]   | [manifest_v4.0.json]         | [YYYY-MM-DD]   |
| [PegaRules] | [manifest_v1.8.json]         | [YYYY-MM-DD]   |

## File Locations

```
Manifest JSONs:  [./manifests/]
Binary files:    [./binaries/]
Screenshots:     [./screenshots/]
```

## Application Description

[Write 2-3 sentences describing what this PEGA application does.
Example: "A loan origination system that processes mortgage applications
through eligibility checks, credit verification, underwriting, and
account setup. Used by loan officers and underwriters."]

## Key Stakeholders

| Role              | Description                              |
|-------------------|------------------------------------------|
| [Product Owner]   | [Owns requirements, signs off on FRD]    |
| [Business Analyst]| [Validates business rules]               |
| [Tech Lead]       | [Reviews technical accuracy]             |

## Priority Flows (Analyze these first)

1. [Flow name — reason it's priority]
2. [Flow name — reason it's priority]
3. [Flow name — reason it's priority]

## Known External Systems

| System Name       | Type        | Purpose                    |
|-------------------|-------------|----------------------------|
| [Credit Bureau]   | [REST API]  | [Credit score retrieval]   |
| [Core Banking]    | [SOAP]      | [Account management]       |
| [Email Service]   | [REST API]  | [Notifications]            |
