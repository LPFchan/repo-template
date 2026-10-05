"""Execute the shipped workflow's shell against local Git repositories."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from test_sync_from_template import ROOT, commit_fixture, run


def workflow_step(name):
    """Read a named YAML literal run block without requiring a YAML package."""
    workflow = (ROOT / "scaffold/template-sync.yml").read_text()
    section = workflow.split(f"      - name: {name}\n", 1)[1]
    block = section.split("        run: |\n", 1)[1]
    lines = []
    for line in block.splitlines():
        if line and not line.startswith("          "):
            break
        lines.append(line[10:] if line else "")
    return "\n".join(lines) + "\n"


class TemplateWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.template = self.root / "template"
        scaffold = self.template / "scaffold"
        shutil.copytree(ROOT / "scaffold", scaffold)
        run("git", "init", "-q", cwd=self.template)
        commit_fixture(self.template)
        self.origin = self.root / "origin.git"
        run("git", "init", "--bare", "-q", "--initial-branch=main", str(self.origin),
            cwd=self.root)
        self.repo = self.root / "adopted"
        self.repo.mkdir()
        run("git", "init", "-q", "--initial-branch=main", cwd=self.repo)
        for line in (scaffold / "manifest.txt").read_text().splitlines():
            if not line or line.startswith("#"):
                continue
            source, destination = line.split(" -> ")
            target = self.repo / destination
            if source.endswith("/"):
                shutil.copytree(scaffold / source, target)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(scaffold / source, target)
                # Model an adopted checkout with runnable shell entry points,
                # even when the template stores a source script as 0644.
                if source.endswith(".sh"):
                    target.chmod(target.stat().st_mode | 0o111)
        shutil.copytree(scaffold / "records", self.repo / "records", dirs_exist_ok=True)
        spec = self.repo / "records/SPEC.md"
        spec.write_text(spec.read_text().replace("- Project id:\n",
                                                "- Project id: fixture-project\n"))
        shutil.copy2(scaffold / "AGENTS.md", self.repo / "AGENTS.md")
        (self.repo / ".github/workflows").mkdir(parents=True, exist_ok=True)
        shutil.copy2(scaffold / "template-sync.yml",
                     self.repo / ".github/workflows/template-sync.yml")
        (self.repo / "CLAUDE.md").write_text("outdated managed instructions\n")
        (self.repo / "project.txt").write_text("project-owned\n")
        commit_fixture(self.repo)
        run("git", "remote", "add", "origin", str(self.origin), cwd=self.repo)
        run("git", "push", "-qu", "origin", "main", cwd=self.repo)
        self.runner = self.root / "runner-temp"
        self.runner.mkdir()
        self.output = self.runner / "github-output"
        self.summary = self.runner / "github-summary"
        self.branch = "main"
        self.repository = "fixture/adopted"

    def remote_head(self, branch="main"):
        return run("git", "rev-parse", f"refs/heads/{branch}", cwd=self.origin).strip()

    def step(self, name, extra=None, check=True):
        env = {**os.environ, "RUNNER_TEMP": str(self.runner),
               "GITHUB_OUTPUT": str(self.output), "GITHUB_REPOSITORY": self.repository,
               "GITHUB_STEP_SUMMARY": str(self.summary),
               "GITHUB_REF_TYPE": "branch", "GITHUB_REF_NAME": self.branch,
               "TEMPLATE_URL": self.template.as_uri(), **(extra or {})}
        return subprocess.run(["bash", "-c", workflow_step(name)], cwd=self.repo,
                              env=env, text=True, capture_output=True, check=check)

    def sync(self):
        self.output.write_text("")
        self.step("Sync from repo-template")
        values = dict(line.split("=", 1) for line in self.output.read_text().splitlines())
        self.assertFalse((self.repo / "sync.log").exists())
        return values

    def commit(self, values, check=True):
        return self.step("Commit changes", {
            "SYNC_VERSION": values["SYNC-VERSION"], "SYNC_STATE": values["state_dir"]
        }, check=check)

    def test_first_run_uses_registered_message_and_repeat_is_noop(self):
        before = self.remote_head()
        values = self.sync()
        self.assertEqual(values["SYNC-CHANGED"], "1")
        state = Path(values["state_dir"])
        self.assertTrue(state.is_relative_to(self.runner))
        self.assertFalse(state.is_relative_to(self.repo))
        self.commit(values)
        after = self.remote_head()
        self.assertNotEqual(before, after)
        self.assertEqual(run("git", "rev-parse", "HEAD", cwd=self.repo).strip(), after)
        message = run("git", "log", "-1", "--format=%B", cwd=self.repo)
        self.assertIn("project: fixture-project\n", message)
        self.assertIn("agent: actions\n", message)
        log_id = next(line.removeprefix("commit: ") for line in message.splitlines()
                      if line.startswith("commit: "))
        registry = self.repo / ".git/repo-template/generated-commit-ids" / log_id
        self.assertTrue(registry.is_file(), "the real generator must register the commit")
        self.assertEqual(run("git", "config", "core.hooksPath", cwd=self.repo).strip(),
                         ".githooks")
        self.assertTrue((state / "commit-message.txt").is_file())
        run("sh", "scripts/check-commit-standards.sh", str(state / "commit-message.txt"),
            cwd=self.repo)
        self.assertEqual(run("git", "status", "--porcelain", cwd=self.repo), "")
        names = run("git", "ls-tree", "-r", "--name-only", "HEAD", cwd=self.repo)
        for artifact in ("sync.log", "commit-message.txt", "changed-paths"):
            self.assertNotIn(artifact, names)
        values = self.sync()
        self.assertEqual(values["SYNC-CHANGED"], "0")
        # The commit step is normally skipped by its if condition. It is also
        # harmless if invoked with an empty change snapshot.
        self.commit(values)
        self.assertEqual(self.remote_head(), after)
        self.assertEqual(run("git", "status", "--porcelain", cwd=self.repo), "")

    def assert_canonical_project_trailer(self, repository, project_id, spec):
        self.repository = repository
        (self.repo / "records/SPEC.md").write_text(spec)
        commit_fixture(self.repo)
        run("git", "push", "-q", cwd=self.repo)
        self.commit(self.sync())
        message = run("git", "log", "-1", "--format=%B", cwd=self.repo)
        self.assertEqual([line for line in message.splitlines()
                          if line.startswith("project:")], [f"project: {project_id}"])
        self.assertEqual(run("git", "rev-parse", "HEAD", cwd=self.repo).strip(),
                         self.remote_head())

    def test_photos_auth_capture_uses_canonical_project_id(self):
        self.assert_canonical_project_trailer(
            "LPFchan/PhotosAuthCapture", "photos-auth-capture",
            "# PhotosAuthCapture Spec\n\n- Project id: photos-auth-capture\n")

    def test_franken_agent_detection_uses_backtick_wrapped_project_id(self):
        self.assert_canonical_project_trailer(
            "LPFchan/franken_agent_detection", "franken-agent-detection",
            "# Franken Agent Detection Spec\n\n- Project id: `franken-agent-detection`\n")

    def test_deepest_crawl_uses_canonical_project_id(self):
        self.assert_canonical_project_trailer(
            "LPFchan/deepest-crawl", "deepest-crawl",
            "# Deepest Crawl Spec\n\n- Project id: deepest-crawl\n")

    def test_fenced_project_examples_are_ignored(self):
        self.assert_canonical_project_trailer(
            "fixture/display-name", "fixture-project",
            "# Spec\n\n```markdown\n- Project id: example-project\n```\n"
            "~~~~markdown\n- Project id: `another-example`\n```\n"
            "- Project id: still-an-example\n~~~~\n"
            "    - Project id: indented-code-example\n"
            "\n- Project id: `fixture-project`\n")

    def test_missing_invalid_or_ambiguous_project_ids_prevent_staging_and_commit(self):
        values = self.sync()
        before = self.remote_head()
        spec = self.repo / "records/SPEC.md"
        cases = {
            "missing file": None,
            "missing field": "# Spec\n",
            "empty field": "- Project id:\n",
            "uppercase display name": "- Project id: PhotosAuthCapture\n",
            "underscored display name": "- Project id: franken_agent_detection\n",
            "spaces": "- Project id: fixture project\n",
            "leading hyphen": "- Project id: -fixture-project\n",
            "trailing hyphen": "- Project id: fixture-project-\n",
            "unclosed backtick": "- Project id: `fixture-project\n",
            "unopened backtick": "- Project id: fixture-project`\n",
            "shell expression": "- Project id: $(touch should-not-exist)\n",
            "different fields": "- Project id: fixture-project\n- Project id: other-project\n",
            "duplicate fields": "- Project id: fixture-project\n- Project id: fixture-project\n",
            "only fenced example": "```markdown\n- Project id: example-project\n```\n",
            "only tilde-fenced example": "~~~\n- Project id: example-project\n~~~\n",
        }
        for label, content in cases.items():
            with self.subTest(case=label):
                if content is None:
                    spec.unlink()
                else:
                    spec.write_text(content)
                result = self.commit(values, check=False)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("records/SPEC.md", result.stderr)
                self.assertEqual(self.remote_head(), before)
                self.assertEqual(run("git", "rev-parse", "HEAD", cwd=self.repo).strip(), before)
                self.assertEqual(run("git", "diff", "--cached", "--name-only", cwd=self.repo), "")
                self.assertFalse((Path(values["state_dir"]) / "commit-message.txt").exists())
                self.assertFalse((self.repo / "should-not-exist").exists())

    def test_dirty_checkout_is_rejected_before_sync(self):
        before = self.remote_head()
        (self.repo / "project.txt").write_text("unrelated modification\n")
        (self.repo / "unrelated.txt").write_text("unrelated untracked file\n")
        result = self.step("Sync from repo-template", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.remote_head(), before)
        self.assertEqual((self.repo / "CLAUDE.md").read_text(),
                         "outdated managed instructions\n")

    def test_only_captured_paths_are_committed(self):
        values = self.sync()
        (self.repo / "project.txt").write_text("later unrelated tracked change\n")
        (self.repo / "unrelated.txt").write_text("later unrelated untracked file\n")
        self.commit(values)
        self.assertEqual(run("git", "show", "HEAD:project.txt", cwd=self.repo),
                         "project-owned\n")
        names = run("git", "ls-tree", "-r", "--name-only", "HEAD", cwd=self.repo)
        self.assertNotIn("unrelated.txt", names)
        self.assertIn(" M project.txt", run("git", "status", "--porcelain", cwd=self.repo))

    def test_later_staged_unrelated_content_prevents_commit(self):
        values = self.sync()
        before = self.remote_head()
        (self.repo / "unrelated.txt").write_text("already staged unrelated file\n")
        run("git", "add", "unrelated.txt", cwd=self.repo)
        result = self.commit(values, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.remote_head(), before)
        self.assertEqual(run("git", "diff", "--cached", "--name-only", cwd=self.repo),
                         "unrelated.txt\n")

    def test_literal_paths_deletions_and_renames_are_captured(self):
        for name in ("old-name.txt", "deleted.txt", ":(glob)*.txt"):
            (self.repo / name).write_text("before\n")
        script = self.repo / "scripts/sync-from-template.sh"
        script.write_text(
            "#!/bin/bash\nset -eu\nmv old-name.txt new-name.txt\nrm deleted.txt\n"
            "printf changed > ':(glob)*.txt'\n"
            "echo SYNC-VERSION=test\necho SYNC-CHANGED=1\n"
        )
        commit_fixture(self.repo)
        run("git", "push", "-q", cwd=self.repo)
        values = self.sync()
        (self.repo / "unrelated.txt").write_text("must not match a magic pathspec\n")
        self.commit(values)
        names = run("git", "ls-tree", "-r", "--name-only", "HEAD", cwd=self.repo).splitlines()
        self.assertIn("new-name.txt", names)
        self.assertNotIn("old-name.txt", names)
        self.assertNotIn("deleted.txt", names)
        self.assertNotIn("unrelated.txt", names)
        self.assertEqual(run("git", "show", "HEAD::(glob)*.txt", cwd=self.repo), "changed")

    def test_sync_pipeline_failure_prevents_commit_and_push(self):
        script = self.repo / "scripts/sync-from-template.sh"
        script.write_text("#!/bin/bash\necho SYNC-VERSION=test\necho SYNC-CHANGED=1\nexit 29\n")
        commit_fixture(self.repo)
        run("git", "push", "-q", cwd=self.repo)
        before = self.remote_head()
        result = self.step("Sync from repo-template", check=False)
        self.assertEqual(result.returncode, 29)
        self.assertEqual(self.remote_head(), before)
        self.assertNotIn("SYNC-CHANGED=", self.output.read_text())
        self.assertFalse((self.repo / "sync.log").exists())

    def test_real_commit_hook_failure_prevents_push(self):
        values = self.sync()
        before = self.remote_head()
        hook = self.repo / ".githooks/prepare-commit-msg"
        hook.write_text("#!/bin/sh\nexit 37\n")
        hook.chmod(0o755)
        result = self.commit(values, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.remote_head(), before)
        self.assertTrue(list((self.repo / ".git/repo-template/generated-commit-ids").iterdir()))

    def test_checker_failure_prevents_commit_and_push(self):
        values = self.sync()
        before = self.remote_head()
        checker = self.repo / "scripts/check-commit-standards.sh"
        checker.write_text("#!/bin/sh\nexit 41\n")
        result = self.commit(values, check=False)
        self.assertEqual(result.returncode, 41)
        self.assertEqual(self.remote_head(), before)

    def test_missing_generated_registration_is_rejected_by_real_hook(self):
        values = self.sync()
        before = self.remote_head()
        generator = self.repo / "scripts/new-commit-message.sh"
        generator.write_text(generator.read_text() +
                             '\nrm -f "$registry_dir/$log_id"\n')
        result = self.commit(values, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("was not registered", result.stderr)
        self.assertEqual(self.remote_head(), before)

    def test_manual_run_pushes_only_the_selected_branch(self):
        main = self.remote_head()
        self.branch = "manual-sync"
        run("git", "switch", "-qc", self.branch, cwd=self.repo)
        run("git", "push", "-qu", "origin", self.branch, cwd=self.repo)
        self.commit(self.sync())
        self.assertEqual(self.remote_head(), main)
        self.assertNotEqual(self.remote_head(self.branch), main)
        self.assertEqual(run("git", "rev-parse", "HEAD", cwd=self.repo).strip(),
                         self.remote_head(self.branch))

    def test_wrong_branch_and_tag_checkouts_are_rejected(self):
        before = self.remote_head()
        for extra in ({"GITHUB_REF_NAME": "different-branch"}, {"GITHUB_REF_TYPE": "tag"}):
            with self.subTest(extra=extra):
                result = self.step("Sync from repo-template", extra, check=False)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.remote_head(), before)

    def test_changed_signal_without_git_delta_is_noop(self):
        script = self.repo / "scripts/sync-from-template.sh"
        script.write_text("#!/bin/bash\necho SYNC-VERSION=test\necho SYNC-CHANGED=1\n")
        commit_fixture(self.repo)
        run("git", "push", "-q", cwd=self.repo)
        before = self.remote_head()
        values = self.sync()
        self.assertEqual(values["SYNC-CHANGED"], "0")
        self.commit(values)
        self.assertEqual(self.remote_head(), before)

    def test_empty_staged_diff_is_noop(self):
        values = self.sync()
        before = self.remote_head()
        run("git", "restore", "CLAUDE.md", cwd=self.repo)
        self.commit(values)
        self.assertEqual(self.remote_head(), before)
        self.assertFalse((Path(values["state_dir"]) / "commit-message.txt").exists())

    def test_workflow_drift_is_reported_without_modifying_workflow(self):
        workflow = self.repo / ".github/workflows/template-sync.yml"
        original = workflow.read_bytes()
        with (self.template / "scaffold/template-sync.yml").open("a") as stream:
            stream.write("\n# A future separately reviewed workflow update.\n")
        commit_fixture(self.template)
        self.commit(self.sync())
        self.assertEqual(workflow.read_bytes(), original)
        self.assertIn("update .github/workflows/template-sync.yml separately",
                      self.summary.read_text())
        self.assertNotIn(".github/workflows/template-sync.yml", run(
            "git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD", cwd=self.repo))

    def test_version_only_change_is_committed_and_repeat_is_noop(self):
        self.sync()
        policy = self.repo / "records/REPO.md"
        original = policy.read_text()
        version_line = next(line for line in original.splitlines()
                            if line.startswith("**Template version:"))
        policy.write_text(original.replace(version_line, "**Template version: 2.0.0**"))
        commit_fixture(self.repo)
        run("git", "push", "-q", cwd=self.repo)
        before = self.remote_head()
        values = self.sync()
        self.assertEqual(values["SYNC-CHANGED"], "1")
        self.commit(values)
        after = self.remote_head()
        self.assertNotEqual(before, after)
        self.assertEqual(policy.read_text(), original)
        self.assertEqual(run("git", "diff-tree", "--no-commit-id", "--name-only", "-r",
                             "HEAD", cwd=self.repo), "records/REPO.md\n")
        self.assertEqual(self.sync()["SYNC-CHANGED"], "0")
        self.assertEqual(self.remote_head(), after)

    def test_mode_only_changes_are_committed_and_repeat_is_noop(self):
        self.commit(self.sync())
        relative = "scripts/sync-preflight.py"
        source = self.template / "scaffold/sync-preflight.py"
        target = self.repo / relative
        original = target.read_bytes()
        for old, new in ((0o755, 0o644), (0o644, 0o755)):
            with self.subTest(source_mode=oct(new)):
                self.assertEqual(target.stat().st_mode & 0o777, old)
                source.chmod(new)
                commit_fixture(self.template)
                before = self.remote_head()
                values = self.sync()
                self.assertEqual(values["SYNC-CHANGED"], "1")
                self.assertEqual(values["SYNC-VERSION"], "2.0.7")
                self.assertEqual(target.stat().st_mode & 0o777, new)
                self.assertEqual(target.read_bytes(), original)
                summary = f" mode change {0o100000 | old:o} => {0o100000 | new:o} {relative}\n"
                self.assertEqual(run("git", "diff", "--summary", cwd=self.repo), summary)
                self.commit(values)
                after = self.remote_head()
                self.assertNotEqual(after, before)
                self.assertEqual(run("git", "rev-parse", "HEAD", cwd=self.repo).strip(), after)
                self.assertEqual(run("git", "diff-tree", "--no-commit-id", "--summary",
                                     "-r", "HEAD", cwd=self.repo), summary)
                self.assertEqual(run("git", "diff-tree", "--no-commit-id", "--numstat",
                                     "-r", "HEAD", cwd=self.repo), f"0\t0\t{relative}\n")
                self.assertEqual(run("git", "status", "--porcelain", cwd=self.repo), "")
                values = self.sync()
                self.assertEqual(values["SYNC-CHANGED"], "0")
                self.commit(values)
                self.assertEqual(self.remote_head(), after)


if __name__ == "__main__":
    unittest.main()
