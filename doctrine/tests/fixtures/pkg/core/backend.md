# Backend rules

A backend is a set of vertical slices. Each slice has a thin transport, a service that owns the rules, and typed values at both edges.

## Structure

### BE-STRUCT-1 · Organize the backend as vertical slices
<!-- doctrine: severity=ORANGE tier=compact principles=P1 -->

**Rule.** Each capability lives in one directory with its service, transport and tests.

**Why.** A change to one capability then touches one directory. Layer-first layouts scatter a feature across the tree.

**How.** Create `notes/` with `service.py`, `views.py` and `tests.py`. Register the slice once.

**Check.** Does every new capability live in its own slice directory?

## Services

### BE-SVC-1 · Put every business rule in a service method
<!-- doctrine: severity=RED tier=micro principles=P1,P2 -->

**Rule.** Handlers parse and respond. Service methods decide.

**Why.** A rule that lives in a handler cannot be reused or tested without the protocol.
The second caller copies it, and the copies drift.

**How.**

1. Parse the request into a domain value.
2. Call one service method.
3. Map the result to a response.

**Example.** The service owns the length rule:

<!-- excerpt: examples/backend/notes/service.py -->
```python
    def add(self, title: str) -> Note:
        if len(title) > MAX_TITLE:
            raise TitleTooLong(title)
```

**Anti-pattern.** A handler that checks the title length itself.

**Check.** Does every branch on a business condition sit in a service method,
not in a handler?

## Transactions

### BE-TXN-1 · Wrap each multi-write service method in one transaction
<!-- doctrine: severity=RED tier=micro principles=P3 -->

**Rule.** A service method that writes more than once runs inside one transaction.

**Why.** Without it a failure between two writes leaves half an action behind.

**How.** Open the transaction at the top of the method, after any remote call.

**Check.** Does every multi-write service method open exactly one transaction?
