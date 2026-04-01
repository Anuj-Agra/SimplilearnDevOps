# Output Structure

```
./functional-specs/                       # Relative to CODEBASE_ROOT
├── README.md                         # Master index — entry point
├── tech-specs-index.md               # Docs found (or "none") and how they were used
├── system/
│   ├── 01-introduction-and-purpose.md
│   ├── 02-project-scope.md
│   ├── 03-user-roles-and-personas.md
│   ├── 04-system-overview.md
│   ├── 05-cross-cutting-concerns.md
│   └── 06-system-flow-diagrams.md
├── modules/
│   ├── <module-name>/
│   │   ├── README.md
│   │   ├── 01-user-stories.md
│   │   ├── 02-screen-descriptions.md
│   │   ├── 03-business-rules.md
│   │   ├── 04-data-requirements.md
│   │   ├── 05-error-handling.md
│   │   ├── 06-flow-diagrams.md
│   │   └── sub-modules/                # Only if sub-modules exist
│   │       └── <sub-module-name>/
│   │           ├── README.md
│   │           ├── 01-user-stories.md
│   │           ├── 02-screen-descriptions.md
│   │           ├── 03-business-rules.md
│   │           ├── 04-data-requirements.md
│   │           ├── 05-error-handling.md
│   │           └── 06-flow-diagrams.md
│   └── <another-module>/
│       └── ...
└── reference/
    ├── business-rules-master.md
    ├── glossary.md
    ├── feature-screen-map.md
    └── assumptions-and-constraints.md
```

## Cross-Linking Conventions

- From module files → parent README: `[← Back to Module](./README.md)`
- From module files → related modules: `[See also: Inventory](../inventory-management/README.md)`
- From module files → system context: `[See User Roles](../../system/03-user-roles-and-personas.md)`
- From system files → module details: `[Order Management details](../modules/order-management/README.md)`
- Master README links to everything

## Generation Order

1. System files (01–06, including system flow diagrams)
2. Module files — one complete module at a time (README through 06)
3. Sub-module files after parent module
4. Reference files (aggregated from all modules)
5. Master README (last — links to everything)
6. Tech specs index (any time after Step 1)

Note: Generate `06-flow-diagrams.md` AFTER all other module layers (01–05) are complete, since diagrams reference user stories, screens, business rules, and state transitions documented in the earlier layers.

## Empty Sections

Always create the file. Write: "No [topic] were identified for this module from the current codebase analysis. This section should be reviewed with the development team to confirm completeness."
