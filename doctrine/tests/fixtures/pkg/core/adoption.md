# Adoption rules

Doctrine serves the host project. These rules say how to bring it in.

## Adoption

### A-1 · Read the project's own instructions before applying Doctrine
<!-- doctrine: severity=RED tier=micro principles=P2 -->

**Rule.** Find and read the project's instruction files and conventions first.

**Why.** The host project wins. A rule applied against local convention plants a second pattern.

**How.** Look for instruction files at the repository root, then for the checks the pipeline runs.

**Check.** Did you read the project's instructions before changing code?

### A-2 · Migrate one slice at a time and finish it
<!-- doctrine: severity=YELLOW tier=compact principles=P3 -->

**Rule.** Move one slice fully to the target shape before starting the next.

**Why.** Half-migrated code carries the cost of both shapes and the benefit of neither.

**How.** Pick the slice with the most change traffic. Finish it, including tests.

**Check.** Is each migrated slice complete before the next one starts?

## Stack translation (reference section, not rules)

| Concept | Server | Client |
|---|---|---|
| decides | service | manager |
| translates | transport | presentation |
