"""Exercise the real sync script against a local, committed template fixture."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = Path("records/upstream-intake")
REGISTERS = (
    "compatibility-watchlist.md",
    "decision-carry-forward.md",
    "known-local-overrides.md",
)
GUIDES = (
    "README.md",
    "intake-method.md",
    "weekly-upstream-intake-template.md",
    "operator-weekly-brief-template.md",
    "reports/README.md",
    "reports/internal-records/README.md",
    "reports/operator-briefs/README.md",
)


def run(*args, cwd, **kwargs):
    return subprocess.run(
        args, cwd=cwd, check=True, text=True, capture_output=True, **kwargs
    ).stdout


def commit_fixture(repo):
    run("git", "add", "-A", cwd=repo)
    run(
        "git", "-c", "user.name=Template Test", "-c",
        "user.email=template-test@example.invalid", "commit", "-qm",
        "bootstrap: isolated sync test fixture", cwd=repo,
    )


class TemplateSyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.template = self.root / "template"
        shutil.copytree(ROOT / "scaffold", self.template / "scaffold")
        run("git", "init", "-q", cwd=self.template)
        commit_fixture(self.template)
        self.scaffold = self.template / "scaffold"
        self.repo = self.root / "adopted"
        self.repo.mkdir()
        run("git", "init", "-q", cwd=self.repo)
        # Existing adopted projects already have these wholly managed trees.
        # Leave them byte-identical: these tests isolate mixed-ownership files
        # and do not require rsync for unrelated skills/hook directory updates.
        for directory in ("skills", ".githooks"):
            shutil.copytree(self.scaffold / directory, self.repo / directory)
        shutil.copyfile(self.scaffold / "AGENTS.md", self.repo / "AGENTS.md")
        (self.repo / "records").mkdir()
        shutil.copyfile(self.scaffold / "records/REPO.md", self.repo / "records/REPO.md")
        (self.repo / "scripts").mkdir()
        shutil.copyfile(self.scaffold / "sync-from-template.sh", self.script)

    @property
    def script(self):
        return self.repo / "scripts/sync-from-template.sh"

    def sync(self):
        output = run(
            "bash", str(self.script), cwd=self.repo,
            env={**os.environ, "TEMPLATE_URL": self.template.as_uri()},
        )
        self.assertEqual(output.count("SYNC-CHANGED="), 1)
        self.assertEqual(output.count("SYNC-VERSION="), 1)
        for name in GUIDES:
            self.assertEqual((self.repo / UPSTREAM / name).stat().st_mode & 0o777, 0o644)
        self.assertTrue(os.access(self.repo / "scripts/new-commit-message.sh", os.X_OK))
        return output

    def write(self, path, data):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    def populate(self):
        expected = {UPSTREAM / name: f"project decisions: {name}\n".encode()
                    for name in REGISTERS}
        expected.update({
            UPSTREAM / "reports/internal-records/UPS-20261004-001-fad-v033.md":
                b"accepted project evidence\n",
            UPSTREAM / "reports/operator-briefs/UPS-20261004-001-fad-v033-operator-brief.md":
                b"operator decision remains deferred\n",
            UPSTREAM / "reports/attachments/nested/evidence.bin": b"\x00\xff\n",
            UPSTREAM / "local-notes.md": b"additional project-owned file\n",
            Path("records/SPEC.md"): b"project specification\n",
        })
        for path, data in expected.items():
            self.write(path, data)
        with (self.repo / "AGENTS.md").open("a") as stream:
            stream.write("\n\n## Repo-Specific Rules\nKeep local instructions.\n")
        expected[Path("AGENTS.md")] = (self.repo / "AGENTS.md").read_bytes()
        return expected

    def assert_preserved(self, expected):
        for path, data in expected.items():
            with self.subTest(path=path):
                self.assertEqual((self.repo / path).read_bytes(), data)

    def test_populated_records_survive_repeated_sync_and_guide_updates(self):
        expected = self.populate()
        self.assertIn("SYNC-CHANGED=1", self.sync())
        self.assert_preserved(expected)
        for name in GUIDES:
            with (self.scaffold / UPSTREAM / name).open("ab") as stream:
                stream.write(b"\nUpdated template guidance.\n")
        for name in REGISTERS:
            (self.scaffold / UPSTREAM / name).write_bytes(b"new seed must not replace records\n")
        commit_fixture(self.template)
        self.assertIn("SYNC-CHANGED=1", self.sync())
        for name in GUIDES:
            self.assertEqual((self.repo / UPSTREAM / name).read_bytes(),
                             (self.scaffold / UPSTREAM / name).read_bytes())
        self.assert_preserved(expected)
        self.assertIn("SYNC-CHANGED=0", self.sync())
        self.assert_preserved(expected)

    def test_clean_project_gets_seeds_and_second_sync_is_noop(self):
        self.assertIn("SYNC-CHANGED=1", self.sync())
        for name in (*REGISTERS, *GUIDES):
            self.assertEqual((self.repo / UPSTREAM / name).read_bytes(),
                             (self.scaffold / UPSTREAM / name).read_bytes())
        self.assertIn("SYNC-CHANGED=0", self.sync())

    def test_only_missing_register_is_seeded(self):
        self.write(UPSTREAM / REGISTERS[0], b"")
        link = self.repo / UPSTREAM / REGISTERS[1]
        link.symlink_to("missing-project-owned-target")
        self.assertIn("SYNC-CHANGED=1", self.sync())
        self.assertEqual((self.repo / UPSTREAM / REGISTERS[0]).read_bytes(), b"")
        self.assertTrue(link.is_symlink())
        self.assertFalse(link.exists())
        self.assertEqual((self.repo / UPSTREAM / REGISTERS[2]).read_bytes(),
                         (self.scaffold / UPSTREAM / REGISTERS[2]).read_bytes())
        self.assertIn("SYNC-CHANGED=0", self.sync())

    def test_executable_guide_mode_is_repaired_without_content_changes(self):
        self.sync()
        guide = self.repo / UPSTREAM / "intake-method.md"
        original = guide.read_bytes()
        guide.chmod(0o755)
        self.assertIn("SYNC-CHANGED=1", self.sync())
        self.assertEqual(guide.read_bytes(), original)
        self.assertEqual(guide.stat().st_mode & 0o777, 0o644)
        self.assertIn("SYNC-CHANGED=0", self.sync())

    def test_project_owned_modes_are_preserved(self):
        expected = self.populate()
        paths = (UPSTREAM / REGISTERS[0], UPSTREAM / "local-notes.md")
        for path in paths:
            (self.repo / path).chmod(0o750)
        self.sync()
        self.assertIn("SYNC-CHANGED=0", self.sync())
        self.assert_preserved(expected)
        for path in paths:
            self.assertEqual((self.repo / path).stat().st_mode & 0o777, 0o750)

    def test_old_consumer_can_upgrade_without_erasing_records(self):
        expected = self.populate()
        shutil.copyfile(ROOT / "tests/fixtures/sync-from-template-v2.0.0.sh", self.script)
        self.assertIn("SYNC-CHANGED=1", self.sync())
        self.assert_preserved(expected)
        self.assertEqual(self.script.read_bytes(),
                         (self.scaffold / "sync-from-template.sh").read_bytes())
        self.assertIn("SYNC-CHANGED=0", self.sync())
        self.assert_preserved(expected)

    def test_old_consumer_seeds_clean_project_on_first_upgrade(self):
        shutil.copyfile(ROOT / "tests/fixtures/sync-from-template-v2.0.0.sh", self.script)
        self.assertIn("SYNC-CHANGED=1", self.sync())
        for name in REGISTERS:
            self.assertEqual((self.repo / UPSTREAM / name).read_bytes(),
                             (self.scaffold / UPSTREAM / name).read_bytes())
        self.assertIn("SYNC-CHANGED=0", self.sync())

    def test_installed_script_survives_later_length_changing_self_update(self):
        expected = self.populate()
        self.sync()
        template_script = self.scaffold / "sync-from-template.sh"
        template_script.write_text(
            "#!/bin/bash\n# A future release changes the script prefix length.\n"
            + template_script.read_text().split("\n", 1)[1]
        )
        commit_fixture(self.template)
        self.assertIn("SYNC-CHANGED=1", self.sync())
        self.assertEqual(self.script.read_bytes(), template_script.read_bytes())
        self.assert_preserved(expected)
        self.assertIn("SYNC-CHANGED=0", self.sync())

    @unittest.skipUnless(os.environ.get("ADOPTED_REPO_UNDER_TEST"),
                         "set ADOPTED_REPO_UNDER_TEST for a real-project recovery check")
    def test_adopted_checkout_records_survive_exactly(self):
        adopted = Path(os.environ["ADOPTED_REPO_UNDER_TEST"])
        shutil.copytree(adopted / UPSTREAM, self.repo / UPSTREAM, dirs_exist_ok=True)
        shutil.copyfile(adopted / "scripts/sync-from-template.sh", self.script)
        expected = {
            path.relative_to(adopted): path.read_bytes()
            for path in (adopted / UPSTREAM).rglob("*")
            if path.is_file() and path.relative_to(adopted / UPSTREAM).as_posix() not in GUIDES
        }
        self.assertTrue(expected, "adopted checkout must contain project-owned records")
        self.sync()
        self.assert_preserved(expected)
        self.assertIn("SYNC-CHANGED=0", self.sync())
        self.assert_preserved(expected)


if __name__ == "__main__":
    unittest.main()
