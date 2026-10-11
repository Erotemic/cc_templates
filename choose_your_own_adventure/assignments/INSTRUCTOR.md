# Instructor notes: feature-first workshops

These workshops target students who know enough Python to read their chosen
starting template. The goal for every session is a **new playable game
feature** and an explanation of the programming concept that made it work.
Clean code is useful, but a pure refactor does not meet the assignment goal.

## Teaching setup

1. Before class, run the appropriate **unmodified template** and the
   assignment's `Done when` playtest steps. Familiarize yourself with the
   new feature and with the original winning route.
2. Students work in `assignments/work/ID.py` after running
   `python assignments/start.py ID`. These are **independent forks**, not a
   cumulative series. Their templates are intentionally not edited in place.
3. Start with a 3–5 minute live demonstration of the *missing* feature.
   Example: show the current forest and ask what is required to make a bridge
   action work. Let students find the relevant code rather than providing
   completed code.
4. Allow 20–40 minutes to implement. Ask for the smallest working increment:
   first a visible choice, then the state transition, then the condition.
5. Reserve the final 10 minutes for students to run the game, try failure
   cases (no item, already collected, full HP, etc.), and explain one state
   change. Optional stretch work is not required.

`assignments/check.py` is *feedback*, not an examiner of a student's writing
style. It checks syntax and graceful startup for all lessons, and behavior via
the game API for intermediate lessons. Beginner feature completion is checked
using the worksheet's manual playtest because those games deliberately have no
separate game API. **Do not tell beginner students that a green syntax/smoke
check proves the feature works.**

The intermediate worksheets declare a few fixed action IDs, room keys, flags,
and item names. Those are interface contracts for the optional checker, not
requirements on displayed dialogue. Students may write their own prose,
add choices, and use different internal helpers.

## Concepts and sequencing

- **B01 → B02 → B03**: dictionary lookup and control flow, then persistent
  numeric state, then inventory-dependent behavior. Each starts from beginner
  v1 so students see how complexity grows in a single loop.
- **B04 → B05**: parameters and return values, then functions that format
  state collected across many turns. Each starts from beginner v2.
- **I01 → I02**: room-only data versus a real new mechanic that needs handler
  functions and state. Both use intermediate v1.
- **I03 → I04**: an object records events; then it uses that state to control
  which actions are legal. Both use intermediate v2.
- **I05 → I06 → I07 → I08**: HP bounds, combat branching, Boolean conditions
  for alternate solutions, and finally generalizing a mechanic that originally
  assumed one enemy. All use intermediate v3.

A student does *not* have to complete the preceding assignments before starting
another, provided they understand the starting template. For students who want
a longer project, combining independently completed features into one game is
a separate design challenge, not something the 30–60 minute timing assumes.

## Coaching guide

| Student symptom | Helpful question (without giving the solution) |
| --- | --- |
| A new menu choice appears but does nothing | Where does its action label get handled? |
| Game forgets a pickup after one turn | Where is this variable initialized relative to the loop? |
| A locked exit shows up anyway | Who decides legal actions: the game or the console? |
| Inventory gains duplicate items | What state records that the reward was already taken? |
| A new room crashes on arrival | Does its key exactly match the destination in the exit? |
| The same enemy flag is set for all fights | Is the rule about *combat in general* or *this enemy*? |
| Student rewrites the whole engine | Can this feature fit in one data entry, condition, or handler? |

## Assessment

A lightweight 4-part check is more informative than counting lines or enforcing
one exact solution:

1. **Feature (primary):** The specified new interaction actually works for a
   player, including an appropriate success state.
2. **Rules:** The important boundary/failure case works too (not enough gold,
   item missing, repeating a reward, HP limit, illegal action, etc.).
3. **Existing story:** The original template's winning objective still works.
4. **Explanation:** The student can identify the state that changes, the code
   that offers the action, and the code that applies it.

During review, have the student **show** the feature. Avoid grading narration
phrasing, ASCII art, or the particular helper names they chose. The checks are
written to avoid testing exact printed story text.

## Extension for early finishers

Ask students to introduce a *second* instance of the new idea rather than a new
framework: another inspection choice, a second guarded location, a different
item trade, or another safe way past an obstacle. A student ready for automated
testing can call `Game.choices()` and `Game.apply()` from a tiny script rather
than automating terminal input.

## Technical notes

- The starting versions remain readable, independently runnable files. There
  is no new dependency on a teaching engine, package, or test framework.
- The checker needs Python 3.10 or newer, matching the existing code's use of
  `str.removeprefix` and built-in generic types.
- `start.py` will never overwrite a student file. To restart, first move or
  rename the old file manually, and then run `start.py` again.
- Intermediate checks ensure the original victory path is still possible.
  They intentionally avoid exact menu positions or story text.
- Keep students' drafts separate from the repository baseline; do not run the
  repository's full test suite on partially completed student work.
