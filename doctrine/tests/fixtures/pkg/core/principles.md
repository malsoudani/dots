# Principles

Three ideas hold the fixture catalog together. Each one names a trade: what the pattern costs and what it buys.

### P1 · Decisions live in one layer
<!-- doctrine: tier=micro -->

**Principle.** Transport translates and services decide. A rule lives in exactly one file.

**Why.** Two places that decide the same thing drift apart. The layer that decides is the layer you test.

**In practice.** `BE-STRUCT-1`, `BE-SVC-1`, `FE-MGR-1`, `T-1`, `R-1`.

### P2 · Parse at the boundary, trust inside
<!-- doctrine: tier=micro -->

**Principle.** Everything that crosses a boundary is parsed once into a typed shape at the edge.

**Why.** Code inside the boundary stops re-checking, and raw input never reaches a decision.

**In practice.** `BE-SVC-1`, `FE-STATE-1`, `CT-1`, `CT-2`, `A-1`.

### P3 · A unit of work is all-or-nothing
<!-- doctrine: tier=compact -->

**Principle.** A user-visible action fully happens or does not happen at all.

**Why.** Partial success is the most expensive failure because nobody is told about it.

**In practice.** `BE-TXN-1`, `T-2`, `D-1`, `D-2`, `R-2`, `A-2`.
