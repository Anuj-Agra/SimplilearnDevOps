# Role Adapter: QA Tester

> Inject this file when the output audience is a QA Engineer or Test Analyst.

## Output adaptation for QA / Tester audience

- **Language**: Testability-focused. Every statement should be verifiable — avoid vague outcomes like "the system behaves correctly."
- **Detail level**: Scenario and condition focused. Enumerate boundary values, error paths, and edge cases explicitly.
- **Format preference**: Gherkin (Given/When/Then) for acceptance criteria. Tables for test data requirements. Checklists for test coverage.
- **PEGA jargon**: Use where it identifies the specific rule under test (e.g. "the Connector rule KYC-Conn-SanctionsAPI"). Otherwise use plain language.
- **Boundary conditions**: Always include tests at exact threshold values (e.g. risk score = 39, 40, 70 — not just "above/below threshold").
- **Negative testing**: Always include: invalid input, missing required data, unauthorised access attempts, service failures.
- **Integration testing**: Specify mock/stub behaviour for every external service scenario.
- **Audit trail**: Include explicit verification of audit log entries — what must be recorded, with what data.
- **SLA testing**: Include timing scenarios — before SLA, at SLA threshold, after SLA breach.
- **Regulatory**: Flag scenarios that directly verify a regulatory obligation — these are mandatory test cases.
- **Data requirements**: List specific test data needed for each scenario (customer attributes, service mock responses).
- **Automation**: Flag which scenarios are candidates for automated regression testing vs manual UAT.
- **Length**: Comprehensive. QA documentation must be complete enough to execute without ambiguity.
