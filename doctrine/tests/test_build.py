"""Case 3: build, then build --check; a changed source makes --check fail naming the stale files."""
import json
import unittest

from support import CliCase, append, cli, edit, fixture_model, fixture_texts, tree

GENERATED = ["dist/doctrine.micro.md", "dist/doctrine.compact.md", "dist/doctrine.compact.backend.md",
             "dist/doctrine.compact.frontend.md", "dist/doctrine.full.md", "dist/checklists.md",
             "dist/rules.json", "agents/README.md"]


class BuildTest(CliCase):
    def setUp(self):
        super().setUp()
        self.pkg = self.copy_fixture()

    def build(self, *flags):
        return self.run_cli("build", *flags, pkg=self.pkg)

    def read(self, rel):
        return (self.pkg / rel).read_bytes().decode("utf-8")

    def stale(self):
        code, out, err = self.build("--check")
        self.assertEqual(code, 1, out + err)
        return [line.split(": ")[0] for line in out.split("\n") if line]

    def test_build_writes_every_generated_file(self):
        code, out, err = self.build()
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(out.split("\n")[:-1], ["wrote " + rel for rel in GENERATED])
        model = fixture_model()
        self.assertEqual(self.read("dist/doctrine.micro.md"), cli.render(model, "micro", "fullstack", ".doctrine"))
        self.assertEqual(self.read("dist/doctrine.compact.md"), cli.render(model, "compact", "fullstack", ".doctrine"))
        self.assertEqual(self.read("dist/doctrine.compact.backend.md"), cli.render(model, "compact", "backend", ".doctrine"))
        self.assertEqual(self.read("dist/doctrine.compact.frontend.md"), cli.render(model, "compact", "frontend", ".doctrine"))
        self.assertEqual(self.read("dist/doctrine.full.md"), cli.render(model, "full", "fullstack", ".doctrine"))
        for rel in GENERATED:
            self.assertNotIn("\r", self.read(rel))
            self.assertTrue(self.read(rel).endswith("\n"))

    def test_build_then_check_passes_and_a_second_build_touches_nothing(self):
        self.assertEqual(self.build()[0], 0)
        code, out, err = self.build("--check")
        self.assertEqual((code, out, err), (0, "build --check: ok\n", ""))
        before = tree(self.pkg)
        code, out, _ = self.build()
        self.assertEqual(code, 0)
        self.assertEqual(out.split("\n")[:-1], ["unchanged " + rel for rel in GENERATED])
        self.assertEqual(tree(self.pkg), before)

    def test_check_before_any_build_lists_every_file_as_missing_and_writes_nothing(self):
        before = tree(self.pkg)
        code, out, err = self.build("--check")
        self.assertEqual(code, 1)
        self.assertEqual(out.split("\n")[:-1], [rel + ": missing" for rel in GENERATED])
        self.assertIn("8 generated file(s) out of date", err)
        self.assertEqual(tree(self.pkg), before)

    def test_changed_core_file_fails_check_naming_the_stale_files(self):
        self.assertEqual(self.build()[0], 0)
        edit(self.pkg / "core/backend.md", "Organize the backend as vertical slices", "Organize the server as vertical slices")
        before = tree(self.pkg)
        self.assertEqual(self.stale(), ["dist/doctrine.compact.md", "dist/doctrine.compact.backend.md",
                                        "dist/doctrine.full.md", "dist/rules.json"])
        self.assertEqual(tree(self.pkg), before)
        self.assertEqual(self.build()[0], 0)
        self.assertEqual(self.build("--check")[0], 0)
        self.assertIn("- `BE-STRUCT-1` Organize the server as vertical slices", self.read("dist/doctrine.compact.md"))

    def test_changed_check_text_makes_the_checklists_stale(self):
        self.assertEqual(self.build()[0], 0)
        edit(self.pkg / "core/review.md", "Does the review name each lens it applied?", "Does the review name every lens?")
        self.assertEqual(self.stale(), ["dist/doctrine.full.md", "dist/checklists.md", "dist/rules.json"])

    def test_changed_howto_registry_and_guide_sources_are_noticed(self):
        self.assertEqual(self.build()[0], 0)
        append(self.pkg / "howto/build-a-slice.md", "\nOne more paragraph.\n")
        self.assertEqual(self.stale(), ["dist/doctrine.full.md"])
        edit(self.pkg / "agents/registry.json", '"name": "Bravo CLI"', '"name": "Bravo Shell"')
        self.assertEqual(self.stale(), ["dist/doctrine.full.md", "agents/README.md"])
        self.assertEqual(self.build()[0], 0)
        append(self.pkg / "agents/guide.tail.md", "\nA closing line.\n")
        self.assertEqual(self.stale(), ["agents/README.md"])

    def test_hand_edited_generated_file_fails_check(self):
        self.assertEqual(self.build()[0], 0)
        append(self.pkg / "dist/doctrine.micro.md", "edited by hand\n")
        code, out, _ = self.build("--check")
        self.assertEqual((code, out), (1, "dist/doctrine.micro.md: differs from the sources\n"))

    def test_build_refuses_to_write_when_lint_fails(self):
        append(self.pkg / "core/checklists.md", "\nSee `BE-NOPE-7`.\n")
        before = tree(self.pkg)
        for flags in ((), ("--check",)):
            code, out, err = self.build(*flags)
            self.assertEqual(code, 1)
            self.assertIn("core/checklists.md:15: unknown rule id `BE-NOPE-7`", out)
            self.assertIn("lint failed", err)
        self.assertEqual(tree(self.pkg), before)
        self.assertFalse((self.pkg / "dist").exists())

    def test_rules_json(self):
        self.assertEqual(self.build()[0], 0)
        data = json.loads(self.read("dist/rules.json"))
        self.assertEqual(sorted(data), ["rules", "version"])
        self.assertEqual(data["version"], "0.9.0")
        self.assertEqual(len(data["rules"]), 18)
        self.assertEqual(list(data["rules"][4]), ["id", "title", "area", "group", "severity", "tier",
                                                  "principles", "check", "file", "line"])
        self.assertEqual(data["rules"], cli.parse_catalogs(fixture_texts())[0])
        self.assertIn("\u00b7", self.read("core/backend.md"))

    def test_checklists_append_the_rule_checks_grouped_by_area(self):
        self.assertEqual(self.build()[0], 0)
        text = self.read("dist/checklists.md")
        source = self.read("core/checklists.md").strip()
        self.assertTrue(text.startswith(source + "\n\n## Rule checks\n\n### Backend\n\n"))
        tail = text[len(source):]
        self.assertEqual([line for line in tail.split("\n") if line.startswith("#")],
                         ["## Rule checks", "### Backend", "### Frontend", "### Contracts", "### Testing",
                          "### Delivery", "### Review", "### Adoption"])
        self.assertIn("### Review\n\n- [ ] `R-1` Does the review name each lens it applied?\n"
                      "- [ ] `R-2` Does every finding carry a rule ID, a location and a failure scenario?\n", tail)
        self.assertIn("- [ ] `BE-SVC-1` Does every branch on a business condition sit in a service method, "
                      "not in a handler?\n", tail)
        self.assertEqual(tail.count("- [ ] `"), 15)
        self.assertNotIn("`P1`", tail)

    def test_agent_guide_is_the_markdown_listing(self):
        self.assertEqual(self.build()[0], 0)
        code, out, _ = self.run_cli("agents", "--markdown", pkg=self.pkg)
        self.assertEqual(code, 0)
        self.assertEqual(self.read("agents/README.md"), out)

    def test_built_package_still_lints_clean(self):
        self.assertEqual(self.build()[0], 0)
        code, out, _ = self.run_cli("lint", pkg=self.pkg)
        self.assertEqual(code, 0, out)


if __name__ == "__main__":
    unittest.main()
