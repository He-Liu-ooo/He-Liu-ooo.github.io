from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class RepositoryPrivacyTests(unittest.TestCase):
    def test_gitignore_excludes_private_and_workflow_sources(self):
        gitignore_path = ROOT / ".gitignore"
        self.assertTrue(gitignore_path.is_file(), ".gitignore must exist")
        ignored = {
            line.strip()
            for line in gitignore_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
        required = {"/CV.pdf", ".worktrees/", ".superpowers/", "docs/superpowers/"}
        missing = required - ignored
        self.assertFalse(missing, f"Missing .gitignore entries: {sorted(missing)}")


if __name__ == "__main__":
    unittest.main()
