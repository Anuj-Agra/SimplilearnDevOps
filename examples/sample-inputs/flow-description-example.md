# Sample Input: Flow Description (plain text)

> Use this with Agent 01 (Flow Narrator) when you don't have JSON/BIN — just a verbal description.

---

**Flow name:** KYC_CDDOnboarding (inferred)
**Application:** KYCOnboarding
**Work type:** KYC-Work-CDD

**Description from stakeholder workshop:**

The CDD onboarding process starts when a KYC Operator opens a new case in PEGA. They collect the customer's personal details — name, date of birth, nationality, and tax ID. The customer also needs to upload their passport and a proof of address (utility bill or bank statement, less than 3 months old).

Once documents are uploaded, PEGA automatically calls our sanctions screening vendor to check the customer against the OFAC, UN, and EU lists. It also checks if they're a PEP. If there's a confirmed sanctions hit, the case goes straight to the Sanctions Review team — they investigate and decide whether to clear it or escalate to the MLRO.

If there's no sanctions hit, the system calculates a risk score based on the customer's country, customer type, PEP status, and the product they're applying for. The score is 0–100 and maps to LOW, MEDIUM, or HIGH.

LOW risk cases are automatically approved — no human needs to review them. MEDIUM risk cases go to the customer's Relationship Manager, who has 48 hours to approve, reject, or escalate to Compliance. HIGH risk cases go straight to a Compliance Officer. If the RM doesn't action the case within 48 hours, it escalates automatically to the Compliance workbasket.

For cases that are HIGH risk or have a PEP flag, the Compliance Officer reviews the case. If they think EDD is needed, they flag it and a separate EDD case is created and linked. The main CDD case waits for the EDD to complete before it resolves.

All decisions — automated and manual — are recorded in the case audit trail with timestamps and user IDs. The audit trail must be kept for 5 years from case closure.

There are SLAs at each stage. The compliance team has told us that any breach needs to be visible in their dashboard immediately, and escalation must happen automatically — they can't rely on people remembering to escalate.

We call three external services: the sanctions/PEP screening API (must respond in under 5 seconds), an identity verification service (checks the passport is genuine), and our core banking CRM (to pull existing customer data if the customer is already known to us).
