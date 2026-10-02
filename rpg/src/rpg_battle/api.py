from __future__ import annotations

"""Student-facing authoring API.

The objects in this module are deliberately small Python building blocks.  A
student uses normal assignment, lists, functions, and object composition to
describe a game.  :class:`Game` then compiles those friendly objects into the
engine's stricter internal specs.
"""

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Callable, Iterable, Sequence

from rpg_battle.audio.library import FileTrackSpec, GeneratedTrackSpec, SynthSoundSpec
from rpg_battle.catalog import (
    ContentIssue,
    ContentValidationError,
    GameContent,
    PresentationSpec,
)
from rpg_battle.core.models import CharacterSpec, EncounterSpec, MoveEffect, MoveKind, MoveSpec, TeamSpec, TargetMode
from rpg_battle.core.scripting import (
    AIStrategy,
    AddStatus,
    ChangeStat,
    CommandTarget,
    Damage,
    Heal,
    MoveContext,
    MoveScriptResult,
)
from rpg_battle.render.effect_builder import EffectSpec, EffectStyle, PathMode, PathProfile

Color = tuple[int, int, int]
MoveScript = Callable[[MoveContext], MoveScriptResult]


def _slug(text: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip()).strip("_").lower()
    if not value:
        raise ValueError("Names must contain at least one letter or number")
    if value[0].isdigit():
        value = f"item_{value}"
    return value


def _id(explicit: str | None, name: str) -> str:
    return explicit or _slug(name)


def status(name: str, *, turns: int = 1, chance: float = 1.0) -> MoveEffect:
    """Create a status rider for a declarative move."""

    return MoveEffect(status=name, chance=chance, duration=turns)


def stat_change(stat: str, stages: int, *, chance: float = 1.0) -> MoveEffect:
    """Create a temporary stat change for a declarative move."""

    return MoveEffect(stat=stat, stages=stages, chance=chance)


def damage(power: int, *, magical: bool = False, target: CommandTarget = "targets") -> Damage:
    """Return a command from a custom move function."""

    return Damage(power=power, magical=magical, target=target)


def heal(power: int, *, target: CommandTarget = "targets") -> Heal:
    """Return a healing command from a custom move function."""

    return Heal(power=power, target=target)


def add_status(
    name: str,
    *,
    turns: int = 1,
    chance: float = 1.0,
    target: CommandTarget = "targets",
) -> AddStatus:
    """Return a status command from a custom move function."""

    return AddStatus(name=name, duration=turns, chance=chance, target=target)


def change_stat(
    stat: str,
    stages: int,
    *,
    chance: float = 1.0,
    target: CommandTarget = "targets",
) -> ChangeStat:
    """Return a stat-change command from a custom move function."""

    return ChangeStat(stat=stat, stages=stages, chance=chance, target=target)


@dataclass(frozen=True)
class Palette:
    """Named colors used by one or more procedural sprites."""

    name: str
    body: Color
    accent: Color
    eye: Color = (255, 255, 255)
    detail: Color = (30, 30, 40)
    id: str | None = None
    extra: dict[str, Color] = field(default_factory=dict)

    @property
    def palette_id(self) -> str:
        return _id(self.id, self.name)

    def compile(self) -> dict[str, Color]:
        return {
            "body": self.body,
            "accent": self.accent,
            "eye": self.eye,
            "detail": self.detail,
            **self.extra,
        }


@dataclass
class Sprite:
    """Procedural character drawing built from readable shape calls."""

    name: str
    palette: Palette
    id: str | None = None
    shapes: list[dict[str, object]] = field(default_factory=list)

    @property
    def sprite_id(self) -> str:
        return _id(self.id, self.name)

    def circle(
        self,
        center: tuple[int, int],
        radius: int,
        *,
        fill: str = "body",
        outline: str = "detail",
        width: int = 2,
    ) -> "Sprite":
        self.shapes.append(
            {
                "kind": "circle",
                "center": center,
                "radius": radius,
                "fill": fill,
                "outline": outline,
                "width": width,
            }
        )
        return self

    def ellipse(
        self,
        center: tuple[int, int],
        size: tuple[int, int],
        *,
        fill: str = "body",
        outline: str = "detail",
        width: int = 2,
    ) -> "Sprite":
        self.shapes.append(
            {
                "kind": "ellipse",
                "center": center,
                "size": size,
                "fill": fill,
                "outline": outline,
                "width": width,
            }
        )
        return self

    def rect(
        self,
        center: tuple[int, int],
        size: tuple[int, int],
        *,
        fill: str = "accent",
        outline: str = "detail",
        width: int = 2,
        border_radius: int = 10,
    ) -> "Sprite":
        self.shapes.append(
            {
                "kind": "rect",
                "center": center,
                "size": size,
                "fill": fill,
                "outline": outline,
                "width": width,
                "border_radius": border_radius,
            }
        )
        return self

    def polygon(
        self,
        points: Sequence[tuple[int, int]],
        *,
        fill: str = "accent",
        outline: str = "detail",
        width: int = 2,
    ) -> "Sprite":
        self.shapes.append(
            {
                "kind": "polygon",
                "points": list(points),
                "fill": fill,
                "outline": outline,
                "width": width,
            }
        )
        return self

    def line(
        self,
        points: Sequence[tuple[int, int]],
        *,
        color: str = "detail",
        width: int = 3,
    ) -> "Sprite":
        self.shapes.append({"kind": "line", "points": list(points), "color": color, "width": width})
        return self

    def polyline(
        self,
        points: Sequence[tuple[int, int]],
        *,
        color: str = "accent",
        width: int = 3,
    ) -> "Sprite":
        self.shapes.append(
            {"kind": "polyline", "points": list(points), "color": color, "width": width}
        )
        return self

    def face(self, y: int = -6) -> "Sprite":
        """Add the project's friendly default face."""

        return (
            self.circle((-12, y), 6, fill="eye", outline="detail", width=1)
            .circle((12, y), 6, fill="eye", outline="detail", width=1)
            .line([(-12, y), (-12, y + 2)], color="detail", width=2)
            .line([(12, y), (12, y + 2)], color="detail", width=2)
            .polyline([(-12, y + 16), (0, y + 22), (12, y + 16)], color="detail", width=2)
        )

    def compile(self) -> dict[str, object]:
        return {"palette": self.palette.palette_id, "shapes": list(self.shapes)}


@dataclass(frozen=True)
class VisualEffect:
    """Friendly wrapper around a visual effect specification."""

    name: str
    style: EffectStyle
    color: Color
    duration: float = 0.5
    id: str | None = None
    radius_start: int = 18
    radius_end: int = 60
    projectile_radius: int = 12
    size_start: int = 10
    size_end: int = 18
    arc_count: int = 3
    path: PathProfile | None = None

    @property
    def effect_id(self) -> str:
        return _id(self.id, self.name)

    @classmethod
    def ring(cls, name: str, *, color: Color, duration: float = 0.5, id: str | None = None) -> "VisualEffect":
        return cls(name=name, style="ring", color=color, duration=duration, id=id)

    @classmethod
    def projectile(
        cls,
        name: str,
        *,
        color: Color,
        duration: float = 0.5,
        radius: int = 12,
        id: str | None = None,
    ) -> "VisualEffect":
        return cls(
            name=name,
            style="projectile",
            color=color,
            duration=duration,
            projectile_radius=radius,
            id=id,
        )

    @classmethod
    def path_effect(
        cls,
        name: str,
        *,
        color: Color,
        mode: PathMode = "sine",
        duration: float = 0.7,
        amplitude: float = 24.0,
        cycles: float = 4.0,
        steps: int = 40,
        width: int = 4,
        stair_steps: int = 6,
        function: Callable[[float], float] | None = None,
        id: str | None = None,
    ) -> "VisualEffect":
        return cls(
            name=name,
            style="path",
            color=color,
            duration=duration,
            id=id,
            path=PathProfile(
                mode=mode,
                amplitude=amplitude,
                cycles=cycles,
                steps=steps,
                width=width,
                stair_steps=stair_steps,
                function=function,
            ),
        )

    @classmethod
    def burst_rect(
        cls,
        name: str,
        *,
        color: Color,
        duration: float = 0.5,
        size_start: int = 10,
        size_end: int = 18,
        id: str | None = None,
    ) -> "VisualEffect":
        return cls(
            name=name,
            style="burst_rect",
            color=color,
            duration=duration,
            size_start=size_start,
            size_end=size_end,
            id=id,
        )

    @classmethod
    def wind(
        cls,
        name: str,
        *,
        color: Color,
        duration: float = 0.55,
        arcs: int = 3,
        id: str | None = None,
    ) -> "VisualEffect":
        return cls(
            name=name,
            style="wind_arcs",
            color=color,
            duration=duration,
            arc_count=arcs,
            id=id,
        )

    def compile(self) -> EffectSpec:
        return EffectSpec(
            effect_id=self.effect_id,
            style=self.style,
            color=self.color,
            duration=self.duration,
            path=self.path,
            radius_start=self.radius_start,
            radius_end=self.radius_end,
            projectile_radius=self.projectile_radius,
            size_start=self.size_start,
            size_end=self.size_end,
            arc_count=self.arc_count,
        )


@dataclass(frozen=True)
class Sound:
    """Synthesized sound effect with classroom-friendly defaults."""

    name: str
    waveform: str = "sine"
    frequency: float = 440.0
    duration: float = 0.12
    volume: float = 0.35
    attack: float = 0.004
    release: float = 0.05
    frequency_end: float | None = None
    duty_cycle: float = 0.5
    vibrato_hz: float = 0.0
    vibrato_depth: float = 0.0
    noise: float = 0.0
    id: str | None = None

    @property
    def sound_id(self) -> str:
        return _id(self.id, self.name)

    def compile(self) -> SynthSoundSpec:
        return SynthSoundSpec(
            waveform=self.waveform,
            frequency=self.frequency,
            duration=self.duration,
            volume=self.volume,
            attack=self.attack,
            release=self.release,
            frequency_end=self.frequency_end,
            duty_cycle=self.duty_cycle,
            vibrato_hz=self.vibrato_hz,
            vibrato_depth=self.vibrato_depth,
            noise=self.noise,
        )


@dataclass(frozen=True)
class Music:
    """Generated or file-backed music track."""

    name: str
    spec: GeneratedTrackSpec | FileTrackSpec
    id: str | None = None

    @property
    def music_id(self) -> str:
        return _id(self.id, self.name)

    @classmethod
    def generated(
        cls,
        name: str,
        *,
        builder: str,
        volume: float = 0.4,
        id: str | None = None,
    ) -> "Music":
        return cls(name=name, spec=GeneratedTrackSpec(builder=builder, volume=volume), id=id)

    @classmethod
    def file(
        cls,
        name: str,
        *,
        path: str | Path,
        volume: float = 0.5,
        id: str | None = None,
    ) -> "Music":
        return cls(name=name, spec=FileTrackSpec(path=path, volume=volume), id=id)


@dataclass(frozen=True)
class Move:
    """One move a character can choose in battle."""

    name: str
    kind: MoveKind = "physical"
    power: int = 0
    accuracy: float = 1.0
    target: TargetMode = "single_enemy"
    animation: VisualEffect | str = "impact"
    sound: Sound | str | None = None
    effects: Sequence[MoveEffect] = ()
    priority: int = 0
    flavor: str = ""
    action: MoveScript | None = None
    id: str | None = None

    @property
    def move_id(self) -> str:
        return _id(self.id, self.name)

    def compile(self) -> MoveSpec:
        animation_id = self.animation.effect_id if isinstance(self.animation, VisualEffect) else self.animation
        if isinstance(self.sound, Sound):
            sound_id = self.sound.sound_id
        elif self.sound is None:
            sound_id = ""
        else:
            sound_id = self.sound
        return MoveSpec(
            move_id=self.move_id,
            name=self.name,
            kind=self.kind,
            power=self.power,
            accuracy=self.accuracy,
            target_mode=self.target,
            animation=animation_id,
            sound_id=sound_id,
            priority=self.priority,
            effects=tuple(self.effects),
            flavor=self.flavor,
            script=self.action,
        )


@dataclass(frozen=True)
class Character:
    """A reusable battler described with direct object references."""

    name: str
    role: str
    hp: int
    attack: int
    defense: int
    magic: int
    speed: int
    sprite: Sprite
    moves: Sequence[Move]
    description: str = ""
    id: str | None = None

    @property
    def character_id(self) -> str:
        return _id(self.id, self.name)

    def compile(self) -> CharacterSpec:
        return CharacterSpec(
            char_id=self.character_id,
            name=self.name,
            role=self.role,
            max_hp=self.hp,
            attack=self.attack,
            defense=self.defense,
            magic=self.magic,
            speed=self.speed,
            sprite_id=self.sprite.sprite_id,
            move_ids=tuple(move.move_id for move in self.moves),
            description=self.description,
        )


@dataclass(frozen=True)
class Team:
    """A party roster.  ``active`` optionally chooses its initial frontline."""

    name: str
    members: Sequence[Character]
    controller: str = "human"
    active: Sequence[Character] | None = None
    strategy: AIStrategy | None = None
    id: str | None = None

    @property
    def team_id(self) -> str:
        return _id(self.id, self.name)

    def compile(self) -> TeamSpec:
        controller_type = (
            "ai" if self.strategy is not None or self.controller in {"ai", "computer"} else "human"
        )
        active = None if self.active is None else tuple(character.character_id for character in self.active)
        return TeamSpec(
            name=self.name,
            members=tuple(character.character_id for character in self.members),
            controller_type=controller_type,
            starting_active=active,
            strategy=self.strategy,
        )


@dataclass(frozen=True)
class Battle:
    """A launchable battle between two registered teams."""

    name: str
    player: Team
    enemy: Team
    active: tuple[int, int] = (1, 1)
    music: Music | None = None
    id: str | None = None
    encounter_id: str | None = None

    @property
    def battle_id(self) -> str:
        return _id(self.id, self.name)

    def compile(self) -> EncounterSpec:
        return EncounterSpec(
            encounter_id=self.encounter_id or self.battle_id,
            title=self.name,
            player_team=self.player.compile(),
            enemy_team=self.enemy.compile(),
            active_limits=self.active,
            music_track_id=self.music.music_id if self.music else None,
        )


@dataclass(frozen=True)
class GamePresentation:
    """Choose the content objects used for standard battle presentation.

    Keeping these as object references means the engine does not rely on hidden
    names such as ``"strike"`` or ``"menu_confirm"``. A different student
    game can use completely different ids without changing engine code.
    """

    basic_attack: Move
    menu_move_sound: Sound
    menu_confirm_sound: Sound
    menu_back_sound: Sound
    damage_sound: Sound
    heal_sound: Sound
    ko_sound: Sound
    switch_sound: Sound
    defend_sound: Sound
    heal_effect: VisualEffect

    def compile(self) -> PresentationSpec:
        return PresentationSpec(
            basic_attack_move_id=self.basic_attack.move_id,
            menu_move_sound_id=self.menu_move_sound.sound_id,
            menu_confirm_sound_id=self.menu_confirm_sound.sound_id,
            menu_back_sound_id=self.menu_back_sound.sound_id,
            damage_sound_id=self.damage_sound.sound_id,
            heal_sound_id=self.heal_sound.sound_id,
            ko_sound_id=self.ko_sound.sound_id,
            switch_sound_id=self.switch_sound.sound_id,
            defend_sound_id=self.defend_sound.sound_id,
            heal_effect_id=self.heal_effect.effect_id,
        )


@dataclass(frozen=True)
class Game:
    """Student-authored game definition that compiles to :class:`GameContent`."""

    title: str
    palettes: Sequence[Palette]
    sprites: Sequence[Sprite]
    effects: Sequence[VisualEffect]
    sounds: Sequence[Sound]
    music: Sequence[Music]
    moves: Sequence[Move]
    characters: Sequence[Character]
    teams: Sequence[Team]
    battles: Sequence[Battle]
    presentation: GamePresentation
    default_battle: Battle
    default_battle_music: Music
    victory_music: Music
    defeat_music: Music

    @staticmethod
    def _unique(items: Iterable[object], id_getter: Callable[[object], str], label: str) -> dict[str, object]:
        result: dict[str, object] = {}
        for item in items:
            item_id = id_getter(item)
            if item_id in result:
                raise ContentValidationError(
                    [ContentIssue(label, f"two objects use the id {item_id!r}")]
                )
            result[item_id] = item
        return result

    def compile(self, *, validate: bool = True) -> GameContent:
        palette_objects = self._unique(self.palettes, lambda item: item.palette_id, "palette")
        sprite_objects = self._unique(self.sprites, lambda item: item.sprite_id, "sprite")
        effect_objects = self._unique(self.effects, lambda item: item.effect_id, "effect")
        sound_objects = self._unique(self.sounds, lambda item: item.sound_id, "sound")
        music_objects = self._unique(self.music, lambda item: item.music_id, "music track")
        move_objects = self._unique(self.moves, lambda item: item.move_id, "move")
        character_objects = self._unique(
            self.characters, lambda item: item.character_id, "character"
        )
        team_objects = self._unique(self.teams, lambda item: item.team_id, "team")
        battle_objects = self._unique(self.battles, lambda item: item.battle_id, "battle")

        teams = {item_id: item.compile() for item_id, item in team_objects.items()}
        # Compile battles from their direct object references. Validation below
        # can then report an unregistered Team or Music object as a content
        # problem instead of leaking a KeyError from this compiler.
        encounters = {
            item_id: battle.compile()
            for item_id, battle in battle_objects.items()
        }

        content = GameContent(
            title=self.title,
            palettes={item_id: item.compile() for item_id, item in palette_objects.items()},
            sprites={item_id: item.compile() for item_id, item in sprite_objects.items()},
            effects={item_id: item.compile() for item_id, item in effect_objects.items()},
            sound_effects={item_id: item.compile() for item_id, item in sound_objects.items()},
            music_tracks={item_id: item.spec for item_id, item in music_objects.items()},
            presentation=self.presentation.compile(),
            moves={item_id: item.compile() for item_id, item in move_objects.items()},
            characters={item_id: item.compile() for item_id, item in character_objects.items()},
            teams=teams,
            encounters=encounters,
            default_encounter_id=self.default_battle.battle_id,
            default_battle_track=self.default_battle_music.music_id,
            default_victory_track=self.victory_music.music_id,
            default_defeat_track=self.defeat_music.music_id,
        )
        if validate:
            content.require_valid()
        return content
