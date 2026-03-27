# Naming Conventions

## Folder Names

| Rule | Example | Wrong |
|------|---------|-------|
| `kebab-case` lowercase | `order-management` | `OrderManagement` |
| Full business English | `user-management` | `usr-mgmt` |
| Business domain, not service name | `inventory-management` | `inventory-service` |
| Maximum 3 words | `customer-support` | `customer-support-ticket-management` |

Fixed folders: `system/`, `modules/`, `reference/`, `sub-modules/`

## File Names

| # | File | Purpose |
|---|------|---------|
| — | `README.md` | Module overview (sorts first in file browsers) |
| 01 | `01-user-stories.md` | User stories |
| 02 | `02-screen-descriptions.md` | Screen descriptions |
| 03 | `03-business-rules.md` | Business rules |
| 04 | `04-data-requirements.md` | Data requirements |
| 05 | `05-error-handling.md` | Error handling |

## ID Conventions

| Type | Format | Example |
|------|--------|---------|
| User Story | `US-[MOD]-NNN` | `US-ORD-001` |
| Business Rule | `BR-[MOD]-NNN` | `BR-ORD-001` |
| Error | `ERR-[MOD]-NNN` | `ERR-ORD-001` |
| Assumption | `A-NNN` | `A-001` |
| Constraint | `C-NNN` | `C-001` |

Module abbreviations: 2-4 uppercase letters (USR, ORD, INV, PAY, RPT, NTF, SUP, APR). For sub-modules, extend parent: `ORD-RET`.

## Code-to-Business Name Translation

| Code Pattern | Business Name |
|---|---|
| `auth`, `security` | User Authentication & Access |
| `user`, `account`, `profile` | User Management |
| `order`, `checkout`, `cart` | Order Management |
| `product`, `catalog` | Product Catalogue |
| `inventory`, `stock`, `warehouse` | Inventory Management |
| `payment`, `billing`, `invoice` | Payments & Billing |
| `report`, `analytics`, `dashboard` | Reporting & Analytics |
| `notification`, `email`, `alert` | Notifications |
| `hr`, `employee`, `leave`, `payroll` | Human Resources |
| `workflow`, `approval`, `task` | Workflow & Approvals |
| `document`, `file`, `upload` | Document Management |
| `schedule`, `calendar`, `booking` | Scheduling & Bookings |
