"""The battle state machine. Content and patterns do not control scene changes."""

from enum import Enum, auto
import textwrap
from .arena import Arena
from .model import Outcome, TurnContext


class Phase(Enum):
    MESSAGE = auto()
    MENU = auto()
    ACT = auto()
    ITEM = auto()
    MERCY = auto()
    ATTACK = auto()
    DEFEND = auto()
    FINISHED = auto()


class Battle:
    def __init__(self, character, player, weapon, seed=0):
        self.character = character
        self.player = player
        self.weapon = weapon
        self.seed = seed
        self.enemy_hp = character.max_hp
        self.calm = 0
        self.turn = 0
        self.selection = 0
        self.phase = Phase.MESSAGE
        self.age = 0.0
        self.message = character.greeting
        self.pages = self.paginate(self.message)
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
        return self.calm >= self.character.calm_needed

    @staticmethod
    def paginate(text):
        lines = textwrap.wrap(text, width=52) or [""]
        return tuple(" ".join(lines[i : i + 3]) for i in range(0, len(lines), 3))

    @property
    def current_message(self):
        return self.pages[self.page]

    @property
    def visible_message(self):
        return self.current_message[: int(self.age * 55)]

    @property
    def message_complete(self):
        return self.age * 55 >= len(self.current_message)

    def set_phase(self, phase):
        self.phase = phase
        self.age = 0.0
        self.selection = 0
        if phase == Phase.DEFEND:
            context = TurnContext(self.turn, self.enemy_hp, self.character.max_hp, self.calm)
            pattern = self.character.choose_pattern(context)
            self.arena = Arena(pattern, self.player.hp, self.seed + self.turn)
            self.turn += 1
        elif phase == Phase.ATTACK:
            self.strike = self.weapon.factory()

    def say(self, message, then=Phase.DEFEND):
        self.message = message
        self.pages = self.paginate(message)
        self.page = 0
        self.after_message = then
        self.set_phase(Phase.MESSAGE)

    def finish(self, outcome, message):
        self.outcome = outcome
        self.say(message, Phase.FINISHED)
        self.cues.append("win" if outcome in (Outcome.SPARED, Outcome.DEFEATED) else "soft")

    def options(self):
        if self.phase == Phase.MENU:
            return ("FIGHT", "ACT", "ITEM", "SPARE")
        if self.phase == Phase.ACT:
            return tuple(act.name for act in self.character.acts) + ("Back",)
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
        self.cues.append("select")
        if self.phase == Phase.MENU:
            self.set_phase((Phase.ATTACK, Phase.ACT, Phase.ITEM, Phase.MERCY)[self.selection])
        elif self.phase == Phase.ACT:
            if self.selection == len(self.character.acts):
                self.set_phase(Phase.MENU)
            else:
                act = self.character.acts[self.selection]
                self.calm = min(self.character.calm_needed, self.calm + act.calm)
                suffix = " They seem ready to let you pass." if self.spare_ready else ""
                self.say(act.reply + suffix)
        elif self.phase == Phase.ITEM:
            if self.selection == 1:
                self.set_phase(Phase.MENU)
            elif self.player.snacks:
                self.player.snacks -= 1
                healed = self.player.heal(7)
                self.cues.append("heal")
                self.say(f"The cocoa is warm. You recover {healed} HP.")
            else:
                self.say(
                    "Your flask is empty. Rest at the lantern fountain to refill it.", Phase.MENU
                )
        elif self.phase == Phase.MERCY:
            if self.selection == 2:
                self.set_phase(Phase.MENU)
            elif self.selection == 1:
                self.finish(
                    Outcome.LEFT, "You wave goodbye. Practice can wait until you are ready."
                )
            elif self.spare_ready:
                self.finish(Outcome.SPARED, self.character.goodbye)
            else:
                self.say("They are still guarded. Try an ACT that helps you understand them.")

    def update(self, dt, controls):
        self.age += dt
        self.portrait_flash = max(0, self.portrait_flash - dt)
        if self.phase == Phase.MESSAGE:
            if controls.cancel or (controls.confirm and not self.message_complete):
                self.age = max(self.age, len(self.current_message) / 55)
            elif controls.confirm:
                if self.page + 1 < len(self.pages):
                    self.page += 1
                    self.age = 0
                else:
                    self.set_phase(self.after_message)
        elif self.phase in (Phase.MENU, Phase.ACT, Phase.ITEM, Phase.MERCY):
            if controls.cancel and self.phase != Phase.MENU:
                self.set_phase(Phase.MENU)
            elif controls.menu_step:
                self.selection = (self.selection + controls.menu_step) % len(self.options())
                self.cues.append("move")
            elif controls.confirm:
                self.choose()
        elif self.phase == Phase.ATTACK:
            self.strike.update(dt, controls)
            if self.strike.done:
                score = self.strike.score
                self.last_damage = max(1, round(self.weapon.power * score)) if score > 0 else 0
                self.enemy_hp = max(0, self.enemy_hp - self.last_damage)
                self.portrait_flash = 0.35 if self.last_damage else 0
                self.cues.append("hit" if self.last_damage else "soft")
                if self.enemy_hp == 0:
                    self.finish(
                        Outcome.DEFEATED,
                        f"{self.character.name} calls the match. You found your way through!",
                    )
                else:
                    quality = (
                        "Perfect timing!"
                        if score > 0.88
                        else "A glancing strike."
                        if score
                        else "The strike misses."
                    )
                    self.say(f"{quality} {self.last_damage} damage. Now watch their reply.")
        elif self.phase == Phase.DEFEND:
            self.arena.update(dt, controls)
            self.player.hp = self.arena.hp
            self.cues.extend(self.arena.cues)
            self.arena.cues.clear()
            if self.player.hp <= 0:
                self.finish(
                    Outcome.LOST,
                    "Time for a breather. The lantern fountain will patch you up. You can try again.",
                )
            elif self.arena.done:
                text = (
                    "You read every move."
                    if not self.arena.hits
                    else f"You made it through. {self.arena.hits} hit(s) taken."
                )
                if self.arena.blocks:
                    text += f" {self.arena.blocks} sparks blocked."
                self.say(text, Phase.MENU)
