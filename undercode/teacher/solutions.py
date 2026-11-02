"""Instructor examples for the four guided missions. Gameplay never imports this.

Compare with a student's work after they have made an attempt. These examples
are also used to test that completing a TODO really changes normal gameplay.
"""


def choose_player_view(facing):
    x, y = facing
    if abs(x) > abs(y):
        return "right" if x > 0 else "left"
    return "up" if y < 0 else "down"


def warm_light(world, obj):
    player = world.session.player
    healed = player.heal(3)
    world.tell(f"{obj.data['name']} restores {healed} HP.")


def update_lantern_pulse(self, arena, dt):
    self.cooldown -= dt
    if self.cooldown <= 0 and arena.elapsed < 3.0:
        arena.spawn(8, arena.height / 2, 160, 0, warmup=0.5)
        self.cooldown += 0.8


def choose_echo_pattern(context):
    from undercode.student import LanternPulse, RippleLanes

    if context.turn >= 1:
        return LanternPulse()
    return RippleLanes()
