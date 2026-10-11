"""Check workshop tooling without asserting exact student-facing story text."""

import ast
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
ASSIGNMENTS_DIR = ROOT / "assignments"
sys.path.insert(0, str(ASSIGNMENTS_DIR))
try:
    from catalog import ASSIGNMENTS
    import start as workshop_start
finally:
    sys.path.remove(str(ASSIGNMENTS_DIR))


def test_assignments_have_self_contained_starters_and_worksheets():
    assert len(ASSIGNMENTS) == 13
    assert set(ASSIGNMENTS) == {
        "B01", "B02", "B03", "B04", "B05",
        "I01", "I02", "I03", "I04", "I05", "I06", "I07", "I08",
    }
    for assignment_id, (starting_file, worksheet) in ASSIGNMENTS.items():
        source = ROOT / starting_file
        sheet = ASSIGNMENTS_DIR / worksheet
        assert source.is_file(), assignment_id
        assert sheet.is_file(), assignment_id
        assert "version" in source.name
        ast.parse(source.read_text(encoding="utf-8"))
        assert sheet.read_text(encoding="utf-8").startswith(f"# {assignment_id}")


def test_starter_copies_source_without_overwriting_student_work(tmp_path, monkeypatch):
    destination = tmp_path / "B01.py"
    monkeypatch.setattr(workshop_start, "work_file", lambda _id: destination)

    workshop_start.main(["B01"])
    assert destination.read_bytes() == (ROOT / "beginner/version1.py").read_bytes()
    destination.write_text("# my saved changes\n", encoding="utf-8")

    with pytest.raises(SystemExit) as exc:
        workshop_start.main(["B01"])
    assert exc.value.code == 1
    assert destination.read_text(encoding="utf-8") == "# my saved changes\n"


@pytest.mark.parametrize("assignment_id", [
    "I01", "I02", "I03", "I04", "I05", "I06", "I07", "I08",
])
def test_unmodified_intermediate_template_is_not_a_completed_feature(assignment_id):
    source, _ = ASSIGNMENTS[assignment_id]
    result = subprocess.run(
        [sys.executable, str(ASSIGNMENTS_DIR / "check.py"), assignment_id,
         "--file", str(ROOT / source)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=10,
        check=False,
    )
    assert result.returncode == 1, result.stdout + result.stderr


def test_beginner_check_is_only_a_smoke_check():
    source, _ = ASSIGNMENTS["B01"]
    result = subprocess.run(
        [sys.executable, str(ASSIGNMENTS_DIR / "check.py"), "B01",
         "--file", str(ROOT / source)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=10,
        check=False,
    )
    assert result.returncode == 0, result.stderr
