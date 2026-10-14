# Build a backend slice end to end

This guide builds the notes slice in the order an author should work.

## 1. Decide the unit of work

Adding a note is one write, so no transaction is needed yet (`BE-TXN-1` applies from the second write on).

## 2. Write the service

The service owns the rule (`BE-SVC-1`). Failures are typed:

<!-- excerpt: examples/backend/notes/service.py -->
```python
class TitleTooLong(Exception):
    """Raised when a note title exceeds the limit."""
```

## 3. Test it

Call the public method (`T-1`). Rules in the `BE-STRUCT-*` group describe the layout.
