# Ship a change from branch to verified deploy

A runbook. Follow it in order; each step names the rule behind it and the evidence to
capture.

1. **Fetch and compare.** Fetch the remote and confirm your base is still the tip
   (`D-11`). If the base moved, rebase or merge deliberately and re-read the diff.
   Evidence: the base commit hash you branched from and the hash you will merge into.
2. **Branch fresh.** Create the branch from current main, not from an old local copy
   (`D-10`). Evidence: the branch name and its parent commit.
3. **Work in small steps.** Each commit changes one thing and leaves the tree
   buildable (`D-12`). Evidence: `git log --oneline` for the branch.
4. **Run the local checks, identical to CI.** The local script runs every check the
   pipeline runs (`D-1`, `D-2`). Fix failures before pushing. Evidence: the exact
   command and its exit status.
5. **Write the change description.** What changed, why, any contract change, the
   evidence, and how to roll back (`D-13`). Evidence: the description text.
6. **Open the change and let CI run.** The pipeline is the same set of checks (`D-1`).
   Do not merge on a red or skipped pipeline. Evidence: the pipeline result per job.
7. **Pass the review and QA gates.** A review with no open RED or ORANGE findings, and
   QA passed (`R-7`). Outstanding findings that are recorded and deferred do not block
   if they are YELLOW and in the ledger (`R-5`). Evidence: review result, QA result.
8. **Merge.** Merge with the repository's default method. Do not merge with a moved
   base or a running pipeline (`D-11`). Evidence: the merge commit or PR number.
9. **Watch the deploy.** The deploy is gated by the health check; a failing check
   stops the rollout (`D-4`, `D-6`). Evidence: the deploy job result.
10. **Verify at the edge.** Exercise the changed behavior against the public entry
    point, not an internal host (`D-9`). Evidence: the request and its response.
11. **Clean up.** Delete the branch; close the change (`D-12`). Evidence: the branch
    is gone.
12. **Rollback procedure.** Know the previous known-good revision before you deploy
    (`D-6`). To roll back, redeploy that revision; do not forward-fix a broken deploy
    under time pressure. Evidence: the revision you would return to.

## What to do when

| Situation | Action |
| --- | --- |
| The base moved after your last push (`D-11`) | Re-read the diff against the new base, then re-run CI. Never merge on a stale base. |
| A local check failed (`D-1`) | Fix it locally and re-run the identical command. Do not push expecting CI to differ. |
| A regression test was never seen red (`T-2`) | Revert the fix, watch the test fail, re-apply. A test that never failed proves nothing. |
| Deploy failed before the swap (`D-4`) | Nothing is serving the new code; fix and redeploy. Evidence: the failed job log. |
| Deploy failed after the swap (`D-6`) | Redeploy the previous known-good revision first, then investigate. |
| The health check passed but the edge is wrong (`D-9`) | Roll back, then reproduce against the edge; the health check is not a substitute for the edge check. |
| Configuration-only change (`D-7`, `D-8`) | Change the value, assert the running configuration changed as intended, then verify at the edge. |
| A safety net cannot be asserted before an irreversible step (`D-7`) | Stop. Fix the net first. |
| The change is large | Split it. A reversible change merges sooner and rolls back cheaper (`P12`). |

## Evidence to keep for the change

- The base commit hash and the branch parent.
- The local check command and its result.
- The pipeline result per job.
- The review result and the QA result.
- The deploy result and the edge verification.
- The previous known-good revision for rollback.