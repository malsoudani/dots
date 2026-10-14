# Doctrine

Doctrine is a written standard for building and reviewing software the same way
every time. It is a set of rule catalogs, a few process checklists, and worked
how-to guides that describe one repeated shape: a thin boundary, a layer that owns
the decisions, and explicit typed values passed between them. Everything in it is
plain Markdown with stable rule IDs, so a person, a reviewer, or an LLM can cite a
rule by name and be understood.

## What is in the box

- `core/` — the rule catalogs. `principles.md` holds the fourteen principles;
  `backend.md`, `frontend.md`, `contracts.md`, `testing.md`, `delivery.md`,
  `review.md`, and `adoption.md` hold the rules that apply them.
- `core/checklists.md` — short, ordered process checklists, each line naming rule IDs.
- `howto/` — worked guides: build a backend slice, build a client experience, review
  a change, adopt Doctrine in an existing project, ship a change to production.
- `examples/backend/` — a runnable server, the invitations slice from the guides.
- `examples/frontend/` — a runnable client, the same invitations experience.
- `agents/` — `registry.json` records where each coding agent reads persistent
  instructions, with a source and a quote for every claim; `README.md` is generated.
- `dist/` — built output: the assembled rule sets, checklists, and `rules.json`.
- `bin/doctrine` — the command line tool that builds `dist/`, lints the sources, and
  installs the rule set into an agent's instruction file.
- `tests/` — the checks that keep every claim in this package true.

## The idea in one screen

The same shape repeats on both sides of the wire. A **boundary** receives input and
turns it into typed values. A layer that **owns the decisions** applies the
business rules and produces results. Between the two, values are **explicit and
typed** — never raw dictionaries or loosely typed blobs. On the server the boundary
is a transport layer and the decision layer is a service; on the client the boundary
is a manager and the decision layer is the services it calls.

The shape is not free. **A pattern is a purchase.** Every layer, interface, and
type you introduce must buy something specific — testability, a real invariant, or a
class of bug that can no longer happen. If it buys nothing, it is ceremony, and it
should be deleted.

## Quick start

```sh
# See the available integration targets and their support levels.
./bin/doctrine agents

# Detect an installed agent and preview its project-level setup.
./bin/doctrine detect --path .
./bin/doctrine install --agent detected --dry-run

# Build the full instruction set, or print a smaller prompt-ready tier.
./bin/doctrine build
./bin/doctrine print --tier compact
```

List the agents Doctrine knows about, then install the rule set for a project or for
every project, and feed the result to whatever agent you use.

## Tiers and profiles

`doctrine print` renders a rule set at one of three tiers and one of three profiles.
Sizes below are from the built `dist/`:

| Tier | Profile | File | Size | Words |
| --- | --- | --- | --- | --- |
| micro | fullstack | `dist/doctrine.micro.md` | 3.8 KB | 616 |
| compact | fullstack | `dist/doctrine.compact.md` | 11 KB | 1,720 |
| compact | backend | `dist/doctrine.compact.backend.md` | 8.6 KB | 1,341 |
| compact | frontend | `dist/doctrine.compact.frontend.md` | 8.0 KB | 1,256 |
| full | fullstack | `dist/doctrine.full.md` | 143 KB | 21,696 |
| — | — | `dist/checklists.md` | 15 KB | 2,703 |
| — | — | `dist/rules.json` | 53 KB | — |

Use **micro** when context is scarce: the principles and the rules that prevent the
most expensive mistakes. Use **compact** for everyday work. Use **full** when you
want every rule and its reasoning. The profile narrows the set to one side of the
wire; `full` always means fullstack.

## Feed it to any LLM

Print the tier you need and use it however your tool accepts instructions:

- Write it to a file and point your agent at it.
- Pipe it into a prompt: `doctrine print --tier compact | your-tool`.
- Paste it into a system prompt or a project instruction file.
- Local model runtimes work the same way; the text is plain Markdown with no
  tool-specific syntax.

`dist/rules.json` is the same content as structured data, for tools that prefer JSON.

## How rules are written and cited

Every rule has a stable ID — `P1`-`P14` for principles, `BE-*`, `FE-*`, `CT-*`,
`T-*`, `D-*`, `R-*`, and `A-*` for the catalogs. Each entry states a **Rule**, a
**Why**, and a **How**, and most state an **Anti-pattern** and a **Check**. Rule and
Why stay stack-neutral; the How carries the specifics. Nothing cites an ID it has
not defined, and a test proves that. Guides cite IDs too, so a how-to reads as the
rules applied in order.

## Reference implementations

`examples/backend/` and `examples/frontend/` are complete, runnable projects — the
same invitations feature on both sides of the wire. They are the source of the code
excerpts in the guides. Each project has its own README with the commands to install
dependencies and run its tests; the excerpts in `howto/` are checked verbatim
against these files, so they cannot drift.

## Keeping it honest

The tests in `tests/` check that the package is internally consistent, not just that
it is spelled correctly:

- Every rule ID and title is unique, and every cited ID resolves to a real rule.
- Principle "In practice" lists match the principles their rules declare.
- Code excerpts are contiguous, verbatim slices of the files they point at.
- The registry validates against its schema, and every agent entry cites a source.
- The build is deterministic: the same sources always render the same bytes.

If a claim in this package cannot be checked, the tests do not claim it.

## Versioning

Doctrine uses semantic versioning in `VERSION`. Rule IDs are stable: a rule may be
clarified, but its ID is not reused for a different meaning. Removing a rule is a
minor change; renaming an ID is a major one. `dist/` is generated, so rebuild it
rather than editing it by hand.
