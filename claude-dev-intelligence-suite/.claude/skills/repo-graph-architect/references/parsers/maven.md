# Maven Multi-Module Parser

## Identify Root POM

```bash
cat <repo_root>/pom.xml | grep -A 20 "<modules>"
```

Look for `<modules><module>...</module></modules>` — these are the top-level sub-modules.

## Recursive Module Discovery

```bash
# Find all pom.xml files (= every Maven module)
find <repo_root> -name "pom.xml" | grep -v "/target/" | sort
```

## Extract Module Identity

For each `pom.xml`, parse:
```xml
<groupId>com.example</groupId>      <!-- may be inherited -->
<artifactId>service-a-core</artifactId>   <!-- = module ID -->
<version>1.0.0-SNAPSHOT</version>
<packaging>jar|war|pom</packaging>  <!-- pom = parent/aggregator -->
```

Use `artifactId` as the node `id`. If `packaging=pom` → this is a parent/aggregator, not a leaf.

## Extract Parent Relationship

```xml
<parent>
  <groupId>com.example</groupId>
  <artifactId>service-a</artifactId>   <!-- parent module -->
  <version>1.0.0-SNAPSHOT</version>
</parent>
```

`parent.artifactId` = this node's `parent` field in the graph.

## Extract Dependencies

```xml
<dependencies>
  <dependency>
    <groupId>com.example</groupId>
    <artifactId>shared-lib</artifactId>     <!-- → edge target -->
    <scope>compile|test|runtime|provided|optional</scope>
  </dependency>
</dependencies>
```

Only record edges where `groupId` matches the repo's own `groupId` — these are **internal** dependencies. External library dependencies are noise for the graph (but can be toggled on).

## Quick Grep Approach (for large repos)

```bash
# Get all internal dependency edges in one pass
grep -rn "<artifactId>" <repo_root> --include="pom.xml" \
  | grep -v "/target/" \
  | awk -F: '{print $1, $2}' \
  | sort > /tmp/pom_artifactids.txt

# Cross-reference parent declarations
grep -rn -A3 "<parent>" <repo_root> --include="pom.xml" \
  | grep "<artifactId>" | grep -v "/target/"
```

## Build System Commands (if Maven is installed)

```bash
# Full dependency tree for a specific module
mvn dependency:tree -pl :service-a-core -am --no-transfer-progress

# Detect circular dependencies across all modules
mvn dependency:analyze-duplicate --no-transfer-progress

# List all module names from root
mvn --quiet exec:exec -Dexec.executable=echo \
  -Dexec.args='${project.artifactId}' 2>/dev/null
```
