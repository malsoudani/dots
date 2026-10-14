"""Case 2: every lint failure class has its own fixture mutation and its own message."""
import json
import re
import shutil
import unittest

from support import FIXTURE, CliCase, append, cli, edit, fixture_texts

SERVICE = "examples/backend/notes/service.py"

# A well-formed rule appended to core/testing.md; each grammar test breaks one thing in it.
RULE = """
### T-9 · Keep every test independent of the others
<!-- doctrine: severity=YELLOW tier=compact principles=P1 -->

**Rule.** Each test builds its own data.

**Why.** Shared data couples tests to the order they run in.

**How.** Create the rows inside the test.

**Check.** Does each test create the data it reads?
"""
PRINCIPLE = """
### P9 · The host project always wins
<!-- doctrine: tier=compact -->

**Principle.** Doctrine serves the project.

**Why.** A competing pattern in one corner costs more than it buys.

**In practice.** `A-1`.
"""
# Assembled at run time so that this file passes the text hygiene check it tests.
ACCESS_KEY = "AKIA" + "ABCDEFGHIJKLMNOP"
KEY_HEADER = "-----BEGIN " + "RSA PRIVATE KEY-----"
REAL_EMAIL = "dev" + "@" + "corp.invalid"


class LintCase(CliCase):
    def setUp(self):
        super().setUp()
        self.pkg = self.copy_fixture()

    def problems(self):
        code, out, _ = self.run_cli("lint", pkg=self.pkg)
        lines = [line for line in out.split("\n") if line]
        self.assertEqual(code, 1 if lines and not out.startswith("lint: ok") else 0, out)
        return [] if out.startswith("lint: ok") else lines

    def assert_only(self, rel, message, line=None):
        """Lint reports exactly one problem, in `rel`, carrying `message`."""
        found = self.problems()
        self.assertEqual(len(found), 1, "\n".join(found))
        match = re.match(r"^(.+?):(\d+): (.*)$", found[0])
        self.assertTrue(match, found[0])
        self.assertEqual(match.group(1), rel)
        self.assertIn(message, match.group(3))
        if line is not None:
            self.assertEqual(int(match.group(2)), line)

    def line_of(self, rel, needle):
        lines = (self.pkg / rel).read_text(encoding="utf-8").split("\n")
        return [number for number, text in enumerate(lines, 1) if needle in text][0]

    def add_rule(self, old=None, new=None, rel="core/testing.md", rule=RULE):
        text = rule if old is None else rule.replace(old, new)
        self.assertTrue(old is None or text != rule, "the mutation changed nothing")
        append(self.pkg / rel, text)


class LintPassTest(LintCase):
    def test_the_fixture_is_clean(self):
        code, out, err = self.run_cli("lint")
        self.assertEqual((code, err), (0, ""))
        self.assertTrue(out.startswith("lint: ok"))

    def test_a_well_formed_extra_rule_and_principle_stay_clean(self):
        self.add_rule()
        self.add_rule(rel="core/principles.md", rule=PRINCIPLE)
        self.assertEqual(self.problems(), [])

    def test_json_output(self):
        code, out, _ = self.run_cli("lint", "--json", pkg=self.pkg)
        self.assertEqual((code, json.loads(out)), (0, {"ok": True, "problems": []}))
        append(self.pkg / "core/checklists.md", "\nSee `BE-NOPE-7`.\n")
        code, out, _ = self.run_cli("lint", "--json", pkg=self.pkg)
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out), {"ok": False, "problems": [{
            "file": "core/checklists.md", "line": self.line_of("core/checklists.md", "BE-NOPE-7"),
            "message": "unknown rule id `BE-NOPE-7`"}]})


class GrammarLintTest(LintCase):
    def test_heading_without_the_middle_dot(self):
        self.add_rule("T-9 · Keep", "T-9 - Keep")
        self.assert_only("core/testing.md", "heading does not match the rule grammar",
                         self.line_of("core/testing.md", "### T-9"))

    def test_heading_with_an_unknown_prefix(self):
        self.add_rule("### T-9", "### QA-9")
        self.assert_only("core/testing.md", "heading does not match the rule grammar")

    def test_heading_with_a_title_under_ten_characters(self):
        self.add_rule("Keep every test independent of the others", "Too short")
        self.assert_only("core/testing.md", "heading does not match the rule grammar")

    def test_heading_inside_a_code_fence_is_not_a_heading(self):
        append(self.pkg / "core/testing.md", "\n```markdown\n### not a rule heading\n**Check.** x\n```\n")
        self.assertEqual(self.problems(), [])

    def test_title_longer_than_eighty_characters(self):
        self.add_rule("Keep every test independent of the others", "x" * 81)
        self.assert_only("core/testing.md", "title is longer than 80 characters (81)",
                         self.line_of("core/testing.md", "### T-9"))

    def test_title_of_exactly_eighty_characters_passes(self):
        self.add_rule("Keep every test independent of the others", "x" * 80)
        self.assertEqual(self.problems(), [])

    def test_metadata_comment_missing(self):
        self.add_rule("<!-- doctrine: severity=YELLOW tier=compact principles=P1 -->\n", "")
        self.assert_only("core/testing.md", "metadata comment is missing",
                         self.line_of("core/testing.md", "### T-9") + 1)

    def test_metadata_comment_not_on_the_next_line(self):
        self.add_rule("others\n<!--", "others\n\n<!--")
        self.assert_only("core/testing.md", "metadata comment is missing")

    def test_metadata_comment_malformed(self):
        cases = (
            ("severity=YELLOW", "severity=PURPLE", "severity must be RED, ORANGE or YELLOW"),
            ("tier=compact", "tier=huge", "tier must be micro or compact"),
            (" principles=P1", "", "expected exactly the keys severity, tier, principles"),
            ("principles=P1", "principles=P1,backend", "principles must be principle ids"),
            ("principles=P1 -->", "principles=P1 extra -->", "expected `<!-- doctrine:"),
            ("tier=compact", "tier=compact tier=micro", "expected exactly the keys"),
        )
        for old, new, message in cases:
            with self.subTest(new=new):
                shutil.rmtree(str(self.pkg))
                self.copy_fixture()
                self.add_rule(old, new)
                self.assert_only("core/testing.md", "metadata comment is malformed: " + message,
                                 self.line_of("core/testing.md", "### T-9") + 1)

    def test_principle_metadata_takes_only_a_tier(self):
        self.add_rule("<!-- doctrine: tier=compact -->", "<!-- doctrine: severity=RED tier=compact principles=P1 -->",
                      rel="core/principles.md", rule=PRINCIPLE)
        self.assert_only("core/principles.md", "metadata comment is malformed: expected exactly the keys tier")

    def test_rule_lacking_a_required_label(self):
        for label in ("Rule", "Why", "How", "Check"):
            with self.subTest(label=label):
                shutil.rmtree(str(self.pkg))
                self.copy_fixture()
                self.add_rule("**%s.**" % label, "%s:" % label)
                self.assert_only("core/testing.md", "rule T-9 lacks **%s.**" % label,
                                 self.line_of("core/testing.md", "### T-9"))

    def test_rule_with_an_empty_check(self):
        self.add_rule("**Check.** Does each test create the data it reads?", "**Check.**")
        self.assert_only("core/testing.md", "rule T-9 has an empty **Check.**")

    def test_principle_lacking_a_required_label(self):
        for label in ("Principle", "Why", "In practice"):
            with self.subTest(label=label):
                shutil.rmtree(str(self.pkg))
                self.copy_fixture()
                self.add_rule("**%s.**" % label, "%s:" % label, rel="core/principles.md", rule=PRINCIPLE)
                self.assert_only("core/principles.md", "principle P9 lacks **%s.**" % label)

    def test_duplicate_id(self):
        self.add_rule("### T-9", "### T-1")
        self.assert_only("core/testing.md", "duplicate id T-1 (first defined at core/testing.md:7)",
                         self.line_of("core/testing.md", "Keep every test independent"))

    def test_duplicate_id_across_files(self):
        self.add_rule("### T-9", "### T-1", rel="core/review.md")
        self.assert_only("core/review.md", "duplicate id T-1 (first defined at core/testing.md:7)")

    def test_rule_citing_an_unknown_principle(self):
        self.add_rule("principles=P1", "principles=P1,P77")
        self.assert_only("core/testing.md", "rule T-9 cites unknown principle P77")


class ReferenceLintTest(LintCase):
    def test_unknown_backticked_id_in_core(self):
        append(self.pkg / "core/checklists.md", "\n- [ ] Also run `T-1` and `BE-NOPE-7`.\n")
        self.assert_only("core/checklists.md", "unknown rule id `BE-NOPE-7`",
                         self.line_of("core/checklists.md", "BE-NOPE-7"))

    def test_unknown_backticked_id_in_a_howto(self):
        append(self.pkg / "howto/build-a-slice.md", "\nThen apply `FE-STATE-99`.\n")
        self.assert_only("howto/build-a-slice.md", "unknown rule id `FE-STATE-99`")

    def test_wildcards_and_other_code_spans_are_not_ids(self):
        append(self.pkg / "howto/build-a-slice.md", "\nSee `BE-SVC-*`, `FE-STATE-5..7`, `X-1`, `service.py` and `HTTP-2xx`.\n")
        self.assertEqual(self.problems(), [])

    def test_excerpt_that_is_not_verbatim(self):
        edit(self.pkg / "howto/build-a-slice.md", "class TitleTooLong(Exception):", "class TitleTooLong(ValueError):")
        self.assert_only("howto/build-a-slice.md", "excerpt is not a contiguous verbatim slice of " + SERVICE,
                         self.line_of("howto/build-a-slice.md", "<!-- excerpt:"))

    def test_excerpt_that_skips_a_line_is_not_contiguous(self):
        edit(self.pkg / "core/backend.md", "        if len(title) > MAX_TITLE:\n", "")
        self.assert_only("core/backend.md", "excerpt is not a contiguous verbatim slice of " + SERVICE)

    def test_excerpt_goes_stale_when_the_source_changes(self):
        edit(self.pkg / SERVICE, '    """Raised when a note title exceeds the limit."""', '    """Too long."""')
        self.assert_only("howto/build-a-slice.md", "excerpt is not a contiguous verbatim slice of " + SERVICE)

    def test_excerpt_ignores_trailing_whitespace(self):
        edit(self.pkg / "howto/build-a-slice.md", "class TitleTooLong(Exception):", "class TitleTooLong(Exception):   ")
        edit(self.pkg / SERVICE, "MAX_TITLE = 80", "MAX_TITLE = 80  ")
        self.assertEqual(self.problems(), [])

    def test_excerpt_of_a_missing_file(self):
        edit(self.pkg / "howto/build-a-slice.md", "<!-- excerpt: " + SERVICE, "<!-- excerpt: examples/backend/notes/gone.py")
        self.assert_only("howto/build-a-slice.md", "excerpt source examples/backend/notes/gone.py does not exist")

    def test_excerpt_path_outside_the_package(self):
        edit(self.pkg / "howto/build-a-slice.md", "<!-- excerpt: " + SERVICE, "<!-- excerpt: ../" + SERVICE)
        self.assert_only("howto/build-a-slice.md", "excerpt path must not contain `..`")

    def test_excerpt_comment_without_a_code_block(self):
        append(self.pkg / "howto/build-a-slice.md", "\n<!-- excerpt: %s -->\n\nNo block follows.\n" % SERVICE)
        self.assert_only("howto/build-a-slice.md", "excerpt comment is not followed by a fenced code block")

    def test_excerpt_inside_a_list_item_is_dedented(self):
        append(self.pkg / "howto/build-a-slice.md",
               "\n1. Cap the title:\n\n   <!-- excerpt: %s -->\n   ```python\n   MAX_TITLE = 80\n   ```\n" % SERVICE)
        self.assertEqual(self.problems(), [])

    def test_excerpt_in_the_package_readme_is_checked(self):
        (self.pkg / "README.md").write_text(
            "# Fixture\n\n<!-- excerpt: %s -->\n```python\nMAX_TITLE = 81\n```\n" % SERVICE, encoding="utf-8")
        self.assert_only("README.md", "excerpt is not a contiguous verbatim slice of " + SERVICE, 3)


class BudgetLintTest(LintCase):
    def test_micro_over_budget(self):
        append(self.pkg / "core/operating.md", "\n" + ("Pad the operating text. " * 130) + "\n")
        self.assert_only("dist/doctrine.micro.md", "micro fullstack is ")
        self.assertIn("over the budget of 4000", self.problems()[0])

    def test_compact_over_budget(self):
        rules = "".join(RULE.replace("T-9", "T-%d" % number)
                        .replace("Keep every test independent of the others", "y" * 80)
                        for number in range(100, 230))
        append(self.pkg / "core/testing.md", rules)
        self.assert_only("dist/doctrine.compact.md", "compact fullstack is ")
        self.assertIn("over the budget of 12000", self.problems()[0])


class RegistryLintTest(LintCase):
    def mutate(self, change):
        path = self.pkg / "agents/registry.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        change(data)
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def agent_line(self, agent_id):
        return self.line_of("agents/registry.json", '"id": "%s"' % agent_id)

    def test_unknown_mode(self):
        self.mutate(lambda data: data["agents"][0]["project"].update(mode="patch"))
        self.assert_only("agents/registry.json", 'agent alpha: project.mode: unknown mode "patch"', self.agent_line("alpha"))

    def test_high_confidence_without_sources(self):
        self.mutate(lambda data: data["agents"][1].update(sources=[]))
        self.assert_only("agents/registry.json",
                         "agent bravo: sources: an agent with confidence high needs at least one source",
                         self.agent_line("bravo"))

    def test_duplicate_ids(self):
        self.mutate(lambda data: data["agents"][2].update(id="alpha"))
        self.assert_only("agents/registry.json", "agent alpha: duplicate id alpha")

    def test_project_path_absolute(self):
        self.mutate(lambda data: data["agents"][3]["project"].update(path="/etc/doctrine.md"))
        self.assert_only("agents/registry.json", 'agent delta: project.path: must be a relative path (got "/etc/doctrine.md")')

    def test_project_path_escaping(self):
        self.mutate(lambda data: data["agents"][3]["project"].update(path="docs/../../doctrine.md"))
        self.assert_only("agents/registry.json", "agent delta: project.path: must not contain `..`")

    def test_global_path_not_anchored(self):
        self.mutate(lambda data: data["agents"][0]["global"].update(path="/etc/alpha/doctrine.md"))
        self.assert_only("agents/registry.json",
                         'agent alpha: global.path: must be anchored at ~ or a {variable} (got "/etc/alpha/doctrine.md")')

    def test_invalid_json(self):
        append(self.pkg / "agents/registry.json", "}\n")
        self.assert_only("agents/registry.json", "invalid JSON")

    def test_missing_registry(self):
        (self.pkg / "agents/registry.json").unlink()
        self.assert_only("agents/registry.json", "required file is missing", 1)


class HygieneLintTest(LintCase):
    def test_access_key_id(self):
        append(self.pkg / "howto/build-a-slice.md", "\nkey = %s\n" % ACCESS_KEY)
        self.assert_only("howto/build-a-slice.md", "text hygiene: looks like an access key id",
                         self.line_of("howto/build-a-slice.md", "key = "))

    def test_private_key_header(self):
        append(self.pkg / SERVICE, "\nPEM = '''%s'''\n" % KEY_HEADER)
        self.assert_only(SERVICE, "text hygiene: private key header")

    def test_private_key_header_without_an_algorithm(self):
        (self.pkg / "notes.txt").write_text(KEY_HEADER.replace("RSA ", "") + "\n", encoding="utf-8")
        self.assert_only("notes.txt", "text hygiene: private key header", 1)

    def test_email_address_outside_the_example_domains(self):
        append(self.pkg / "core/checklists.md", "\nAsk %s for access.\n" % REAL_EMAIL)
        self.assert_only("core/checklists.md", "text hygiene: email address at corp.invalid")

    def test_email_under_a_subdomain_of_an_example_domain_is_still_reported(self):
        append(self.pkg / "core/checklists.md", "\nAsk %s for access.\n" % REAL_EMAIL.replace("corp.invalid", "mail.example.com"))
        self.assert_only("core/checklists.md", "text hygiene: email address at mail.example.com")

    def test_allowed_look_alikes_pass(self):
        append(self.pkg / "howto/build-a-slice.md",
               "\nMail someone@example.com, Other.Person+tag@EXAMPLE.org or a@example.net.\n"
               "Pin typescript@6.0.2 and actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1.\n"
               "A decorator like @dataclass, a handle like @reviewer and the word AKIA are fine.\n")
        self.assertEqual(self.problems(), [])

    def test_registry_source_quotes_are_exempt_but_other_registry_text_is_not(self):
        path = self.pkg / "agents/registry.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["agents"][0]["sources"][0]["quote"] = "Write to %s for \\\"help\\\"." % REAL_EMAIL
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.assertEqual(self.problems(), [])
        data["agents"][0]["notes"] = ["Write to %s." % REAL_EMAIL]
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.assert_only("agents/registry.json", "text hygiene: email address at corp.invalid")

    def test_dependency_directories_and_binary_files_are_skipped(self):
        vendored = self.pkg / "examples/frontend/node_modules/left"
        vendored.mkdir(parents=True)
        (vendored / "README.md").write_text("Maintainer: %s\n" % REAL_EMAIL, encoding="utf-8")
        (self.pkg / "examples/backend/db.sqlite3").write_bytes(b"SQLite\0" + REAL_EMAIL.encode("ascii"))
        self.assertEqual(self.problems(), [])


class MissingFilesLintTest(LintCase):
    def test_each_required_file_is_reported_by_name(self):
        (self.pkg / "agents/guide.tail.md").unlink()
        self.assert_only("agents/guide.tail.md", "required file is missing", 1)

    def test_missing_core_files_are_all_listed(self):
        shutil.rmtree(str(self.pkg / "core"))
        found = self.problems()
        for rel in cli.REQUIRED_CORE:
            self.assertIn("%s:1: required file is missing" % rel, found)

    def test_bad_version(self):
        (self.pkg / "VERSION").write_text("next\n", encoding="utf-8")
        self.assert_only("VERSION", "must hold a version like 0.1.0", 1)


class CatalogParserTest(unittest.TestCase):
    """Direct tests of the pure parser."""

    def test_records_carry_every_field(self):
        records, problems = cli.parse_catalogs(fixture_texts())
        self.assertEqual(problems, [])
        by_id = dict((record["id"], record) for record in records)
        self.assertEqual(by_id["BE-SVC-1"], {
            "id": "BE-SVC-1", "title": "Put every business rule in a service method", "area": "backend",
            "group": "Services", "severity": "RED", "tier": "micro", "principles": ["P1", "P2"],
            "check": "Does every branch on a business condition sit in a service method, not in a handler?",
            "file": "core/backend.md", "line": 20})
        self.assertEqual(by_id["P3"], {
            "id": "P3", "title": "A unit of work is all-or-nothing", "area": "principles", "group": "",
            "severity": None, "tier": "compact", "principles": [], "check": None,
            "file": "core/principles.md", "line": 23})
        self.assertEqual(by_id["A-2"]["check"], "Is each migrated slice complete before the next one starts?")

    def test_records_follow_file_order_and_areas_follow_the_prefix(self):
        records, _ = cli.parse_catalogs(fixture_texts())
        self.assertEqual([record["id"] for record in records],
                         ["P1", "P2", "P3", "BE-STRUCT-1", "BE-SVC-1", "BE-TXN-1", "FE-STATE-1", "FE-MGR-1",
                          "CT-1", "CT-2", "T-1", "T-2", "D-1", "D-2", "R-1", "R-2", "A-1", "A-2"])
        areas = dict((record["id"], record["area"]) for record in records)
        self.assertEqual([areas[i] for i in ("P1", "BE-TXN-1", "FE-MGR-1", "CT-1", "T-1", "D-1", "R-1", "A-1")],
                         ["principles", "backend", "frontend", "contracts", "testing", "delivery", "review", "adoption"])

    def test_heading_regex_is_the_one_in_the_specification(self):
        self.assertEqual(cli.HEADING_RE.pattern,
                         "^### ((?:P|BE|FE|CT|T|D|R|A)(?:-[A-Z]+)?-?\\d+) · (.{10,80})$")
        for good in ("### P14 · The host project wins", "### BE-TXN-2 · Never hold a transaction open",
                     "### T-10 · Ten characters"):
            self.assertTrue(cli.HEADING_RE.match(good), good)
        for bad in ("### BE-TXN-2 - Never hold a transaction open", "### be-txn-2 · Never hold a transaction",
                    "## BE-TXN-2 · Never hold a transaction open", "### BE-TXN-2 · Short"):
            self.assertFalse(cli.HEADING_RE.match(bad), bad)

    def test_fences_nest_by_length(self):
        kinds = [kind for _, _, kind in cli.scan_lines("a\n````md\n```py\nx\n```\n````\nb\n~~~\n```\n~~~")]
        self.assertEqual(kinds, ["text", "open", "code", "code", "code", "close", "text", "open", "code", "close"])

    def test_metadata_parser(self):
        self.assertEqual(cli.parse_meta("<!-- doctrine: severity=RED tier=micro principles=P1,P5 -->", False),
                         ({"severity": "RED", "tier": "micro", "principles": ["P1", "P5"]}, None))
        self.assertEqual(cli.parse_meta("<!-- doctrine: tier=micro -->", True), ({"tier": "micro"}, None))
        self.assertIn("is missing", cli.parse_meta("", False)[1])
        self.assertIn("is malformed", cli.parse_meta("<!-- doctrine: tier=micro -->", False)[1])

    def test_lint_is_pure_and_clean_on_the_fixture(self):
        texts = fixture_texts()
        before = dict(texts)
        self.assertEqual(cli.lint(texts), [])
        self.assertEqual(texts, before)

    def test_email_pattern_matches_the_specification_examples(self):
        self.assertIsNone(cli.EMAIL_RE.search("typescript@6.0.2"))
        self.assertIsNone(cli.EMAIL_RE.search("actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1"))
        self.assertEqual(cli.EMAIL_RE.search("mail " + REAL_EMAIL + " now").group(1), "corp.invalid")
        self.assertEqual(cli.check_hygiene("a.md", "x\n" + ACCESS_KEY + " " + REAL_EMAIL),
                         [("a.md", 2, "text hygiene: looks like an access key id (AKIA...)"),
                          ("a.md", 2, "text hygiene: email address at corp.invalid "
                                      "(only example.com, example.org, example.net are allowed)")])


if __name__ == "__main__":
    unittest.main()
