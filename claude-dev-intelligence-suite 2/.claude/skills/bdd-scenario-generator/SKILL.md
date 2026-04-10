---
name: bdd-scenario-generator
description: >
  Convert FR-XXX functional requirements and use cases from the FRD into Gherkin
  feature files (Given/When/Then) ready for Cucumber (Java) or Cypress/Playwright
  BDD. Use when asked: 'BDD scenarios', 'Gherkin', 'Cucumber features', 'Given
  When Then', 'acceptance tests from requirements', 'feature files', 'BDD from
  FRD', 'acceptance criteria to Gherkin', 'behaviour driven', 'living documentation',
  'executable specifications'. Bridges requirements and automated acceptance tests.
  Each FR-XXX becomes one or more scenarios. Each business rule becomes a scenario
  outline with examples. Output includes step definitions scaffold.
---
# BDD Scenario Generator

Convert requirements into executable Gherkin specifications with Cucumber step definitions.

---

## Input Sources (in priority order)

1. **FRD document** — use FR-XXX statements and use cases directly
2. **Business rules** — each BR-XXX becomes a scenario outline with boundary examples
3. **User stories** — each "As a / I want / So that" becomes a scenario
4. **Gap detector findings** — each scenario gap becomes a negative test scenario
5. **Direct description** — user describes the feature in plain English

---

## Step 1 — Parse Input into Scenario Seeds

For each FR-XXX / use case / user story, extract:
- **Actor**: who (maps to Gherkin background or given)
- **Precondition**: what must be true first (Given)
- **Action**: what they do (When)
- **Expected result**: what should happen (Then)
- **Alternate flows**: what goes wrong (additional scenarios)
- **Business rules**: conditions that change the result (Scenario Outline + Examples)

---

## Step 2 — Generate Feature Files

### Feature file structure

```gherkin
# src/test/resources/features/[module]/[feature].feature
Feature: [Business capability name — from FRD module name]
  As a [user role from FRD Section 3]
  I want to [capability description]
  So that [business benefit]

  # Reference: FRD Section 5, FR-[MOD]-[###]

  Background:
    Given I am logged in as a "[role]"
    And the system has the following [entities]:
      | [field1]   | [field2]   | [field3]   |
      | [value1]   | [value2]   | [value3]   |

  # ── Happy Path ─────────────────────────────────────────────────────────

  Scenario: Successfully [action] with valid [data]
    # FR-[MOD]-001: The system shall [requirement]
    Given I am on the "[Screen Name]" screen
    And I have [precondition]
    When I [action verb] with the following details:
      | Field          | Value              |
      | [field label]  | [realistic value]  |
      | [field label]  | [realistic value]  |
    And I click "[Button Label]"
    Then I should see "[success message]"
    And the [entity] should be [saved/updated/created] with [status]
    And I should be on the "[Next Screen]" screen

  # ── Validation Scenarios ────────────────────────────────────────────────

  Scenario: Cannot [action] when [required field] is empty
    # FR-[MOD]-002: The system shall prevent submission when mandatory field missing
    Given I am on the "[Screen Name]" screen
    When I submit the form with "[required field]" left blank
    Then I should see the error "[exact error message from FRD Section 9]"
    And the form should not be submitted

  Scenario Outline: Cannot [action] when [field] is invalid
    # Data-driven — covers all validation rules for this field
    Given I am on the "[Screen Name]" screen
    When I enter "<value>" in the "[field label]" field
    And I click "[Submit Button]"
    Then I should see the error "<expected_error>"

    Examples:
      | value                    | expected_error                             |
      | [empty string]           | "[Field] is required"                      |
      | [over max length string] | "[Field] must not exceed [N] characters"   |
      | [invalid format]         | "[Field] must be a valid [format]"         |
      | [boundary value - 1]     | "[Field] must be greater than [minimum]"   |

  # ── Business Rule Scenarios ─────────────────────────────────────────────

  Scenario Outline: [Business rule description]
    # BR-[MOD]-001: [Rule statement from FRD Section 8]
    Given [entity] with total of <order_total>
    When I submit the [entity]
    Then the system should <expected_outcome>

    Examples:
      | order_total | expected_outcome                          |
      | £9,999      | process immediately without approval       |
      | £10,000     | process immediately without approval       |  # AT boundary
      | £10,001     | require manager approval before processing |  # ABOVE boundary
      | £50,000     | require manager approval before processing |

  # ── Permission Scenarios ────────────────────────────────────────────────

  Scenario: [Unauthorised role] cannot access [feature]
    Given I am logged in as a "[unauthorised role]"
    When I navigate to the "[Screen Name]" screen
    Then I should see "[access denied message]"
    And I should be redirected to the "[Home/Login]" screen

  # ── Edge Case Scenarios (from gap detector) ─────────────────────────────

  Scenario: System handles double-submit gracefully
    Given I am on the "[Screen Name]" screen
    And I have filled in all required fields
    When I click "[Submit Button]" twice rapidly
    Then only one [entity] should be created
    And I should see "[success message]" once

  Scenario: [Feature] recovers when session expires mid-form
    Given I am on the "[Screen Name]" screen
    And I have partially filled in the form
    When my session expires
    Then I should be redirected to the login screen
    And I should see "Your session has expired. Please log in again."

  Scenario: [Feature] handles [downstream service] being unavailable
    Given the [downstream service] is unavailable
    When I [perform action]
    Then I should see "[graceful degradation message]"
    And my [action] should be queued for retry
```

---

## Step 3 — Generate Step Definition Scaffold

### Java / Cucumber

```java
// src/test/java/[package]/steps/[Feature]Steps.java
package com.yourorg.bdd.steps;

import io.cucumber.java.en.*;
import io.cucumber.datatable.DataTable;
import org.springframework.beans.factory.annotation.Autowired;
import static org.assertj.core.api.Assertions.*;

public class [Feature]Steps {

    @Autowired private [Feature]Page page;         // Page Object or API client
    @Autowired private TestDataContext context;     // Shared scenario context
    @Autowired private AuthHelper auth;

    @Given("I am logged in as a {string}")
    public void iAmLoggedInAs(String role) {
        auth.loginAs(role);
    }

    @Given("I am on the {string} screen")
    public void iAmOnScreen(String screenName) {
        page.navigateTo(screenName);
    }

    @Given("the system has the following {word}:")
    public void theSystemHas(String entityType, DataTable table) {
        List<Map<String,String>> rows = table.asMaps();
        rows.forEach(row -> context.createEntity(entityType, row));
    }

    @When("I submit the form with {string} left blank")
    public void iSubmitFormWithFieldBlank(String fieldName) {
        page.clearField(fieldName);
        page.clickPrimaryButton();
    }

    @When("I enter {string} in the {string} field")
    public void iEnterValueInField(String value, String fieldLabel) {
        page.setField(fieldLabel, value);
    }

    @When("I click {string}")
    public void iClick(String buttonLabel) {
        page.clickButton(buttonLabel);
    }

    @Then("I should see {string}")
    public void iShouldSee(String text) {
        assertThat(page.isTextVisible(text))
            .as("Expected to see text: '%s'", text)
            .isTrue();
    }

    @Then("I should see the error {string}")
    public void iShouldSeeError(String errorMessage) {
        assertThat(page.getValidationError())
            .as("Expected validation error")
            .contains(errorMessage);
    }

    @Then("I should be on the {string} screen")
    public void iShouldBeOnScreen(String screenName) {
        assertThat(page.getCurrentScreenTitle())
            .as("Expected to be on screen: '%s'", screenName)
            .isEqualTo(screenName);
    }

    @Then("the {word} should be {word} with {string}")
    public void theEntityShouldBeWithStatus(String entity, String action, String status) {
        assertThat(context.getLastCreated(entity).getStatus())
            .isEqualTo(status);
    }
}
```

### Cucumber + Spring Boot test runner

```java
// src/test/java/[package]/CucumberRunner.java
@Suite
@IncludeEngines("cucumber")
@SelectClasspathResource("features")
@ConfigurationParameter(key = GLUE_PROPERTY_NAME,       value = "com.yourorg.bdd")
@ConfigurationParameter(key = PLUGIN_PROPERTY_NAME,     value = "pretty, html:target/cucumber-reports/index.html")
@ConfigurationParameter(key = FILTER_TAGS_PROPERTY_NAME, value = "not @skip")
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
public class CucumberRunner {}
```

---

## Step 4 — Scenario Coverage Matrix

After generation, show coverage:

```
BDD SCENARIO COVERAGE: [Module Name]

Functional requirements covered:
  FR-[MOD]-001 ✅ Happy path + 2 validation scenarios
  FR-[MOD]-002 ✅ Scenario outline with 4 examples
  FR-[MOD]-003 ✅ Permission scenario (2 roles)
  FR-[MOD]-004 ⚠️  No scenario generated — requirement was vague
  FR-[MOD]-005 ❌ Not covered — add manually

Business rules covered:
  BR-[MOD]-001 ✅ Scenario outline — threshold at £10,000 with boundary examples
  BR-[MOD]-002 ✅ Role-based permission scenarios

Gap detector findings covered:
  SG-[003] ✅ Double-submit scenario
  SG-[007] ✅ Session expiry scenario
  SG-[012] ⬜ Not yet covered — [describe gap]

TOTAL:
  Feature files generated:  [N]
  Scenarios generated:      [N]
  Step definitions:         [N] (scaffold — implement with page objects)
  FRD coverage:             [N]% of FR-XXX statements
```

---

## Step 5 — Living Documentation Config

```yaml
# cucumber.yml — generates HTML report as living documentation
default: >
  --format pretty
  --format html:target/cucumber-reports/index.html
  --format json:target/cucumber-reports/report.json
  --tags "not @skip"
  --glue com.yourorg.bdd
  features/

# View report after test run:
# open target/cucumber-reports/index.html
```
