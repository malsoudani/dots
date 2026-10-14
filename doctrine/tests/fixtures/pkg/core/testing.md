# Testing rules

Tests exist to keep decisions true. Test the layer that decides, through its public surface.

## Testing

### T-1 · Test the service through its public methods
<!-- doctrine: severity=ORANGE tier=micro principles=P1 -->

**Rule.** Service tests call service methods and assert on returned values and stored rows.

**Why.** Tests bound to private helpers break on every refactor and prove nothing about behavior.

**How.** Build the service with its factory. Assert on what a caller can observe.

**Check.** Do the new tests call only public service methods?

### T-2 · Prove the rollback with a failing second write
<!-- doctrine: severity=YELLOW tier=compact principles=P3 -->

**Rule.** Each multi-write method has a test that fails the second write and asserts nothing was stored.

**Why.** A transaction nobody tested is a comment, not a guarantee. See `BE-TXN-1`.

**How.** Inject a collaborator that raises on the second call.

**Check.** Is there a test that fails the second write and asserts an empty table?
