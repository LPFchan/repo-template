"""Run the shipped pre-commit hook against a staged fixture repository."""

from pathlib import Path
import subprocess
import tempfile
import unittest

HOOK = Path(__file__).resolve().parents[1] / "scaffold/.githooks/pre-commit"


class PreCommitLineLimitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)

    def stage(self, path, lines):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("x\n" * lines)
        subprocess.run(["git", "add", path], cwd=self.repo, check=True)

    def hook(self):
        result = subprocess.run(["sh", str(HOOK)], cwd=self.repo, text=True,
                                capture_output=True)
        self.assertEqual(result.returncode, 0)
        return result.stderr

    def test_long_code_file_warns_without_blocking(self):
        self.stage("src/big file.py", 1001)
        self.assertIn("src/big file.py has 1001 lines (limit 1000)", self.hook())

    def test_code_at_limit_docs_records_and_non_code_are_quiet(self):
        self.stage("src/ok.ts", 1000)
        self.stage("docs/guide.py", 2000)
        self.stage("records/notes.sh", 2000)
        self.stage("README.md", 2000)
        self.stage("package-lock.json", 2000)
        self.assertEqual(self.hook(), "")

    def test_only_staged_content_is_measured(self):
        self.stage("app.go", 10)
        (self.repo / "app.go").write_text("x\n" * 5000)
        self.assertEqual(self.hook(), "")


if __name__ == "__main__":
    unittest.main()
