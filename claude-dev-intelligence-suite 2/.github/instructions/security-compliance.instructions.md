---
applyTo: "**/*Security*.java,**/*Auth*.java,**/*Config*.java,**/*Controller*.java"
description: "Automatically triggered when working with security/auth files or when user asks about vulnerabilities, GDPR, PII, compliance, or data protection"
---

# Security & Compliance Skills

When working with security/auth/compliance concerns:

- **security-audit** (`.claude/skills/security-audit/SKILL.md`)
  Triggers: "security audit", "OWASP", "vulnerabilities", "injection risk",
  "hardcoded secrets", "CSRF", "XSS", "pen test", "security review"

- **gdpr-compliance-scanner** (`.claude/skills/gdpr-compliance-scanner/SKILL.md`)
  Triggers: "GDPR", "PII", "data protection", "Article 30", "KYC audit",
  "AML review", "compliance", "right to erasure", "data retention"

- **data-lineage-mapper** (`.claude/skills/data-lineage-mapper/SKILL.md`)
  Triggers: "trace this field", "where does X go", "data lineage",
  "data flow", "where is customerId used"

Load the relevant SKILL.md before auditing. Never suppress security findings.
