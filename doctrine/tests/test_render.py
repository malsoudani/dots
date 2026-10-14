"""Case 1: render micro, compact and full for each profile; deterministic; budgets."""
import unittest

from support import CliCase, cli, fixture_model, fixture_texts

ALL_IDS = ["P1", "P2", "P3", "BE-STRUCT-1", "BE-SVC-1", "BE-TXN-1", "FE-STATE-1", "FE-MGR-1",
           "CT-1", "CT-2", "T-1", "T-2", "D-1", "D-2", "R-1", "R-2", "A-1", "A-2"]
MICRO_IDS = ["P1", "P2", "BE-SVC-1", "BE-TXN-1", "FE-STATE-1", "CT-2", "T-1", "D-1", "R-2", "A-1"]


def listed(text):
    """The ids that appear as `- \\`ID\\` Title` lines, in order."""
    return [line.split("`")[1] for line in text.split("\n") if line.startswith("- `") and "` " in line
            and cli.re.match("^" + cli.ID_PATTERN + "$", line.split("`")[1])]


class RenderTest(unittest.TestCase):
    def setUp(self):
        self.model = fixture_model()

    def test_every_tier_and_profile_has_the_header_and_clean_newlines(self):
        for tier in cli.TIERS:
            for profile in cli.PROFILES:
                with self.subTest(tier=tier, profile=profile):
                    text = cli.render(self.model, tier, profile, ".doctrine")
                    self.assertTrue(text.startswith("# Doctrine %s v0.9.0\n\n" % tier))
                    self.assertTrue(text.endswith("\n") and not text.endswith("\n\n"))
                    self.assertNotIn("\r", text)
                    self.assertNotIn("\n\n\n", text)

    def test_render_is_deterministic_and_independent_of_load_order(self):
        texts = fixture_texts()
        shuffled = dict((key, texts[key]) for key in reversed(sorted(texts)))
        other = cli.build_model(shuffled)
        for tier in cli.TIERS:
            for profile in cli.PROFILES:
                with self.subTest(tier=tier, profile=profile):
                    first = cli.render(self.model, tier, profile, ".doctrine")
                    self.assertEqual(first, cli.render(self.model, tier, profile, ".doctrine"))
                    self.assertEqual(first, cli.render(other, tier, profile, ".doctrine"))

    def test_micro_lists_only_micro_tier_principles_and_rules(self):
        text = cli.render(self.model, "micro", "fullstack", ".doctrine")
        self.assertEqual(listed(text), MICRO_IDS)
        self.assertIn("You are working under the fixture edition of Doctrine.", text)
        self.assertNotIn("# Doctrine — operating instructions", text)
        self.assertLess(text.index("## Principles"), text.index("## Rules"))
        self.assertLess(text.index("## Rules"), text.index("### Backend"))
        self.assertIn("- `BE-TXN-1` Wrap each multi-write service method in one transaction\n", text)
        self.assertNotIn("Deep dives", text)

    def test_micro_profiles_drop_the_other_side(self):
        backend = listed(cli.render(self.model, "micro", "backend", ".doctrine"))
        frontend = listed(cli.render(self.model, "micro", "frontend", ".doctrine"))
        self.assertEqual(backend, [i for i in MICRO_IDS if not i.startswith("FE-")])
        self.assertEqual(frontend, [i for i in MICRO_IDS if not i.startswith("BE-")])

    def test_compact_lists_every_title_grouped_by_area(self):
        text = cli.render(self.model, "compact", "fullstack", ".doctrine")
        self.assertEqual(listed(text), ALL_IDS)
        headings = [line for line in text.split("\n") if line.startswith("## ")]
        self.assertEqual(headings, ["## Principles", "## Backend", "## Frontend", "## Contracts", "## Testing",
                                    "## Delivery", "## Review", "## Adoption", "## Deep dives"])
        self.assertNotIn("**Rule.**", text)

    def test_compact_profiles_filter_rules_and_deep_dives(self):
        backend = cli.render(self.model, "compact", "backend", ".doctrine")
        frontend = cli.render(self.model, "compact", "frontend", ".doctrine")
        self.assertEqual(listed(backend), [i for i in ALL_IDS if not i.startswith("FE-")])
        self.assertEqual(listed(frontend), [i for i in ALL_IDS if not i.startswith("BE-")])
        self.assertNotIn("## Frontend", backend)
        self.assertNotIn("core/frontend.md", backend)
        self.assertIn("core/backend.md", backend)
        self.assertNotIn("## Backend", frontend)
        self.assertNotIn("core/backend.md", frontend)

    def test_compact_deep_dives_point_into_the_reference_directory(self):
        text = cli.render(self.model, "compact", "fullstack", "/srv/ref/")
        for stem in ("principles", "backend", "frontend", "contracts", "testing", "delivery", "review", "adoption"):
            self.assertIn("`/srv/ref/core/%s.md`" % stem, text)
        self.assertIn("- Checklists: `/srv/ref/checklists.md`", text)
        self.assertIn("- `/srv/ref/howto/build-a-slice.md`: Build a backend slice end to end", text)
        self.assertNotIn(".doctrine", text)

    def test_compact_without_a_reference_directory_points_at_the_cli(self):
        text = cli.render(self.model, "compact", "fullstack", None)
        self.assertIn("## Deep dives", text)
        self.assertIn("doctrine print --tier full", text)
        self.assertNotIn("core/backend.md", text)

    def test_full_holds_every_source_in_order_with_contents(self):
        text = cli.render(self.model, "full", "fullstack", ".doctrine")
        order = ["core/operating.md", "core/principles.md", "core/backend.md", "core/frontend.md",
                 "core/contracts.md", "core/testing.md", "core/delivery.md", "core/review.md",
                 "core/adoption.md", "core/checklists.md", "howto/build-a-slice.md"]
        cursor = text.index("\n\n---\n\n")
        preamble = text[:cursor]
        self.assertIn("Version 0.9.0. 3 principles, 15 rules.", preamble)
        self.assertIn("## Contents", preamble)
        for number, rel in enumerate(order, 1):
            with self.subTest(rel=rel):
                body = self.model.texts[rel].strip()
                self.assertIn("%d. %s (`%s`)" % (number, body.split("\n")[0][2:], rel), preamble)
                found = text.find("\n\n---\n\n" + body, cursor)
                self.assertGreaterEqual(found, cursor, rel + " is missing or out of order")
                cursor = found + 1
        self.assertEqual(text.count("\n---\n"), len(order))

    def test_full_profiles_drop_the_other_catalog(self):
        backend = cli.render(self.model, "full", "backend", ".doctrine")
        frontend = cli.render(self.model, "full", "frontend", ".doctrine")
        self.assertNotIn("### FE-STATE-1", backend)
        self.assertIn("### BE-SVC-1", backend)
        self.assertIn("3 principles, 13 rules.", backend)
        self.assertNotIn("### BE-SVC-1", frontend)
        self.assertIn("### FE-STATE-1", frontend)
        self.assertIn("3 principles, 12 rules.", frontend)

    def test_fixture_fits_the_budgets(self):
        self.assertLessEqual(len(cli.render(self.model, "micro", "fullstack", ".doctrine")), cli.BUDGETS["micro"])
        self.assertLessEqual(len(cli.render(self.model, "compact", "fullstack", ".doctrine")), cli.BUDGETS["compact"])
        self.assertEqual(cli.BUDGETS, {"micro": 4000, "compact": 12000})

    def test_unknown_tier_or_profile_is_rejected(self):
        self.assertRaises(ValueError, cli.render, self.model, "huge", "fullstack", None)
        self.assertRaises(ValueError, cli.render, self.model, "micro", "mobile", None)


class PrintCommandTest(CliCase):
    def test_print_matches_the_pure_function_for_every_tier_and_profile(self):
        model = fixture_model()
        for tier in cli.TIERS:
            for profile in cli.PROFILES:
                with self.subTest(tier=tier, profile=profile):
                    code, out, err = self.run_cli("print", "--tier", tier, "--profile", profile)
                    self.assertEqual((code, err), (0, ""))
                    self.assertEqual(out, cli.render(model, tier, profile, ".doctrine"))

    def test_print_defaults_to_compact_fullstack(self):
        code, out, _ = self.run_cli("print")
        self.assertEqual(code, 0)
        self.assertEqual(out, cli.render(fixture_model(), "compact", "fullstack", ".doctrine"))

    def test_print_reference_dir(self):
        code, out, _ = self.run_cli("print", "--reference-dir", "~/.doctrine")
        self.assertEqual(code, 0)
        self.assertIn("`~/.doctrine/core/backend.md`", out)

    def test_print_for_an_agent_adds_its_front_matter(self):
        code, out, err = self.run_cli("print", "--agent", "alpha")
        self.assertEqual((code, err), (0, ""))
        self.assertTrue(out.startswith(
            "---\ndescription: \"Doctrine: engineering standards\"\nalwaysApply: true\n"
            "globs:\n  - \"**/*\"\npriority: 1\n---\n# Doctrine compact v0.9.0\n"), out[:200])

    def test_print_for_an_agent_falls_back_to_a_tier_that_fits(self):
        model = fixture_model()
        micro = cli.render(model, "micro", "fullstack", ".doctrine")
        self.assertTrue(len(micro) <= 1500 < len(cli.render(model, "compact", "fullstack", ".doctrine")))
        code, out, err = self.run_cli("print", "--agent", "charlie")
        self.assertEqual(code, 0)
        self.assertEqual(out, micro)
        self.assertIn("compact does not fit the 1500 character limit of charlie; printing micro", err)

    def test_print_for_an_agent_fails_when_micro_does_not_fit(self):
        code, out, err = self.run_cli("print", "--agent", "echo")
        self.assertEqual((code, out), (1, ""))
        self.assertIn("over the limit of 120", err)

    def test_print_for_an_unknown_agent_fails(self):
        code, _, err = self.run_cli("print", "--agent", "zulu")
        self.assertEqual(code, 1)
        self.assertIn("unknown agent zulu", err)


class FrontMatterTest(unittest.TestCase):
    def test_scalars_are_quoted_only_when_needed(self):
        self.assertEqual(cli.yaml_scalar("plain words"), "plain words")
        self.assertEqual(cli.yaml_scalar(True), "true")
        self.assertEqual(cli.yaml_scalar(False), "false")
        self.assertEqual(cli.yaml_scalar(12), "12")
        for raw in ("a: b", "#x", "**", "{a}", "[a]", "a,b", "&a", "!a", "a|b", "a>b", "it's", 'say "x"',
                    "50%", "a@b", " lead", "trail ", "", "true", "No", "null", "12", "-dash", "~"):
            with self.subTest(raw=raw):
                rendered = cli.yaml_scalar(raw)
                self.assertTrue(rendered.startswith('"') and rendered.endswith('"'), rendered)
        self.assertEqual(cli.yaml_scalar('say "x" \\ now'), '"say \\"x\\" \\\\ now"')

    def test_front_matter_block(self):
        self.assertEqual(cli.render_frontmatter(None), "")
        self.assertEqual(cli.render_frontmatter({}), "")
        self.assertEqual(cli.render_frontmatter({"applyTo": "**", "on": True, "tags": ["a b", "c:d"], "none": []}),
                         '---\napplyTo: "**"\non: true\ntags:\n  - a b\n  - "c:d"\nnone: []\n---\n')

    def test_fit_tier_walks_down_and_fails_below_micro(self):
        sizes = {"full": "x" * 300, "compact": "x" * 200, "micro": "x" * 100}
        self.assertEqual(cli.fit_tier(sizes.get, "full", None), ("full", sizes["full"]))
        self.assertEqual(cli.fit_tier(sizes.get, "full", 250), ("compact", sizes["compact"]))
        self.assertEqual(cli.fit_tier(sizes.get, "compact", 150), ("micro", sizes["micro"]))
        self.assertEqual(cli.fit_tier(sizes.get, "micro", 100), ("micro", sizes["micro"]))
        self.assertRaises(cli.DoctrineError, cli.fit_tier, sizes.get, "full", 99)


if __name__ == "__main__":
    unittest.main()
