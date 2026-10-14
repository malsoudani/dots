"""The command line: argument parsing for every command, package location, clear errors."""
import os
import shutil
import stat
import subprocess
import sys
import unittest

from support import BIN, FIXTURE, PKG, CliCase, cli, tree


class ParserTest(unittest.TestCase):
    def parse(self, *argv):
        return cli.build_parser().parse_args(list(argv))

    def test_simple_commands(self):
        self.assertEqual(self.parse("version").command, "version")
        self.assertEqual(vars(self.parse("agents")), {"command": "agents", "json": False, "markdown": False})
        self.assertTrue(self.parse("agents", "--markdown").markdown)
        self.assertEqual(vars(self.parse("detect", "--path", "x", "--json")), {"command": "detect", "path": "x", "json": True})
        self.assertEqual(vars(self.parse("lint")), {"command": "lint", "json": False})
        self.assertEqual(vars(self.parse("build", "--check")), {"command": "build", "check": True})
        self.assertEqual(vars(self.parse("status", "--json")), {"command": "status", "json": True})

    def test_print_defaults_and_options(self):
        self.assertEqual(vars(self.parse("print")), {"command": "print", "tier": "compact", "profile": "fullstack",
                                                     "reference_dir": ".doctrine", "agent": None})
        args = self.parse("print", "--tier", "micro", "--profile", "backend", "--reference-dir", "/ref")
        self.assertEqual((args.tier, args.profile, args.reference_dir), ("micro", "backend", "/ref"))

    def test_install_defaults(self):
        self.assertEqual(vars(self.parse("install", "--agent", "alpha")), {
            "command": "install", "agent": "alpha", "scope": "project", "path": None, "each_repo": False,
            "depth": 2, "tier": "compact", "profile": "fullstack", "no_reference": False, "with_examples": False,
            "local": False, "file": None, "comment": None, "base": None, "dry_run": False, "force": False, "json": False})

    def test_install_every_option(self):
        args = self.parse("install", "--agent", "alpha,bravo", "--scope", "workspace", "--path", "w", "--each-repo",
                          "--depth", "3", "--tier", "full", "--profile", "frontend", "--no-reference",
                          "--with-examples", "--local", "--file", "f.md", "--comment", "hash", "--base", "m",
                          "--dry-run", "--force", "--json")
        self.assertEqual(vars(args), {
            "command": "install", "agent": "alpha,bravo", "scope": "workspace", "path": "w", "each_repo": True,
            "depth": 3, "tier": "full", "profile": "frontend", "no_reference": True, "with_examples": True,
            "local": True, "file": "f.md", "comment": "hash", "base": "m", "dry_run": True, "force": True, "json": True})

    def test_scope_aliases(self):
        for given, scope in (("project", "project"), ("workspace", "workspace"), ("namespace", "workspace"),
                             ("global", "global"), ("user", "global")):
            self.assertEqual(self.parse("install", "--agent", "a", "--scope", given).scope, scope)
            self.assertEqual(self.parse("uninstall", "--agent", "a", "--scope", given).scope, scope)

    def test_uninstall_and_update(self):
        self.assertEqual(vars(self.parse("uninstall", "--agent", "custom", "--file", "p.md", "--dry-run")), {
            "command": "uninstall", "agent": "custom", "scope": "project", "path": None, "each_repo": False,
            "file": "p.md", "dry_run": True, "json": False})
        self.assertEqual(vars(self.parse("update")), {"command": "update", "agent": None, "dry_run": False, "json": False})
        self.assertEqual(self.parse("update", "--agent", "alpha", "--json").agent, "alpha")


class CommandLineTest(CliCase):
    def test_version_reads_the_package_named_by_the_environment(self):
        self.assertEqual(self.run_cli("version"), (0, "doctrine 0.9.0\n", ""))

    def test_version_of_the_real_package_comes_from_the_script_location(self):
        expected = (PKG / "VERSION").read_text(encoding="utf-8").strip()
        self.assertEqual(self.run_cli("version", pkg=None), (0, "doctrine %s\n" % expected, ""))

    def test_package_is_found_through_a_symlink_to_the_script(self):
        pkg = self.copy_fixture()
        (pkg / "bin").mkdir()
        shutil.copy(str(BIN), str(pkg / "bin" / "doctrine"))
        link = self.tmp / "doctrine-link"
        os.symlink(str(pkg / "bin" / "doctrine"), str(link))
        env = dict((key, value) for key, value in os.environ.items() if key != "DOCTRINE_PKG")
        done = subprocess.run([sys.executable, str(link), "version"], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual((done.returncode, done.stdout.decode("utf-8")), (0, "doctrine 0.9.0\n"))

    def test_script_is_executable_with_a_portable_shebang(self):
        self.assertTrue(os.stat(str(BIN)).st_mode & stat.S_IXUSR)
        self.assertEqual(BIN.read_text(encoding="utf-8").split("\n")[0], "#!/usr/bin/env python3")

    def test_lifecycle_commands_are_wired(self):
        self.assertIn("detected:", self.run_cli("detect")[1])
        self.assertIn("no installs", self.run_cli("status")[1])
        self.assertEqual(self.run_cli("update")[0], 0)
        (self.tmp / "AGENTS.md").write_text("# Notes\n", encoding="utf-8")
        code, out, err = self.run_cli("install", "--agent", "bravo", "--dry-run")
        self.assertEqual((code, err), (0, ""))
        self.assertIn("+++", out)
        self.assertIn("+<!-- doctrine:begin", out)
        self.assertIn("dry-run: nothing written", out)
        self.assertEqual((self.tmp / "AGENTS.md").read_text(encoding="utf-8"), "# Notes\n")

    def test_install_reports_unknown_agent(self):
        code, _, err = self.run_cli("install", "--agent", "nope")
        self.assertEqual(code, 1)
        self.assertIn("unknown agent nope", err)

    def test_usage_errors_exit_1(self):
        for argv in (["frobnicate"], ["print", "--tier", "huge"], ["print", "--profile", "mobile"],
                     ["install"], ["install", "--agent", "a", "--scope", "galaxy"],
                     ["install", "--agent", "a", "--depth", "deep"], ["uninstall"], ["lint", "--fast"]):
            with self.subTest(argv=argv):
                code, out, err = self.run_cli(*argv)
                self.assertEqual((code, out), (1, ""))
                self.assertIn("error:", err)
                self.assertIn("usage: doctrine", err)

    def test_no_command_prints_help_and_exits_1(self):
        code, out, err = self.run_cli()
        self.assertEqual((code, out), (1, ""))
        for command in ("version", "agents", "detect", "print", "lint", "build", "install", "uninstall", "update", "status"):
            self.assertIn(command, err)

    def test_help_exits_0(self):
        code, out, _ = self.run_cli("install", "--help")
        self.assertEqual(code, 0)
        self.assertIn("--each-repo", out)

    def test_package_root_that_is_not_a_directory(self):
        code, out, err = self.run_cli("version", pkg=self.tmp / "nowhere")
        self.assertEqual((code, out), (1, ""))
        self.assertIn("is not a directory (check DOCTRINE_PKG)", err)

    def test_package_without_core_documents_fails_clearly(self):
        pkg = self.tmp / "bare"
        (pkg / "agents").mkdir(parents=True)
        shutil.copy(str(FIXTURE / "VERSION"), str(pkg / "VERSION"))
        self.assertEqual(self.run_cli("version", pkg=pkg), (0, "doctrine 0.9.0\n", ""))
        code, out, err = self.run_cli("print", pkg=pkg)
        self.assertEqual((code, out), (1, ""))
        self.assertTrue(err.startswith("doctrine: error: the package is incomplete, missing: core/operating.md, "
                                       "core/principles.md, core/backend.md"), err)
        self.assertEqual(self.run_cli("agents", pkg=pkg), (1, "", "doctrine: error: agents/registry.json is missing\n"))
        self.assertEqual(self.run_cli("agents", "--markdown", pkg=pkg)[0], 1)
        code, out, err = self.run_cli("build", pkg=pkg)
        self.assertEqual(code, 1)
        self.assertIn("core/operating.md:1: required file is missing", out)
        self.assertIn("agents/registry.json:1: required file is missing", out)
        self.assertEqual(sorted(p.name for p in pkg.iterdir()), ["VERSION", "agents"])
        self.assertEqual(list((pkg / "agents").iterdir()), [])

    def test_package_without_a_version_fails_clearly(self):
        pkg = self.copy_fixture()
        (pkg / "VERSION").unlink()
        code, _, err = self.run_cli("version", pkg=pkg)
        self.assertEqual(code, 1)
        self.assertIn("VERSION is missing", err)
        code, _, err = self.run_cli("print", pkg=pkg)
        self.assertEqual(code, 1)
        self.assertIn("the package is incomplete, missing: VERSION", err)

    def test_print_refuses_a_catalog_with_grammar_problems(self):
        pkg = self.copy_fixture()
        path = pkg / "core" / "review.md"
        path.write_text(path.read_text(encoding="utf-8").replace("**Check.** Does the review", "Check: does the review"),
                        encoding="utf-8")
        code, out, err = self.run_cli("print", pkg=pkg)
        self.assertEqual((code, out), (1, ""))
        self.assertIn("the rule catalog has 1 problem(s), first: core/review.md:7: rule R-1 lacks **Check.**", err)

    def test_read_only_commands_leave_the_package_and_home_untouched(self):
        pkg = self.copy_fixture()
        before = (tree(pkg), tree(self.home))
        for argv in (["version"], ["lint"], ["lint", "--json"], ["print"], ["print", "--tier", "full"],
                     ["agents"], ["agents", "--json"], ["agents", "--markdown"], ["build", "--check"]):
            self.run_cli(*argv, pkg=pkg)
        self.assertEqual((tree(pkg), tree(self.home)), before)

    def test_source_stays_within_the_supported_python_subset(self):
        source = BIN.read_text(encoding="utf-8")
        self.assertIn("from __future__ import annotations", source)
        imported = set()
        for line in source.split("\n"):
            if line.startswith("import "):
                imported.add(line.split()[1])
            elif line.startswith("from "):
                imported.add(line.split()[1].split(".")[0])
        allowed = {"__future__", "argparse", "datetime", "difflib", "hashlib", "json", "os", "pathlib", "re",
                   "shutil", "subprocess", "sys", "tempfile", "typing"}
        self.assertEqual(imported - allowed, set())
        compile(source, str(BIN), "exec")


if __name__ == "__main__":
    unittest.main()
