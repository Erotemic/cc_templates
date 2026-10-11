# Build-a-feature assignments

**Each workshop adds something playable that is not in its starting game.** The
assignments are for 30–60 minute sessions. They use the beginner and
intermediate *reference templates* without changing them, and need only Python
and a terminal. Start at the level where the underlying Python concepts are
familiar. An assignment is a small feature project, not an instruction to
refactor code for its own sake.

## Start a workshop

Open a terminal in `choose_your_own_adventure/` and run:

```bash
python assignments/start.py B01
python assignments/work/B01.py
python assignments/check.py B01
```

Change `B01` to the assignment you want to work on. **Read the worksheet
before editing.** The `start.py` command copies the *entire* starting program
into `assignments/work/B01.py`; students edit only their copy. It refuses to
overwrite existing work. The `.gitignore` in `work/` protects student drafts
from accidentally entering the template repository. To intentionally submit
work, copy the finished file to your class submission location.

Every assignment is **independent**: B02 starts from the original
`beginner/version1.py`, not from B01. That keeps prerequisite knowledge clear,
means a student can join the course late, and preserves the tiny story as a
reference. To build one larger personal game instead, merge selected features
into a separate project *after* completing the individual workshops.

## Choose an assignment

| ID | Time | Starting template | New playable feature | Main programming concept |
| --- | --- | --- | --- | --- |
| [B01](beginner/B01_orchard.md) | 35–45 min | beginner v1 | Visit an orchard and return | Dictionaries, `if`/`elif` |
| [B02](beginner/B02_hidden_coins.md) | 35–50 min | beginner v1 | Find coins only once | Numbers, state, `if` |
| [B03](beginner/B03_rope_bridge.md) | 45–60 min | beginner v1 | Unlock a rope bridge with an item | Lists, membership, conditions |
| [B04](beginner/B04_travel_hints.md) | 30–45 min | beginner v2 | Ask for situation-aware hints | Functions, arguments, returns |
| [B05](beginner/B05_travel_journal.md) | 45–60 min | beginner v2 | Read a journal of places visited | Lists, loops, helper functions |
| [I01](intermediate/I01_lookout.md) | 30–45 min | intermediate v1 | Explore a lookout and telescope | Room data, data-only choices |
| [I02](intermediate/I02_berry_barter.md) | 45–60 min | intermediate v1 | Trade a berry for a charm | Function dispatch, inventory, state |
| [I03](intermediate/I03_field_notes.md) | 45–60 min | intermediate v2 | Open a visit-history journal | Object state, sets, API separation |
| [I04](intermediate/I04_hidden_watchtower.md) | 45–60 min | intermediate v2 | Learn a secret route to a watchtower | Object state, legal actions |
| [I05](intermediate/I05_healing_potion.md) | 45–60 min | intermediate v3 | Find and drink a healing potion | Conditions, inventory, boundaries |
| [I06](intermediate/I06_defend.md) | 40–55 min | intermediate v3 | Defend instead of attacking | Combat state, arithmetic, methods |
| [I07](intermediate/I07_pacify_spider.md) | 50–60 min | intermediate v3 | Reach the tower without fighting | Boolean logic, alternate paths |
| [I08](intermediate/I08_lake_crab.md) | 50–60 min | intermediate v3 | Fight a second enemy for gold | Dataclasses, generalization, state |

## How to use the checks

`python assignments/check.py B01` checks Python syntax and whether the game
still starts and can quit. **Beginner features are checked by playing the
specific steps on the worksheet**, not by testing the exact wording of a
student's story. A passing command for a beginner file does *not* mean the new
feature is complete.

For **intermediate assignments**, `check.py` also exercises the new feature
through the existing game functions or `Game` API. These checks use the action
IDs and item names specified in the worksheet: those names are contracts with
the test, not rules for the prose a student prints. Students are free to
rewrite descriptions, prompts, and narrative. All checks use the Python
standard library; no `pytest` installation is required. The tool also checks
that the original treasure / Star Crystal objective remains achievable.

The final acceptance test for **every** assignment is a human playing the game
and seeing the promised feature. Automated checks complement, but do not
replace, that test.

## Workshop rhythm

Budget roughly **5 minutes** to play the starting program, **5 minutes** to
locate the code that controls the intended behavior, **20–35 minutes** to make
the feature, and **10 minutes** to test and explain it. When time is short,
prioritize the worksheet's **Done when** criteria; stretch challenges are
optional. Discuss what changed in the player's experience, which variables
record it, and why the feature still works after leaving and returning.

Instructors: see [INSTRUCTOR.md](INSTRUCTOR.md) for pacing, coaching, and
assessment guidelines.
