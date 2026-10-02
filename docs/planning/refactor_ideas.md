# Teaching Refactor Ideas

## Status

This document banks a breadth-first review of the repository as material for
teaching high-school students how to code. It is **not** a specification, a
curriculum, or an instruction to implement every item below.

The review intentionally looked across many demos quickly. That makes it useful
for discovering themes and possible follow-up work, but it also means some ideas
may change or disappear after a deeper review of an individual demo, its intended
student, or the way it is actually taught.

In particular:

- Do not treat shorter code or fewer concepts as automatically better teaching.
- Do not assume students must understand every line of a working project before
  they can productively modify it.
- Do not hide so much implementation that students only edit configuration.
- Preserve examples that expose real software structure when that exposure is
  part of the lesson.
- Prefer adding complementary lessons over flattening every demo into the same
  beginner progression.

### Maintainer decision: `python_basics/main_keywords.py`

`python_basics/main_keywords.py` stays as-is. It is a deliberate broad survey of
Python concepts. Earlier review suggested splitting or simplifying it; that is
**not** the direction to take.

Smaller, focused lessons can be added around it so students can study individual
ideas in more depth before or after seeing the broad survey. The existence of a
focused lesson should not require rewriting `main_keywords.py`.

## Teaching goals worth optimizing for

These are candidate design goals rather than hard requirements:

1. **Fast cause-and-effect.** A student should often be able to make a small
   change, run the program, and see what changed.
2. **Actual programming.** Easy entry points are useful, but students should
   progress from changing data/constants into writing expressions,
   conditionals, loops, and functions.
3. **Visible progression.** When a project is intended to teach organization or
   architecture, adjacent stages should make the new idea identifiable.
4. **Authentic software.** Larger engines and real project structure are useful
   when students have a deliberately chosen surface from which to enter them.
5. **Low setup friction.** Environment and dependency work should be taught
   intentionally rather than encountered accidentally before the interesting
   part of a lesson.
6. **Room for depth.** Each demo should be reviewed in its own teaching context
   before broad refactors are applied across the repository.

## Cross-cutting ideas to investigate

### Add a clearer map of learning paths

The root README currently orders projects roughly by comfort level. It may be
useful to make the different purposes more explicit instead of presenting one
linear ladder.

One possible framing is:

- **Learn Python concepts** -- syntax, expressions, control flow, collections,
  functions, debugging.
- **Build and modify games** -- use visible game behavior as feedback while
  gradually writing more code.
- **Explore real software** -- inspect larger programs, architecture, historical
  code, libraries, and implementation details without requiring full mastery.

This is only one possible organization. A deeper pass should determine whether
students actually benefit from explicit lanes or whether the current loose
collection works better in practice.

### Add focused lessons without replacing survey examples

`notes/lesson-idea.md` already sketches a useful toolbox of concepts: literals
and variables, operators, expressions, conditionals, collections, loops,
functions, imports, and errors.

A candidate extension is to add small runnable lessons for individual concepts.
These could supplement broad examples such as `main_keywords.py`, not replace
them. Small files also give teachers convenient places to isolate a concept when
a student gets stuck.

Questions for a deeper pass:

- Which concepts actually need dedicated lessons?
- Which concepts are better learned inside a game or other motivating project?
- Should the focused examples precede a survey, follow it, or be used on demand?
- How much repetition is useful before it becomes busywork?

### Distinguish "student edit surface" from "whole program"

Several projects can reasonably contain hundreds or thousands of lines if a
student is not expected to understand all of them at once. The more important
question is whether the intended entry point is obvious.

For each larger project, consider documenting:

- the first file a student should open;
- the first five-minute edit;
- the code they are expected to understand now;
- code they can safely ignore for the current lesson;
- a next step that crosses one boundary deeper into the implementation.

A separate student-facing file can sometimes help, but it should not become a
rule. Keeping the student next to the real implementation may be better when the
lesson is about reading unfamiliar code.

### Move from customization into programming

Changing colors, constants, map data, characters, or item definitions is a good
way to get an immediate success. It is not sufficient by itself for a coding
curriculum.

A useful progression inside a project might be:

1. change a value;
2. change an expression;
3. add a conditional rule;
4. use a loop over existing data;
5. write or modify a function;
6. add a new behavior that combines several ideas.

This progression should be adapted to each demo rather than imposed mechanically.

### Add prediction and explanation to exercises

Many exercises can become stronger without changing the program at all. A
possible structure is:

1. **Predict** what a change will do.
2. **Change** the code.
3. **Run** the program and observe it.
4. **Explain** why the result did or did not match the prediction.

This encourages students to build a model of program execution instead of only
searching for settings that look good.

For deterministic helper functions, small `assert` examples may also provide a
lightweight introduction to checking assumptions before introducing a testing
framework.

### Treat setup as curriculum only when intended

The top-level projects with `pyproject.toml` already try to support `python
main.py` and report missing dependencies. That direction is useful.

A deeper review could ask whether each first-run path:

- reaches visible output quickly;
- gives a useful message when a dependency is missing;
- avoids pulling in optional dependencies for features the student is not using;
- behaves consistently across classroom machines;
- has a deliberate later lesson for environments, packages, editable installs,
  Git, and other project tooling.

The goal is not to hide tooling forever. It is to choose when it enters the
lesson.

### Use friendly validation at student-authored boundaries

When students type identifiers or build declarative content, an engine can often
turn a typo into a targeted teaching moment. For example, a missing move,
character, track, or team id could report the bad value and nearby known values
instead of exposing an implementation-level traceback.

This is most useful at APIs intentionally presented as student edit surfaces. A
normal Python traceback should still be available when the lesson is explicitly
about debugging Python.

## Project-specific discoveries

These are observations and candidate directions to preserve for later, not
approved refactors.

### `python_basics`

- Keep `main_keywords.py` unchanged.
- Consider adding focused companion lessons for concepts that teachers want to
  isolate or revisit.
- Preserve the distinction between a **survey of many language features** and a
  **single-concept lesson**; both can be useful.
- A future teacher guide could suggest several ways to use `main_keywords.py`:
  first exposure, keyword scavenger hunt, code tracing, or review after focused
  lessons.

### `choose_your_own_adventure`

The versioned adventure is a natural place to teach how a program evolves, but
there are several different dimensions of growth mixed together: world content,
control flow, data modeling, code organization, UI, and architecture.

Snapshot from this review:

| File | Approximate size |
| --- | ---: |
| `version0.py` | 184 lines |
| `version1.py` | 691 lines |
| `version2.py` | 609 lines |
| `version3.py` | 1,596 lines |
| `version4.py` | 2,679 lines |
| `version6.py` | 3,658 lines |
| `version7.py` | 4,173 lines |
| `version8.py` | 3,835 lines |

Line count is not itself a problem. The follow-up question is whether a student
can tell what changed *conceptually* between neighboring versions.

Ideas to investigate:

- Keep the story/world more constant across selected adjacent stages when the
  teaching objective is specifically code organization. This can make diffs more
  legible because the architecture changes while the behavior stays familiar.
- Alternatively, if expanding the world is part of the motivation, explicitly
  call out which changes are new content and which introduce a new programming
  idea.
- Identify the point where later versions become architecture/reference examples
  rather than files intended to be read top-to-bottom by a beginner.
- Consider teacher notes that identify a small set of functions or subsystems to
  inspect in the larger versions.

Before changing the progression, review the versions in depth. There may be
teaching intent encoded in their current differences that a breadth-first pass
missed.

### `platformer`

Promising current student-facing surfaces include `platformer/settings.py` and
level/map data. The project would benefit from the same kind of student guide the
RPG already has.

Ideas to investigate:

- Add a sequence of edits that progresses from constants/map data to physics or
  game-rule code.
- Make it clear which files are intended for first edits and which are engine or
  asset plumbing.
- Check whether rectangle-only mode can avoid importing sprite/Pillow-related
  machinery until sprite mode is enabled. `sprites.py` currently imports
  `SpriteSheet` and `get_default_paths` even with `USE_SPRITES = False`.
- Remove developer-local commented paths in `sprites.py` if they are no longer
  useful documentation.
- Audit tile-map characters and their meaning; make accidental or unsupported
  characters produce a useful error instead of being silently surprising.

These are good candidates for a focused platformer review because dependency
loading and level semantics should be understood before refactoring them.

### `rpg`

The separation between `src/rpg_battle/content/` and engine code is a useful
teaching direction. The current student guide gives approachable customization
entry points.

Ideas to investigate:

- Add exercises that explicitly cross from content editing into writing
  conditionals, loops, and functions.
- Decide how much of the typed/model construction syntax should be visible to a
  beginner. A thin helper API might make some first exercises easier, but could
  also hide useful real Python structure.
- Add friendly validation for student-authored ids where appropriate.
- Create a path for progressively entering engine code instead of treating
  `content/` as a permanent boundary.

Concrete documentation drift noticed during this review:

- `rpg/docs/student_guide.md` and `rpg/README.md` say the default battle track is
  `soft_dungeon_crawl`.
- `src/rpg_battle/content/audio.py` currently sets
  `DEFAULT_BATTLE_TRACK = "bluesy_overhaul"`, and a test asserts that value.

That mismatch should be handled separately from larger teaching refactors.

### `fpx3d`

The README's "One-Hour Student Mods" and the comments in the implementation
already establish a useful first-edit mindset.

Ideas to investigate:

- Make the student edit region easier to find, possibly by moving level/rule data
  to its own small module. Do this only if it improves teaching; the current
  single-file locality may also be valuable.
- Add exercises that require writing a conditional, loop, or function rather than
  only moving objects or changing constants.
- Consider whether beginner-facing data should use plain Python values and let
  the engine convert them to Panda3D-specific types, or whether direct exposure
  to Panda3D types is part of the intended lesson.
- Give students a deliberate path from modifying arena data into understanding
  one engine behavior such as collection, hazards, jumping, or scoring.

### `rts`

The README already provides important context: this is a fairly faithful port of
a 2007 high-school project and is explicitly **not** presented as a best-practice
RTS implementation.

That history is educational and should not be erased merely to make the code
look modern.

Possible uses to investigate:

- Treat the original as a "real student project" or code-archaeology example.
- Ask students to find duplicated logic, large responsibilities, state, or places
  they would refactor.
- If a simpler RTS is desired for introductory construction, consider a separate
  `rts_lite`-style project rather than rewriting the historical artifact into
  something it never was.

### `manim/hello_world`

The current example is a richer animation: scene construction, a moving circle,
a parametric sine path, tracing, transformations, and render configuration. It
can be useful precisely because it demonstrates several capabilities at once.

Rather than assuming it should be simplified, investigate adding smaller Manim
examples alongside it, such as:

- create text or one shape;
- move a shape;
- define a small path;
- then study the existing richer example.

This follows the same general principle as `main_keywords.py`: a broad example
can stay broad while focused examples provide depth.

### `teaching/tranforms.md`

The affine-transform lesson moves quickly into homogeneous coordinates, NumPy,
matrix multiplication, and Matplotlib.

Possible preceding lesson:

- transform a handful of `(x, y)` points using ordinary Python arithmetic;
- write the transformation as a function;
- apply it with a loop;
- then show how matrices/NumPy generalize the same operation.

That would let a coding lesson and a matrix lesson reinforce each other. It is
also possible that the current audience is already ready for NumPy, so this
should be decided from classroom context rather than assumed.

Minor cleanup candidate: the filename is currently `tranforms.md`; consider
renaming it to `transforms.md` if nothing intentionally depends on the existing
name.

### `teaching/challenge_problems.md`

The Two Sum material includes Lean/formalization content. That can be a strong
extension for advanced students, but it is conceptually distinct from solving
Two Sum in introductory Python.

Ideas to investigate:

- Label the Lean section as an optional formal-methods extension if the document
  is meant to serve students at several levels.
- State the intended Two Sum semantics explicitly. The shown Lean proposition
  allows `i == j`, so `[5]` with target `10` evaluates true. Many formulations of
  Two Sum require two distinct indices. Either interpretation is valid if it is
  deliberate and explained.

## Things not to standardize prematurely

A future refactor should resist turning every demo into the same shape.
Different examples can teach different skills:

- tracing unfamiliar code;
- editing a small self-contained script;
- working through a deliberately broad survey;
- extending a data-driven game;
- crossing a library/API boundary;
- debugging a real traceback;
- reading legacy code;
- refactoring toward better structure;
- using a professional engine without first understanding its internals.

The repository can benefit from this variety as long as teachers and students
can tell what each example is for.

## Questions for the deeper review

Before making substantial changes to any individual demo, answer as many of
these as possible:

1. What age/experience level is this demo actually targeting?
2. Is it teacher-led, self-guided, or both?
3. Is the student expected to read the whole program or work from a selected
   edit surface?
4. What is the first meaningful success the student should achieve?
5. What new programming idea is the demo supposed to teach?
6. Which existing concepts does it assume?
7. What should a student be able to write themselves by the end?
8. Is setup/tooling part of the lesson or merely a prerequisite?
9. Is authenticity more important here than minimal complexity?
10. What parts are historical or demonstrative artifacts that should be
    preserved rather than normalized?
11. Can the exercise distinguish prediction/reasoning from trial-and-error?
12. How does the next lesson deepen the same idea rather than only introducing
    another one?

## Candidate follow-up passes

Instead of implementing this list wholesale, a useful next step would be to pick
one area and review it in depth. Possible passes include:

- the adventure version-to-version teaching progression;
- a complete platformer student lesson sequence;
- the RPG boundary between content editing and programming;
- focused Python lessons that complement `main_keywords.py`;
- a teacher-facing map showing prerequisites and intended learning outcomes for
  every demo;
- classroom setup and error-message behavior on clean Windows/Linux machines.

Each deeper pass should be allowed to contradict or discard ideas in this
breadth-first note.
