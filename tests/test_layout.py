"""Portfolio standard checks: the required files exist and no public file carries a grade.

There is no lock test: the repo is not pre-registered (PROPOSAL.md), so there is no
locked proposal to pin. When a confirmatory cycle locks PROPOSAL.md, add its SHA-256 here.
"""
import os
import re
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQUIRED = [
    "README.md", "PROPOSAL.md", "REPORT.md", "CHANGELOG.md", "CITATION.cff", "SECURITY.md", "LICENSE",
    "src/run_learn.py", "src/run_build.py", "src/run_deep.py", "src/stress.py", "src/export_texts.py",
    "results/results_learn.json", "results/results_build.json", "results/results_deep.json",
    "results/results_stress.json", "results/documents_export.json",
    "docs/decisions/0001-named-substitutions.md",
]
# Public grade forms: "8,700 of 10,000", "7650/10000", "Grade: ...", rubric columns like "/1000", "Grade (of 10)".
GRADE = re.compile(r"of 10,000|/ ?10,?000\b|\bGrade:|Grade \(of|/1000\b|\bgrade [0-9][0-9,]*/", re.IGNORECASE)


def public_files():
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    if not out:  # not a git checkout: walk the tree instead
        out = [os.path.relpath(os.path.join(d, f), ROOT) for d, _, fs in os.walk(ROOT)
               if "node_modules" not in d and ".git" not in d for f in fs]
    return [p for p in out if p.endswith((".md", ".jsx", ".js", ".html", ".cff")) and not p.startswith("tests/")]


class TestLayout(unittest.TestCase):
    def test_required_files_exist(self):
        missing = [p for p in REQUIRED if not os.path.exists(os.path.join(ROOT, p))]
        self.assertEqual(missing, [], "missing: " + ", ".join(missing))

    def test_no_public_grade(self):
        hits = []
        for p in public_files():
            with open(os.path.join(ROOT, p), encoding="utf-8", errors="replace") as f:
                for n, line in enumerate(f, 1):
                    if GRADE.search(line):
                        hits.append(f"{p}:{n}: {line.strip()}")
        self.assertEqual(hits, [], "grades are internal only:\n" + "\n".join(hits))

    def test_grade_pattern_catches_the_old_forms(self):
        for bad in ("Grade: 8,700 of 10,000.", "grade 7,650/10,000", "| Total /1000 |", "| Grade (of 10) |"):
            self.assertTrue(GRADE.search(bad), bad)
        self.assertIsNone(GRADE.search("158 of 160 fields, accuracy 0.9875"))

    def test_readme_abstract_and_lifecycle(self):
        with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as f:
            text = f.read()
        for key in ("**Question.**", "**Headline.**", "**Field.**", "**Job family.**", "**Verdict.**"):
            self.assertIn(key, text)
        stages = re.findall(r"^- (\w+): ", text.split("## Lifecycle", 1)[1], flags=re.M)[:8]
        self.assertEqual(stages, ["Question", "Proposal", "Baseline", "Build", "Evaluate", "Report", "Review",
                                  "Release"])


if __name__ == "__main__":
    unittest.main()
