"""ENCOUNTER LEARNING ROUTE -- GUIDED MISSIONS 4 AND 5 -- Build a new defense, then give it to Echo.

The RippleLanes class is a working example. LanternPulse is YOUR new mechanic:
its update() is called by the game but spawns nothing until you implement it.
Read encounters/engine.py and its phase handlers to understand the caller.
Run --practice pulse to test it, then connect it in choose_echo_pattern().
F2 shows phase/turn state. --check-exercise pulse/tactics runs YOUR implementation.
Each mission below explains the inputs, small steps, and visible success checks.
"""

import math
from .encounters.arena import DefensePattern
from .encounters.model import Act, Opponent
from .student_art import draw_echo


class RippleLanes(DefensePattern):
    """Worked defense example: falling rows with a two-lane opening that slides sideways."""

    name = "Ripples in the margins"
    hint = "Move through the spaces between the ripples."
    duration = 5.4

    def __init__(self):
        """Give this turn its own cooldown, wave counter, and editable spawn interval in seconds."""
        self.cooldown = 0.3
        self.wave = 0
        self.spawn_interval = 0.7  # TRY: .9 is calmer; .5 is busier.

    def update(self, *, arena, seconds):
        """Consume the elapsed seconds and create any ripple rows due during the spawn window.

        Compute a sliding gap from the wave counter and warn before projectiles
        fall. Arena moves and removes them; this method only schedules hazards.
        """
        if self.spawn_interval <= 0:
            raise ValueError("Ripple spawn_interval must be positive.")
        self.cooldown -= seconds
        while self.cooldown <= 0 and arena.elapsed < 3.8:
            # The opening slides left/right instead of being completely random.
            gap = 2 + round(math.sin(self.wave * 0.9) * 2)
            for lane in range(7):
                if lane not in (gap, gap + 1):
                    arena.spawn(
                        x=(lane + 0.5) * arena.width / 7,
                        y=5,
                        vx=0,
                        vy=105,
                        radius=6,
                        color=(137, 235, 202),
                        warmup=0.4,
                    )
            self.wave += 1
            self.cooldown += self.spawn_interval


class LanternPulse(DefensePattern):
    """MISSION 4 -- Send warned sparks from the left, one every 0.8 seconds.

    YOUR INPUTS:
      seconds: seconds since the last frame (roughly 1/60).
      self.cooldown: seconds until the next spark; starts at 0.3.
      arena.elapsed: seconds since this defense started.
      arena.width / height: local playfield size, independent of the window.
      arena.spawn(x=..., y=..., vx=..., vy=..., warmup=...): add a projectile.
        x,y are its starting position; vx,vy are pixels per second.
        warmup is warning time before movement and damage begin.

    WALKTHROUGH (in update below):
    1. Run --practice pulse. The arena is empty: you are adding its attack.
       Enable the diagnostic and watch cooldown. Currently it never changes.
    2. Subtract seconds from self.cooldown. Run again: it should decrease.
    3. When cooldown <= 0 AND arena.elapsed < 3.0, create one spark.
       Start at x=8, halfway down the arena (arena.height / 2).
       Use vx=160, vy=0 to move right. Add warmup=0.5 so a warning appears.
    4. In that SAME branch, add 0.8 to cooldown so sparks do not appear
       every frame. Try it without this line briefly: why is it so crowded?
    5. Dodge up/down. Watch the spark warn, move, and leave. The time limit
       leaves room for the final spark to cross before this phase ends.

    TEST IT: preview twice; sparks should appear at the same times. Try R.
    STRETCH: alternate heights, add safe gaps, or warn from both sides.
    """

    name = "Lantern pulse"
    hint = "Watch the left edge. Step above or below the sparks."
    duration = 7.5

    def __init__(self):
        """Initialize this turn's timer; mission 4 supplies the code that counts it down."""
        self.cooldown = 0.3

    def update(self, *, arena, seconds):
        """MISSION 4: implement the timer and warned sparks described above.

        Arena calls this once per defense update with seconds in seconds. Keep state
        on self and create projectiles through arena.spawn; the starter has no
        effect until you replace the TODOs with your own implementation.
        """
        if False:
            print(
                "PULSE DEBUG:",
                "time=",
                round(arena.elapsed, 2),
                "cooldown=",
                round(self.cooldown, 2),
            )

        # TODO 1: Decrease cooldown by seconds.
        # TODO 2: When ready (and elapsed < 3), spawn a warned right-moving spark.
        # TODO 3: Add 0.8 to cooldown in that branch.
        pass


def choose_echo_pattern(*, context):
    """MISSION 5 -- Let Echo change patterns after the opening turn.

    YOUR INPUTS:
      context.turn: 0 for the first defense, 1 for the next, then 2, ...
      context.calm: understanding earned through ACT choices.
      context.opponent_hp / opponent_max_hp: Echo's remaining / maximum health.

    WALKTHROUGH:
    1. Finish mission 4 and preview LanternPulse with --practice pulse.
    2. Run --encounter echo. Use ITEM or ACT, survive a defense, then repeat.
       Enable the diagnostic to see how turn changes between defenses.
    3. Before the fallback, add an if asking whether context.turn >= 1.
    4. In that branch return LanternPulse(). Keep RippleLanes() as the
       fallback, so the opening defense still uses the worked example.
    5. Play two turns again. Is the SECOND defense visibly your new pattern?
       The name above the arena should change from Ripples to Lantern pulse.

    TEST IT: opening turn = ripples; next turn = pulse. Restart resets it.
    Return a NEW instance each time: parentheses construct a fresh timer.
    STRETCH: use calm or HP instead of turn; explain your condition first.
    """
    if False:
        print(
            "ECHO DEBUG:", "turn=", context.turn, "calm=", context.calm, "HP=", context.opponent_hp
        )

    # TODO: Add the condition and return your new pattern in its branch.
    return RippleLanes()


ECHO = Opponent(
    key="echo",
    name="Echo",
    description="A lantern spirit learning to listen.",
    color=(115, 227, 193),
    portrait=draw_echo,
    acts=(
        Act(name="Listen", reply="You wait. Echo finds the words they were looking for.", calm=2),
        Act(name="Share a story", reply="Your story makes their light a little warmer.", calm=1),
        Act(
            name="Make a face",
            reply="Echo makes a face right back. It is a very good face.",
            calm=0,
        ),
    ),
    choose_pattern=choose_echo_pattern,
    max_hp=20,
    greeting='Echo lights up the quiet observatory. "Let us make something together."',
    goodbye="Echo lends you a little light for the road. A new friend counts as progress.",
)

# Registration is ordinary Python data. Add your own keys here and place a new
# character letter in a Python level legend. --practice previews a pattern.
EXTRA_OPPONENTS = (ECHO,)
EXTRA_PATTERNS = {"ripples": RippleLanes, "pulse": LanternPulse}
