"""ELEVEN GUIDED PROJECTS. Pick one; do not try them all in one class.

The game already works with three levels, stars, an exit, music, and jumping.
The numbered functions below are deliberately incomplete. They are called by
other files unless a mission explicitly tells you to edit a level or song.

How to work:
  1. Read ONE function's explanation and its success check.
  2. Turn its ``if False:`` into ``if True:`` to observe actual game values.
  3. Try a small code change, run the game, and test it.
  4. Turn the diagnostic off when finished.

The later missions require editing several files, just like a real game.
You can find a shorter lesson checklist in MISSIONS.md. For independent
ideas with fewer hints, open challenge.py.
"""

from . import settings

# MISSION 0: Change these, run the game, and see what happens!
GAME_TITLE = "LITTLE PLATFORMER"
HERO_COLOR = (100, 218, 238)  # red, green, blue (each 0 to 255)

# MISSION 5: Change this to 1.2 seconds, then implement draw_transition().
# Zero means the current instant level change stays in place.
TRANSITION_SECONDS = 0.0


def bounce_from_pad(player):
    """MISSION 1: Make the orange spring launch the player upward.

    Already working: gravity, landing, and detection of standing on the pad.
    This function runs when the player STANDS ON the orange pad.

    Useful: player.vy is vertical speed (negative = up).
            player.on_ground is True while standing on a surface.

    1. Stand on the pad and change if False below to if True.
    2. Watch vy and on_ground in the terminal.
    3. Set player.vy to -850 to launch upward.
    4. Set player.on_ground to False because the player left the ground.
    5. Try different speeds such as -650 and -1000.

    SUCCESS: The spring launches you without needing to press jump.
    """
    if False:
        print("PAD", "vy=", round(player.vy), "on_ground=", player.on_ground)
    # TODO(student): set the two player attributes described above.
    pass


def move_enemy(enemy, seconds):
    """MISSION 2: Make the purple creature patrol between two boundaries.

    Already working: enemy position, collision with the hero, drawing.

    enemy.x: left side of enemy; enemy.speed: pixels per second.
    enemy.direction: +1 for right, -1 for left.
    left_limit and right_limit are valid endpoints for enemy.x.

    1. Turn on the diagnostic; observe x, speed, and direction.
    2. Add enemy.speed * enemy.direction * seconds to enemy.x.
    3. When x reaches right_limit, turn left (direction = -1).
    4. When x reaches left_limit, turn right (direction = +1).
    5. Keep x inside those limits. Test each boundary.

    SUCCESS: The creature goes back and forth instead of walking away.
    """
    if False:
        print("ENEMY", "x=", round(enemy.x), "speed=", enemy.speed,
              "direction=", enemy.direction,
              "limits=", (enemy.left_limit, enemy.right_limit),
              "seconds=", round(seconds, 3))
    # TODO(student): move horizontally and change direction at the ends.
    pass


def design_fourth_level():
    """MISSION 3: Make a fourth level that you invented.

    This mission edits DATA, not a function called every frame.
    Open platformer/level.py. Read the three maps and their legend.

    1. Copy LEVEL_3 to create LEVEL_4 with a different layout.
    2. Each row must have exactly 24 characters; use 15 rows.
    3. Keep one P (start), D (door), E (enemy), ^ (spring), and a star.
    4. Add LEVEL_4 to LEVELS and its name to LEVEL_NAMES.
    5. Run the game and reach your new level by beating level 3.
    6. Run `python -m unittest discover -s tests` to validate your maps.

    SUCCESS: Level 3's door takes you to a PLAYABLE fourth level,
    and the final win screen appears after the last level, not level 3.
    STRETCH: Move the start, try a harder path, and add optional stars.
    """
    # Nothing needs to run here. The real task is in level.py.
    pass


def hero_speech(event, game):
    """MISSION 4: Make the robot TALK when hurt or collecting a star.

    The game calls this function ONLY on a "hurt" or "star" event.
    Return text to put in a speech bubble beside the player.
    Return None to say nothing (the unfinished starting behavior).

    1. Turn on the diagnostic. Get hit and pick up a star.
    2. Use if event == "star": to choose a happy response.
    3. Use if event == "hurt": to choose a different response.
    4. Return a short string, such as "Oof!", for one event.
    5. Test that the bubble appears, moves with the hero, then disappears.

    SUCCESS: The robot says TWO different things for the two events.
    STRETCH: Use game.collected or game.level_index for more reactions.
    """
    if False:
        print("SPEECH", "event=", event, "stars=", game.collected,
              "level=", game.level_index + 1)
    # TODO(student): use conditions and return a string or None.
    return None


def draw_transition(screen, progress, next_level):
    """MISSION 5: Draw an animation BETWEEN two levels.

    First change TRANSITION_SECONDS (above) to 1.2. The game will wait
    before entering the next room. This function is called EVERY frame
    of that wait, after the normal room has been drawn.

    screen: pygame Surface. progress: 0.0 at the start, 1.0 at the end.
    next_level: the name of the upcoming level (a string).

    1. Enable the diagnostic; finish a level and watch progress increase.
    2. Import pygame inside this function (if you need pygame.draw).
    3. Draw a rectangle whose width grows with progress. Example idea:
       width = int(progress * screen.get_width()).
    4. Try drawing next_level with pygame.font.Font(None, 44).
    5. Keep everything within the window and test the full transition.

    SUCCESS: The screen visibly animates BEFORE the next level appears.
    STRETCH: Fade, slide, or make a two-part wipe.
    """
    if False:
        print("TRANSITION", "progress=", round(progress, 2),
              "next=", next_level)
    # TODO(student): use pygame drawing operations on screen.
    pass


def update_boss(boss, game, seconds):
    """MISSION 6: Turn the large creature in level 3 into a boss fight.

    The boss is already drawn. It does NOT attack or block progress yet.
    Only level 3 has a B tile by default. This function runs every frame
    while the boss exists; your code determines the battle rules.

    boss.rect: rectangle for collisions; boss.health: starts at 3.
    boss.active: if True AND health > 0, the exit stays locked.
    boss.hit_cooldown: seconds of protection after taking a hit.
    game.player.rect: hero rectangle; game.player.vy: vertical speed.

    1. Turn on the diagnostic, visit level 3, and inspect the boss.
    2. Set boss.active = True to require defeating it before exiting.
    3. Decide HOW to damage it (e.g. land on its head from above).
    4. Detect contact using game.player.rect.colliderect(boss.rect).
    5. Decrease health only once per hit. Use hit_cooldown as a timer.
    6. Give the player feedback: a bounce, a sound, or a message.
    7. Test that reaching zero health unlocks the door.

    SUCCESS: The boss takes three separate hits and becomes defeatable.
    STRETCH: Add an attack pattern or second stage when health gets low.
    """
    if False:
        print("BOSS", "health=", boss.health, "active=", boss.active,
              "touch=", game.player.rect.colliderect(boss.rect),
              "cooldown=", round(boss.hit_cooldown, 2))
    # TODO(student): activate boss; detect hits; change health/state.
    pass


def level_melody(level_index):
    """MISSION 7: Compose a NEW song for one of the levels.

    The current music is built from MIDI note numbers in sound.py.
    Return None to reuse the original song (the starting behavior), or
    return a tuple of note numbers for a different song.

    1. Open platformer/sound.py and find MELODY and make_music().
    2. Find how note 69 becomes the frequency 440 Hz.
    3. Write your own tuple of 8 or 16 note numbers here.
    4. Return it when level_index == 1 (the SECOND level, index starts at 0).
    5. Return None in the other levels. Restart and listen on level 2.

    SUCCESS: Level 2 sounds different, and the original song returns
    when you go back to a level without a custom melody.
    STRETCH: A boss theme, rests, or rhythm changes in make_music().
    """
    if False:
        print("SONG", "level_index=", level_index)
    # TODO(student): choose a tuple of note numbers for a particular level.
    return None


def camera_view(player):
    """MISSION 8: Zoom the camera and FOLLOW the player.

    Return (center_x, center_y, zoom). The engine does the cropping and
    drawing for you. Zoom 1.0 means the whole one-screen level is visible.
    Zoom 1.6 shows a smaller part of the room, but makes it look larger.

    1. Turn on the diagnostic and move; read player.rect.centerx/centery.
    2. First return (480, 300, 1.6) to test a fixed zoomed-in camera.
    3. Replace 480, 300 with player.rect.centerx and .centery.
    4. Walk to each edge. The drawing code keeps the camera in bounds.
    5. Try different zoom factors. The HUD should NOT move with the camera.

    SUCCESS: The hero stays near the center when possible, and the view
    follows while you move. Pressing H is not required; just test movement.
    STRETCH: Smooth following using a remembered camera position.
    """
    if False:
        print("CAMERA", "player_center=", player.rect.center)
    # TODO(student): change center and zoom; do not change player physics.
    return (settings.WIDTH / 2, settings.HEIGHT / 2, 1.0)


def try_double_jump(player, jump_pressed):
    """MISSION 9: Let the hero jump ONCE more before landing.

    Called each frame BEFORE normal player physics. Regular ground jumps
    already work. This function may add an AIRBORNE jump; return True if
    it actually performed one, otherwise False.

    player.on_ground says whether the previous frame ended on a platform.
    player.extra_jump_used starts False (see sprites.py, Player.__init__).

    1. Turn on the diagnostic and jump once, then press X again in midair.
    2. When player.on_ground is True, reset extra_jump_used to False.
    3. If jump_pressed while AIRBORNE and you have not used the extra jump,
       make player.vy negative, and set extra_jump_used to True.
    4. Return True only on that second jump (the engine plays a sound).
    5. Test pressing jump THREE times before landing. Only two should work.

    SUCCESS: You can jump twice, not infinitely, until you land.
    """
    if False and jump_pressed:
        print("DOUBLE JUMP", "ground=", player.on_ground,
              "used=", player.extra_jump_used,
              "vy=", round(player.vy))
    # TODO(student): reset the flag on ground, and consume it in the air.
    return False


def move_platform(platform, seconds):
    """MISSION 10: Make the blue platform move while you STAND on it.

    A blue platform marked M is already placed in level 2. It is solid
    and carries the hero sideways when its position changes.

    platform.x: its horizontal position; platform.direction: +1 or -1.
    platform.left_limit and right_limit: where it should reverse.
    platform.speed: pixels per second. seconds: time since previous frame.

    1. Find the blue ledge in level 2 and enable the diagnostic.
    2. Change platform.x by speed * direction * seconds each frame.
    3. If it reaches the right limit, set direction to -1.
    4. If it reaches the left limit, set direction to +1.
    5. Clamp x to the limits, then test standing on it and jumping away.

    SUCCESS: The platform goes back and forth without throwing the hero off.
    STRETCH: Pause at the edges or change speed when carrying a passenger.
    """
    if False:
        print("MOVING PLATFORM", "x=", round(platform.x),
              "direction=", platform.direction,
              "limits=", (platform.left_limit, platform.right_limit))
    # TODO(student): change x and direction at the edges.
    pass


def activate_switch(game):
    """MISSION 11: Make the small switch reveal a BONUS STAR.

    A switch marked S is already drawn in level 2. The engine calls this
    function when the hero overlaps it. It starts red, unpressed.

    game.switch_pressed: starts False; turns the switch green when True.
    game.stars: list of pygame.Rect collectibles.
    game.total_stars: total number of stars required for the exit.
    game.bonus_star: a prepared Rect where a secret star can appear.

    1. Turn on the diagnostic. Stand on the switch.
    2. Only act if game.switch_pressed is False. Otherwise repeated frames
       could spawn dozens of stars!
    3. Set game.switch_pressed to True to remember the event.
    4. Add game.bonus_star to game.stars and increment total_stars by 1.
    5. Pick up the newly revealed star and verify the exit counts it.

    SUCCESS: One touch reveals ONE bonus star. The switch stays green.
    STRETCH: Make a puzzle requiring two switches in the right order.
    """
    if False:
        print("SWITCH", "pressed=", game.switch_pressed,
              "stars_left=", len(game.stars))
    # TODO(student): only once, activate and reveal the prepared bonus star.
    pass
