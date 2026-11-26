"""The `>>>` examples of the README and of each page in docs/ give the output that they show.

Each page runs in a fresh interpreter, because a page shows what a fresh process imports. An example of a backend
whose optional package is not installed is skipped, not failed: the CI test extra does not install every backend.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PAGES = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]

_RUN = r'''
import doctest, json, sys
from pathlib import Path

class Runner(doctest.DocTestRunner):
    missing = []

    def report_unexpected_exception(self, out, test, example, exc_info):
        error = exc_info[1]
        if isinstance(error, ImportError) and (error.name or isinstance(error.__cause__, ModuleNotFoundError)):
            self.missing.append(example.source.strip())
            return
        super().report_unexpected_exception(out, test, example, exc_info)

page = Path(sys.argv[1])
test = doctest.DocTestParser().get_doctest(page.read_text(encoding="utf-8"), {}, page.name, str(page), 0)
runner = Runner(optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
report = []
runner.run(test, out=report.append)
print(json.dumps({"examples": len(test.examples), "failures": runner.failures, "missing": runner.missing,
                  "report": "".join(report)}))
'''


@pytest.mark.parametrize("page", PAGES, ids=lambda page: page.relative_to(ROOT).as_posix())
def test_page_examples(page):
    done = subprocess.run([sys.executable, "-c", _RUN, str(page)], capture_output=True, text=True, check=True,
                          cwd=ROOT)
    result = json.loads(done.stdout.splitlines()[-1])
    if not result["examples"]:
        pytest.skip("no examples")
    assert result["failures"] == len(result["missing"]), result["report"]
    if result["missing"] and len(result["missing"]) == result["examples"]:
        pytest.skip(f"every example needs a backend that is not installed: {result['missing'][0]}")
