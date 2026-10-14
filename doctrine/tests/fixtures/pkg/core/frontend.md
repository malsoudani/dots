# Frontend rules

A client is a set of experiences. Each experience has a manager that turns events into states and a presentation layer that renders them.

## Events and state

### FE-STATE-1 · Model state as a closed union with a discriminator
<!-- doctrine: severity=ORANGE tier=micro principles=P2 -->

**Rule.** Every state the screen can show is one named member of a closed union.

**Why.** A closed set lets the compiler prove that every case is rendered.

**How.** Give each member a `kind` field and switch on it exhaustively.

**Check.** Is every renderable state a named member of one closed union?

## Manager

### FE-MGR-1 · Keep the manager free of framework imports
<!-- doctrine: severity=RED tier=compact principles=P1 -->

**Rule.** The manager is a plain class. The framework binding lives in its own file.

**Why.** A manager with no framework imports is tested without rendering anything.

**How.** Inject services through the constructor and expose `dispatch` and `subscribe`.

**Check.** Does the manager module import nothing from the UI framework?
