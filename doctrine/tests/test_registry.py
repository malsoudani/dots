"""Registry schema validation, path expansion (case 16) and the generated agent guide."""
import copy
import json
import unittest

from support import CliCase, cli, fixture_registry_data, fixture_texts


def problems_after(change):
    data = fixture_registry_data()
    change(data)
    return ["%s: %s" % (agent or "-", message) for agent, message in cli.validate_registry(data)]


def agent(data, agent_id):
    return [entry for entry in data["agents"] if entry["id"] == agent_id][0]


class RegistrySchemaTest(unittest.TestCase):
    def assert_problem(self, change, expected):
        self.assertEqual(problems_after(change), [expected])

    def test_fixture_registry_is_valid(self):
        self.assertEqual(cli.validate_registry(fixture_registry_data()), [])

    def test_top_level_shape(self):
        self.assertEqual(cli.validate_registry([]), [(None, "the registry must be a JSON object")])
        self.assert_problem(lambda d: d.update(schema=2), "-: schema: must be 1")
        self.assert_problem(lambda d: d.update(verified_on="yesterday"), "-: verified_on: must be a date YYYY-MM-DD")
        self.assert_problem(lambda d: d.update(agents=[]), "-: agents: must be a non-empty list")

    def test_ids(self):
        self.assert_problem(lambda d: d["agents"][1].update(id="alpha"), "alpha: duplicate id alpha")
        self.assert_problem(lambda d: d["agents"][0].update(id="Alpha One"),
                            "-: agents[0]: must be an object whose id matches [a-z0-9][a-z0-9-]*")
        for reserved in ("all", "detected", "custom"):
            self.assert_problem(lambda d: d["agents"][0].update(id=reserved), "%s: id: %s is reserved" % (reserved, reserved))

    def test_unknown_mode_on_each_target(self):
        expected = 'unknown mode "append" (expected file, block, modelfile, text)'
        self.assert_problem(lambda d: agent(d, "bravo")["project"].update(mode="append"), "bravo: project.mode: " + expected)
        self.assert_problem(lambda d: agent(d, "bravo")["global"].update(mode="append"), "bravo: global.mode: " + expected)
        self.assert_problem(lambda d: agent(d, "bravo")["workspace"].update(mode="append"), "bravo: workspace.mode: " + expected)
        self.assert_problem(lambda d: agent(d, "bravo")["project"].pop("mode"),
                            "bravo: project.mode: unknown mode null (expected file, block, modelfile, text)")

    def test_every_known_mode_is_accepted(self):
        for mode in ("file", "block", "modelfile", "text"):
            self.assertEqual(problems_after(lambda d: agent(d, "foxtrot")["project"].update(mode=mode)), [])

    def test_high_confidence_needs_sources(self):
        self.assert_problem(lambda d: agent(d, "alpha").update(sources=[]),
                            "alpha: sources: an agent with confidence high needs at least one source")
        self.assertEqual(problems_after(lambda d: agent(d, "alpha").update(sources=[], confidence="medium")), [])
        self.assert_problem(lambda d: agent(d, "alpha").update(confidence="certain"),
                            "alpha: confidence: must be high or medium")
        self.assert_problem(lambda d: agent(d, "alpha")["sources"][0].update(url="see the manual"),
                            "alpha: sources[0]: needs an http(s) url, a quote and an accessed date YYYY-MM-DD")

    def test_project_paths_must_stay_inside_the_root(self):
        for bad in ("/etc/rules.md", "~/rules.md", "{xdg_config}/rules.md", "C:/rules.md", "\\\\server\\rules.md"):
            with self.subTest(bad=bad):
                self.assert_problem(lambda d: agent(d, "alpha")["project"].update(path=bad),
                                    "alpha: project.path: must be a relative path (got %s)" % json.dumps(bad))
        for bad in ("../rules.md", "a/../../rules.md", "a\\..\\rules.md"):
            with self.subTest(bad=bad):
                self.assert_problem(lambda d: agent(d, "alpha")["project"].update(path=bad),
                                    "alpha: project.path: must not contain `..` (got %s)" % json.dumps(bad))
        self.assert_problem(lambda d: agent(d, "alpha")["project"].update(path=""),
                            "alpha: project.path: must be a non-empty string")
        self.assert_problem(lambda d: agent(d, "alpha")["workspace"].update(path="/ALPHA.md"),
                            'alpha: workspace.path: must be a relative path (got "/ALPHA.md")')
        self.assert_problem(lambda d: agent(d, "delta")["register"].update(file="~/.delta.conf.yml"),
                            'delta: register.file: must be a relative path (got "~/.delta.conf.yml")')

    def test_global_paths_must_be_anchored(self):
        for bad in ("/etc/alpha/rules.md", "rules/doctrine.md", "~alpha/rules.md", "$HOME/rules.md"):
            with self.subTest(bad=bad):
                self.assert_problem(lambda d: agent(d, "alpha")["global"].update(path=bad),
                                    "alpha: global.path: must be anchored at ~ or a {variable} (got %s)" % json.dumps(bad))
        self.assert_problem(lambda d: agent(d, "alpha")["global"].update(path="{home}/rules.md"),
                            "alpha: global.path: unknown path variable {home} (known: xdg_config, vscode_user, appdata)")
        self.assert_problem(lambda d: agent(d, "alpha")["global"].update(path="~/../rules.md"),
                            'alpha: global.path: must not contain `..` (got "~/../rules.md")')
        self.assert_problem(lambda d: agent(d, "alpha")["global"]["platform_paths"].update(windows="C:/rules.md"),
                            'alpha: global.platform_paths.windows: must be anchored at ~ or a {variable} (got "C:/rules.md")')
        self.assert_problem(lambda d: agent(d, "alpha")["global"]["platform_paths"].update(solaris="~/rules.md"),
                            'alpha: global.platform_paths: unknown platform "solaris"')
        for good in ("~", "~/.alpha/rules.md", "{xdg_config}/a.md", "{vscode_user}/a.md", "{appdata}/a.md"):
            self.assertEqual(problems_after(lambda d: agent(d, "alpha")["global"].update(path=good)), [])

    def test_missing_global_needs_a_reason(self):
        self.assert_problem(lambda d: agent(d, "charlie").pop("global_unsupported_reason"),
                            "charlie: global_unsupported_reason: required when global is null")
        self.assert_problem(lambda d: agent(d, "alpha").update({"global": None}),
                            "alpha: global_unsupported_reason: required when global is null")

    def test_workspace_shape(self):
        self.assert_problem(lambda d: agent(d, "charlie")["workspace"].pop("reason"),
                            "charlie: workspace.reason: required when workspace.supported is false")
        self.assert_problem(lambda d: agent(d, "charlie").update(workspace={"supported": "no"}),
                            "charlie: workspace: must be an object with a boolean `supported`")

    def test_front_matter_shape(self):
        self.assert_problem(lambda d: agent(d, "bravo")["project"].update(frontmatter={"a": "b"}),
                            "bravo: project.frontmatter: only a `file` target can carry front matter")
        self.assert_problem(lambda d: agent(d, "alpha")["project"].update(frontmatter={"nested": {"a": 1}}),
                            "alpha: project.frontmatter: must map plain keys to booleans, numbers, strings or lists of strings")

    def test_scalar_fields(self):
        cases = (
            (lambda d: agent(d, "alpha").update(kind="plugin"), "alpha: kind: must be agent or runtime"),
            (lambda d: agent(d, "alpha").update(rank=0), "alpha: rank: must be a positive integer"),
            (lambda d: agent(d, "alpha").update(rank=True), "alpha: rank: must be a positive integer"),
            (lambda d: agent(d, "alpha").update(name=" "), "alpha: name: must be a non-empty string"),
            (lambda d: agent(d, "alpha").pop("vendor"), "alpha: vendor: must be a non-empty string"),
            (lambda d: agent(d, "alpha").update(max_chars=-5), "alpha: max_chars: must be null or a positive integer"),
            (lambda d: agent(d, "alpha").update(reads_agents_md="yes"), "alpha: reads_agents_md: must be true or false"),
            (lambda d: agent(d, "alpha").update(notes="one"), "alpha: notes: must be a list of strings"),
            (lambda d: agent(d, "alpha").update(oneshot=3), "alpha: oneshot: must be a string or null"),
            (lambda d: agent(d, "alpha")["project"].update(comment="slash"), "alpha: project.comment: must be html or hash"),
            (lambda d: agent(d, "delta")["register"].update(comment="slash"), "delta: register.comment: must be html or hash"),
            (lambda d: agent(d, "delta")["register"].pop("yaml_list_key"),
             "delta: register.yaml_list_key: must be a non-empty string"),
            (lambda d: agent(d, "alpha").update(detect=[]),
             "alpha: detect: must be an object with the string lists commands, paths and project_paths"),
            (lambda d: agent(d, "alpha")["detect"].update(paths=["/opt/alpha"]),
             'alpha: detect.paths: must be anchored at ~ or a {variable} (got "/opt/alpha")'),
            (lambda d: agent(d, "alpha")["detect"].update(project_paths=["../ALPHA.md"]),
             'alpha: detect.project_paths: must not contain `..` (got "../ALPHA.md")'),
        )
        for change, expected in cases:
            with self.subTest(expected=expected):
                self.assert_problem(change, expected)

    def test_validation_does_not_change_its_input(self):
        data = fixture_registry_data()
        before = copy.deepcopy(data)
        cli.validate_registry(data)
        cli.normalize_registry(data)
        self.assertEqual(data, before)

    def test_normalize_orders_by_rank_and_fills_defaults(self):
        data = fixture_registry_data()
        data["agents"].reverse()
        for key in ("register", "max_chars", "also_reads", "notes", "verify", "oneshot", "local_models"):
            del agent(data, "bravo")[key]
        del agent(data, "bravo")["project"]["comment"]
        self.assertEqual(cli.validate_registry(data), [])
        registry = cli.normalize_registry(data)
        self.assertEqual([entry["id"] for entry in registry["agents"]],
                         ["alpha", "bravo", "charlie", "delta", "echo", "foxtrot"])
        bravo = agent(registry, "bravo")
        self.assertEqual([bravo[key] for key in ("register", "max_chars", "also_reads", "notes", "oneshot")],
                         [None, None, [], [], None])
        self.assertEqual(bravo["project"], {"path": "AGENTS.md", "mode": "block", "frontmatter": None, "comment": "html"})
        self.assertEqual(agent(registry, "charlie")["workspace"],
                         {"supported": False, "reason": "Charlie reads only the repository root."})

    def test_build_registry_reports_a_broken_registry_as_one_error(self):
        texts = fixture_texts()
        self.assertEqual(len(cli.build_registry(texts)["agents"]), 6)
        del texts["agents/registry.json"]
        self.assertRaisesRegex(cli.DoctrineError, "agents/registry.json is missing", cli.build_registry, texts)
        texts["agents/registry.json"] = '{"schema": 1, "verified_on": "2026-01-15", "agents": []}'
        self.assertRaisesRegex(cli.DoctrineError, "agents: must be a non-empty list", cli.build_registry, texts)


class PathExpansionTest(unittest.TestCase):
    """Case 16, pure half."""

    ENV = {"HOME": "/home/kim", "XDG_CONFIG_HOME": "", "APPDATA": ""}

    def expand(self, template, platform, **overrides):
        return cli.expand_path(template, platform, dict(self.ENV, **overrides))

    def test_home(self):
        for platform in cli.PLATFORMS:
            self.assertEqual(self.expand("~/.alpha/rules/doctrine.md", platform), "/home/kim/.alpha/rules/doctrine.md")
            self.assertEqual(self.expand("~", platform), "/home/kim")
        self.assertEqual(self.expand("docs/~/x.md", "linux"), "docs/~/x.md")

    def test_xdg_config(self):
        self.assertEqual(self.expand("{xdg_config}/bravo/AGENTS.md", "linux"), "/home/kim/.config/bravo/AGENTS.md")
        self.assertEqual(self.expand("{xdg_config}/bravo/AGENTS.md", "darwin"), "/home/kim/.config/bravo/AGENTS.md")
        self.assertEqual(self.expand("{xdg_config}/bravo/AGENTS.md", "linux", XDG_CONFIG_HOME="/cfg"), "/cfg/bravo/AGENTS.md")

    def test_vscode_user_per_platform(self):
        template = "{vscode_user}/prompts/doctrine.md"
        self.assertEqual(self.expand(template, "darwin"),
                         "/home/kim/Library/Application Support/Code/User/prompts/doctrine.md")
        self.assertEqual(self.expand(template, "darwin", XDG_CONFIG_HOME="/cfg"),
                         "/home/kim/Library/Application Support/Code/User/prompts/doctrine.md")
        self.assertEqual(self.expand(template, "linux"), "/home/kim/.config/Code/User/prompts/doctrine.md")
        self.assertEqual(self.expand(template, "linux", XDG_CONFIG_HOME="/cfg"), "/cfg/Code/User/prompts/doctrine.md")
        self.assertEqual(self.expand(template, "windows", APPDATA="C:/Users/kim/AppData/Roaming"),
                         "C:/Users/kim/AppData/Roaming/Code/User/prompts/doctrine.md")
        self.assertEqual(self.expand(template, "windows"), "/home/kim/AppData/Roaming/Code/User/prompts/doctrine.md")

    def test_appdata(self):
        self.assertEqual(self.expand("{appdata}/Echo/instructions.txt", "windows", APPDATA="D:/Roaming"),
                         "D:/Roaming/Echo/instructions.txt")
        self.assertEqual(self.expand("{appdata}/Echo/instructions.txt", "linux"),
                         "/home/kim/AppData/Roaming/Echo/instructions.txt")

    def test_unknown_platform(self):
        self.assertRaises(ValueError, self.expand, "~/x", "solaris")

    def test_global_template_prefers_the_platform_path(self):
        registry = cli.build_registry(fixture_texts())
        alpha = cli.find_agent(registry, "alpha")
        self.assertEqual(cli.global_template(alpha, "darwin"), "~/.alpha/rules/doctrine.md")
        self.assertEqual(cli.global_template(alpha, "linux"), "~/.alpha/rules/doctrine.md")
        self.assertEqual(cli.global_template(alpha, "windows"), "{appdata}/Alpha/rules/doctrine.md")
        self.assertIsNone(cli.global_template(cli.find_agent(registry, "charlie"), "linux"))
        self.assertRaises(cli.DoctrineError, cli.find_agent, registry, "zulu")


class AgentsCommandTest(CliCase):
    """Case 16, black-box half: `agents --json` resolves the global path for the platform."""

    def resolved(self, platform, **env):
        env = dict(env, DOCTRINE_PLATFORM=platform)
        code, out, err = self.run_cli("agents", "--json", env=env)
        self.assertEqual((code, err), (0, ""))
        data = json.loads(out)
        self.assertEqual(data["platform"], platform)
        return dict((entry["id"], entry["resolved"]["global"]) for entry in data["agents"])

    def test_darwin(self):
        home = str(self.home)
        self.assertEqual(self.resolved("darwin"), {
            "alpha": home + "/.alpha/rules/doctrine.md",
            "bravo": home + "/.config/bravo/AGENTS.md",
            "charlie": None,
            "delta": home + "/Library/Application Support/Code/User/prompts/doctrine.md",
            "echo": home + "/AppData/Roaming/Echo/instructions.txt",
            "foxtrot": home + "/.foxtrot/doctrine.prompt.md"})

    def test_linux_with_and_without_xdg_config_home(self):
        home = str(self.home)
        found = self.resolved("linux", XDG_CONFIG_HOME=str(self.tmp / "xdg"))
        self.assertEqual(found["bravo"], str(self.tmp / "xdg") + "/bravo/AGENTS.md")
        self.assertEqual(found["delta"], str(self.tmp / "xdg") + "/Code/User/prompts/doctrine.md")
        self.assertEqual(found["alpha"], home + "/.alpha/rules/doctrine.md")
        found = self.resolved("linux", XDG_CONFIG_HOME="")
        self.assertEqual(found["bravo"], home + "/.config/bravo/AGENTS.md")
        self.assertEqual(found["delta"], home + "/.config/Code/User/prompts/doctrine.md")

    def test_windows(self):
        appdata = str(self.tmp / "AppData" / "Roaming")
        found = self.resolved("windows", APPDATA=appdata)
        self.assertEqual(found["alpha"], appdata + "/Alpha/rules/doctrine.md")
        self.assertEqual(found["delta"], appdata + "/Code/User/prompts/doctrine.md")
        self.assertEqual(found["echo"], appdata + "/Echo/instructions.txt")
        self.assertEqual(found["foxtrot"], str(self.home) + "/.foxtrot/doctrine.prompt.md")

    def test_unknown_platform_is_an_error(self):
        code, out, err = self.run_cli("agents", "--json", env={"DOCTRINE_PLATFORM": "solaris"})
        self.assertEqual((code, out), (1, ""))
        self.assertIn("DOCTRINE_PLATFORM must be one of darwin, linux, windows", err)

    def test_json_lists_the_normalized_registry_in_rank_order(self):
        code, out, _ = self.run_cli("agents", "--json")
        data = json.loads(out)
        self.assertEqual((code, data["schema"], data["verified_on"]), (0, 1, "2026-01-15"))
        self.assertEqual([entry["id"] for entry in data["agents"]],
                         ["alpha", "bravo", "charlie", "delta", "echo", "foxtrot"])
        self.assertEqual(data["agents"][3]["register"], {"file": ".delta.conf.yml", "comment": "hash", "yaml_list_key": "read"})

    def test_plain_listing(self):
        code, out, err = self.run_cli("agents", env={"DOCTRINE_PLATFORM": "windows"})
        self.assertEqual((code, err), (0, ""))
        lines = out.split("\n")
        self.assertEqual(lines[0].split(), ["ID", "NAME", "KIND", "PROJECT", "GLOBAL"])
        self.assertEqual(lines[1].split(), ["alpha", "Alpha", "Agent", "agent", ".alpha/rules/doctrine.md",
                                            "{appdata}/Alpha/rules/doctrine.md"])
        self.assertEqual(lines[3].split(), ["charlie", "Charlie", "agent", "AGENTS.md", "-"])
        self.assertEqual(len(lines), 8)

    def test_json_and_markdown_are_exclusive(self):
        code, _, err = self.run_cli("agents", "--json", "--markdown")
        self.assertEqual(code, 1)
        self.assertIn("not allowed with", err)

    def test_invalid_registry_is_one_clear_error(self):
        pkg = self.copy_fixture()
        path = pkg / "agents/registry.json"
        path.write_text(path.read_text(encoding="utf-8").replace('"mode": "modelfile"', '"mode": "patch"'), encoding="utf-8")
        for flags in ((), ("--json",), ("--markdown",)):
            code, out, err = self.run_cli("agents", *flags, pkg=pkg)
            self.assertEqual((code, out), (1, ""))
            self.assertIn('agents/registry.json is invalid: agent foxtrot: project.mode: unknown mode "patch"', err)


class GuideTest(CliCase):
    def guide(self):
        code, out, err = self.run_cli("agents", "--markdown")
        self.assertEqual((code, err), (0, ""))
        return out

    def test_guide_is_head_then_generated_sections_then_tail(self):
        texts = fixture_texts()
        guide = self.guide()
        head, tail = texts["agents/guide.head.md"].strip(), texts["agents/guide.tail.md"].strip()
        self.assertTrue(guide.startswith(head + "\n\n## Supported agents\n\n"))
        self.assertTrue(guide.endswith("\n\n" + tail + "\n"))
        self.assertEqual(guide, cli.render_guide(head, tail, cli.build_registry(texts)))
        self.assertIn("paths verified on 2026-01-15", guide)
        self.assertNotIn(str(self.home), guide)

    def test_summary_table(self):
        rows = [line for line in self.guide().split("\n") if line.startswith("|")]
        self.assertEqual(rows[0], "| Agent | Project target | Global target | Workspace | Reads AGENTS.md | Limit |")
        self.assertEqual(rows[2], "| Alpha Agent (`alpha`) | `.alpha/rules/doctrine.md` (file) | "
                                  "`~/.alpha/rules/doctrine.md` (file) | `ALPHA.md` (block) | no | none |")
        self.assertEqual(rows[4], "| Charlie (`charlie`) | `AGENTS.md` (block) | not supported | not supported | "
                                  "yes | 1500 chars |")
        self.assertEqual(len(rows), 8)

    def test_sections_follow_rank_order(self):
        headings = [line for line in self.guide().split("\n") if line.startswith("### ")]
        self.assertEqual(headings, ["### Alpha Agent (`alpha`)", "### Bravo CLI (`bravo`)", "### Charlie (`charlie`)",
                                    "### Delta Pair (`delta`)", "### Echo (`echo`)", "### Foxtrot Runtime (`foxtrot`)"])

    def section(self, agent_id):
        guide = self.guide()
        start = guide.index("(`%s`)\n" % agent_id)
        end = guide.find("\n### ", start)
        return guide[start:end if end != -1 else guide.index("\n## Anything else")]

    def test_section_for_an_agent_with_every_scope(self):
        text = self.section("alpha")
        self.assertIn("- Project: `.alpha/rules/doctrine.md` (file)\n", text)
        self.assertIn("- Global: `~/.alpha/rules/doctrine.md` (file); windows: `{appdata}/Alpha/rules/doctrine.md`\n", text)
        self.assertIn("- Workspace: `ALPHA.md` (block)\n", text)
        self.assertIn("- Also reads: `ALPHA.local.md`.\n", text)
        self.assertIn("- Sources: [1](https://example.com/docs/alpha/rules).\n", text)
        self.assertIn("```sh\ndoctrine install --agent alpha\ndoctrine install --agent alpha --scope global\n"
                      "doctrine install --agent alpha --scope workspace --path DIR\n```", text)
        self.assertIn("**Verify.** Run `alpha rules` and look for doctrine.md in the list.", text)
        self.assertIn('**One-shot.** `alpha run --prompt "review this change"`', text)
        self.assertIn("**Local models.** Point `ALPHA_BASE_URL` at a local model server.", text)
        self.assertIn("**Notes.**\n\n- Rules files load at session start; restart after installing.", text)
        self.assertNotIn("Alpha loads every Markdown file", text)

    def test_section_for_an_agent_without_global_or_workspace(self):
        text = self.section("charlie")
        self.assertIn("- Global: not supported. Charlie has no user-level instruction file.\n", text)
        self.assertIn("- Workspace: not supported. Charlie reads only the repository root.\n", text)
        self.assertIn("- Reads `AGENTS.md` natively.\n", text)
        self.assertIn("- Limit: 1500 characters.", text)
        self.assertIn("```sh\ndoctrine install --agent charlie\n"
                      "doctrine install --agent charlie --scope workspace --path DIR --each-repo\n```", text)
        self.assertNotIn("--scope global", text)
        self.assertNotIn("**One-shot.**", text)
        self.assertNotIn("Sources", text)

    def test_section_for_register_and_runtime_modes(self):
        self.assertIn("The installer also registers the target in `.delta.conf.yml` under the `read:` list.",
                      self.section("delta"))
        text = self.section("foxtrot")
        self.assertIn("Acme. Kind: runtime. Confidence: high.", text)
        self.assertIn("doctrine install --agent foxtrot --base MODEL\n", text)
        self.assertIn("doctrine install --agent foxtrot --scope global\n", text)


if __name__ == "__main__":
    unittest.main()
