from __future__ import annotations

"""Normalized content catalog consumed by the RPG engine.

The engine receives one explicit :class:`GameContent` bundle instead of
importing a particular classroom game's modules.  This keeps engine mechanics
reusable and lets a student-authored game compile into the same runtime model.
"""

from dataclasses import dataclass
from typing import Mapping

from rpg_battle.audio.library import FileTrackSpec, GeneratedTrackSpec, SynthSoundSpec
from rpg_battle.core.models import CharacterSpec, EncounterSpec, MoveSpec, TeamSpec
from rpg_battle.core.scripting import (
    script_source_label,
    smoke_test_ai_strategy,
    smoke_test_move_script,
)
from rpg_battle.render.effect_builder import EffectSpec

Color = tuple[int, int, int]
PaletteSpec = Mapping[str, Color]
SpriteRecipe = Mapping[str, object]
MusicSpec = GeneratedTrackSpec | FileTrackSpec


@dataclass(frozen=True)
class PresentationSpec:
    """Content ids used by the generic battle presentation layer."""

    basic_attack_move_id: str
    menu_move_sound_id: str
    menu_confirm_sound_id: str
    menu_back_sound_id: str
    damage_sound_id: str
    heal_sound_id: str
    ko_sound_id: str
    switch_sound_id: str
    defend_sound_id: str
    heal_effect_id: str


@dataclass(frozen=True)
class ContentIssue:
    """One student-facing validation problem."""

    where: str
    message: str

    def __str__(self) -> str:
        return f"{self.where}: {self.message}"


class ContentValidationError(ValueError):
    """Raised when student-authored content cannot be safely launched."""

    def __init__(self, issues: list[ContentIssue]) -> None:
        self.issues = issues
        super().__init__(format_validation_report(issues))


@dataclass(frozen=True)
class GameContent:
    """Complete, normalized content bundle for one game."""

    title: str
    moves: Mapping[str, MoveSpec]
    characters: Mapping[str, CharacterSpec]
    teams: Mapping[str, TeamSpec]
    encounters: Mapping[str, EncounterSpec]
    palettes: Mapping[str, PaletteSpec]
    sprites: Mapping[str, SpriteRecipe]
    effects: Mapping[str, EffectSpec]
    music_tracks: Mapping[str, MusicSpec]
    sound_effects: Mapping[str, SynthSoundSpec]
    presentation: PresentationSpec
    default_encounter_id: str
    default_battle_track: str
    default_victory_track: str
    default_defeat_track: str

    @property
    def default_encounter(self) -> EncounterSpec:
        return self.encounters[self.default_encounter_id]

    def validate(self) -> list[ContentIssue]:
        """Return all content problems instead of stopping at the first one."""

        issues: list[ContentIssue] = []

        if not self.moves:
            issues.append(ContentIssue("game", "add at least one move"))
        if not self.characters:
            issues.append(ContentIssue("game", "add at least one character"))
        if not self.encounters:
            issues.append(ContentIssue("game", "add at least one battle"))

        valid_move_kinds = {"physical", "magical", "heal", "buff", "debuff", "status"}
        valid_target_modes = {
            "self", "single_enemy", "single_ally", "all_enemies", "all_allies", "none"
        }
        valid_effect_styles = {"ring", "projectile", "path", "burst_rect", "wind_arcs"}
        valid_path_modes = {"sine", "square", "stairs", "zigzag", "triangle"}

        for move_id, move in self.moves.items():
            where = f'move "{move.name}"'
            if move_id != move.move_id:
                issues.append(ContentIssue(where, f"catalog id is {move_id!r}, spec id is {move.move_id!r}"))
            if move.kind not in valid_move_kinds:
                issues.append(ContentIssue(where, f"unknown kind {move.kind!r}"))
            if move.target_mode not in valid_target_modes:
                issues.append(ContentIssue(where, f"unknown target mode {move.target_mode!r}"))
            if move.power < 0:
                issues.append(ContentIssue(where, "power cannot be negative"))
            if not 0.0 <= move.accuracy <= 1.0:
                issues.append(ContentIssue(where, "accuracy must be between 0.0 and 1.0"))
            if move.animation and move.animation not in self.effects:
                issues.append(
                    ContentIssue(where, f'animation "{move.animation}" is not defined in student_game/effects.py')
                )
            if move.sound_id and move.sound_id not in self.sound_effects:
                issues.append(
                    ContentIssue(where, f'sound "{move.sound_id}" is not defined in student_game/audio.py')
                )
            if move.script is not None:
                location = script_source_label(move.script)
                for problem in smoke_test_move_script(move.script):
                    issues.append(
                        ContentIssue(
                            f'{where} custom function at {location}',
                            problem,
                        )
                    )

        for effect_id, effect in self.effects.items():
            where = f'effect "{effect_id}"'
            if effect.style not in valid_effect_styles:
                issues.append(ContentIssue(where, f"unknown style {effect.style!r}"))
            if effect.style == "path":
                if effect.path is None:
                    issues.append(ContentIssue(where, "path effects need a path profile"))
                elif effect.path.mode not in valid_path_modes:
                    issues.append(ContentIssue(where, f"unknown path mode {effect.path.mode!r}"))

        for char_id, character in self.characters.items():
            where = f'character "{character.name}"'
            if char_id != character.char_id:
                issues.append(
                    ContentIssue(where, f"catalog id is {char_id!r}, spec id is {character.char_id!r}")
                )
            if character.max_hp <= 0:
                issues.append(ContentIssue(where, "hp must be greater than zero"))
            if not character.move_ids:
                issues.append(ContentIssue(where, "add at least one move to moves=[...]"))
            for move_id in character.move_ids:
                if move_id not in self.moves:
                    issues.append(ContentIssue(where, f'uses unknown move "{move_id}"'))
            if character.sprite_id not in self.sprites:
                issues.append(ContentIssue(where, f'uses unknown sprite "{character.sprite_id}"'))

        known_team_specs = list(self.teams.values())
        for team_id, team in self.teams.items():
            where = f'team "{team.name}"'
            if not team.members:
                issues.append(ContentIssue(where, "add at least one character"))
            if len(set(team.members)) != len(team.members):
                issues.append(ContentIssue(where, "the same character appears more than once"))
            if team.starting_active is not None and len(set(team.starting_active)) != len(team.starting_active):
                issues.append(ContentIssue(where, "the same starting character appears more than once"))
            for char_id in team.members:
                if char_id not in self.characters:
                    issues.append(ContentIssue(where, f'uses unknown character "{char_id}"'))
            if team.starting_active is not None:
                for char_id in team.starting_active:
                    if char_id not in team.members:
                        issues.append(
                            ContentIssue(where, f'starting character "{char_id}" is not on the team')
                        )
            if team.strategy is not None:
                location = script_source_label(team.strategy)
                for char_id in team.members:
                    character = self.characters.get(char_id)
                    if character is None:
                        continue
                    for problem in smoke_test_ai_strategy(
                        team.strategy,
                        user_name=character.name,
                        available_move_ids=frozenset(character.move_ids),
                    ):
                        issues.append(
                            ContentIssue(
                                f'{where} strategy at {location}',
                                f'for {character.name}: {problem}',
                            )
                        )

        for encounter_id, encounter in self.encounters.items():
            where = f'battle "{encounter.title}"'
            if encounter.player_team not in known_team_specs:
                issues.append(ContentIssue(where, "player team is not registered in this game"))
            if encounter.enemy_team not in known_team_specs:
                issues.append(ContentIssue(where, "enemy team is not registered in this game"))
            for label, team, limit in (
                ("player", encounter.player_team, encounter.active_limits[0]),
                ("enemy", encounter.enemy_team, encounter.active_limits[1]),
            ):
                if limit <= 0:
                    issues.append(ContentIssue(where, f"{label} active count must be positive"))
                if limit > len(team.members):
                    issues.append(
                        ContentIssue(
                            where,
                            f"wants {limit} active {label} characters, but team {team.name!r} has only {len(team.members)}",
                        )
                    )
            if encounter.music_track_id and encounter.music_track_id not in self.music_tracks:
                issues.append(
                    ContentIssue(where, f'uses unknown music track "{encounter.music_track_id}"')
                )

        presentation = self.presentation
        if presentation.basic_attack_move_id not in self.moves:
            issues.append(
                ContentIssue(
                    "game presentation",
                    f'basic attack move "{presentation.basic_attack_move_id}" is not defined',
                )
            )
        for label, sound_id in (
            ("menu move sound", presentation.menu_move_sound_id),
            ("menu confirm sound", presentation.menu_confirm_sound_id),
            ("menu back sound", presentation.menu_back_sound_id),
            ("damage sound", presentation.damage_sound_id),
            ("heal sound", presentation.heal_sound_id),
            ("knockout sound", presentation.ko_sound_id),
            ("switch sound", presentation.switch_sound_id),
            ("defend sound", presentation.defend_sound_id),
        ):
            if sound_id not in self.sound_effects:
                issues.append(
                    ContentIssue(
                        "game presentation", f'{label} "{sound_id}" is not defined'
                    )
                )
        if presentation.heal_effect_id not in self.effects:
            issues.append(
                ContentIssue(
                    "game presentation",
                    f'heal effect "{presentation.heal_effect_id}" is not defined',
                )
            )

        for sprite_id, recipe in self.sprites.items():
            palette_id = recipe.get("palette")
            if palette_id not in self.palettes:
                issues.append(
                    ContentIssue(f'sprite "{sprite_id}"', f'uses unknown palette "{palette_id}"')
                )
            shapes = recipe.get("shapes")
            if not isinstance(shapes, list) or not shapes:
                issues.append(ContentIssue(f'sprite "{sprite_id}"', "add at least one shape"))

        if self.default_encounter_id not in self.encounters:
            issues.append(
                ContentIssue("game", f'default battle "{self.default_encounter_id}" is not defined')
            )
        for label, track_id in (
            ("default battle music", self.default_battle_track),
            ("victory music", self.default_victory_track),
            ("defeat music", self.default_defeat_track),
        ):
            if track_id and track_id not in self.music_tracks:
                issues.append(ContentIssue("game", f'{label} "{track_id}" is not defined'))

        return issues

    def require_valid(self) -> "GameContent":
        issues = self.validate()
        if issues:
            raise ContentValidationError(issues)
        return self


def format_validation_report(issues: list[ContentIssue]) -> str:
    """Format validation failures for students instead of emitting a traceback."""

    count = len(issues)
    heading = f"Your game has {count} problem{'s' if count != 1 else ''}:"
    lines = [heading, ""]
    lines.extend(f"  {index}. {issue}" for index, issue in enumerate(issues, start=1))
    return "\n".join(lines)

_DEFAULT_CONTENT: GameContent | None = None


def set_default_content(content: GameContent) -> None:
    """Register the content bundle used by compatibility entry points.

    Normal application code should pass content explicitly. This hook exists so
    older classroom helpers such as ``new_battle()`` keep working after a game
    module has been loaded, without making the engine import that game.
    """

    global _DEFAULT_CONTENT
    _DEFAULT_CONTENT = content


def get_default_content() -> GameContent:
    """Return the registered default content or explain how to provide it."""

    if _DEFAULT_CONTENT is None:
        raise RuntimeError(
            "No RPG content has been loaded. Import student_game.CONTENT or pass content=... explicitly."
        )
    return _DEFAULT_CONTENT
