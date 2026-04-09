# Gradle Multi-Project Parser

## Identify Root Settings File

```bash
cat <repo_root>/settings.gradle      # Groovy DSL
cat <repo_root>/settings.gradle.kts  # Kotlin DSL
```

Look for `include(":service-a", ":service-a:core")` — these are all registered sub-projects.

## Extract All Sub-Projects

```bash
# Groovy DSL
grep -n "include" <repo_root>/settings.gradle \
  | grep -v "//" | sed "s/include[[:space:]]*//"

# Kotlin DSL
grep -n "include(" <repo_root>/settings.gradle.kts \
  | grep -v "//"
```

Each `include(":a:b:c")` → node with id `a:b:c`, parent `a:b`, label `c`.

## Locate Build Files

```bash
# Find all build.gradle and build.gradle.kts
find <repo_root> -name "build.gradle" -o -name "build.gradle.kts" \
  | grep -v "/build/" | sort
```

## Extract Dependencies from build.gradle

Pattern match these configurations:

```groovy
dependencies {
  implementation project(':shared-lib')           // internal dep (Groovy)
  implementation(project(":shared-lib"))          // internal dep (Kotlin)
  testImplementation project(':test-utils')
  api project(':common-api')
  compileOnly project(':legacy-adapter')
  runtimeOnly project(':db-driver')
}
```

Map Gradle configurations to edge types:
| Gradle config | Edge type |
|---|---|
| `implementation`, `compile` | compile |
| `api` | api (stronger — leaks to consumers) |
| `testImplementation`, `testCompile` | test |
| `runtimeOnly` | runtime |
| `compileOnly` | provided |
| `annotationProcessor` | annotation |

## Grep Approach

```bash
# All internal project() dependencies
grep -rn "project('" <repo_root> \
  --include="*.gradle" --include="*.gradle.kts" \
  | grep -v "/build/" | grep -v "^//"
```

## Build System Commands (if Gradle wrapper present)

```bash
# List all sub-projects
./gradlew projects --quiet 2>/dev/null

# Dependency tree for a specific project
./gradlew :service-a:core:dependencies --configuration compileClasspath \
  --no-daemon --quiet 2>/dev/null

# Output dependency graph as dot (if plugin available)
./gradlew generateDependencyGraph --no-daemon 2>/dev/null
```

## Kotlin DSL Patterns

```kotlin
// settings.gradle.kts
include(":service-a", ":service-a:core", ":service-a:api")
rootProject.name = "my-mono-repo"

// build.gradle.kts
dependencies {
    implementation(project(":shared-lib"))
    testImplementation(project(":test-fixtures"))
}
```
