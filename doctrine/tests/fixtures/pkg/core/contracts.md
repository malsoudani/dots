# Contract rules

The contract is the set of shapes the client and the server agree on. Both sides parse it.

## Contract

### CT-1 · Define every response shape once on the server
<!-- doctrine: severity=RED tier=compact principles=P2 -->

**Rule.** Each response body is built from one response domain.

**Why.** Two builders for one shape produce two shapes within a few changes.

**How.** Return the response domain from the service and serialize it in the transport.

**Check.** Is every response body built from exactly one response domain?

### CT-2 · Parse every response on the client before using it
<!-- doctrine: severity=ORANGE tier=micro principles=P2 -->

**Rule.** The client service parses each response into a model and returns a result value.

**Why.** An unparsed response moves the failure from the boundary to a random component.

**How.** Decode in the service. Return a failure code when decoding fails.

**Check.** Does every client service parse the response before returning it?
