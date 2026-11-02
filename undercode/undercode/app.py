"""Connect the two engines. Read Game.update to see the complete scene handoff.

Construction imports ONLY the content the chosen mode needs. --encounter and
--practice work even if student_world.py has an unfinished edit. --overworld
never loads encounter definitions. Game stores requests during a fade, applies
one change under its covered midpoint, then resumes the destination engine.
"""

from dataclasses import dataclass, replace
from enum import Enum, auto
from .contracts import EncounterRequest, EncounterResult, RoomRequest, Outcome
from .controls import Controls
from .model import Player, Session
from .settings import PLAYER_NAME


class Scene(Enum):
    """The active engine; the window chooses its music and renderer from this name."""

    WORLD = auto()
    ENCOUNTER = auto()


@dataclass(kw_only=True)
class Transition:
    """Store a concrete request during a fade, rather than a hidden callback closure."""

    request: EncounterRequest | EncounterResult | RoomRequest
    elapsed: float = 0
    duration: float = 0.72
    applied: bool = False

    @property
    def opacity(self):
        """Cover the scene at the middle, then uncover the new one."""
        return max(0, min(1, 1 - abs(self.elapsed / self.duration * 2 - 1)))


class Game:
    """Own the active mode and persistent session, not walking or encounter rules."""

    def __init__(self, *, seed=7, encounter=None, practice=None, level=None, entry=None):
        """Start one mode; rooms and encounters are loaded separately when needed."""
        self.seed = seed
        self.initial_encounter = encounter
        self.initial_practice = practice
        self.initial_level = level
        self.initial_entry = entry
        self.session = Session(player=Player(name=PLAYER_NAME))
        self.world = None
        self.encounter = None
        self.finished_result = None
        self.encounter_key = None
        self.transition = None
        self.time = 0.0
        self.help_open = False
        self.debug_open = False
        self.cues = []
        self.tones = []
        self.sound_label = "M: sound"
        self.technique_name = "choose technique"
        self.scene = Scene.WORLD
        if encounter is not None:
            self.start_encounter(encounter_id=encounter)
        elif practice is not None:
            self.start_practice(pattern_id=practice)
        else:
            self.create_world(level=level, entry=entry)

    def create_world(self, *, level=None, entry=None):
        """Compile the author's rooms and start at a named marker; no opponents needed."""
        from .student_world import LEVELS, START_LEVEL, START_ENTRY
        from .overworld.maps import compile_rooms, validate_start
        from .overworld.engine import World

        rooms = compile_rooms(definitions=LEVELS)
        room_key = level or START_LEVEL
        if room_key not in rooms:
            raise ValueError(f"Unknown level {room_key!r}. Choose: {', '.join(rooms)}")
        spawn = entry
        if spawn is None:
            spawn = START_ENTRY if room_key == START_LEVEL else next(iter(rooms[room_key].spawns))
        validate_start(rooms=rooms, room_key=room_key, spawn_name=spawn)
        self.world = World(rooms=rooms, session=self.session, room_key=room_key, spawn=spawn)

    def make_encounter(self, *, opponent):
        """Borrow the same Player for an encounter with the currently selected technique."""
        from .encounters.content import WEAPONS
        from .encounters.engine import Encounter

        self.technique_name = WEAPONS[self.session.player.weapon].name
        return Encounter(
            opponent=opponent,
            player=self.session.player,
            weapon=WEAPONS[self.session.player.weapon],
            seed=self.seed,
        )

    def start_encounter(self, *, encounter_id):
        """Load an opponent by ID; this needs no overworld definition or window."""
        from .encounters.content import OPPONENTS

        characters = {character.key: character for character in OPPONENTS}
        if encounter_id not in characters:
            raise ValueError(f"Unknown character {encounter_id!r}. Choose: {', '.join(characters)}")
        self.encounter = self.make_encounter(opponent=characters[encounter_id])
        self.scene = Scene.ENCOUNTER

    def start_practice(self, *, pattern_id):
        """Create an isolated defense lab; it imports no rooms and starts in DEFEND."""
        from .encounters.content import OPPONENTS, PATTERNS
        from .encounters.model import Act
        from .encounters.engine import Phase

        if pattern_id not in PATTERNS:
            raise ValueError(f"Unknown pattern {pattern_id!r}. Choose: {', '.join(PATTERNS)}")
        factory = PATTERNS[pattern_id]

        # A named function shows why each retry gets NEW timers. The factory
        # is a class/function to call later, not an already-running pattern.
        def choose_practice_pattern(*, context):
            """Return a fresh lab pattern on every defense turn."""
            return factory()

        trainer = replace(
            OPPONENTS[0],
            key="practice",
            name="Pattern Lab",
            max_hp=999,
            choose_pattern=choose_practice_pattern,
            acts=(Act(name="Try the pattern again", reply="Watch the warnings.", calm=0),),
        )
        self.encounter = self.make_encounter(opponent=trainer)
        self.encounter.set_phase(phase=Phase.DEFEND)
        self.scene = Scene.ENCOUNTER

    def restart(self):
        """Recreate this launch setup with a new Session; Python files reload on relaunch."""
        self.__init__(
            seed=self.seed,
            encounter=self.initial_encounter,
            practice=self.initial_practice,
            level=self.initial_level,
            entry=self.initial_entry,
        )

    def begin_transition(self, *, request):
        """Pause gameplay while covering one concrete room/encounter change."""
        if self.transition is None:
            self.transition = Transition(request=request)
            self.cues.append("transition")

    def apply_request(self, *, request):
        """Apply one message. This is the only place that connects the two engines."""
        if isinstance(request, EncounterRequest):
            self.encounter_key = request.person_id
            self.start_encounter(encounter_id=request.encounter_id)
        elif isinstance(request, RoomRequest):
            self.world.change_room(
                destination=request.destination_room, landing=request.destination_spawn
            )
        elif isinstance(request, EncounterResult):
            if request.outcome in (Outcome.SPARED, Outcome.DEFEATED) and self.encounter_key:
                self.session.resolved[self.encounter_key] = request.outcome
            if self.world is None:
                self.create_world()
            if request.outcome == Outcome.LOST:
                from .student_world import START_LEVEL, START_ENTRY

                self.session.player.rest()
                self.world.change_room(destination=START_LEVEL, landing=START_ENTRY)
                self.world.tell(text="A fresh start. HP and cocoa restored at camp.")
            else:
                self.world.tell(text=f"{request.opponent_name}: until next time.")
            self.world.talking = None
            self.encounter = None
            self.scene = Scene.WORLD

    def change_weapon(self):
        """Cycle an encounter technique only when the player asks for it with Tab."""
        if self.scene != Scene.WORLD or self.transition is not None:
            return
        from .encounters.content import WEAPONS

        player = self.session.player
        player.weapon = (player.weapon + 1) % len(WEAPONS)
        self.technique_name = WEAPONS[player.weapon].name
        self.world.tell(text=f"Technique: {self.technique_name}")
        self.cues.append("select")

    def update(self, *, seconds, controls=Controls()):
        """Read the whole frame: help pause → fade → active engine → request.

        Returning during a fade is important: the Z press that accepted an
        invitation must not also pick FIGHT in the encounter's first frame.
        """
        self.time += seconds
        if self.finished_result is not None or self.help_open:
            return
        if self.transition is not None:
            transition = self.transition
            transition.elapsed += seconds
            if transition.elapsed >= transition.duration / 2 and not transition.applied:
                self.apply_request(request=transition.request)
                transition.applied = True
            if transition.elapsed >= transition.duration:
                self.transition = None
            return
        if self.scene == Scene.WORLD:
            request = self.world.update(seconds=seconds, controls=controls)
            self.tones.extend(self.world.tones)
            self.world.tones.clear()
        else:
            self.encounter.update(seconds=seconds, controls=controls)
            self.cues.extend(self.encounter.cues)
            self.encounter.cues.clear()
            request = self.encounter.result
        if isinstance(request, EncounterResult) and self.world is None:
            # A standalone exercise ends in its own system. Loading rooms here
            # would make an unrelated unfinished map break a completed encounter.
            self.finished_result = request
            return
        if request is not None:
            self.begin_transition(request=request)
