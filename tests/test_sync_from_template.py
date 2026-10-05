"""Exercise the real sync script against a local, committed template fixture."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock


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
        boundary = b'done < "$MANIFEST"'
        for version in ("2.0.0", "2.0.1"):
            legacy = (ROOT / f"tests/fixtures/sync-from-template-v{version}.sh").read_bytes()
            self.assertEqual(self.script.read_bytes().index(boundary), legacy.index(boundary),
                             "preserve the legacy reader offset by adjusting header padding")
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

    def test_cross_filesystem_self_update_and_v201_upgrade(self):
        # The clone always lives in /tmp. Locally, the checkout's parent is on
        # another filesystem; CI selects /dev/shm explicitly.
        cross_root = os.environ.get("CROSS_FILESYSTEM_TEST_ROOT", str(ROOT.parent))
        with tempfile.TemporaryDirectory(dir=cross_root) as directory:
            if Path(directory).stat().st_dev == Path("/tmp").stat().st_dev:
                self.skipTest("set CROSS_FILESYSTEM_TEST_ROOT to another filesystem")
            target = Path(directory) / "adopted"
            shutil.copytree(self.repo, target)
            self.repo = target
            expected = self.populate()
            shutil.copyfile(ROOT / "tests/fixtures/sync-from-template-v2.0.1.sh", self.script)
            self.assertIn("SYNC-CHANGED=1", self.sync())
            self.assert_preserved(expected)
            template_script = self.scaffold / "sync-from-template.sh"
            template_script.write_text(
                "#!/bin/bash\n# Longer future prefix on a different filesystem.\n"
                + template_script.read_text().split("\n", 1)[1]
            )
            commit_fixture(self.template)
            with self.script.open("rb") as running_script:
                old_bytes = running_script.read()
                old_inode = os.fstat(running_script.fileno()).st_ino
                self.assertIn("SYNC-CHANGED=1", self.sync())
                running_script.seek(0)
                self.assertEqual(running_script.read(), old_bytes)
                self.assertNotEqual(self.script.stat().st_ino, old_inode)
            self.assertEqual(self.script.read_bytes(), template_script.read_bytes())
            self.assert_preserved(expected)
            self.assertIn("SYNC-CHANGED=0", self.sync())
            self.assertEqual(list(self.repo.rglob("*.template-sync.*")), [])

    def test_failed_replacement_keeps_original_and_removes_sibling(self):
        self.sync()
        original = self.script.read_bytes()
        template_script = self.scaffold / "sync-from-template.sh"
        template_script.write_bytes(original + b"\n# A new template release.\n")
        commit_fixture(self.template)
        for command in ("cp", "mv"):
            with self.subTest(command=command):
                binary = self.root / command
                binary.mkdir()
                shim = binary / command
                failure = 'printf partial > "$arg"; exit 73' if command == "cp" else "exit 73"
                shim.write_text(
                    "#!/bin/bash\n"
                    "for arg; do\n"
                    f"  case \"$arg\" in *.template-sync.*) {failure} ;; esac\n"
                    "done\n"
                    f"exec {shutil.which(command)} \"$@\"\n"
                )
                shim.chmod(0o755)
                with mock.patch.dict(os.environ, {"PATH": f"{binary}:{os.environ['PATH']}"}):
                    with self.assertRaises(subprocess.CalledProcessError):
                        self.sync()
                self.assertEqual(self.script.read_bytes(), original)
                self.assertEqual(list(self.repo.rglob("*.template-sync.*")), [])
        self.assertIn("SYNC-CHANGED=1", self.sync())
        self.assertEqual(self.script.read_bytes(), template_script.read_bytes())

    def test_failed_seed_copy_is_clean_and_retryable_for_legacy_consumers(self):
        binary = self.root / "fail-seed-bin"
        binary.mkdir()
        shim = binary / "cp"
        shim.write_text(
            "#!/bin/bash\n"
            "for arg; do\n"
            "  case \"$arg\" in */compatibility-watchlist.md.template-sync.*)\n"
            "    printf partial > \"$arg\"; exit 73 ;;\n"
            "  esac\n"
            "done\n"
            f"exec {shutil.which('cp')} \"$@\"\n"
        )
        shim.chmod(0o755)
        for version in ("current", "2.0.0", "2.0.1"):
            with self.subTest(version=version):
                for name in REGISTERS:
                    (self.repo / UPSTREAM / name).unlink(missing_ok=True)
                source = (self.scaffold / "sync-from-template.sh" if version == "current"
                          else ROOT / f"tests/fixtures/sync-from-template-v{version}.sh")
                shutil.copyfile(source, self.script)
                if version == "2.0.1":
                    # Its inode-replacing update continues the legacy reader.
                    # The versioned manifest defers seeds until the new script runs.
                    self.sync()
                    for name in REGISTERS:
                        self.assertFalse((self.repo / UPSTREAM / name).exists())
                with mock.patch.dict(os.environ, {"PATH": f"{binary}:{os.environ['PATH']}"}):
                    with self.assertRaises(subprocess.CalledProcessError):
                        self.sync()
                self.assertFalse((self.repo / UPSTREAM / REGISTERS[0]).exists())
                self.assertEqual(list(self.repo.rglob("*.template-sync.*")), [])
                self.assertIn("SYNC-CHANGED=1", self.sync())
                for name in REGISTERS:
                    self.assertEqual((self.repo / UPSTREAM / name).read_bytes(),
                                     (self.scaffold / UPSTREAM / name).read_bytes())
                self.assertIn("SYNC-CHANGED=0", self.sync())

    def test_concurrent_project_register_wins_over_seed(self):
        binary = self.root / "race-seed-bin"
        binary.mkdir()
        shim = binary / "cp"
        shim.write_text(
            "#!/bin/bash\n"
            f"{shutil.which('cp')} \"$@\" || exit $?\n"
            "for arg; do\n"
            "  case \"$arg\" in */compatibility-watchlist.md.template-sync.*)\n"
            "    printf project-owned > \"${arg%.template-sync.*}\" ;;\n"
            "  esac\n"
            "done\n"
        )
        shim.chmod(0o755)
        with mock.patch.dict(os.environ, {"PATH": f"{binary}:{os.environ['PATH']}"}):
            self.sync()
        self.assertEqual((self.repo / UPSTREAM / REGISTERS[0]).read_bytes(), b"project-owned")
        self.assertEqual(list(self.repo.rglob("*.template-sync.*")), [])
        self.assertIn("SYNC-CHANGED=0", self.sync())

    def test_unsupported_seed_publication_fails_clearly_without_partial_files(self):
        expected = self.populate()
        missing = UPSTREAM / REGISTERS[0]
        del expected[missing]
        (self.repo / missing).unlink()
        injection = self.root / "unsupported-link"
        injection.mkdir()
        for error_name in ("EOPNOTSUPP", "ENOSYS", "EPERM"):
            with self.subTest(error_name=error_name):
                (injection / "sitecustomize.py").write_text(
                    "import errno, os\n"
                    "def unsupported(*args, **kwargs):\n"
                    f"    raise OSError(errno.{error_name}, 'hard links unavailable')\n"
                    "os.link = unsupported\n"
                )
                with mock.patch.dict(os.environ, {
                    "PYTHONPATH": str(injection), "PYTHONDONTWRITEBYTECODE": "1"
                }):
                    for _ in range(2):
                        with self.assertRaises(subprocess.CalledProcessError) as error:
                            self.sync()
                        self.assertIn("unavailable or not permitted", error.exception.stderr)
                        self.assertIn("Initialize the missing register manually", error.exception.stderr)
                        self.assertNotIn("Traceback", error.exception.stderr)
                        self.assertFalse((self.repo / missing).exists())
                        self.assertEqual(list(self.repo.rglob("*.template-sync.*")), [])
                        self.assert_preserved(expected)
        self.assertIn("SYNC-CHANGED=1", self.sync())
        self.assertEqual((self.repo / missing).read_bytes(), (self.scaffold / missing).read_bytes())
        self.assertIn("SYNC-CHANGED=0", self.sync())

    def test_failed_agents_update_preserves_local_tail_and_mode(self):
        self.populate()
        self.sync()
        agents = self.repo / "AGENTS.md"
        original = agents.read_bytes()
        agents.chmod(0o600)
        template_agents = self.scaffold / "AGENTS.md"
        template_agents.write_text(template_agents.read_text().replace(
            "# Agent Instructions", "# Updated Agent Instructions", 1))
        commit_fixture(self.template)
        for version in ("current", "2.0.0", "2.0.1"):
            for command in ("cp", "mv"):
                with self.subTest(version=version, command=command):
                    source = (self.scaffold / "sync-from-template.sh" if version == "current"
                              else ROOT / f"tests/fixtures/sync-from-template-v{version}.sh")
                    shutil.copyfile(source, self.script)
                    if version == "2.0.1":
                        self.sync()
                        self.assertEqual(agents.read_bytes(), original)
                        self.assertEqual(agents.stat().st_mode & 0o777, 0o600)
                    binary = self.root / f"fail-agents-{version}-{command}"
                    binary.mkdir()
                    shim = binary / command
                    failure = 'printf partial > "$arg"; exit 73' if command == "cp" else "exit 73"
                    shim.write_text(
                        "#!/bin/bash\n"
                        "for arg; do\n"
                        f"  case \"$arg\" in */AGENTS.md.template-sync.*) {failure} ;; esac\n"
                        "done\n"
                        f"exec {shutil.which(command)} \"$@\"\n"
                    )
                    shim.chmod(0o755)
                    with mock.patch.dict(os.environ, {"PATH": f"{binary}:{os.environ['PATH']}"}):
                        with self.assertRaises(subprocess.CalledProcessError):
                            self.sync()
                    self.assertEqual(agents.read_bytes(), original)
                    self.assertEqual(agents.stat().st_mode & 0o777, 0o600)
                    self.assertEqual(list(self.repo.rglob("*.template-sync.*")), [])
        self.assertIn("SYNC-CHANGED=1", self.sync())
        self.assertEqual(agents.read_bytes(), original.replace(
            b"# Agent Instructions", b"# Updated Agent Instructions", 1))
        self.assertEqual(agents.stat().st_mode & 0o777, 0o600)
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
