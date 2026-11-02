"""Encounter definitions: ACT replies, opponents, selection context and techniques."""

from dataclasses import dataclass
from typing import Callable

Color = tuple[int, int, int]


@dataclass(frozen=True, kw_only=True)
class Act:
    """Define an ACT menu label, its reply, and its nonnegative understanding gain."""

    name: str
    reply: str
    calm: int = 1


@dataclass(frozen=True, kw_only=True)
class TurnContext:
    """Give a pattern selector a read-only snapshot at the start of a defense.

    turn starts at 0. opponent_hp/opponent_max_hp describe the opponent; calm is the
    understanding earned through ACT. Return a new pattern using these values.
    """

    turn: int
    opponent_hp: int
    opponent_max_hp: int
    calm: int


@dataclass(frozen=True, kw_only=True)
class Opponent:
    """Define a reusable battle character and its behavior hooks.

    key identifies this encounter definition. Overworld people are separate
    records and optionally refer to this key. portrait(surface=..., center=..., scale=..., time=...) draws its art, while
    choose_pattern(context=...) returns a fresh DefensePattern for each turn.
    acts and calm_needed determine how the player can reach SPARE.
    """

    key: str
    name: str
    description: str
    color: Color
    portrait: Callable
    acts: tuple[Act, ...]
    choose_pattern: Callable[[TurnContext], object]
    max_hp: int = 22
    calm_needed: int = 3
    greeting: str = "A friendly challenger steps forward."
    goodbye: str = "There is more than one way to finish a conversation."


@dataclass(frozen=True, kw_only=True)
class Weapon:
    """Pair a menu name and damage power with a factory for a fresh Strike.

    The strike supplies timing accuracy; Encounter combines it with power to apply
    damage. A factory is a callable such as TimingStrike, not an existing instance.
    """

    name: str
    factory: Callable[[], object]
    power: int = 12
