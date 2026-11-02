"""Instructor examples for the six guided missions. Gameplay never imports this.

Compare with a student's work after they have made an attempt. These examples
are also used to test that completing a TODO really changes normal gameplay.
"""


def choose_player_view(*, facing):
    """Instructor example: choose the strongest facing axis, with vertical ties and a down fallback."""
    x, y = facing
    if abs(x) > abs(y):
        return "right" if x > 0 else "left"
    return "up" if y < 0 else "down"


def warm_light(*, world, obj):
    """Instructor example: restore up to 3 HP and tell the player the actual amount healed."""
    player = world.session.player
    healed = player.heal(amount=3)
    world.tell(text=f"{obj.definition.name} restores {healed} HP.")


def update_lantern_pulse(self, *, arena, seconds):
    """Instructor example: count down the elapsed seconds and emit one warned spark when due.

    Used as LanternPulse.update in regression fixtures; self owns the timer and
    arena owns projectile movement. Stop spawning early enough for sparks to leave.
    """
    self.cooldown -= seconds
    if self.cooldown <= 0 and arena.elapsed < 3.0:
        arena.spawn(x=8, y=arena.height / 2, vx=160, vy=0, warmup=0.5)
        self.cooldown += 0.8


def choose_echo_pattern(*, context):
    """Instructor example: create Ripples on turn 0 and a fresh LanternPulse on later turns."""
    from undercode.student_encounters import LanternPulse, RippleLanes

    if context.turn >= 1:
        return LanternPulse()
    return RippleLanes()


def movement_speed(*, controls):
    """Instructor example: let the world's existing movement step apply a chosen speed."""
    return 230 if controls.sprint_held else 155


def clicked_button(*, mouse_position, buttons):
    """Instructor example: pure hit testing; the engine owns executing the action."""
    if mouse_position is None:
        return None
    for button in buttons:
        if button.rect.collidepoint(mouse_position):
            return button.index
    return None
