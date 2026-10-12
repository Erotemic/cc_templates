from __future__ import annotations

"""Small deterministic arena adapter over the actual RPG battle simulator."""

from dataclasses import dataclass, replace
import random

from rpg_battle.core.models import EncounterSpec, MoveSpec, TeamSpec
from rpg_battle.core.scripting import AIStrategy
from rpg_battle.teaching.simulate import SimulationResult, simulate_once
from student_game import CONTENT

ARENA_ID = "team_arena_match"
ROSTER = ("arena_guardian", "arena_mage")

# Classroom-specific content. No changes to the story game or combat formulas.
# Both sides get exactly the same two character templates and available moves.
MOVE_SPECS = (
    MoveSpec("arena_crush", "Crush", "physical", 20, 1.0, "single_enemy"),
    MoveSpec("arena_sweep", "Sweep", "physical", 7, 1.0, "all_enemies"),
    MoveSpec("arena_spark", "Spark", "magical", 19, 1.0, "single_enemy"),
    MoveSpec("arena_storm", "Storm", "magical", 10, 1.0, "all_enemies"),
    MoveSpec("arena_patch", "Patch", "heal", 17, 1.0, "single_ally"),
)

# Reuse the existing RPG's sprite recipes, changing only battle stats and moves.
GUARDIAN = replace(
    CONTENT.characters["guardian"],
    char_id="arena_guardian", name="Arena Guardian", role="defender",
    max_hp=78, attack=14, defense=11, magic=6, speed=6,
    move_ids=("arena_crush", "arena_sweep", "arena_patch"),
)
MAGE = replace(
    CONTENT.characters["moon_mage"],
    char_id="arena_mage", name="Arena Mage", role="caster",
    max_hp=59, attack=6, defense=6, magic=16, speed=10,
    move_ids=("arena_spark", "arena_storm", "arena_patch"),
)


def content_for_match(
    left_name: str, left: AIStrategy | None,
    right_name: str, right: AIStrategy | None,
):
    """Return an independent content bundle without mutating student_game.CONTENT."""
    first = TeamSpec(left_name, ROSTER, controller_type="ai", strategy=left)
    second = TeamSpec(right_name, ROSTER, controller_type="ai", strategy=right)
    encounter = EncounterSpec(ARENA_ID, "Algorithm Arena", first, second, (2, 2))
    return replace(
        CONTENT,
        moves={**CONTENT.moves, **{move.move_id: move for move in MOVE_SPECS}},
        characters={**CONTENT.characters, GUARDIAN.char_id: GUARDIAN, MAGE.char_id: MAGE},
        teams={**CONTENT.teams, "team_arena_left": first, "team_arena_right": second},
        encounters={**CONTENT.encounters, ARENA_ID: encounter},
    )


def single_match(
    left_name: str, left: AIStrategy | None,
    right_name: str, right: AIStrategy | None,
    *, seed: int = 0, max_steps: int = 300,
) -> SimulationResult:
    bundle = content_for_match(left_name, left, right_name, right)
    # The battle engine already uses a seed-local RNG. Seed the module-level RNG
    # too so ordinary student use of random.choice() is repeatable on replays.
    saved_state = random.getstate()
    try:
        random.seed(seed)
        return simulate_once(bundle, ARENA_ID, seed=seed, max_steps=max_steps)
    finally:
        random.setstate(saved_state)


@dataclass(frozen=True)
class MatchSummary:
    """Paired-seat results; unfinished games earn neither controller points."""

    left: str
    right: str
    wins: int
    losses: int
    draws: int
    unfinished: int
    seeds: int
    first_result: SimulationResult | None = None

    @property
    def matches(self) -> int:
        return self.wins + self.losses + self.draws + self.unfinished

    @property
    def score(self) -> float:
        return (self.wins + 0.5 * self.draws) / self.matches if self.matches else 0.0


def compare(
    left_name: str, left: AIStrategy | None,
    right_name: str, right: AIStrategy | None,
    *, runs: int, seed: int = 0, max_steps: int = 300,
) -> MatchSummary:
    """Use the same seed with swapped team seats for every matchup."""
    if runs <= 0:
        raise ValueError("runs must be positive")
    wins = losses = draws = unfinished = 0
    first_result = None
    for index in range(runs):
        game_seed = seed + index
        for swapped in (False, True):
            if swapped:
                result = single_match(right_name, right, left_name, left,
                                      seed=game_seed, max_steps=max_steps)
                who = None if result.winner is None else 1 - result.winner
            else:
                result = single_match(left_name, left, right_name, right,
                                      seed=game_seed, max_steps=max_steps)
                who = result.winner
                if first_result is None:
                    first_result = result
            if who is None:
                # The current RPG engine has no completed tied-game state.
                # winner=None means the simulation hit its step limit.
                unfinished += 1
            elif who == 0:
                wins += 1
            else:
                losses += 1
    return MatchSummary(left_name, right_name, wins, losses, draws, unfinished, runs, first_result)


def friendly_description() -> str:
    items = ["Two identical two-character teams (Guardian + Mage) start with full HP."]
    basic = CONTENT.moves[CONTENT.basic_attack_move_id]
    items.append(f"Every fighter can Attack (power={basic.power}) or Defend without learning a skill.")
    for character in (GUARDIAN, MAGE):
        items.append(
            f"{character.name}: HP={character.max_hp} attack={character.attack} "
            f"defense={character.defense} magic={character.magic} speed={character.speed}"
        )
        for name in character.move_ids:
            move = next(move for move in MOVE_SPECS if move.move_id == name)
            items.append(
                f"  {move.move_id}: {move.kind}, power={move.power}, "
                f"target={move.target_mode}, accuracy={move.accuracy:g}"
            )
    items.append("All moves use the RPG's actual damage/heal rules; defend reduces incoming damage.")
    return "\n".join(items)
