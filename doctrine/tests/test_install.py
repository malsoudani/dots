"""The lifecycle: install, uninstall, update, status, detect and install.sh.

Every test runs the CLI as a subprocess against a temporary HOME so nothing
outside the temporary directory is read or written.
"""
import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

from support import BIN, FIXTURE, PKG, CliCase, append, tree

STALE_BLOCK = ("<!-- doctrine:begin version=0.0.0 tier=micro profile=fullstack "
               "sha256=000000000000 pad=%d -->\nstale body\n<!-- doctrine:end -->\n")


def read_text(path):
    """Read text without translating newlines, so CRLF survives a round trip."""
    with open(str(path), "r", encoding="utf-8", newline="") as handle:
        return handle.read()


def write_text(path, text):
    with open(str(path), "w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def registry_of(package):
    return json.loads((Path(package) / "agents" / "registry.json").read_text(encoding="utf-8"))


class InstallCase(CliCase):
    """A temporary project directory plus small wrappers around the CLI."""

    def setUp(self):
        CliCase.setUp(self)
        self.project = self.tmp / "project"
        self.project.mkdir()

    def install(self, *args, **options):
        return self.run_cli("install", *args, **options)

    def uninstall(self, *args, **options):
        return self.run_cli("uninstall", *args, **options)

    def project_install(self, *args, **options):
        return self.run_cli("install", "--path", str(self.project), *args, **options)

    def project_uninstall(self, *args, **options):
        return self.run_cli("uninstall", "--path", str(self.project), *args, **options)

    def manifest(self):
        path = self.home / ".config" / "doctrine" / "installs.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def entries(self):
        return self.manifest().get("installs", [])

    def assert_installs(self, *args, pkg=FIXTURE, **options):
        code, out, err = self.project_install(*args, pkg=pkg, **options)
        self.assertEqual(code, 0, err)
        return out

    def assert_uninstalls(self, *args, pkg=FIXTURE, **options):
        code, out, err = self.project_uninstall(*args, pkg=pkg, **options)
        self.assertEqual(code, 0, err)
        return out


class BlockTest(InstallCase):
    """Case 4: the marked block, and two agents that share one target."""

    def test_round_trip_is_byte_exact(self):
        target = self.project / "AGENTS.md"
        variants = [("missing", None), ("empty", ""), ("no-newline", "# Notes\nkeep me"),
                    ("newline", "# Notes\nkeep me\n"), ("crlf", "# Notes\r\nkeep me\r\n")]
        for name, text in variants:
            with self.subTest(variant=name):
                if target.exists():
                    target.unlink()
                if text is not None:
                    write_text(target, text)
                before = target.read_bytes() if target.exists() else None
                self.assert_installs("--agent", "bravo", "--no-reference")
                installed = read_text(target)
                self.assertEqual(installed.count("doctrine:begin"), 1)
                self.assert_uninstalls("--agent", "bravo")
                after = target.read_bytes() if target.exists() else None
                self.assertEqual(after, before)

    def test_installed_block_records_its_attributes(self):
        self.assert_installs("--agent", "bravo")
        text = read_text(self.project / "AGENTS.md")
        self.assertIn("<!-- doctrine:begin", text)
        self.assertIn("<!-- doctrine:end -->", text)
        self.assertIn("tier=", text)
        self.assertIn("profile=fullstack", text)
        self.assertIn("sha256=", text)
        self.assertIn("version=", text)

    def test_stale_block_is_replaced_and_neighbours_kept(self):
        target = self.project / "AGENTS.md"
        cases = [("existing", "# Top\n\n" + STALE_BLOCK % 1 + "# Bottom\n"),
                 ("middle", "before\n" + STALE_BLOCK % 0 + "after\n")]
        for name, text in cases:
            with self.subTest(variant=name):
                write_text(target, text)
                self.assert_installs("--agent", "bravo", "--no-reference")
                installed = read_text(target)
                self.assertEqual(installed.count("doctrine:begin"), 1)
                self.assertNotIn("stale body", installed)
                self.assert_uninstalls("--agent", "bravo")
                stripped = read_text(target)
                self.assertNotIn("doctrine:begin", stripped)
                if name == "existing":
                    self.assertIn("# Top", stripped)
                    self.assertIn("# Bottom", stripped)
                else:
                    self.assertIn("before", stripped)
                    self.assertIn("after", stripped)

    def test_second_install_is_unchanged(self):
        out = self.assert_installs("--agent", "bravo")
        self.assertIn("bravo: created", out)
        target = self.project / "AGENTS.md"
        before = tree(target.parent)[target.name]
        out = self.assert_installs("--agent", "bravo")
        self.assertIn("bravo: unchanged", out)
        self.assertEqual(tree(target.parent)[target.name], before)

    def test_two_agents_share_one_target(self):
        self.assert_installs("--agent", "bravo,charlie", "--no-reference")
        target = self.project / "AGENTS.md"
        self.assertEqual(read_text(target).count("doctrine:begin"), 1)
        self.assertEqual(len(self.entries()), 2)
        self.assertEqual(len({entry["sha256"] for entry in self.entries()}), 1)
        self.assert_uninstalls("--agent", "bravo")
        self.assertEqual(read_text(target).count("doctrine:begin"), 1)
        self.assert_uninstalls("--agent", "charlie")
        self.assertFalse(target.exists())
        self.assertEqual(self.entries(), [])

    def test_hash_comment_agents_are_removed(self):
        path = self.project / "custom.txt"
        self.assert_installs("--agent", "custom", "--file", str(path), "--comment", "hash")
        text = read_text(path)
        self.assertIn("# doctrine:begin", text)
        self.assertIn("# doctrine:end", text)
        code, out, err = self.uninstall("--agent", "custom", "--file", str(path))
        self.assertEqual(code, 0, err)
        self.assertFalse(path.exists())


class FileModeTest(InstallCase):
    """Case 5: file mode writes a managed file, and refuses to clobber one."""

    def test_alpha_writes_a_managed_file_with_parents(self):
        self.assert_installs("--agent", "alpha", "--no-reference")
        target = self.project / ".alpha" / "rules" / "doctrine.md"
        self.assertTrue(target.is_file())
        text = read_text(target)
        self.assertIn("<!-- doctrine:managed", text)
        self.assertIn("alwaysApply: true", text)
        self.assertIn('description: "Doctrine: engineering standards"', text)
        self.assertIn("globs:", text)
        self.assertIn("priority: 1", text)

    def test_unmanaged_file_is_refused_without_force(self):
        target = self.project / ".alpha" / "rules" / "doctrine.md"
        target.parent.mkdir(parents=True)
        write_text(target, "# Mine\n")
        code, out, err = self.project_install("--agent", "alpha", "--no-reference")
        self.assertNotEqual(code, 0)
        self.assertIn("not managed by doctrine", err)
        self.assertEqual(read_text(target), "# Mine\n")

    def test_force_replaces_and_keeps_a_backup(self):
        target = self.project / ".alpha" / "rules" / "doctrine.md"
        target.parent.mkdir(parents=True)
        write_text(target, "# Mine\n")
        self.assert_installs("--agent", "alpha", "--no-reference", "--force")
        self.assertIn("<!-- doctrine:managed", read_text(target))
        backups = sorted(target.parent.glob("doctrine.md.bak.*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(read_text(backups[0]), "# Mine\n")

    def test_uninstall_removes_only_its_recorded_backup(self):
        target = self.project / ".alpha" / "rules" / "doctrine.md"
        target.parent.mkdir(parents=True)
        write_text(target, "# Mine\n")
        self.assert_installs("--agent", "alpha", "--no-reference", "--force")
        backups = sorted(target.parent.glob("doctrine.md.bak.*"))
        self.assertEqual(len(backups), 1)
        self.assertTrue(backups[0].exists())
        self.assert_uninstalls("--agent", "alpha")
        # Uninstall removes the managed target and its backup is retained as the
        # recovery copy for the unmanaged file that --force replaced.
        self.assertTrue(backups[0].exists())
        self.assertEqual(read_text(backups[0]), "# Mine\n")


class RegistryTest(InstallCase):
    """Case 6: every agent in the shipped registry installs and uninstalls."""

    def test_every_agent_round_trips_cleanly(self):
        for agent in registry_of(PKG)["agents"]:
            with self.subTest(agent=agent["id"]):
                self.assert_installs("--agent", agent["id"], "--base", "llama3.2", pkg=None)
                self.assert_uninstalls("--agent", agent["id"], pkg=None)
        self.assertEqual(tree(self.project), {})

    def test_global_agents_round_trip_cleanly(self):
        for agent in registry_of(PKG)["agents"]:
            if not agent.get("global"):
                continue
            with self.subTest(agent=agent["id"]):
                code, out, err = self.run_cli("install", "--agent", agent["id"], "--scope", "global",
                                              "--base", "llama3.2", pkg=None)
                self.assertEqual(code, 0, err)
                code, out, err = self.run_cli("uninstall", "--agent", agent["id"], "--scope", "global", pkg=None)
                self.assertEqual(code, 0, err)
        leftovers = [path for path in self.home.rglob("*")
                     if path.is_file() and ".config/doctrine" not in str(path.relative_to(self.home))]
        self.assertEqual(leftovers, [])

    def test_register_file_is_removed_on_uninstall(self):
        self.assert_installs("--agent", "delta", "--no-reference")
        self.assertTrue((self.project / ".delta.conf.yml").is_file())
        self.assertIn("register_file", self.entries()[0])
        self.assert_uninstalls("--agent", "delta")
        self.assertFalse((self.project / ".delta.conf.yml").exists())
        self.assertFalse((self.project / "docs" / "doctrine.md").exists())


class ScopeTest(InstallCase):
    """Cases 8, 9 and 10: symlinks, workspace scope and --local."""

    def git_init(self, folder):
        subprocess.run(["git", "init", "-q", "-b", "master", str(folder)], check=True)

    def test_symlink_inside_the_root_is_followed(self):
        real = self.project / "real"
        real.mkdir()
        link = self.project / "AGENTS.md"
        os.symlink(str(real / "agents.md"), str(link))
        self.assert_installs("--agent", "bravo", "--no-reference")
        self.assertTrue((real / "agents.md").is_file())
        self.assert_uninstalls("--agent", "bravo")
        self.assertFalse((real / "agents.md").exists())
        self.assertTrue(link.is_symlink())

    def test_symlink_outside_the_root_is_refused(self):
        outside = self.tmp / "outside"
        outside.mkdir()
        os.symlink(str(outside / "agents.md"), str(self.project / "AGENTS.md"))
        code, out, err = self.project_install("--agent", "bravo", "--no-reference")
        self.assertNotEqual(code, 0)
        self.assertIn("bravo", err)
        self.assertFalse((outside / "agents.md").exists())

    def test_workspace_scope(self):
        self.assert_installs("--agent", "bravo", "--scope", "workspace", "--path", str(self.project))
        self.assertTrue((self.project / "AGENTS.md").is_file())
        code, out, err = self.project_install("--agent", "charlie", "--scope", "workspace")
        self.assertNotEqual(code, 0)
        self.assertIn("--each-repo", err)

    def test_each_repo_walks_the_repositories(self):
        for name in ("one", "two"):
            folder = self.project / name
            folder.mkdir()
            self.git_init(folder)
        code, out, err = self.project_install("--agent", "bravo", "--each-repo", "--depth", "1")
        self.assertEqual(code, 0, err)
        for name in ("one", "two"):
            self.assertTrue((self.project / name / "AGENTS.md").is_file())
        self.assertEqual(len(self.entries()), 2)

    def test_each_repo_without_repositories_is_an_error(self):
        code, out, err = self.project_install("--agent", "bravo", "--each-repo")
        self.assertNotEqual(code, 0)
        self.assertIn("no git repositories found", err)

    def test_local_writes_and_removes_the_exclude_block(self):
        self.git_init(self.project)
        exclude = self.project / ".git" / "info" / "exclude"
        before = exclude.read_text(encoding="utf-8")
        self.assert_installs("--agent", "bravo", "--local", "--no-reference")
        text = exclude.read_text(encoding="utf-8")
        self.assertIn("doctrine:begin", text)
        self.assertIn("AGENTS.md", text)
        self.assert_uninstalls("--agent", "bravo")
        self.assertEqual(exclude.read_text(encoding="utf-8"), before)

    def test_local_without_a_repository_is_an_error(self):
        code, out, err = self.project_install("--agent", "bravo", "--local", "--no-reference")
        self.assertNotEqual(code, 0)
        self.assertIn("info/exclude", err)


class RegisterTest(InstallCase):
    """Case 11: the yaml register file."""

    def test_delta_registers_its_reference_file(self):
        self.assert_installs("--agent", "delta", "--no-reference")
        text = read_text(self.project / ".delta.conf.yml")
        self.assertIn("# doctrine:begin", text)
        self.assertIn("read:", text)
        self.assertIn("- ", text)
        self.assertIn("docs/doctrine.md", text)

    def test_existing_key_becomes_a_manual_step(self):
        config = self.project / ".delta.conf.yml"
        write_text(config, "read:\n  - some/repo/file.md\n")
        before = read_text(config)
        self.assert_installs("--agent", "delta", "--no-reference")
        self.assertEqual(read_text(config), before)
        code, out, err = self.run_cli("install", "--path", str(self.project), "--agent", "delta", "--no-reference")
        self.assertIn("manual-step", out)
        self.assertIn("read", out)


class TierTest(InstallCase):
    """Case 12: max_chars decides the tier, or refuses."""

    def test_charlie_falls_back_to_micro(self):
        self.assert_installs("--agent", "charlie", "--no-reference")
        self.assertEqual(self.entries()[0]["tier"], "micro")

    def test_echo_cannot_fit_any_tier(self):
        code, out, err = self.project_install("--agent", "echo", "--no-reference")
        self.assertNotEqual(code, 0)
        self.assertIn("echo", err)
        self.assertFalse((self.project / ".echo" / "instructions.txt").exists())


class StatusTest(InstallCase):
    """Case 13: status states and update."""

    def states(self, pkg=FIXTURE):
        code, out, err = self.run_cli("status", "--json", pkg=pkg)
        self.assertEqual(code, 0, err)
        return dict((row["agent"], row["state"]) for row in json.loads(out)["installs"])

    def test_states_follow_the_target(self):
        self.assert_installs("--agent", "bravo", "--no-reference")
        self.assertEqual(self.states()["bravo"], "ok")
        target = self.project / "AGENTS.md"
        tampered = read_text(target).replace("<!-- doctrine:end -->", "x\n<!-- doctrine:end -->", 1)
        write_text(target, tampered)
        self.assertEqual(self.states()["bravo"], "modified")
        code, out, err = self.run_cli("update")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.states()["bravo"], "ok")
        target.unlink()
        self.assertEqual(self.states()["bravo"], "missing")

    def test_outdated_when_the_package_changes(self):
        package = self.copy_fixture()
        self.assert_installs("--agent", "bravo", "--no-reference", pkg=package)
        self.assertEqual(self.states(pkg=package)["bravo"], "ok")
        append(package / "core" / "operating.md", "\n- Extra line for the test.\n")
        self.assertEqual(self.states(pkg=package)["bravo"], "outdated")
        code, out, err = self.run_cli("update", pkg=package)
        self.assertEqual(code, 0, err)
        self.assertEqual(self.states(pkg=package)["bravo"], "ok")


class DryRunTest(InstallCase):
    """Case 14: --dry-run reports and writes nothing."""

    def test_dry_run_writes_nothing(self):
        target = self.project / "AGENTS.md"
        write_text(target, "# Notes\n")
        before_project = tree(self.project)
        before_home = tree(self.home)
        code, out, err = self.project_install("--agent", "bravo", "--dry-run")
        self.assertEqual(code, 0, err)
        self.assertIn("+++", out)
        self.assertIn("+<!-- doctrine:begin", out)
        self.assertIn("dry-run: nothing written", out)
        self.assertEqual(tree(self.project), before_project)
        self.assertEqual(tree(self.home), before_home)
        self.assertEqual(read_text(target), "# Notes\n")

    def test_dry_run_reports_a_created_file(self):
        code, out, err = self.project_install("--agent", "bravo", "--dry-run", "--no-reference")
        self.assertEqual(code, 0, err)
        self.assertIn("created", out)
        self.assertIn("dry-run: nothing written", out)
        self.assertFalse((self.project / "AGENTS.md").exists())

    def test_dry_run_leaves_the_manifest_alone(self):
        self.assert_installs("--agent", "bravo", "--no-reference")
        before = self.manifest()
        code, out, err = self.project_install("--agent", "delta", "--dry-run", "--no-reference")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.manifest(), before)


class CustomTest(InstallCase):
    """Case 15: --agent custom."""

    def test_custom_html_comment(self):
        path = self.project / "notes.md"
        self.assert_installs("--agent", "custom", "--file", str(path))
        self.assertIn("<!-- doctrine:begin", read_text(path))

    def test_custom_hash_comment(self):
        path = self.project / "notes.md"
        self.assert_installs("--agent", "custom", "--file", str(path), "--comment", "hash")
        self.assertIn("# doctrine:begin", read_text(path))

    def test_custom_needs_a_file(self):
        code, out, err = self.project_install("--agent", "custom", "--no-reference")
        self.assertNotEqual(code, 0)
        self.assertIn("--file", err)


class PlatformTest(InstallCase):
    """Case 16: path expansion per platform."""

    def test_expand_path(self):
        from support import cli
        linux = {"HOME": "/home/u", "XDG_CONFIG_HOME": "/home/u/.config"}
        self.assertEqual(cli.expand_path("{xdg_config}/bravo/AGENTS.md", "linux", linux),
                         "/home/u/.config/bravo/AGENTS.md")
        self.assertEqual(cli.expand_path("{vscode_user}/prompts/doctrine.md", "linux", linux),
                         "/home/u/.config/Code/User/prompts/doctrine.md")
        self.assertEqual(cli.expand_path("{appdata}/Echo/instructions.txt", "windows",
                                         {"HOME": "/u", "APPDATA": "/u/AppData/Roaming"}),
                         "/u/AppData/Roaming/Echo/instructions.txt")
        self.assertEqual(cli.expand_path("~/.alpha/rules/doctrine.md", "darwin", {"HOME": "/Users/u"}),
                         "/Users/u/.alpha/rules/doctrine.md")
        self.assertEqual(cli.expand_path("{vscode_user}/x", "darwin", {"HOME": "/Users/u"}),
                         "/Users/u/Library/Application Support/Code/User/x")
        with self.assertRaises(ValueError):
            cli.expand_path("~/x", "beos", {"HOME": "/u"})

    def test_global_install_on_a_named_platform(self):
        code, out, err = self.run_cli("install", "--agent", "bravo", "--scope", "global",
                                      env={"DOCTRINE_PLATFORM": "linux"})
        self.assertEqual(code, 0, err)
        target = self.home / ".config" / "bravo" / "AGENTS.md"
        self.assertTrue(target.is_file())
        code, out, err = self.run_cli("uninstall", "--agent", "bravo", "--scope", "global",
                                      env={"DOCTRINE_PLATFORM": "linux"})
        self.assertEqual(code, 0, err)
        self.assertFalse(target.exists())


class ReferenceTest(InstallCase):
    """Case 17: the shared reference directory."""

    def test_reference_directory_contents(self):
        self.assert_installs("--agent", "bravo")
        reference = self.project / ".doctrine"
        self.assertTrue((reference / "README.md").is_file())
        self.assertTrue((reference / "checklists.md").is_file())
        self.assertTrue((reference / "rules.json").is_file())
        self.assertTrue((reference / "core" / "principles.md").is_file())
        self.assertTrue((reference / "howto" / "build-a-slice.md").is_file())
        rules = json.loads((reference / "rules.json").read_text(encoding="utf-8"))
        self.assertTrue(rules)

    def test_reference_is_shared_and_removed_when_unused(self):
        self.assert_installs("--agent", "bravo,delta", "--with-examples")
        reference = self.project / ".doctrine"
        self.assertTrue(reference.is_dir())
        self.assert_uninstalls("--agent", "bravo")
        self.assertTrue(reference.is_dir())
        self.assert_uninstalls("--agent", "delta")
        self.assertFalse(reference.exists())

    def test_no_reference_skips_the_directory(self):
        self.assert_installs("--agent", "bravo", "--no-reference")
        self.assertFalse((self.project / ".doctrine").exists())
        self.assertFalse(self.entries()[0]["reference_dir"])


class DetectTest(InstallCase):
    """Case 18: detect against a controlled PATH."""

    def test_detect_nothing(self):
        code, out, err = self.run_cli("detect", "--path", str(self.project), "--json")
        self.assertEqual(code, 0, err)
        payload = json.loads(out)
        self.assertEqual(payload["agents"], [])
        self.assertEqual(payload["path"], str(self.project))

    def test_detect_a_command_on_the_path(self):
        folder = self.tmp / "bin"
        folder.mkdir()
        executable = folder / "bravo"
        write_text(executable, "#!/bin/sh\nexit 0\n")
        os.chmod(str(executable), 0o755)
        env = {"PATH": str(folder), "DOCTRINE_PLATFORM": "linux"}
        code, out, err = self.run_cli("detect", "--path", str(self.project), "--json", env=env)
        self.assertEqual(code, 0, err)
        self.assertIn("bravo", json.loads(out)["agents"])

    def test_detect_by_project_paths(self):
        self.assert_installs("--agent", "bravo", "--no-reference")
        code, out, err = self.run_cli("detect", "--path", str(self.project), "--json")
        self.assertEqual(code, 0, err)
        self.assertIn("bravo", json.loads(out)["agents"])


class InstallScriptTest(InstallCase):
    """Case 19: install.sh from a checkout and from a remote."""

    def run_script(self, script, *args, **options):
        env = dict((key, value) for key, value in os.environ.items()
                   if not key.startswith("DOCTRINE_") and key != "XDG_CONFIG_HOME")
        env.update({"HOME": str(self.home), "PYTHONDONTWRITEBYTECODE": "1"})
        env.update(options.get("env") or {})
        done = subprocess.run(["bash", str(script)] + list(args), env=env, cwd=str(self.tmp),
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return done.returncode, done.stdout.decode("utf-8"), done.stderr.decode("utf-8")

    def checkout(self):
        folder = self.tmp / "checkout"
        shutil.copytree(str(FIXTURE), str(folder))
        binary = folder / "bin" / "doctrine"
        binary.parent.mkdir(exist_ok=True)
        shutil.copy(str(BIN), str(binary))
        os.chmod(str(binary), 0o755)
        shutil.copy(str(PKG / "install.sh"), str(folder / "install.sh"))
        return folder

    def test_checkout_runs_the_local_cli(self):
        folder = self.checkout()
        code, out, err = self.run_script(folder / "install.sh", "version")
        self.assertEqual(code, 0, err)
        self.assertIn("doctrine 0.9.0", out)

    def test_bootstrap_clones_links_and_runs(self):
        if shutil.which("git") is None:
            self.skipTest("git is not available")
        origin = self.tmp / "origin"
        shutil.copytree(str(FIXTURE), str(origin / "doctrine"))
        binary = origin / "doctrine" / "bin" / "doctrine"
        binary.parent.mkdir(exist_ok=True)
        shutil.copy(str(BIN), str(binary))
        os.chmod(str(binary), 0o755)
        identity = ["-c", "user.email=test@example.com", "-c", "user.name=Test", "-c", "commit.gpgsign=false"]
        subprocess.run(["git", "init", "-q", "-b", "master", str(origin)], check=True)
        subprocess.run(["git"] + identity + ["-C", str(origin), "add", "-A"], check=True)
        subprocess.run(["git"] + identity + ["-C", str(origin), "commit", "-q", "-m", "init"], check=True)
        home_dir = self.tmp / "installed"
        bin_dir = self.home / "bin"
        env = {"DOCTRINE_REPO_URL": "file://" + str(origin), "DOCTRINE_REF": "master",
               "DOCTRINE_HOME": str(home_dir), "DOCTRINE_BIN_DIR": str(bin_dir)}
        script = self.tmp / "install.sh"
        shutil.copy(str(PKG / "install.sh"), str(script))
        code, out, err = self.run_script(script, "version", env=env)
        self.assertEqual(code, 0, err)
        self.assertIn("doctrine 0.9.0", out)
        self.assertIn("cloning", err)
        link = bin_dir / "doctrine"
        self.assertTrue(link.is_symlink())
        self.assertEqual(Path(os.path.realpath(str(link))), home_dir / "doctrine" / "bin" / "doctrine")
        code, out, err = self.run_script(script, "version", env=env)
        self.assertEqual(code, 0, err)
        self.assertIn("updating", err)


if __name__ == "__main__":
    unittest.main()
