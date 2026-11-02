"""Scene ownership and transitions. World and Battle remain independent models."""

from dataclasses import dataclass, replace
from enum import Enum, auto
from typing import Callable
from .battle import Battle, Phase
from .controls import Controls
from .model import Act, Outcome, Player, Session
from .world import World
from .content import CHARACTERS, WEAPONS, PATTERNS, ROOMS, START_LEVEL, START_ENTRY
from .student import PLAYER_NAME


class Scene(Enum):
    WORLD = auto()
    BATTLE = auto()


@dataclass
class Transition:
    on_covered: Callable[[], None]
    elapsed: float = 0
    duration: float = 0.72
    swapped: bool = False

    @property
    def opacity(self):
        return max(0, min(1, 1 - abs(self.elapsed / self.duration * 2 - 1)))


class Game:
    def __init__(self, seed=7, encounter=None, practice=None, level=None, entry=None):
        self.seed = seed
        self.initial_level = level
        self.initial_entry = entry
        self.initial_encounter = encounter
        self.initial_practice = practice
        self.session = Session(Player(name=PLAYER_NAME))
        self.characters = {c.key: c for c in CHARACTERS}
        start = level or START_LEVEL
        spawn = entry or (START_ENTRY if start == START_LEVEL else next(iter(ROOMS[start].spawns)))
        self.world = World(ROOMS, self.session, start, spawn)
        self.scene = Scene.WORLD
        self.battle = None
        self.encounter_key = None
        self.transition = None
        self.time = 0.0
        self.help_open = False
        self.cues = []
        self.sound_label = "M: sound"
        if encounter:
            self.encounter_key = encounter
            self.battle = self.make_battle(self.characters[encounter])
            self.scene = Scene.BATTLE
        elif practice:
            factory = PATTERNS[practice]
            trainer = replace(
                CHARACTERS[0],
                key="practice",
                name="Pattern Lab",
                description="A place to try one pattern without walking through the world.",
                choose_pattern=lambda context: factory(),
                max_hp=999,
                acts=(Act("Try the pattern again", "Here it comes. Watch the warnings.", 0),),
            )
            self.battle = self.make_battle(trainer)
            self.battle.set_phase(Phase.DEFEND)
            self.scene = Scene.BATTLE

    def make_battle(self, character):
        return Battle(
            character, self.session.player, WEAPONS[self.session.player.weapon], self.seed
        )

    def restart(self):
        self.__init__(
            self.seed,
            self.initial_encounter,
            self.initial_practice,
            self.initial_level,
            self.initial_entry,
        )

    def begin_transition(self, action):
        if self.transition is None:
            self.transition = Transition(action)
            self.cues.append("transition")

    def encounter(self, person):
        def enter():
            self.encounter_key = person.key
            self.battle = self.make_battle(self.characters[person.character])
            self.scene = Scene.BATTLE

        self.begin_transition(enter)

    def leave_battle(self):
        outcome = self.battle.outcome
        name = self.battle.character.name

        def leave():
            if outcome in (Outcome.SPARED, Outcome.DEFEATED) and self.encounter_key:
                self.session.resolved[self.encounter_key] = outcome
            if outcome == Outcome.LOST:
                self.session.player.rest()
                self.world.change_room(START_LEVEL, START_ENTRY)
                self.world.tell("A fresh start. HP and cocoa restored at camp.")
            else:
                self.world.tell(f"{name}: until next time. You can return for a rematch.")
            self.world.talking = None
            self.battle = None
            self.scene = Scene.WORLD

        self.begin_transition(leave)

    def change_weapon(self):
        if self.scene == Scene.WORLD and not self.transition:
            player = self.session.player
            player.weapon = (player.weapon + 1) % len(WEAPONS)
            self.world.tell(f"Technique: {WEAPONS[player.weapon].name}")
            self.cues.append("select")

    def update(self, dt, controls=Controls()):
        self.time += dt
        if self.help_open:
            return
        if self.transition:
            transition = self.transition
            transition.elapsed += dt
            if transition.elapsed >= transition.duration / 2 and not transition.swapped:
                transition.swapped = True
                transition.on_covered()
            if transition.elapsed >= transition.duration:
                self.transition = None
            return  # Freeze both scenes; the interaction key cannot leak into battle.
        if self.scene == Scene.WORLD:
            request = self.world.update(dt, controls)
            if request:
                kind, payload = request
                if kind == "encounter":
                    self.encounter(payload)
                else:
                    self.begin_transition(
                        lambda: self.world.change_room(payload.destination, payload.landing)
                    )
        else:
            self.battle.update(dt, controls)
            self.cues.extend(self.battle.cues)
            self.battle.cues.clear()
            if self.battle.phase == Phase.FINISHED:
                self.leave_battle()
