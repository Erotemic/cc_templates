"""Assignment IDs and independent starting templates.

This is instructor tooling, not part of the code students are asked to edit.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent

# id: (starting file relative to choose_your_own_adventure/, worksheet)
ASSIGNMENTS = {
    "B01": ("beginner/version1.py", "beginner/B01_orchard.md"),
    "B02": ("beginner/version1.py", "beginner/B02_hidden_coins.md"),
    "B03": ("beginner/version1.py", "beginner/B03_rope_bridge.md"),
    "B04": ("beginner/version2.py", "beginner/B04_travel_hints.md"),
    "B05": ("beginner/version2.py", "beginner/B05_travel_journal.md"),
    "I01": ("intermediate/version1.py", "intermediate/I01_lookout.md"),
    "I02": ("intermediate/version1.py", "intermediate/I02_berry_barter.md"),
    "I03": ("intermediate/version2.py", "intermediate/I03_field_notes.md"),
    "I04": ("intermediate/version2.py", "intermediate/I04_hidden_watchtower.md"),
    "I05": ("intermediate/version3.py", "intermediate/I05_healing_potion.md"),
    "I06": ("intermediate/version3.py", "intermediate/I06_defend.md"),
    "I07": ("intermediate/version3.py", "intermediate/I07_pacify_spider.md"),
    "I08": ("intermediate/version3.py", "intermediate/I08_lake_crab.md"),
}


def work_file(assignment_id):
    return ROOT / "work" / f"{assignment_id}.py"
