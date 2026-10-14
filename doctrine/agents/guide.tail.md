## Custom files

Any file that an agent or tool reads as instructions can carry Doctrine: a sub-agent prompt, a system prompt file, a prompt template.

```sh
doctrine install --agent custom --file prompts/reviewer.md
doctrine install --agent custom --file prompts/system.txt --comment hash
```

This inserts the same marked block. Use `--comment hash` when the file is not Markdown or HTML and needs `#` comment markers. Uninstall with the same `--agent custom --file PATH`.

## Raw models and runtimes

A model with no agent around it takes Doctrine as its system prompt.

- Print the text and pass it yourself: `doctrine print --tier compact > doctrine.md`. Supply that file as the system prompt of your API call or chat template.
- Small context window: use `--tier micro`. It fits in 4,000 characters. `compact` fits in 12,000.
- A local model runtime listed above installs in one of two ways: as a model definition built on a base model that you name with `--base MODEL`, or as a plain prompt file plus the command that loads it.
- `--reference-dir PATH` changes where the Deep dives section points. A model can follow those pointers only if it can read files. When it cannot, use `--tier full` if the context window allows.

## Update and uninstall

```sh
doctrine status                  # ok, outdated, modified or missing, for each install
doctrine update                  # re-apply every recorded install with its recorded options
doctrine uninstall --agent ID    # pass the same --scope and --path as the install
```

Run `update` after you pull a new version of Doctrine. `uninstall` removes the block or file, the reference directory once no other install uses it, and any directory it created that is now empty. A file that existed before the install returns to its exact previous bytes.

## Troubleshooting

- **The agent ignores the rules.** Run the agent's verify step. Most agents read instruction files only when a session starts, so restart the session.
- **The installer refuses to overwrite a file.** The target exists and Doctrine did not write it. Move your content elsewhere, or pass `--force` to back the file up beside itself and replace it.
- **The installer says `use --each-repo`.** The agent does not read instruction files from parent directories. Install into each repository instead.
- **The text was cut down to a smaller tier.** The agent documents a size limit. Every rule is still in the reference directory.
- **Status says `modified`.** Someone edited inside the marked block. Move the edit outside the block, then run `doctrine update`.
- **Two agents share one file.** This is expected. One block serves both, and it is removed when the last of them is uninstalled.
- **Nothing was detected.** `detect` looks for each agent's command on `PATH` and for its configuration directory. Name the agent explicitly with `--agent ID`.
