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
    """Name which model currently owns player input: the world or a battle."""

    WORLD = auto()
    BATTLE = auto()


@dataclass
class Transition:
    """Track a fade that hides one scene change at its midpoint.

    on_covered is a no-argument function that Game.update calls once when the
    screen is covered. elapsed and duration are seconds; swapped remembers
    that the callback already ran so subsequent frames cannot run it again.
    """

    on_covered: Callable[[], None]
    elapsed: float = 0
    duration: float = 0.72
    swapped: bool = False

    @property
    def opacity(self):
        """Return fade strength from 0 (clear) to 1 (covered), then back to 0."""
        return max(0, min(1, 1 - abs(self.elapsed / self.duration * 2 - 1)))


class Game:
    """Coordinate the world, battles, transitions, and shared session state.

    main.py calls update once per active frame; View only reads this model.
    World and Battle request changes, while Game decides when to swap scenes.
    cues stores sound names for the main loop to play and clear.
    """

    def __init__(self, seed=7, encounter=None, practice=None, level=None, entry=None):
        """Start a fresh session using registered character, pattern, and level keys.

        seed makes battle randomness repeatable. encounter starts a character
        battle; practice starts a defense immediately. Otherwise level/entry
        choose a room and named arrival marker, with story defaults when omitted.
        The launcher checks keys before calling this constructor.
        """
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
        """Return a new Battle using this session's player and selected weapon.

        character is a Character definition, not a placement on the map.
        The battle shares Player so damage, healing, and snacks persist.
        """
        return Battle(
            character, self.session.player, WEAPONS[self.session.player.weapon], self.seed
        )

    def restart(self):
        """Clear this run's progress and recreate its original launch setup.

        Keep the seed and initial encounter, practice pattern, or level/entry.
        Player health, snacks, story flags, and remembered outcomes start over.
        """
        self.__init__(
            self.seed,
            self.initial_encounter,
            self.initial_practice,
            self.initial_level,
            self.initial_entry,
        )

    def begin_transition(self, action):
        """Schedule action for the midpoint of a fade, if no fade is running.

        action takes no arguments. Gameplay pauses until the fade finishes;
        its scene-changing work runs once under the opaque part of the fade.
        """
        if self.transition is None:
            self.transition = Transition(action)
            self.cues.append("transition")

    def encounter(self, person):
        """Fade into a battle for person, a character placement from the world.

        Remember its placement key so this particular neighbor can later
        remember being spared or defeated, even if other NPCs share its art.
        """

        def enter():
            """Create the battle and switch scenes when the fade reaches its midpoint."""
            self.encounter_key = person.key
            self.battle = self.make_battle(self.characters[person.character])
            self.scene = Scene.BATTLE

        self.begin_transition(enter)

    def leave_battle(self):
        """Schedule the return from a finished battle to the overworld.

        Remember spare/combat outcomes on the placement. A loss restores the
        player at the story's starting marker; other outcomes keep position.
        The actual state change waits for the fade's covered midpoint.
        """
        outcome = self.battle.outcome
        name = self.battle.character.name

        def leave():
            """Apply the captured outcome and restore the world under the fade."""
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
        """Cycle the selected technique in the world and queue feedback, unless fading."""
        if self.scene == Scene.WORLD and not self.transition:
            player = self.session.player
            player.weapon = (player.weapon + 1) % len(WEAPONS)
            self.world.tell(f"Technique: {WEAPONS[player.weapon].name}")
            self.cues.append("select")

    def update(self, dt, controls=Controls()):
        """Advance the active scene by dt seconds using this frame's Controls.

        The help overlay pauses gameplay. During a fade, advance only its
        clock and run the scene swap once. Otherwise update World or Battle,
        handle its requests/results, and collect sound cues for main.py.
        """
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
