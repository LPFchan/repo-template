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
        # Existing adopted projects already have these baseline files.
        # Keep the wholly managed hooks identical so mixed-ownership tests do
        # not require rsync for unrelated hook directory updates.
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

    def checkpoint(self):
        # These fixtures model committed adopted state and caller-owned commits
        # between syncs. Dirty-data regressions explicitly disable this step.
        if run("git", "status", "--porcelain", "--untracked-files=all", cwd=self.repo):
            commit_fixture(self.repo)

    def sync(self, checkpoint=True):
        if checkpoint:
            self.checkpoint()
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

    def project_snapshot(self):
        snapshot = {}
        for path in self.repo.rglob("*"):
            relative = path.relative_to(self.repo)
            if ".git" in relative.parts:
                continue
            mode = path.lstat().st_mode
            if path.is_symlink():
                snapshot[relative] = (mode, os.readlink(path))
            elif path.is_file():
                snapshot[relative] = (mode, path.read_bytes())
            else:
                snapshot[relative] = (mode, None)
        return snapshot

    def assert_mode_only_diff(self, expected):
        self.assertEqual(
            set(run("git", "diff", "--summary", cwd=self.repo).splitlines()),
            {f" mode change {0o100000 | old:o} => {0o100000 | new:o} {path}"
             for path, (old, new) in expected.items()},
        )
        self.assertEqual(
            set(run("git", "diff", "--numstat", cwd=self.repo).splitlines()),
            {f"0\t0\t{path}" for path in expected},
        )
        self.assertEqual(run("git", "diff", "--cached", "--name-only", cwd=self.repo), "")

    def assert_mode_sync_noop_after_commit(self):
        self.checkpoint()
        output = self.sync(checkpoint=False)
        self.assertIn("SYNC-CHANGED=0", output)
        self.assertIn("SYNC-VERSION=2.0.7", output)
        self.assertEqual(run("git", "status", "--porcelain", cwd=self.repo), "")

    def test_identical_shell_scripts_gain_execute_mode_from_nonexecutable_sources(self):
        names = ("sync-from-template.sh", "new-commit-message.sh",
                 "check-commit-standards.sh", "install-hooks.sh")
        for name in names:
            (self.scaffold / name).chmod(0o644)
        if run("git", "status", "--porcelain", cwd=self.template):
            commit_fixture(self.template)
        self.sync()
        for name in names:
            target = self.repo / "scripts" / name
            self.assertEqual(target.read_bytes(), (self.scaffold / name).read_bytes())
            target.chmod(0o644)
        self.checkpoint()

        output = self.sync(checkpoint=False)
        for name in names:
            with self.subTest(script=name):
                target = self.repo / "scripts" / name
                self.assertEqual((self.scaffold / name).stat().st_mode & 0o777, 0o644)
                self.assertEqual(target.stat().st_mode & 0o777, 0o755)
                self.assertEqual(target.read_bytes(), (self.scaffold / name).read_bytes())
        self.assert_mode_only_diff({f"scripts/{name}": (0o644, 0o755) for name in names})
        self.assertIn("SYNC-CHANGED=1", output)
        self.assertIn("SYNC-VERSION=2.0.7", output)
        self.assert_mode_sync_noop_after_commit()

    def test_failed_mode_only_shell_repair_preserves_file_and_version(self):
        self.sync()
        target = self.repo / "scripts/new-commit-message.sh"
        original = target.read_bytes()
        self.assertEqual(original, (self.scaffold / "new-commit-message.sh").read_bytes())
        target.chmod(0o644)
        policy = self.repo / "records/REPO.md"
        policy.write_bytes(policy.read_bytes().replace(
            b"**Template version: 2.0.7**", b"**Template version: 2.0.0**", 1))
        self.checkpoint()
        before = self.project_snapshot()
        original_policy = policy.read_bytes()
        binary = self.root / "fail-mode-chmod"
        binary.mkdir()
        shim = binary / "chmod"
        shim.write_text(
            "#!/bin/bash\nfor arg; do\n"
            "  case \"$arg\" in *.template-sync.*) exit 73 ;; esac\n"
            "done\n"
            f"exec {shutil.which('chmod')} \"$@\"\n"
        )
        shim.chmod(0o755)

        with mock.patch.dict(os.environ, {"PATH": f"{binary}:{os.environ['PATH']}"}):
            with self.assertRaises(subprocess.CalledProcessError) as error:
                self.sync(checkpoint=False)
        self.assertEqual(error.exception.returncode, 73)
        self.assertEqual(target.read_bytes(), original)
        self.assertEqual(target.stat().st_mode & 0o777, 0o644)
        self.assertEqual(policy.read_bytes(), original_policy)
        self.assertNotIn("SYNC-VERSION=", error.exception.stdout)
        self.assertEqual(list(self.repo.rglob("*.template-sync.*")), [])
        self.assertEqual(self.project_snapshot(), before)
        self.assertIn("SYNC-CHANGED=1", self.sync(checkpoint=False))
        self.assertEqual(target.read_bytes(), original)
        self.assertEqual(target.stat().st_mode & 0o777, 0o755)
        self.assert_mode_sync_noop_after_commit()

    def test_helper_and_ordinary_file_follow_source_execute_mode_both_directions(self):
        paths = {"sync-preflight.py": "scripts/sync-preflight.py",
                 "ordinary.data": "tools/ordinary.data"}
        (self.scaffold / "ordinary.data").write_bytes(b"ordinary managed data\n")
        with (self.scaffold / "manifest.txt").open("a") as stream:
            stream.write("\nordinary.data -> tools/ordinary.data\n")
        for source in paths:
            (self.scaffold / source).chmod(0o644)
        commit_fixture(self.template)
        self.sync()
        for source, destination in paths.items():
            self.assertEqual((self.repo / destination).stat().st_mode & 0o777, 0o644)
            self.assertEqual((self.repo / destination).read_bytes(),
                             (self.scaffold / source).read_bytes())
        self.checkpoint()

        for old, new in ((0o644, 0o755), (0o755, 0o644)):
            with self.subTest(source_mode=oct(new)):
                for source, destination in paths.items():
                    self.assertEqual((self.repo / destination).stat().st_mode & 0o777, old)
                    (self.scaffold / source).chmod(new)
                commit_fixture(self.template)
                output = self.sync(checkpoint=False)
                for source, destination in paths.items():
                    self.assertEqual((self.repo / destination).stat().st_mode & 0o777, new)
                    self.assertEqual((self.repo / destination).read_bytes(),
                                     (self.scaffold / source).read_bytes())
                self.assert_mode_only_diff({destination: (old, new)
                                           for destination in paths.values()})
                self.assertIn("SYNC-CHANGED=1", output)
                self.assertIn("SYNC-VERSION=2.0.7", output)
                self.assert_mode_sync_noop_after_commit()

    def test_managed_markdown_loses_execute_mode_without_content_changes(self):
        relative = Path("skills/README.md")
        source, target = self.scaffold / relative, self.repo / relative
        source.chmod(0o755)
        commit_fixture(self.template)
        self.sync()
        target.chmod(0o755)
        self.checkpoint()
        self.assertEqual(target.read_bytes(), source.read_bytes())

        output = self.sync(checkpoint=False)
        self.assertEqual(source.stat().st_mode & 0o777, 0o755)
        self.assertEqual(target.stat().st_mode & 0o777, 0o644)
        self.assertEqual(target.read_bytes(), source.read_bytes())
        self.assert_mode_only_diff({relative: (0o755, 0o644)})
        self.assertIn("SYNC-CHANGED=1", output)
        self.assertIn("SYNC-VERSION=2.0.7", output)
        self.assert_mode_sync_noop_after_commit()

    def test_recursive_hooks_follow_source_execute_mode_both_directions(self):
        paths = (Path(".githooks/commit-msg"), Path(".githooks/nested/helper"))
        nested = self.scaffold / paths[1]
        nested.parent.mkdir()
        nested.write_bytes(b"#!/bin/sh\nexit 0\n")
        nested.chmod(0o755)
        shutil.copytree(nested.parent, self.repo / ".githooks/nested")
        commit_fixture(self.template)
        self.sync()
        self.checkpoint()

        for old, new in ((0o755, 0o644), (0o644, 0o755)):
            with self.subTest(source_mode=oct(new)):
                for relative in paths:
                    self.assertEqual((self.repo / relative).stat().st_mode & 0o777, old)
                    (self.scaffold / relative).chmod(new)
                commit_fixture(self.template)
                output = self.sync(checkpoint=False)
                for relative in paths:
                    self.assertEqual((self.repo / relative).stat().st_mode & 0o777, new)
                    self.assertEqual((self.repo / relative).read_bytes(),
                                     (self.scaffold / relative).read_bytes())
                self.assert_mode_only_diff({relative: (old, new) for relative in paths})
                self.assertIn("SYNC-CHANGED=1", output)
                self.assertIn("SYNC-VERSION=2.0.7", output)
                self.assert_mode_sync_noop_after_commit()

    def test_recursive_mapping_repairs_directory_modes_without_content_changes(self):
        nested = self.scaffold / ".githooks/nested"
        nested.mkdir()
        (nested / "guide.txt").write_bytes(b"nested hook guidance\n")
        shutil.copytree(nested, self.repo / ".githooks/nested")
        commit_fixture(self.template)
        self.sync()
        self.checkpoint()
        paths = (Path(".githooks"), Path(".githooks/nested"))
        for relative in paths:
            (self.repo / relative).chmod(0o700)
        self.assertEqual(run("git", "status", "--porcelain", cwd=self.repo), "")

        output = self.sync(checkpoint=False)
        for relative in paths:
            self.assertEqual((self.repo / relative).stat().st_mode & 0o777, 0o755)
        self.assertEqual(run("git", "status", "--porcelain", cwd=self.repo), "")
        self.assertIn("SYNC-CHANGED=1", output)
        self.assertIn("SYNC-VERSION=2.0.7", output)
        self.assert_mode_sync_noop_after_commit()

    def test_internal_recursive_root_alias_is_idempotent_and_legacy_modes_are_repaired(self):
        self.sync()
        alias = self.repo / ".githooks"
        referent = self.repo / "hook-store"
        shutil.move(alias, referent)
        alias.symlink_to("hook-store", target_is_directory=True)
        self.checkpoint()
        before = self.project_snapshot()
        for _ in range(2):
            self.assertIn("SYNC-CHANGED=0", self.sync(checkpoint=False))
            self.assertTrue(alias.is_symlink())
            self.assertEqual(os.readlink(alias), "hook-store")
            self.assertEqual(self.project_snapshot(), before)
            self.assertEqual(run("git", "status", "--porcelain", cwd=self.repo), "")

        referent.chmod(0o700)
        shutil.copyfile(ROOT / "tests/fixtures/sync-from-template-v2.0.0.sh", self.script)
        self.checkpoint()
        output = self.sync(checkpoint=False)
        self.assertIn("SYNC-CHANGED=1", output)
        self.assertIn("SYNC-VERSION=2.0.7", output)
        self.assertTrue(alias.is_symlink())
        self.assertEqual(os.readlink(alias), "hook-store")
        self.assertEqual(referent.stat().st_mode & 0o777, 0o755)
        for source in (self.scaffold / ".githooks").iterdir():
            self.assertEqual((referent / source.name).read_bytes(), source.read_bytes())
        self.assert_mode_sync_noop_after_commit()
        self.assertTrue(alias.is_symlink())
        self.assertEqual(os.readlink(alias), "hook-store")

    def test_v200_first_upgrade_repairs_helper_ordinary_file_and_hook_modes(self):
        paths = {"sync-preflight.py": "scripts/sync-preflight.py",
                 "ordinary.data": "tools/ordinary.data",
                 ".githooks/commit-msg": ".githooks/commit-msg"}
        (self.scaffold / "ordinary.data").write_bytes(b"ordinary managed data\n")
        with (self.scaffold / "manifest.txt").open("a") as stream:
            stream.write("\nordinary.data -> tools/ordinary.data\n")
        for source in paths:
            (self.scaffold / source).chmod(0o644)
        commit_fixture(self.template)
        hook = self.repo / ".githooks/commit-msg"
        self.assertEqual(hook.stat().st_mode & 0o777, 0o755)
        self.assertEqual(hook.read_bytes(), (self.scaffold / ".githooks/commit-msg").read_bytes())
        shutil.copyfile(ROOT / "tests/fixtures/sync-from-template-v2.0.0.sh", self.script)

        output = self.sync()
        self.assertIn("SYNC-CHANGED=1", output)
        self.assertIn("SYNC-VERSION=2.0.7", output)
        self.assertEqual(self.script.read_bytes(),
                         (self.scaffold / "sync-from-template.sh").read_bytes())
        self.assertEqual(self.script.stat().st_mode & 0o777, 0o755)
        for source, destination in paths.items():
            with self.subTest(path=destination):
                self.assertEqual((self.repo / destination).stat().st_mode & 0o777, 0o644)
                self.assertEqual((self.repo / destination).read_bytes(),
                                 (self.scaffold / source).read_bytes())
        self.assertEqual(run("git", "diff", "--summary", "--", ".githooks/commit-msg",
                             cwd=self.repo), " mode change 100755 => 100644 .githooks/commit-msg\n")
        self.assertEqual(run("git", "diff", "--numstat", "--", ".githooks/commit-msg",
                             cwd=self.repo), "0\t0\t.githooks/commit-msg\n")
        self.assert_mode_sync_noop_after_commit()

    def test_v200_replaces_recursive_child_alias_without_modifying_its_referent(self):
        source = self.scaffold / ".githooks/nested"
        source.mkdir()
        (source / "helper").write_bytes(b"#!/bin/sh\nexit 0\n")
        (source / "helper").chmod(0o755)
        commit_fixture(self.template)
        referent = self.repo / "local-hook-tools"
        shutil.copytree(source, referent)
        referent.chmod(0o700)
        (referent / "helper").chmod(0o640)
        original = (referent.stat().st_mode, (referent / "helper").stat().st_mode,
                    (referent / "helper").read_bytes())
        alias = self.repo / ".githooks/nested"
        alias.symlink_to("../local-hook-tools", target_is_directory=True)
        self.assertEqual(run("diff", "-qr", str(self.scaffold / ".githooks"),
                             str(self.repo / ".githooks"), cwd=self.repo), "")
        shutil.copyfile(ROOT / "tests/fixtures/sync-from-template-v2.0.0.sh", self.script)
        self.checkpoint()

        self.assertIn("SYNC-CHANGED=1", self.sync(checkpoint=False))
        self.assertFalse(alias.is_symlink())
        self.assertEqual(alias.stat().st_mode & 0o777, 0o755)
        self.assertEqual((alias / "helper").stat().st_mode & 0o777, 0o755)
        self.assertEqual((alias / "helper").read_bytes(), (source / "helper").read_bytes())
        self.assertEqual((referent.stat().st_mode, (referent / "helper").stat().st_mode,
                          (referent / "helper").read_bytes()), original)
        self.assertEqual(run("git", "diff", "--", "local-hook-tools", cwd=self.repo), "")
        self.assert_mode_sync_noop_after_commit()
        self.assertEqual((referent.stat().st_mode, (referent / "helper").stat().st_mode,
                          (referent / "helper").read_bytes()), original)

    def test_v200_replaces_flat_file_alias_without_modifying_its_referent(self):
        source = self.scaffold / "ordinary.data"
        source.write_bytes(b"ordinary managed data\n")
        source.chmod(0o644)
        with (self.scaffold / "manifest.txt").open("a") as stream:
            stream.write("\nordinary.data -> tools/ordinary.data\n")
        commit_fixture(self.template)
        referent = self.repo / "local-data.bin"
        referent.write_bytes(source.read_bytes())
        referent.chmod(0o750)
        original = (referent.stat().st_ino, referent.stat().st_mode, referent.read_bytes())
        alias = self.repo / "tools/ordinary.data"
        alias.parent.mkdir()
        alias.symlink_to("../local-data.bin")
        self.assertEqual(alias.read_bytes(), source.read_bytes())
        shutil.copyfile(ROOT / "tests/fixtures/sync-from-template-v2.0.0.sh", self.script)
        self.checkpoint()

        self.assertIn("SYNC-CHANGED=1", self.sync(checkpoint=False))
        self.assertFalse(alias.is_symlink())
        self.assertEqual(alias.stat().st_mode & 0o777, 0o644)
        self.assertEqual(alias.read_bytes(), source.read_bytes())
        self.assertNotEqual(alias.stat().st_ino, referent.stat().st_ino)
        self.assertEqual((referent.stat().st_ino, referent.stat().st_mode,
                          referent.read_bytes()), original)
        self.assertEqual(run("git", "diff", "--", "local-data.bin", cwd=self.repo), "")
        self.assertEqual(list(self.repo.rglob("*.template-sync.*")), [])
        self.assert_mode_sync_noop_after_commit()
        self.assertEqual((referent.stat().st_ino, referent.stat().st_mode,
                          referent.read_bytes()), original)

    def test_skill_manifest_explicitly_lists_every_shipped_file(self):
        mappings = [line.split(" -> ")
                    for line in (self.scaffold / "manifest.txt").read_text().splitlines()
                    if line.startswith("skills/")]
        shipped = {path.relative_to(self.scaffold).as_posix()
                   for path in (self.scaffold / "skills").rglob("*") if path.is_file()}
        self.assertTrue(shipped)
        self.assertEqual({source for source, _ in mappings}, shipped)
        self.assertEqual(len(mappings), len(shipped))
        for source, destination in mappings:
            self.assertEqual(source, destination)
            self.assertFalse(source.endswith("/"), "skills have mixed ownership")

    def check_project_skills_survive_sync(self, version):
        expected = self.populate()
        expected.update({
            Path("skills/custom-crawler/SKILL.md"): b"project-specific crawling procedure\n",
            Path("skills/custom-crawler/scripts/extract.py"): b"print('local helper')\n",
            Path("skills/custom-crawler/scripts/__pycache__/extract.cpython-313.pyc"):
                b"\x00\xffproject-generated cache\n",
            Path("skills/custom-crawler/assets/nested/sample.bin"): b"\x00\xff\x01\n",
            Path("skills/local-notes.md"): b"project-owned skill notes\n",
        })
        skill_files = [path.relative_to(self.scaffold)
                       for path in (self.scaffold / "skills").rglob("*") if path.is_file()]
        for path in skill_files:
            self.write(path, b"outdated managed guidance\n")
            if path.name == "SKILL.md":
                expected[path.parent / "assets/local.bin"] = b"project helper asset\x00\xff"
                expected[path.parent / "__pycache__/local.cpython-313.pyc"] = b"local cache\x00"
        # Exercise missing managed-file installation as well as replacement.
        (self.repo / "skills/README.md").unlink()
        for path, data in expected.items():
            self.write(path, data)
            (self.repo / path).chmod(0o640)
        helper = Path("skills/custom-crawler/scripts/extract.py")
        (self.repo / helper).chmod(0o750)
        modes = {path: (self.repo / path).stat().st_mode & 0o777 for path in expected}
        if version != "current":
            shutil.copyfile(ROOT / f"tests/fixtures/sync-from-template-v{version}.sh",
                            self.script)

        def assert_skills():
            self.assert_preserved(expected)
            for path, mode in modes.items():
                self.assertEqual((self.repo / path).stat().st_mode & 0o777, mode)
            for path in skill_files:
                self.assertEqual((self.repo / path).read_bytes(),
                                 (self.scaffold / path).read_bytes())
                self.assertEqual((self.repo / path).stat().st_mode & 0o777, 0o644)

        self.assertIn("SYNC-CHANGED=1", self.sync())
        self.assertEqual(self.script.read_bytes(),
                         (self.scaffold / "sync-from-template.sh").read_bytes())
        assert_skills()
        self.assertIn("SYNC-CHANGED=0", self.sync())
        assert_skills()
        for path in skill_files:
            with (self.scaffold / path).open("ab") as stream:
                stream.write(b"\nUpdated template skill guidance.\n")
        commit_fixture(self.template)
        self.assertIn("SYNC-CHANGED=1", self.sync())
        assert_skills()
        self.assertIn("SYNC-CHANGED=0", self.sync())
        assert_skills()

    def test_project_skills_survive_current_sync_and_managed_updates(self):
        self.check_project_skills_survive_sync("current")

    def test_project_skills_survive_v200_upgrade_and_managed_updates(self):
        self.check_project_skills_survive_sync("2.0.0")

    def test_project_skills_survive_v201_upgrade_and_managed_updates(self):
        self.check_project_skills_survive_sync("2.0.1")

    def test_unsafe_template_version_is_rejected_before_project_writes(self):
        self.populate()
        version_file = self.scaffold / "records/REPO.md"
        original = version_file.read_text()
        version_line = next(line for line in original.splitlines()
                            if line.startswith("**Template version:"))

        before = self.project_snapshot()
        for version in ("1.99.99", "2.0.0", "2.0.1", "2.0.2", "2.0.3", "2.0.4", "2.0.5", "2.0.6", "2.0", "unknown"):
            with self.subTest(version=version):
                version_file.write_text(original.replace(version_line,
                                                         f"**Template version: {version}**"))
                commit_fixture(self.template)
                with self.assertRaises(subprocess.CalledProcessError) as error:
                    self.sync()
                self.assertIn("minimum is 2.0.7", error.exception.stderr)
                self.assertEqual(self.project_snapshot(), before)
                self.assertEqual(list(self.repo.rglob("*.template-sync.*")), [])

    def test_workflow_destinations_and_ancestors_are_rejected_before_writes(self):
        self.populate()
        self.write(Path(".github/workflows/local.yml"), b"project-reviewed workflow\n")
        self.write(Path("skills/local/__pycache__/host.pyc"), b"host cache\x00")
        (self.repo / "workflow-alias").symlink_to(".github/workflows", target_is_directory=True)
        before = self.project_snapshot()
        manifest = self.scaffold / "manifest.txt"
        original = manifest.read_text()
        mappings = (
            "template-sync.yml -> .github/workflows/new.yml",
            ".githooks/ -> .github/workflows/",
            ".githooks/ -> .github/",
            ".githooks/ -> ./",
            "template-sync.yml -> ./.github/workflows/new.yml",
            "template-sync.yml -> .github//workflows/new.yml",
            "template-sync.yml -> x/../.github/workflows/new.yml",
            ".githooks/ -> ./.github/",
            "template-sync.yml -> workflow-alias/new.yml",
            "template-sync.yml -> ../outside.yml",
            "template-sync.yml -> /tmp/outside.yml",
            ".github/workflows/new.yml",
            ".github/workflows/",
            "  .github/workflows/new.yml  ",
        )
        for mapping in mappings:
            with self.subTest(mapping=mapping):
                manifest.write_text(original + "\n" + mapping + "\n")
                commit_fixture(self.template)
                with self.assertRaises(subprocess.CalledProcessError) as error:
                    self.sync()
                self.assertIn("Refusing", error.exception.stderr)
                self.assertEqual(self.project_snapshot(), before)

    def test_indented_manifest_comments_and_blank_lines_are_ignored(self):
        for name in ("manifest.txt", "seed-manifest-v2.txt"):
            with (self.scaffold / name).open("a") as stream:
                stream.write("\n   \n  # .github/workflows/comment.yml\n")
        commit_fixture(self.template)
        self.assertIn("SYNC-CHANGED=1", self.sync())
        self.assertFalse((self.repo / ".github/workflows/comment.yml").exists())
        self.assertIn("SYNC-CHANGED=0", self.sync())

    def test_workflow_seed_is_rejected_before_any_managed_write(self):
        self.populate()
        before = self.project_snapshot()
        manifest = self.scaffold / "seed-manifest-v2.txt"
        with manifest.open("a") as stream:
            stream.write("\ntemplate-sync.yml -> .github/workflows/new.yml\n")
        commit_fixture(self.template)
        with self.assertRaises(subprocess.CalledProcessError) as error:
            self.sync()
        self.assertIn("Refusing workflow destination", error.exception.stderr)
        self.assertEqual(self.project_snapshot(), before)

    def test_safe_template_versions_are_compared_numerically(self):
        version_file = self.scaffold / "records/REPO.md"
        original = version_file.read_text()
        version_line = next(line for line in original.splitlines()
                            if line.startswith("**Template version:"))
        for version in ("2.0.7", "2.0.10", "2.1.0", "3.0.0"):
            with self.subTest(version=version):
                content = original.replace(version_line, f"**Template version: {version}**")
                if version_file.read_text() != content:
                    version_file.write_text(content)
                    commit_fixture(self.template)
                self.assertIn(f"SYNC-VERSION={version}", self.sync())

    def test_version_only_update_is_exact_and_preserves_local_policy(self):
        expected = self.populate()
        self.write(Path("skills/local/__pycache__/host.pyc"), b"project host cache\x00")
        expected[Path("skills/local/__pycache__/host.pyc")] = b"project host cache\x00"
        self.sync()
        version_file = self.scaffold / "records/REPO.md"
        source = version_file.read_text()
        version_line = next(line for line in source.splitlines()
                            if line.startswith("**Template version:"))
        if version_line != "**Template version: 2.0.7**":
            version_file.write_text(source.replace(version_line, "**Template version: 2.0.7**"))
            commit_fixture(self.template)
        policy = self.repo / "records/REPO.md"
        for old_version in ("2.0.0", "2.0.70"):
            with self.subTest(old_version=old_version):
                before = (f"# Local policy\r\n\r\n**Template version: {old_version}**\r\n"
                          f"\r\nRetain prose mentioning Template version: {old_version}.\r\n"
                          "## Local Divergence\r\nKeep local decisions.\r\n").encode()
                policy.write_bytes(before)
                policy.chmod(0o640)
                self.assertIn("SYNC-CHANGED=1", self.sync())
                after = before.replace(f"**Template version: {old_version}**".encode(),
                                       b"**Template version: 2.0.7**", 1)
                self.assertEqual(policy.read_bytes(), after)
                self.assertEqual(policy.stat().st_mode & 0o777, 0o640)
                self.assert_preserved(expected)
                self.assertIn("SYNC-CHANGED=0", self.sync())
                self.assertEqual(policy.read_bytes(), after)
                self.assertEqual(policy.stat().st_mode & 0o777, 0o640)

    def test_failed_version_replacement_preserves_policy_and_cleans_staging(self):
        self.sync()
        policy = self.repo / "records/REPO.md"
        original = b"# Local policy\n**Template version: 2.0.0**\nKeep local policy.\n"
        policy.write_bytes(original)
        policy.chmod(0o600)
        for command in ("cp", "cat", "mv"):
            with self.subTest(command=command):
                binary = self.root / f"fail-version-{command}"
                binary.mkdir()
                shim = binary / command
                if command == "cat":
                    pattern = "*/repo-version.md"
                    failure = "printf partial; exit 73"
                else:
                    pattern = "*/records/REPO.md.template-sync.*"
                    failure = 'printf partial > "$arg"; exit 73' if command == "cp" else "exit 73"
                shim.write_text(
                    "#!/bin/bash\nfor arg; do\n"
                    f"  case \"$arg\" in {pattern}) {failure} ;; esac\n"
                    "done\n"
                    f"exec {shutil.which(command)} \"$@\"\n"
                )
                shim.chmod(0o755)
                with mock.patch.dict(os.environ, {"PATH": f"{binary}:{os.environ['PATH']}"}):
                    with self.assertRaises(subprocess.CalledProcessError):
                        self.sync()
                self.assertEqual(policy.read_bytes(), original)
                self.assertEqual(policy.stat().st_mode & 0o777, 0o600)
                self.assertEqual(list(self.repo.rglob("*.template-sync.*")), [])
        self.assertIn("SYNC-CHANGED=1", self.sync())
        self.assertEqual(policy.stat().st_mode & 0o777, 0o600)
        self.assertIn("SYNC-CHANGED=0", self.sync())

    def test_only_canonical_header_version_changes(self):
        self.sync()
        policy = self.repo / "records/REPO.md"
        examples = (
            ("2.0.0", b"## Local Divergence\n```md\n**Template version: 2.0.7**\n```\n"),
            ("2.0.7", b"## Local Divergence\n**Template version: 2.0.0**\n"),
            ("2.0.0", b"## Local Divergence\n**Template version: 2.0.1**\n"
                       b"**Template version: 2.0.2**\n"),
        )
        for current, tail in examples:
            with self.subTest(current=current, tail=tail):
                before = f"# Local policy\n\n**Template version: {current}**\n\n".encode() + tail
                policy.write_bytes(before)
                policy.chmod(0o640)
                output = self.sync()
                self.assertIn(f"SYNC-CHANGED={int(current != '2.0.7')}", output)
                self.assertEqual(policy.read_bytes(), before.replace(
                    f"**Template version: {current}**".encode(), b"**Template version: 2.0.7**", 1))
                self.assertEqual(policy.stat().st_mode & 0o777, 0o640)
        policy.write_bytes(b"# Local policy\n```\n**Template version: 2.0.1**\n```\n"
                           b"**Template version: 2.0.0**\n## Local\n")
        self.sync()
        self.assertEqual(policy.read_bytes(), b"# Local policy\n```\n**Template version: 2.0.1**\n```\n"
                                             b"**Template version: 2.0.7**\n## Local\n")

    def test_resolved_destinations_cannot_escape_repository(self):
        self.sync()
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "keep.txt").write_bytes(b"external data\n")
        (self.repo / "shared").symlink_to(outside, target_is_directory=True)
        self.checkpoint()
        before = self.project_snapshot()
        for name, mapping in (
            ("manifest.txt", "CLAUDE.md -> shared/guide.md"),
            ("manifest.txt", ".githooks/ -> shared/hooks/"),
            ("seed-manifest-v2.txt", "CLAUDE.md -> shared/seed.md"),
        ):
            with self.subTest(manifest=name, mapping=mapping):
                manifest = self.scaffold / name
                original = manifest.read_text()
                manifest.write_text(original + "\n" + mapping + "\n")
                commit_fixture(self.template)
                with self.assertRaises(subprocess.CalledProcessError) as error:
                    self.sync(checkpoint=False)
                self.assertIn("outside the repository", error.exception.stderr)
                self.assertEqual(self.project_snapshot(), before)
                self.assertEqual(list(outside.iterdir()), [outside / "keep.txt"])
                self.assertEqual((outside / "keep.txt").read_bytes(), b"external data\n")
                manifest.write_text(original)
                commit_fixture(self.template)

    def test_direct_sync_refuses_staged_unstaged_and_deleted_managed_files(self):
        self.sync()
        self.checkpoint()
        for relative in ("skills/commit-generator/SKILL.md", "AGENTS.md", "records/REPO.md"):
            target = self.repo / relative
            original = target.read_bytes()
            for kind in ("unstaged", "staged", "deleted"):
                with self.subTest(path=relative, kind=kind):
                    if kind == "deleted":
                        target.unlink()
                    else:
                        target.write_bytes(b"uncommitted managed content\n")
                    if kind == "staged":
                        run("git", "add", relative, cwd=self.repo)
                    before = self.project_snapshot()
                    with self.assertRaises(subprocess.CalledProcessError) as error:
                        self.sync(checkpoint=False)
                    self.assertIn("uncommitted sync destination", error.exception.stderr)
                    self.assertEqual(self.project_snapshot(), before)
                    target.write_bytes(original)
                    run("git", "reset", "-q", "HEAD", "--", relative, cwd=self.repo)

    def test_direct_sync_refuses_staged_and_unstaged_managed_execute_mode_changes(self):
        self.sync()
        self.checkpoint()
        for relative in ("scripts/sync-from-template.sh", "scripts/sync-preflight.py",
                         "skills/commit-generator/SKILL.md", ".githooks/commit-msg"):
            target = self.repo / relative
            original = target.read_bytes()
            original_mode = target.stat().st_mode & 0o777
            for kind in ("unstaged", "staged"):
                with self.subTest(path=relative, kind=kind):
                    target.chmod(original_mode ^ 0o111)
                    if kind == "staged":
                        run("git", "add", relative, cwd=self.repo)
                    before = self.project_snapshot()
                    diff_args = ("--cached",) if kind == "staged" else ()
                    summary = run("git", "diff", *diff_args, "--summary", cwd=self.repo)
                    self.assertIn("mode change", summary)
                    self.assertEqual(run("git", "diff", *diff_args, "--numstat",
                                         cwd=self.repo), f"0\t0\t{relative}\n")
                    with self.assertRaises(subprocess.CalledProcessError) as error:
                        self.sync(checkpoint=False)
                    self.assertIn("uncommitted sync destination", error.exception.stderr)
                    self.assertIn(relative, error.exception.stderr)
                    self.assertEqual(self.project_snapshot(), before)
                    self.assertEqual(target.read_bytes(), original)
                    self.assertEqual(target.stat().st_mode & 0o777, original_mode ^ 0o111)
                    self.assertEqual(run("git", "diff", *diff_args, "--summary",
                                         cwd=self.repo), summary)
                    run("git", "restore", "--staged", "--worktree", "--", relative,
                        cwd=self.repo)
                    self.assertEqual(target.stat().st_mode & 0o777, original_mode)

    def test_existing_skill_parent_symlink_cannot_write_external_data(self):
        self.sync()
        skill = self.repo / "skills/clean-correction"
        external = self.root / "external-skill"
        shutil.move(skill, external)
        skill.symlink_to(external, target_is_directory=True)
        self.checkpoint()
        before = self.project_snapshot()
        external_bytes = (external / "SKILL.md").read_bytes()
        external_mode = (external / "SKILL.md").stat().st_mode
        with self.assertRaises(subprocess.CalledProcessError) as error:
            self.sync(checkpoint=False)
        self.assertIn("outside the repository", error.exception.stderr)
        self.assertEqual(self.project_snapshot(), before)
        self.assertEqual((external / "SKILL.md").read_bytes(), external_bytes)
        self.assertEqual((external / "SKILL.md").stat().st_mode, external_mode)

    def test_direct_sync_refuses_untracked_and_ignored_managed_data(self):
        self.sync()
        self.write(Path(".gitignore"), b".githooks/ignored-cache/\n")
        self.checkpoint()
        for relative in (".githooks/local-note.txt", ".githooks/ignored-cache/host.bin"):
            with self.subTest(path=relative):
                self.write(Path(relative), b"local data\x00")
                before = self.project_snapshot()
                with self.assertRaises(subprocess.CalledProcessError) as error:
                    self.sync(checkpoint=False)
                self.assertIn("uncommitted sync destination", error.exception.stderr)
                self.assertEqual(self.project_snapshot(), before)
                (self.repo / relative).unlink()
        source = self.scaffold / "local-guide.md"
        source.write_text("template guidance\n")
        with (self.scaffold / "manifest.txt").open("a") as stream:
            stream.write("\nlocal-guide.md -> skills/new-local-guide.md\n")
        commit_fixture(self.template)
        self.write(Path("skills/new-local-guide.md"), b"existing untracked user draft\n")
        before = self.project_snapshot()
        with self.assertRaises(subprocess.CalledProcessError) as error:
            self.sync(checkpoint=False)
        self.assertIn("uncommitted sync destination", error.exception.stderr)
        self.assertEqual(self.project_snapshot(), before)

    def test_direct_sync_preserves_unrelated_dirty_records_caches_and_logs(self):
        self.populate()
        self.sync()
        self.checkpoint()
        expected = {
            Path("records/SPEC.md"): b"uncommitted project truth\n",
            UPSTREAM / REGISTERS[0]: b"uncommitted project register\n",
            Path("skills/custom/__pycache__/host.pyc"): b"host cache\x00",
            Path("skills/commit-generator/assets/local.bin"): b"custom skill asset\xff",
            Path("sync.log"): b"legacy workflow output\n",
        }
        for path, data in expected.items():
            self.write(path, data)
        with (self.scaffold / "skills/README.md").open("a") as stream:
            stream.write("\nNew template guidance.\n")
        commit_fixture(self.template)
        self.assertIn("SYNC-CHANGED=1", self.sync(checkpoint=False))
        self.assert_preserved(expected)

    def test_agents_render_failure_is_fatal_before_any_project_write(self):
        self.populate()
        self.sync()
        template_agents = self.scaffold / "AGENTS.md"
        original_template = template_agents.read_bytes()
        for location in ("template", "project"):
            with self.subTest(location=location):
                if location == "template":
                    template_agents.write_bytes(b"# No managed boundary\n")
                    commit_fixture(self.template)
                else:
                    (self.repo / "AGENTS.md").write_bytes(b"# No recognized local boundary\n")
                self.checkpoint()
                before = self.project_snapshot()
                with self.assertRaises(subprocess.CalledProcessError) as error:
                    self.sync(checkpoint=False)
                self.assertIn("AGENTS.md", error.exception.stderr)
                self.assertNotIn("SYNC-VERSION=", error.exception.stdout)
                self.assertNotIn("SYNC-CHANGED=", error.exception.stdout)
                self.assertEqual(self.project_snapshot(), before)
                if location == "template":
                    template_agents.write_bytes(original_template)
                    commit_fixture(self.template)

    def test_agents_render_io_error_does_not_advance_version(self):
        self.sync()
        self.write(Path("records/REPO.md"), b"# Local policy\n**Template version: 2.0.0**\n")
        self.checkpoint()
        before = self.project_snapshot()
        injection = self.root / "fail-agents-render"
        injection.mkdir()
        (injection / "sitecustomize.py").write_text(
            "from pathlib import Path\n"
            "original = Path.write_bytes\n"
            "def write(self, data):\n"
            "    if self.name == 'agents-merged.md':\n"
            "        raise OSError('injected AGENTS rendering failure')\n"
            "    return original(self, data)\n"
            "Path.write_bytes = write\n"
        )
        with mock.patch.dict(os.environ, {"PYTHONPATH": str(injection), "PYTHONDONTWRITEBYTECODE": "1"}):
            with self.assertRaises(subprocess.CalledProcessError) as error:
                self.sync(checkpoint=False)
        self.assertIn("injected AGENTS rendering failure", error.exception.stderr)
        self.assertNotIn("SYNC-VERSION=", error.exception.stdout)
        self.assertEqual(self.project_snapshot(), before)

    def test_legacy_tee_workflow_can_upgrade_twice_with_worktree_log(self):
        self.populate()
        shutil.copyfile(ROOT / "tests/fixtures/sync-from-template-v2.0.0.sh", self.script)
        self.checkpoint()

        def legacy_step():
            return run("bash", "-c", "set -euo pipefail; bash scripts/sync-from-template.sh | tee sync.log",
                       cwd=self.repo, env={**os.environ, "TEMPLATE_URL": self.template.as_uri()})

        self.assertIn("SYNC-CHANGED=1", legacy_step())
        self.checkpoint()
        with (self.scaffold / "skills/README.md").open("a") as stream:
            stream.write("\nSecond upgrade guidance.\n")
        commit_fixture(self.template)
        self.assertIn("SYNC-CHANGED=1", legacy_step())
        self.assertEqual((self.repo / "skills/README.md").read_bytes(),
                         (self.scaffold / "skills/README.md").read_bytes())
        self.checkpoint()
        self.assertIn("SYNC-CHANGED=0", legacy_step())

    def test_workflow_is_preserved_on_current_and_legacy_upgrades(self):
        self.populate()
        workflow = self.repo / ".github/workflows/template-sync.yml"
        self.write(workflow.relative_to(self.repo), b"project-reviewed workflow\n")
        workflow.chmod(0o640)
        for version in ("current", "2.0.0", "2.0.1"):
            with self.subTest(version=version):
                source = (self.scaffold / "sync-from-template.sh" if version == "current"
                          else ROOT / f"tests/fixtures/sync-from-template-v{version}.sh")
                shutil.copyfile(source, self.script)
                self.sync()
                self.assertEqual(workflow.read_bytes(), b"project-reviewed workflow\n")
                self.assertEqual(workflow.stat().st_mode & 0o777, 0o640)
                repeated = self.sync()
                self.assertIn("SYNC-CHANGED=0", repeated)
                self.assertIn("SYNC-WORKFLOW-DRIFT=1", repeated)
                self.assertEqual(workflow.read_bytes(), b"project-reviewed workflow\n")
                self.assertEqual(workflow.stat().st_mode & 0o777, 0o640)
        shutil.copyfile(self.scaffold / "template-sync.yml", workflow)
        self.assertIn("SYNC-WORKFLOW-DRIFT=0", self.sync())

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
