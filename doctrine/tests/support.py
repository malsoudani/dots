"""Shared helpers for the doctrine test suite. Standard library only."""
import importlib.machinery
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent
PKG = TESTS.parent
BIN = PKG / "bin" / "doctrine"
FIXTURE = TESTS / "fixtures" / "pkg"
DOCTRINE_ENV = ("DOCTRINE_PKG", "DOCTRINE_PLATFORM", "XDG_CONFIG_HOME", "APPDATA")


def load_cli():
    """Import bin/doctrine as a module so its pure functions can be called directly."""
    name = "doctrine_cli"
    if name in sys.modules:
        return sys.modules[name]
    loader = importlib.machinery.SourceFileLoader(name, str(BIN))
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


cli = load_cli()


def fixture_texts():
    return cli.load_texts(FIXTURE, everything=True)


def fixture_model():
    return cli.build_model(cli.load_texts(FIXTURE))


def fixture_registry_data():
    return json.loads((FIXTURE / "agents" / "registry.json").read_text(encoding="utf-8"))


class CliCase(unittest.TestCase):
    """Runs the CLI as a subprocess with a temporary HOME and an explicit package root."""

    maxDiff = None

    def setUp(self):
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        self.tmp = Path(holder.name).resolve()
        self.home = self.tmp / "home"
        self.home.mkdir()

    def copy_fixture(self):
        target = self.tmp / "pkg"
        shutil.copytree(str(FIXTURE), str(target))
        return target

    def run_cli(self, *args, **options):
        """Return (exit code, stdout, stderr). Options: pkg (None = real package), env."""
        env = dict((key, value) for key, value in os.environ.items() if key not in DOCTRINE_ENV)
        env.update({"HOME": str(self.home), "XDG_CONFIG_HOME": str(self.home / ".config"),
                    "PYTHONDONTWRITEBYTECODE": "1"})
        pkg = options.get("pkg", FIXTURE)
        if pkg is not None:
            env["DOCTRINE_PKG"] = str(pkg)
        env.update(options.get("env") or {})
        done = subprocess.run([sys.executable, str(BIN)] + list(args), env=env, cwd=str(self.tmp),
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return done.returncode, done.stdout.decode("utf-8"), done.stderr.decode("utf-8")


def edit(path, old, new):
    """Replace exactly one occurrence of `old` in the file."""
    text = Path(path).read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise AssertionError("expected one occurrence of %r in %s, found %d" % (old, path, text.count(old)))
    Path(path).write_text(text.replace(old, new), encoding="utf-8")


def append(path, text):
    with open(str(path), "a", encoding="utf-8") as handle:
        handle.write(text)


def tree(root):
    """Snapshot a directory: relative path -> (size, mtime in ns)."""
    snapshot = {}
    for folder, _, files in os.walk(str(root)):
        for name in files:
            path = Path(folder) / name
            stat = path.stat()
            snapshot[path.relative_to(root).as_posix()] = (stat.st_size, stat.st_mtime_ns)
    return snapshot
