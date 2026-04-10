---
name: cicd-pipeline-auditor
description: >
  Read CI/CD pipeline configurations (GitHub Actions, Jenkins, GitLab CI, Azure DevOps)
  and flag missing steps: no security scan, no performance gate, no smoke test after
  deployment, missing rollback, no environment promotion gates. Use when asked: 'audit
  my pipeline', 'CI/CD review', 'pipeline gaps', 'deployment risks', 'missing pipeline
  steps', 'GitHub Actions review', 'Jenkins audit', 'pipeline best practices',
  'deployment safety', 'release pipeline'. Produces a pipeline maturity scorecard.
---
# CI/CD Pipeline Auditor

Audit CI/CD pipelines for safety, security, and quality gates.

## Step 1 — Discover Pipeline Files
```bash
find . -name "*.yml" -o -name "*.yaml" | \
  grep -i ".github/workflows\|Jenkinsfile\|gitlab-ci\|azure-pipelines\|.circleci" | head -20
find . -name "Jenkinsfile*" | head -10
```

## Step 2 — Parse Each Pipeline
Read each file. For each pipeline, map the stages/steps and check against this matrix:

### Required Gates (flag MISSING as findings)

**Build & Quality**
- [ ] Dependency vulnerability scan (Snyk, OWASP Dependency Check, Trivy)
- [ ] SAST (static application security testing — SonarQube, SpotBugs, Checkstyle)
- [ ] Unit test execution with coverage gate (e.g. fail if < 80%)
- [ ] Integration test execution
- [ ] Code coverage report published
- [ ] Build artefact versioned (not `latest` tag)

**Security**
- [ ] Container image scan (if Docker used)
- [ ] Secret scanning (no hardcoded credentials in code)
- [ ] Licence compliance check (no GPL in commercial product)

**Deployment Safety**
- [ ] Smoke test after deployment (verify app is alive)
- [ ] Health check endpoint polled after deploy
- [ ] Environment promotion gate (manual approval for production)
- [ ] Rollback mechanism defined and tested
- [ ] Blue/green or canary deployment strategy
- [ ] Database migration run BEFORE app deploy (not after)

**Observability**
- [ ] Deployment event sent to monitoring system
- [ ] Alert rules updated post-deploy
- [ ] Performance baseline checked post-deploy

## Step 3 — Pipeline Maturity Scorecard

```
CI/CD PIPELINE AUDIT: [Pipeline name]
Maturity Level: [1-Chaotic / 2-Basic / 3-Defined / 4-Managed / 5-Optimising]
Score: [N/25 gates present]

CRITICAL GAPS (production risk):
  CICD-001: No rollback mechanism defined
    Risk: Cannot recover from a bad deployment
    Fix: Add revert job triggered on post-deploy health check failure

  CICD-002: Database migrations run after app deploy
    Risk: New app version starts before schema is ready → runtime errors
    Fix: Run Flyway/Liquibase migrate as a pre-deploy step

HIGH GAPS:
  CICD-003: No vulnerability scan on dependencies
    Risk: Known CVE shipped to production undetected

MEDIUM GAPS: ...

RECOMMENDED PIPELINE STRUCTURE:
  1. Build → 2. Unit Tests → 3. SAST + Dependency Scan → 4. Integration Tests →
  5. Build Image → 6. Image Scan → 7. Deploy to Staging → 8. Smoke Test →
  9. Manual Gate (prod) → 10. Deploy to Prod → 11. Health Check → 12. Notify
```
