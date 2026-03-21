# Skill: PEGA Rule Types

> Inject this file into any agent that needs to identify, name, or work with PEGA rule types.

---

## PEGA rule type reference

### Process automation rules

| Rule type | Purpose | When used |
|-----------|---------|----------|
| **Flow** | Orchestrates a business process — steps, decisions, assignments, sub-flows | Core of every KYC process |
| **Flow Action** | Defines a user action within a flow step (button + associated processing) | Submit, Approve, Reject actions |
| **Activity** | Procedural step-by-step logic (Classic PEGA; avoid in Constellation) | Legacy automations, batch |
| **Queue Processor** | Processes items from a PEGA queue asynchronously | Background screening jobs |
| **Robotic Automation** | RPA integration for external system automation | Legacy system interaction |

### Decision & logic rules

| Rule type | Purpose | When used |
|-----------|---------|----------|
| **Decision Table** | Row-based conditional logic → single result | Country risk ratings, document acceptance |
| **Decision Tree** | Hierarchical branching logic | Complex risk scoring |
| **When** | Boolean condition expression | Flow branching conditions |
| **Declare Expression** | Calculated property value (forward chaining) | Derived risk indicators |
| **Declare Trigger** | Event-driven rule execution | SLA breach notifications |
| **Map Value** | Simple value mapping table | Code → description lookups |

### Data rules

| Rule type | Purpose | When used |
|-----------|---------|----------|
| **Data Transform** | Maps, sets, appends, removes property values between pages | Request/response mapping, initialisation |
| **Data Page** | Parameterised cached data source (D_ prefix) | Country lists, lookup tables |
| **Property** | Defines a data field (type, format, required) | All data model fields |
| **Class** | Object type definition (groups properties + rules) | Customer, Case, Document classes |
| **Page List / Page Group** | Multi-value data structures | Document lists, UBO lists |
| **Report Definition** | Query and aggregate case/data data | Dashboards, regulatory reports |

### Integration rules

| Rule type | Purpose | When used |
|-----------|---------|----------|
| **Connector and Metadata (REST)** | Outbound REST API call definition | Sanctions, identity, credit bureau |
| **Connector and Metadata (SOAP)** | Outbound SOAP call definition | Legacy core banking integrations |
| **Connector and Metadata (MQ)** | Outbound MQ message | Async event publishing |
| **File Listener** | Reads incoming files from SFTP/filesystem | Batch sanctions list updates |
| **Service REST** | Exposes PEGA as a REST service (inbound) | External system calling PEGA |
| **Service SOAP** | Exposes PEGA as a SOAP service (inbound) | Legacy inbound integrations |
| **Auth Profile** | Authentication configuration (OAuth, API key, mTLS) | Credential management for connectors |
| **Keystore** | Certificate and secret storage | TLS and OAuth credentials |

### UI rules

| Rule type | Purpose | When used |
|-----------|---------|----------|
| **Harness** | Full-page container (wraps sections) | Case workspace, review pages |
| **Section** | Reusable UI panel (fields, buttons, embedded sections) | Field groups, sub-panels |
| **Dynamic Layout** | Responsive layout container | Multi-column form layouts |
| **Navigation** | Tab and menu structures | Case tabs, portal navigation |
| **Portal** | Full application shell | KYC Operator portal, Customer portal |
| **Correspondence** | Email/letter templates | Notifications, decision letters |
| **Paragraph** | Reusable text block within correspondence | Boilerplate clauses |

### Case management rules

| Rule type | Purpose | When used |
|-----------|---------|----------|
| **Case Type** | Defines a work object type (stages, processes, steps) | KYC-Work-CDD, KYC-Work-EDD |
| **Stage** | High-level case lifecycle phase | Initiation, Review, Approval, Complete |
| **Process** | Named group of steps within a stage | CDD Process, Document Verification |
| **SLA** | Service Level Agreement timing and escalation | All assignment and case SLAs |
| **Router** | Assignment routing logic (workbasket, skill, direct) | All routing decisions |
| **Assignment** | A unit of work assigned to a person or queue | Every human task |
| **Skill** | Operator capability for skill-based routing | Specialist routing |
| **Workbasket** | Queue of assignments for a team | KYC-Ops, Compliance, RM workbaskets |

### Governance & security rules

| Rule type | Purpose | When used |
|-----------|---------|----------|
| **Access Group** | Groups operators with a common role | KYC-Operator, Compliance, RM |
| **Role** | Set of privileges within an access group | Edit, Read, Approve, Reject |
| **Privilege** | Named permission for a specific action | ApproveCDDCase, ViewKYCData |
| **RuleSet** | Versioned container for rules | KYCOnboarding:01-01-01 |
| **Application** | Defines the PEGA application and its layers | KYCOnboarding application |

---

## Rule naming conventions (recommended)

| Pattern | Example | Used for |
|---------|---------|---------|
| `[App]_[Purpose]` | `KYC_CDDOnboarding` | Flow rules |
| `[App]_[Entity][Action]` | `KYC_BuildSanctionsRequest` | Data Transforms |
| `[App]-Conn-[Service]` | `KYC-Conn-SanctionsAPI` | Connectors |
| `[App]-[Entity]-[Field]` | `KYC-Data-Customer` | Classes |
| `[App][Screen][Type]` | `KYCCDDInitiationSect` | Sections |
| `D_[DataSource]` | `D_CountryList` | Data Pages |
| `[App]-SLA-[Process]` | `KYC-SLA-CDDReview` | SLA rules |
