# RPG engine architecture: one battle session

This is a map for an advanced student or maintainer. Beginning students edit
`student_game/workshop.py` or `team_arena/players/my_team.py` and do not need
to read engine internals.

## Follow one decision

```text
student_game/             Defines a game (fighters, moves, encounters)
      |
      v
catalog.GameContent       Full authoring + presentation catalog
      |
      +-----------------------------> BattleScene uses art, audio, effects
      |
      v
core.models.CombatContent  Only character, move, and basic attack definitions
      |
      v
BattleSession             Owns the active turn/round, RNG, pending decisions
      |   next_step() -> events + optional DecisionRequest
      |           ^
      |           | BattleAction or reserve fighter ID
      |      Human menu / student AI / built-in AI / recorded replay
      |           |
      |   submit(decision)
      v
core.rules               Validates the choice; modifies BattleState;
                         emits ordered factual events (including HP snapshots)
      |
      +--> BattleScene   Plays events as visuals, audio, and readable logs
      +--> simulator     Scores headless battles and collects statistics
      +--> recorder      Stores chosen decisions and RNG checkpoints
```

There is **one** turn-advancement implementation:
`src/rpg_battle/battle/session.py:BattleSession`. The graphical scene, teaching
simulator, and arena replay each supply *decisions* to that same session. They
do not choose the next actor or decide when a round ends.

## The session contract

A session has two methods to understand:

- `next_step()` makes **at most one automatic transition** (for example, round
  start, turn start, or end-of-round status ticks). It returns a `SessionStep`
  containing `events` and, if appropriate, a `DecisionRequest`. Calling it
  again when a request is waiting does not change the state or consume RNG.
- `submit(decision)` accepts the requested choice. For an `action` request,
  submit a `BattleAction`; for `replacement`, submit a living reserve fighter's
  ID. Invalid choices raise an error **without consuming the turn or RNG**.

```python
session = BattleSession(encounter, content=content, seed=42)
while not session.finished:
    step = session.next_step()
    display(step.events)
    if step.request is None:
        continue

    request = step.request
    decision = controller_for(request.team_index).choose(request, session.state)
    display(session.submit(decision))
```

The loop is illustrative; controller choice is not a special engine method.
Human input can take minutes, while an AI policy may produce a decision
immediately. Neither changes session mechanics. See the real loops in
`teaching/simulate.py` and `battle/battle_scene.py`.

`DecisionRequest` explicitly distinguishes an action from a forced replacement.
That distinction is important: replacing a fainted fighter is **not** an
ordinary turn action and should not consume its team's turn.

## State and responsibility

| Module | Owns | Does not own |
|---|---|---|
| `core/models.py` | Character/Move/Team specs, `BattleAction`, `BattleState`, narrow `CombatContent` | Input policies or graphics |
| `core/battle_state.py` | Instantiate fighters, active/reserve placements, replacement bookkeeping | Turn selection |
| `battle/session.py` | Turn order, RNG, round progression, pending requests, submission | Choosing *which* move an AI prefers |
| `core/rules.py` | Action legality, HP/status/stat effects, knockouts, factual events | Animation or menus |
| `core/ai.py` | Built-in AI and student strategy adapter | Turn progression |
| `battle/battle_scene.py` | Pygame menus, event playback, HUD, effects | Combat formulas or actor selection |
| `teaching/simulate.py` | Headless loop, results/statistics, optional recording hooks | Its own turn-state machine |
| `team_arena/recording.py` | Student prints and recorded decisions/RNG checkpoints | Its own combat resolver |
| `team_arena/viewer.py` | Spectator labels, printed output, playback controls | Intercepting or rewriting battle turns |

`BattleState` now contains `pending_turn_order`, `current_actor_id`, and
`round_announced`. Those were previously private `BattleController` fields.
The session owns **when** they change; they live with the combat state because
they are facts about the battle phase, not facts about the UI. Random-generator
state remains in the session, and the arena recording captures it where needed.

The combat state retains only `CombatContent` (characters, moves, basic attack
ID). It does **not** retain sprites, effect recipes, or music. Full
`GameContent` is still available to the outer application. Importing the
combat models or state helpers does not eagerly import the art/audio catalog.

## Invariants

1. Only the current actor may submit a `BattleAction`.
2. A request is fulfilled before the session advances to a different actor.
3. A forced replacement may be supplied by **either** team; the session never
   assumes team 0 is human or team 1 is AI.
4. Only learned skills are legal `Skill` actions; Attack and Defend are
   universally available. Target legality is checked before mutation or RNG.
5. A battle ends with `victory` or `draw`, and exactly one `battle_end` event.
   A simulation step limit is `ongoing`, never a completed draw.
6. Given the same content, initial seed, decisions, and RNG checkpoints, the
   simulator and visual replay must reach the same state and emit the same
   consequences.
7. A record of damage/heal/status ticks contains intermediate HP snapshots,
   rather than asking a renderer to reconstruct past state from final HP.
8. Mana belongs to each combatant: `0 <= current_mana <= max_mana`. A Skill
   action must be affordable **before** the session accepts the decision.
   Basic Attack and Defend cost 0 MP and restore 3 and 7 MP respectively, capped
   at each fighter's max. Skill cost is paid once, including when the move misses.
   Switching preserves each combatant's mana. `mana` events have before/after
   snapshots so replay/animation can show changes in order.

`BattleController` remains as a **thin compatibility facade** in
`battle/battle_controller.py` for older workshop/test callers. It delegates
all turn progression and submissions to `BattleSession`. New modules should
import `BattleSession` directly. It deliberately contains no independent turn
queue, actor selection, or combat rules.

## Trace a real decision without graphics

From `rpg/`, without installing pygame:

```bash
python trace_turn.py --encounter default --seed 3 --decisions 2
```

Use `python trace_turn.py --help` to list encounter IDs. The trace prints each
automatic event, the pending request, the chosen action or replacement, and the
resulting effects. For arithmetic detail inside a custom move, use the existing
teaching lab (`python lab.py scenario healing`, for example).

To trace the implementation, start at `BattleSession.next_step()`, follow
`BattleSession.submit()`, then `core.rules.resolve_action()` and
`_apply_move_command()`. Events flow outward to the simulator or the
`BattleScene._handle_battle_event()` presentation code.

## Extending without building a second system

- **New skill:** add one declarative `MoveSpec` or a student-authored move
  returning existing damage/heal/status/stat commands. Never copy the damage
  formula into the skill or controller.
- **New universal action:** add a `BattleAction` kind, centralized validation
  and resolution, then update the human menu and the student-facing helpers.
- **New controller:** implement a function to answer `DecisionRequest`. Use
  the session's existing `submit()` method; do not calculate damage or invent
  your own battle loop.
- **New animation:** consume ordered event fields. Graphics should not decide
  whether a hit landed or how much HP was lost.

## Mana: one resource model, not another turn loop

`MoveSpec.mana_cost` and `CharacterSpec.max_mana` define the rules.
`CombatantState.current_mana` is authoritative; `BattleSession.submit_action()`
uses `core.rules.validate_action()` to reject unaffordable moves without
changing RNG, mana, HP, or the pending decision. `core.mana.change_mana()`
clamps resources and emits a factual `mana` event; `resolve_action()` calls it
for spend/recovery. Both the human menu and built-in/student AI use the same
validator and see the same resource balance. Scripted moves pay a flat
per-use cost, *not* per effect command or affected target.

`TurnContext.user.mana`, `.max_mana`, `.skill_costs` and `.can_use(...)`
provide read-only observations to student controllers. The source of costs
is the registered `MoveSpec`, never a controller-supplied number. Legacy
content defaults to zero mana and zero-cost skills until authored explicitly.

## Deferred, independent cleanup
- **Active/reserve representation:** fighter activity flags and team roster
  membership still overlap. Simplifying them requires a separate migration
  with explicit invariant tests for switches, fainting, and animation slots.
- **Game authoring catalog:** the outer `catalog.py` still validates visual
  and gameplay content together. This does not leak into `CombatContent`, but
  the authoring/validation modules can eventually be separated further.
