# Shared Context: KYC & PEGA Glossary

---

## KYC / AML terms

| Term | Definition |
|------|-----------|
| **AML** | Anti-Money Laundering — the set of laws, regulations, and procedures intended to prevent criminals from disguising illegally obtained funds as legitimate income |
| **CDD** | Customer Due Diligence — the process of verifying a customer's identity and assessing the risk they pose for money laundering or terrorist financing |
| **EDD** | Enhanced Due Diligence — a more rigorous version of CDD applied to higher-risk customers, involving additional information gathering, senior approval, and enhanced ongoing monitoring |
| **SDD** | Simplified Due Diligence — a reduced level of CDD applied to very low-risk customers (e.g. listed companies, government bodies) where full CDD may be disproportionate |
| **KYC** | Know Your Customer — the overall process of identifying, verifying, and understanding a customer, including CDD and ongoing monitoring |
| **PEP** | Politically Exposed Person — an individual who holds or has held a prominent public function (head of state, senior politician, senior government official, senior executive of state-owned enterprise, etc.) |
| **UBO** | Ultimate Beneficial Owner — the natural person(s) who ultimately own or control an entity; typically defined as owning > 25% (some jurisdictions: > 10%) |
| **AML Screening** | The process of checking customers and transactions against sanctions lists, PEP lists, and adverse media sources |
| **Sanctions** | Restrictions imposed by governments or international organisations on countries, entities, or individuals for political, security, or human rights reasons |
| **OFAC** | Office of Foreign Assets Control — US Treasury department that administers and enforces economic and trade sanctions |
| **SDN** | Specially Designated Nationals — OFAC's list of individuals and companies subject to US sanctions |
| **SAR** | Suspicious Activity Report — a report filed with the Financial Intelligence Unit when there are grounds to suspect money laundering or terrorist financing |
| **STR** | Suspicious Transaction Report — equivalent to SAR in some jurisdictions |
| **FIU** | Financial Intelligence Unit — the national body responsible for collecting, analysing, and disseminating financial intelligence (e.g. FinCEN in the US, NCA in the UK) |
| **FATF** | Financial Action Task Force — the intergovernmental organisation that sets the global standard for AML/CFT |
| **AMLD** | Anti-Money Laundering Directive — EU legislative framework for AML/CFT compliance |
| **CTF / CFT** | Counter-Terrorist Financing — measures to prevent the financing of terrorism |
| **Ongoing monitoring** | Continuous or periodic review of a customer's transactions and profile to ensure they remain consistent with the stated business relationship |
| **Periodic review** | A scheduled full KYC review performed at a frequency determined by the customer's risk rating |
| **Trigger event** | An event that requires an ad-hoc KYC review outside the periodic schedule (e.g. change of country, sanctions alert, suspicious transaction) |
| **Source of funds** | The origin of the specific funds used in a transaction or to fund an account |
| **Source of wealth** | The origin of the customer's total wealth (e.g. employment income, inheritance, business ownership) |
| **Correspondent banking** | A banking arrangement where one bank provides services on behalf of another bank, typically across borders |
| **Shell company** | A company with no genuine business activity, often used to obscure beneficial ownership |
| **SPV** | Special Purpose Vehicle — a legal entity created for a specific, limited purpose (common in finance and real estate) |
| **Maker-checker** | A dual-control approval pattern where one person (Maker) initiates or approves a decision, and a second person (Checker) independently verifies it |
| **Four-eyes principle** | Equivalent to maker-checker — requires two independent approvers for sensitive decisions |
| **MLRO** | Money Laundering Reporting Officer — the individual within a regulated entity responsible for receiving internal SAR reports and determining whether to file with the FIU |
| **De-risking** | The practice of exiting or refusing business relationships with customer categories deemed high-risk — discouraged by regulators as a blanket approach |
| **Risk appetite** | The level and type of risk an organisation is willing to accept in pursuit of its objectives |
| **Risk-based approach** | Applying proportionate AML/CFT measures based on the assessed risk level of the customer, product, geography, and delivery channel |

---

## PEGA platform terms

| Term | Definition |
|------|-----------|
| **Rule** | The fundamental unit of configuration in PEGA — a named, versioned, class-scoped definition of a behaviour, process, UI, or data element |
| **RuleSet** | A versioned container of rules; the unit of deployment and version control in PEGA |
| **Class** | A PEGA object type that groups related rules and properties; analogous to a class in object-oriented programming |
| **Class hierarchy** | The 4-tier inheritance structure: Enterprise → Division → Application → Work type |
| **Work object** | A PEGA case instance — the running record of a business process (e.g. a specific CDD case for Customer X) |
| **Case** | Equivalent to work object in PEGA Infinity — a business transaction tracked through its lifecycle |
| **Assignment** | A unit of work assigned to a person or queue (workbasket) for action |
| **Workbasket** | A shared queue of assignments for a team or role |
| **Flow rule** | A PEGA rule that defines the sequence of steps, decisions, and assignments in a business process |
| **Data Transform** | A PEGA rule that maps, sets, or calculates property values |
| **Decision Table** | A PEGA rule that evaluates conditions in rows and returns a result |
| **Connector** | A PEGA rule (Connector and Metadata rule) that defines an outbound call to an external service |
| **Data Page** | A parameterised, cached data source (D_ prefix) accessible across the clipboard |
| **Clipboard** | PEGA's in-memory data store for the current session — properties, pages, and page lists live here during processing |
| **Property** | A named data field defined in a PEGA class (equivalent to a database column or object attribute) |
| **Page** | A structured data container in PEGA's clipboard (analogous to an object instance) |
| **Page List** | An ordered list of pages (analogous to an array or database table) |
| **Declare Expression** | A PEGA rule that reactively calculates a property value when source properties change |
| **When condition** | A PEGA rule that defines a named Boolean expression — true or false |
| **SLA rule** | A PEGA rule that defines goal and deadline intervals with escalation chains for an assignment |
| **Router rule** | A PEGA rule that determines who receives an assignment |
| **Section rule** | A reusable PEGA UI component (group of fields and layouts) |
| **Harness rule** | A PEGA full-page UI container that wraps sections |
| **Constellation** | PEGA's modern UI framework (introduced in PEGA 8.7, primary in PEGA 23+) — replaces Classic/Cosmos |
| **Classic UI** | PEGA's legacy UI framework (Cosmos/Reskin) used in PEGA 7.x and 8.x |
| `pyClassName` | The property that holds the PEGA class name of a rule or object |
| `pyRuleName` | The property that holds the name of a PEGA rule |
| `pzInsKey` | The unique internal key of a PEGA work object (case ID) |
| `pyStatusWork` | The current status of a PEGA work object (e.g. `Open-KYCReview`, `Resolved-Approved`) |
| `pyAssignedOperatorID` | The operator or workbasket to which the current assignment is directed |
| `D_` prefix | Naming convention for Data Page rules (e.g. `D_CountryList`) |
| `pyServiceFailed` | Boolean property set to `true` when a connector call fails |
