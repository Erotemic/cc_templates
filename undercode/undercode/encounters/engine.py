"""The battle state machine. Content and patterns do not control scene changes."""

from enum import Enum, auto
from .arena import Arena
from .model import TurnContext
from ..contracts import Outcome, EncounterResult
from ..dialogue import paginate
from .. import student_encounters
from .menu import ACTION_LABELS, main_buttons, option_buttons


class Phase(Enum):
    """Name the current step of a battle so one input cannot control several steps."""

    MESSAGE = auto()
    MENU = auto()
    ACT = auto()
    ITEM = auto()
    MERCY = auto()
    ATTACK = auto()
    DEFEND = auto()
    FINISHED = auto()


class Encounter:
    """Manage a single encounter's dialogue, menu choices, turns and outcome.

    Share Player with the session so health/snacks persist. Each defense uses
    its own Arena; each timed attack uses a fresh Strike. Game handles world
    transitions after the closing message reaches Phase.FINISHED.
    """

    def __init__(self, *, opponent, player, weapon, seed=0):
        """Start character's encounter with the shared player and chosen weapon.

        seed controls defense randomness. Initialize enemy health and progress,
        then display the character's greeting before opening the main menu.
        """
        self.opponent = opponent
        self.player = player
        self.weapon = weapon
        self.seed = seed
        self.opponent_hp = opponent.max_hp
        self.calm = 0
        self.turn = 0
        self.selection = 0
        self.phase = Phase.MESSAGE
        self.age = 0.0
        self.message = opponent.greeting
        self.pages = self.paginate(text=self.message)
        self.page = 0
        self.after_message = Phase.MENU
        self.outcome = None
        self.strike = None
        self.arena = None
        self.cues = []
        self.last_damage = 0
        self.portrait_flash = 0.0

    @property
    def spare_ready(self):
        """Return whether ACT choices have built enough understanding to spare the enemy."""
        return self.calm >= self.opponent.calm_needed

    @staticmethod
    def paginate(*, text):
        """Return text split into pages of at most three wrapped 52-character lines."""
        return tuple(paginate(text=text, width=52))

    @property
    def current_message(self):
        """Return the entire current page, including characters not yet revealed."""
        return self.pages[self.page]

    @property
    def visible_message(self):
        """Return the current page prefix revealed at 55 characters per second."""
        return self.current_message[: int(self.age * 55)]

    @property
    def message_complete(self):
        """Return whether the typewriter has revealed the entire current page."""
        return self.age * 55 >= len(self.current_message)

    def set_phase(self, *, phase):
        """Enter phase and reset its elapsed age and menu selection.

        DEFEND asks the character for a new pattern using a TurnContext, creates
        an Arena, then increments the turn counter. ATTACK creates the selected
        weapon's Strike. Other phases do not create a mini-game.
        """
        self.phase = phase
        self.age = 0.0
        self.selection = 0
        if phase == Phase.DEFEND:
            context = TurnContext(
                turn=self.turn,
                opponent_hp=self.opponent_hp,
                opponent_max_hp=self.opponent.max_hp,
                calm=self.calm,
            )
            pattern = self.opponent.choose_pattern(context=context)
            self.arena = Arena(pattern=pattern, player=self.player, seed=self.seed + self.turn)
            self.turn += 1
        elif phase == Phase.ATTACK:
            self.strike = self.weapon.factory()

    def say(self, *, message, then=Phase.DEFEND):
        """Page message and show it before entering then (DEFEND by default).

        Reset the page index and typewriter. Revealing or advancing text does
        not itself select a menu action or consume another battle turn.
        """
        self.message = message
        self.pages = self.paginate(text=message)
        self.page = 0
        self.after_message = then
        self.set_phase(phase=Phase.MESSAGE)

    def finish(self, *, outcome, message):
        """Record outcome and show a final message before Phase.FINISHED.

        Queue the matching result cue. Game waits until the player finishes
        reading this message before scheduling the return to the world.
        """
        self.outcome = outcome
        self.say(message=message, then=Phase.FINISHED)
        self.cues.append("win" if outcome in (Outcome.SPARED, Outcome.DEFEATED) else "soft")

    def options(self):
        """Return the selectable labels for the current menu, or an empty tuple outside menus."""
        if self.phase == Phase.MENU:
            return ACTION_LABELS
        if self.phase == Phase.ACT:
            return tuple(act.name for act in self.opponent.acts) + ("Back",)
        if self.phase == Phase.ITEM:
            return (f"Cocoa ({self.player.snacks}) — restore 7 HP", "Back")
        if self.phase == Phase.MERCY:
            return (
                "Spare" if self.spare_ready else "Spare — not ready yet",
                "Leave practice",
                "Back",
            )
        return ()

    def choose(self):
        """Execute the current menu selection in the active phase.

        Main-menu choices enter submenus or an attack. ACT changes understanding,
        ITEM can consume cocoa and heal the shared player, and MERCY may finish
        the encounter. Queue feedback/messages rather than drawing or changing rooms.
        """
        self.cues.append("select")
        if self.phase == Phase.MENU:
            self.set_phase(phase=(Phase.ATTACK, Phase.ACT, Phase.ITEM, Phase.MERCY)[self.selection])
        elif self.phase == Phase.ACT:
            if self.selection == len(self.opponent.acts):
                self.set_phase(phase=Phase.MENU)
            else:
                act = self.opponent.acts[self.selection]
                self.calm = min(self.opponent.calm_needed, self.calm + act.calm)
                suffix = " They seem ready to let you pass." if self.spare_ready else ""
                self.say(message=act.reply + suffix)
        elif self.phase == Phase.ITEM:
            if self.selection == 1:
                self.set_phase(phase=Phase.MENU)
            elif self.player.snacks:
                self.player.snacks -= 1
                healed = self.player.heal(amount=7)
                self.cues.append("heal")
                self.say(message=f"The cocoa is warm. You recover {healed} HP.")
            else:
                self.say(
                    message="Your flask is empty. Rest at the lantern fountain to refill it.",
                    then=Phase.MENU,
                )
        elif self.phase == Phase.MERCY:
            if self.selection == 2:
                self.set_phase(phase=Phase.MENU)
            elif self.selection == 1:
                self.finish(
                    outcome=Outcome.LEFT,
                    message="You wave goodbye. Practice can wait until you are ready.",
                )
            elif self.spare_ready:
                self.finish(outcome=Outcome.SPARED, message=self.opponent.goodbye)
            else:
                self.say(
                    message="They are still guarded. Try an ACT that helps you understand them."
                )

    def update(self, *, seconds, controls):
        """Advance ONLY the current phase. Follow the named handler to trace one turn."""
        self.age += seconds
        self.portrait_flash = max(0, self.portrait_flash - seconds)
        if self.phase == Phase.MESSAGE:
            self.update_message(seconds=seconds, controls=controls)
        elif self.phase in (Phase.MENU, Phase.ACT, Phase.ITEM, Phase.MERCY):
            self.update_menu(seconds=seconds, controls=controls)
        elif self.phase == Phase.ATTACK:
            self.update_attack(seconds=seconds, controls=controls)
        elif self.phase == Phase.DEFEND:
            self.update_defense(seconds=seconds, controls=controls)

    def update_message(self, *, seconds, controls):
        """Reveal, advance a page, or enter its remembered destination; never choose an action."""
        if controls.cancel_pressed or (controls.confirm_pressed and not self.message_complete):
            # One extra character-time avoids rounding just below a full reveal.
            self.age = max(self.age, (len(self.current_message) + 1) / 55)
        elif controls.confirm_pressed:
            if self.page + 1 < len(self.pages):
                self.page += 1
                self.age = 0
            else:
                self.set_phase(phase=self.after_message)

    def update_menu(self, *, seconds, controls):
        """Use one keyboard action or the student's mouse hit test in this menu.

        The caller only enters here during a menu phase. Clicks cannot reveal
        messages, stop a timing strike, jump, or act during a fade. After a hit,
        choose() follows the ordinary action path and this frame returns.
        """
        if controls.cancel_pressed and self.phase != Phase.MENU:
            self.set_phase(phase=Phase.MENU)
            return
        if controls.mouse_click is not None:
            if self.phase == Phase.MENU:
                buttons = main_buttons()
            else:
                buttons = option_buttons(labels=self.options(), selection=self.selection)
            clicked = student_encounters.clicked_button(
                mouse_position=controls.mouse_click, buttons=buttons
            )
            # Index 0 is a real option (FIGHT in the main menu), not no choice.
            if clicked is not None:
                self.selection = clicked
                self.choose()  # The same action path used by keyboard confirm.
                return  # This click cannot also confirm the submenu it opens.
        if controls.menu_step:
            self.selection = (self.selection + controls.menu_step) % len(self.options())
            self.cues.append("move")
        elif controls.confirm_pressed:
            self.choose()

    def update_attack(self, *, seconds, controls):
        """Ask the Strike for accuracy, then apply damage here when it finishes.

        The timing sequence does not own opponent health. Keeping this decision
        here lets any Weapon supply a different sequence without copying damage.
        """
        self.strike.update(seconds=seconds, controls=controls)
        if self.strike.done:
            score = self.strike.score
            self.last_damage = max(1, round(self.weapon.power * score)) if score > 0 else 0
            self.opponent_hp = max(0, self.opponent_hp - self.last_damage)
            self.portrait_flash = 0.35 if self.last_damage else 0
            self.cues.append("hit" if self.last_damage else "soft")
            if self.opponent_hp == 0:
                self.finish(
                    outcome=Outcome.DEFEATED,
                    message=f"{self.opponent.name} calls the match. You found your way through!",
                )
            else:
                if score > 0.88:
                    quality = "Perfect timing!"
                elif score > 0:
                    quality = "A glancing strike."
                else:
                    quality = "The strike misses."
                self.say(message=f"{quality} {self.last_damage} damage. Now watch their reply.")

    def update_defense(self, *, seconds, controls):
        """Advance Arena, relay cues, and select the next message from its result.

        Arena and Encounter borrow the same Player, so damage is already visible.
        This method decides whether the next message means menu, or a loss.
        """
        self.arena.update(seconds=seconds, controls=controls)
        self.cues.extend(self.arena.cues)
        self.arena.cues.clear()
        if self.player.hp <= 0:
            self.finish(
                outcome=Outcome.LOST,
                message="Time for a breather. The lantern fountain will patch you up. You can try again.",
            )
        elif self.arena.done:
            text = (
                "You read every move."
                if not self.arena.hits
                else f"You made it through. {self.arena.hits} hit(s) taken."
            )
            if self.arena.blocks:
                text += f" {self.arena.blocks} sparks blocked."
            self.say(message=text, then=Phase.MENU)

    @property
    def result(self):
        """Expose a result only after the final message; Game owns what happens next."""
        if self.phase == Phase.FINISHED:
            return EncounterResult(outcome=self.outcome, opponent_name=self.opponent.name)
        return None
