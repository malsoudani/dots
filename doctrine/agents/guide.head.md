# Using Doctrine with coding agents

Doctrine reaches an agent through the instruction file that agent already reads. The `doctrine` command writes that file, records what it wrote, and removes it again without touching anything else. This guide has three parts: the recipe that works for every agent, one generated section per supported agent, and what to do when your agent or model is not listed.

## The recipe

1. List the agents Doctrine knows, then the ones present on this machine and in this project:

   ```sh
   doctrine agents
   doctrine detect --path .
   ```

2. Preview. `--dry-run` prints every planned action and a diff, and writes nothing:

   ```sh
   doctrine install --agent detected --dry-run
   ```

3. Install, then confirm with the agent's own verify step (listed in its section below):

   ```sh
   doctrine install --agent detected
   doctrine status
   ```

`--agent` takes one id, several ids separated by commas, `all`, or `detected`.

## Scopes

Pick the narrowest scope that covers the work.

| Scope | Flag | Applies to | Written under |
|---|---|---|---|
| project | `--scope project` (default) | one repository | the repository root: `--path`, else the git top level of the current directory |
| workspace | `--scope workspace --path DIR` | every project inside one directory | `DIR`, for agents that read instruction files from parent directories |
| global | `--scope global` | every project of this user | the agent's user-level location |

`namespace` is an alias of `workspace`. `user` is an alias of `global`. When an agent has no workspace support, add `--each-repo` to install into every git repository found under `DIR`; `--depth` limits the search (default 2).

## What gets written

- The agent's instruction target. This is either a file Doctrine owns outright, or a marked block inside a file you share with it, from `doctrine:begin` to `doctrine:end`. Everything outside the block is preserved byte for byte.
- A reference directory: `.doctrine/` in the project or workspace, `~/.doctrine/` for the global scope. It holds the full rule text, the how-to guides, the checklists and `rules.json`. The installed text lists rule titles and points here for depth. Skip it with `--no-reference`. Add the reference implementations with `--with-examples`.
- A manifest entry, so that `status`, `update` and `uninstall` know what exists.

Commit these files to share Doctrine with the team. To keep them out of version control instead, pass `--local`: the installer lists them in the repository's local exclude file, so nothing shows up as untracked.

## Tiers and profiles

`--tier` sets how much text the agent loads on every request:

- `micro`: the operating instructions and the titles of the most important rules.
- `compact`: every principle and rule title, plus pointers into the reference directory. This is the default.
- `full`: every rule in full, the checklists and the how-to guides.

`--profile backend` or `--profile frontend` drops the other side's rules. When an agent documents a size limit, the installer falls back to the next smaller tier and says so.
