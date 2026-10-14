# Delivery rules

Delivery is how a change reaches users without surprising them.

## Continuous integration

### D-1 · Run the same checks locally and in continuous integration
<!-- doctrine: severity=RED tier=micro principles=P3 -->

**Rule.** One script runs every check. Developers and the pipeline both call it.

**Why.** Two definitions of green means one of them is wrong on the day it matters.

**How.** Keep the script in the repository and call it from the pipeline definition.

**Check.** Does the pipeline call the same script a developer runs locally?

## Deploy

### D-2 · Verify the deploy at the edge before calling it done
<!-- doctrine: severity=ORANGE tier=compact principles=P3 -->

**Rule.** After a deploy, request a real route through the public address and check the version.

**Why.** A green pipeline only says the artifact was built, not that users receive it.

**How.** Fetch the health route at `https://app.example.com/health` and compare the version field.

**Check.** Did someone verify the new version through the public address?
