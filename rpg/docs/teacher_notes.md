# Teacher Notes

## Teaching objective

This project should support a long runway: a student can begin by editing a number and
eventually program game mechanics, procedural graphics, mathematical effects, AI, or
engine internals without switching to an unrelated codebase.

The project is intentionally richer than a minimal tutorial. The teaching boundary is
what changes: students begin in the small public authoring vocabulary under `student_game/`,
while the complete engine remains available underneath.

## Architecture to explain to students

```text
student Python objects in student_game/
          |
          v
rpg_battle.api.Game.compile()
          |
          v
validated GameContent
          |
          v
engine (rules / AI / rendering / audio)
```

The engine never imports the shipped game's content. `GameContent` is passed into the
runtime. `GamePresentation` carries the game's chosen basic attack, UI/combat sounds,
and standard heal effect, so the engine does not depend on magic ids such as `strike`.
The old `rpg_battle.content.*` modules are compatibility views only.

This matters pedagogically because students see real software separation rather than a
special classroom-only copy of the mechanics.

## Suggested progression

### 1. Values and prediction

Change stats, colors, sound frequencies, and team order. Ask students to predict the
result before running.

### 2. References and composition

Swap `Move`, `Character`, `Sprite`, `Music`, and `Team` objects. This reinforces that
variables can refer to structured objects and those objects can be composed.

### 3. Lists

Roster lists, move lists, shape lists, and the catalog lists provide repeated concrete
uses of ordered collections.

### 4. Functions and conditionals

Use custom move functions. The scripting surface deliberately exposes read-only facts
plus a small set of commands so students focus on control flow instead of mutation
bookkeeping.

### 5. Geometry and math

Procedural art and custom path functions connect coordinates, functions, waves, and
sampling to immediate visual feedback.

### 6. Software architecture

Trace one authored object through compilation to an internal spec and then through the
runtime. Discuss why the engine accepts `GameContent` instead of importing a particular
game.

### 7. Engine work

Students who are ready can change target selection, damage formulas, AI, menu flow,
rendering, or add a new authoring primitive.

## Good project prompts

- Design a new three-character party where every member has a distinct role.
- Write a move whose behavior changes below half health.
- Design a boss with a recognizable strategy rather than simply high stats.
- Create a new sprite from at least three geometric primitive types.
- Implement and visualize a mathematical function as a spell path.
- Create matching visual and audio identities for one character.
- Compare two balance changes by holding everything else constant.

## Keep the engine rich

Do not remove advanced content merely because a beginner does not understand it yet.
The starter game includes systems that can motivate later learning. Instead distinguish:

- what students are expected to edit now;
- what they may reuse without understanding yet;
- what they can inspect when they want to go deeper.

## Validation and classroom recovery

Use this before launching:

```bash
python main.py --check
```

The content validator catches cross-object problems before pygame starts. Syntax errors
and ordinary Python exceptions are intentionally not hidden; those remain opportunities
to learn normal debugging.

The preview tools shorten the edit-feedback cycle for art, effects, audio, and battle
layout. Prefer them when a lesson is about one subsystem rather than whole-game play.

## Current advanced areas

These remain appropriate for deeper students or instructor-guided exploration:

- `src/rpg_battle/core/rules.py`
- `src/rpg_battle/core/ai.py`
- `src/rpg_battle/battle/battle_scene.py`
- `src/rpg_battle/audio/tracks.py`
- `src/rpg_battle/render/`

They are not off-limits; they simply are not prerequisites for creating meaningful new
content.
