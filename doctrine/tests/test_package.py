"""Case 20: real-package checks.

Unlike the other suites, these run against the real package ($PKG), not the
fixture. They depend on the content tracks having landed: a failure here is a
real failure, not a reason to weaken the test.
"""
import json
import unittest

from support import PKG, CliCase


class RealPackageTest(CliCase):
    def test_lint_passes_on_the_real_package(self):
        code, out, err = self.run_cli("lint", pkg=PKG)
        self.assertEqual(code, 0, "lint reported problems:\n" + out + err)
        self.assertEqual(err, "")
        self.assertIn("lint: ok", out)

    def test_build_check_reports_no_stale_outputs(self):
        code, out, err = self.run_cli("build", "--check", pkg=PKG)
        self.assertEqual(code, 0, "build --check found stale outputs:\n" + out)
        self.assertEqual(err, "")

    def test_every_registry_agent_cites_a_source(self):
        data = json.loads((PKG / "agents" / "registry.json").read_text(encoding="utf-8"))
        self.assertTrue(data["agents"], "the registry has no agents")
        for agent in data["agents"]:
            sources = agent.get("sources") or []
            self.assertTrue(sources, "%s has no sources" % agent["id"])
            for source in sources:
                self.assertTrue(source["url"].startswith("https://"),
                                "%s has a non-https source" % agent["id"])
                self.assertTrue(source["quote"].strip(),
                                "%s has an empty source quote" % agent["id"])


if __name__ == "__main__":
    unittest.main()