# Contract rules

The client and the server are written by different hands at different times. The
contract between them is the only thing both can rely on, so it is small, written
down, and tested on both sides.

## Contract

### CT-1 · One documented error shape; clients parse only that
<!-- doctrine: severity=RED tier=compact principles=P3,P9 -->

**Rule.** The API has exactly one error body shape, documented in one place. The client's HTTP layer parses that shape and nothing else.
**Why.** Every additional shape is a client code path nobody tests until production produces it.
**How.** Server side is `BE-API-2`; the client (`FE-SVC-4`) parses `{"error": string}` into its HTTP error type and falls back to a status-based message otherwise.
**Check.** Do both sides implement the same single error shape?

### CT-2 · Status codes carry meaning both sides act on
<!-- doctrine: severity=ORANGE tier=compact principles=P3 -->

**Rule.** 400 is an invalid request or a broken business rule; 401 is dead credentials only; 403 is forbidden; 404 is unknown or not yours; 409 is a conflict; 5xx is a server or upstream failure. Clients act on the class, not on the message.
**Why.** The client's behaviour (retry, refresh, sign out, show the message) is keyed on the status. A wrong status triggers the wrong behaviour.
**How.** The server follows `BE-API-9`, the client's refresh logic follows `FE-SVC-5`. Validation never produces 401 or 5xx.
**Check.** Does each failure path return the status this table assigns?

### CT-3 · Absent and null mean the same; clients omit empty optionals
<!-- doctrine: severity=YELLOW tier=compact principles=P2 -->

**Rule.** For optional request fields the server treats a missing key and an explicit null identically. Clients omit optional fields that are empty.
**Why.** Clients differ in how they serialize "nothing". A server that distinguishes the two breaks one of them.
**How.** Optional fields default to null on request domains; the client builds bodies with conditional spreads.
**Check.** Does each optional field accept both an omitted key and null?

### CT-4 · The server owns workflow state; the client derives display from it
<!-- doctrine: severity=ORANGE tier=micro principles=P1,P4 -->

**Rule.** Where the user is in a multi-step flow is stored and decided by the server. The client renders what the server reports; a local override (going back a step) is pinned to the server value it was taken from and expires when that value changes.
**Why.** Two owners of "current step" disagree after the first refresh, the second tab or a resumed session.
**How.** Mutations return the new state (`CT-5`); the client's override stores `{serverStep, shownStep}` and applies only while `serverStep` matches.
**Check.** Does the client persist or compute workflow position independently of the server?

### CT-5 · Every mutation returns the full updated snapshot
<!-- doctrine: severity=YELLOW tier=compact principles=P9 -->

**Rule.** A write endpoint responds with the complete updated resource state, the same shape the read endpoint returns.
**Why.** The client replaces its state instead of patching it, so client and server cannot drift.
**How.** Service write methods end by building the same domain the read method returns.
**Check.** Does each write endpoint return the same shape as its read endpoint?

### CT-6 · Read paths tolerate legacy data and unknown fields
<!-- doctrine: severity=ORANGE tier=compact principles=P2 -->

**Rule.** The server normalizes obsolete stored values on read. The client supplies defaults for missing fields and ignores unknown ones.
**Why.** Deployed clients and stored rows are always older than the code. A removed step or a new field must not break a session that started last week.
**How.** Server: scrub retired values in the shared derivation (`BE-SVC-7`) with a back-compat test. Client: defaults in `fromResponse` (`FE-SVC-7`).
**Check.** Is there a test reading a record that contains a retired value?

### CT-7 · A contract change lands on both sides with tests and a written note
<!-- doctrine: severity=RED tier=compact principles=P7 -->

**Rule.** Changing a request field, response field, status or error message is done on the server and the client together, with a test on each side and a "contract changes" note in the change description and the slice README.
**Why.** Tightening the server alone (a new required offset on a timestamp, a newly rejected value) breaks deployed clients silently.
**How.** List every request the client can send and check each against the new validation before merging. Deploy order: the server accepts both shapes first, then the client changes, then the server drops the old shape.
**Check.** Does the change description list every contract change and the client impact of each?

### CT-8 · State the auth transport and its consequences
<!-- doctrine: severity=ORANGE tier=compact principles=P13 -->

**Rule.** The project documents whether the client authenticates with bearer tokens or cookies, and applies the matching protections: explicit allowed origins for cross-origin bearer APIs; CSRF protection for cookies; a recorded decision about where tokens are stored.
**Why.** Each transport has a different threat. Bearer tokens in web storage are readable by any injected script; that is a decision to record, not to discover in an audit.
**How.** Allowed origins come from configuration, never a wildcard in production. Record token-storage risk in the debt ledger if accepted (`R-5`).
**Check.** Is the auth transport documented with its origin policy and token-storage decision?