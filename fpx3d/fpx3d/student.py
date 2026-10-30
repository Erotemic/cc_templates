"""YOUR FIRST EDITS: eight guided missions for Prism Vault.

The game is ALREADY playable. Every function below is called automatically
by fpx3d/engine.py; you're not expected to write window or 3D code first.

To learn: turn an ``if False:`` diagnostic into ``if True:`` temporarily.
Observe what the game tells you, then turn it off after making changes.

Coordinates: X = left/right, Y = forward/back, Z = UP.
Seconds: multiply speeds by seconds so behavior doesn't depend on FPS.
State: if something must be remembered, put it on the right object.

Missions 7 and 8 control a new robot. You write its decisions, while the
engine handles drawing, movement speed, and walls.

For less-guided work, visit ``challenge.py``. It describes goals but NOT
implementation locations or starter functions.
"""

# First five minutes: change the name and restart. Then change a color in
# world.py, or try moving a crystal in world.CORES to a different location.
YOUR_VAULT_NAME = "THE PRISM VAULT"


def bonus_reward(state, pickup):
    """MISSION 1 -- Give optional golden gems a real reward.

    The six colored prisms already open the portal, without your code.
    Golden bonus gems also disappear on contact, but give NO bonus yet.
    This hook is called ONCE for each bonus gem you collect.

    INPUTS: pickup.name, pickup.kind, state.bonus_points, state.hearts,
    state.time_left. The score HUD displays bonus_points.

    1. Look for a golden gem on an elevated balcony or in the south garden.
    2. Enable the print below to inspect the item when touching it.
    3. Increase state.bonus_points by 10 (``+= 10`` is useful).
    4. OPTIONAL: also add 5 seconds to state.time_left or heal one heart.
       Use ``min(3, state.hearts + 1)`` to prevent too much health.
    5. Try to collect a second bonus gem. Each should reward you ONCE.

    SUCCESS: collecting a bonus makes the score change without affecting
    the six required prisms. Changing the reward changes the gameplay.
    """
    if False:
        print("BONUS:", pickup.name, "score=", state.bonus_points)

    # TODO(student): add the reward you want here.
    pass


def move_drone(drone, seconds):
    """MISSION 2 -- Make a security drone patrol instead of standing still.

    Drones already exist, are visible, and hurt you on contact. Only their
    movement is unfinished; you do NOT have to draw or collide them.

    INPUTS: drone.x (current location), drone.direction (+1 or -1),
    drone.speed, drone.left_limit, drone.right_limit, seconds.

    1. Find a drone, enable the print, and watch its x and direction.
    2. Try: drone.x += drone.direction * drone.speed * seconds
       Running only that step makes it move away forever. Why?
    3. When x passes right_limit, set direction to -1 (toward the left).
    4. When x passes left_limit, set direction to +1 (toward the right).
    5. Clamp x to the limits when reversing to prevent a jittery edge.

    SUCCESS: the drone repeatedly patrols its short route and never
    leaves its bounds. Test at different frame rates (30 and 60 FPS).
    STRETCH: let it pause at an end using a countdown timer.
    """
    if False:
        print("DRONE:", drone.name, round(drone.x, 2),
              drone.direction, round(seconds, 3))

    # TODO(student): update x and change direction at the limits.
    pass


def update_scanner(scanner, seconds):
    """MISSION 3 -- Turn the central scanner into a timed hazard.

    The floor scanner is visible, but starts switched OFF. The engine
    already checks its circular region when scanner.active is True.

    INPUTS: scanner.age (seconds since the run started), scanner.active,
    scanner.radius, scanner.x, scanner.y, seconds.

    1. Walk through the central scanner now: it is harmless.
    2. Turn on the print and see scanner.age increase each frame.
    3. First try ``scanner.active = True`` to verify you can be hurt.
    4. Then alternate ON and OFF. For example, try a repeating cycle
       based on ``scanner.age % 4`` (the remainder after dividing by 4).
       Choose what part of each 4-second cycle is dangerous.
    5. Make sure you can tell from the scanner's color when it is safe.

    SUCCESS: the hazard follows a predictable ON/OFF pattern rather
    than switching once and staying on forever.
    STRETCH: speed up the scanner when time is running out.
    """
    if False:
        print("SCANNER:", round(scanner.age, 2), scanner.active)

    # TODO(student): change scanner.active based on the passage of time.
    pass


def activate_checkpoint(state, pad):
    """MISSION 4 -- Remember where the player should respawn.

    There are two green checkpoint pads. They don't save anything yet.
    The engine calls this function while you stand on one. It already
    handles losing hearts and returning to state.respawn_at.

    INPUTS: pad.x, pad.y; state.checkpoint_name (string),
    state.respawn_at (x, y, z tuple).

    1. Walk to a checkpoint and turn on the diagnostic. See pad.x/pad.y.
    2. Set state.respawn_at to the pad's position, with z=0.0.
       Hint: a tuple looks like ``(pad.x, pad.y, 0.0)``.
    3. Set state.checkpoint_name to ``f"{pad.x},{pad.y}"``. This marks
       the checkpoint as activated, so the HUD and pad can acknowledge it.
    4. Hit a danger pad three times and see where you reappear.
    5. Travel to the OTHER checkpoint and try again.

    SUCCESS: your latest activated checkpoint becomes the new respawn.
    STRETCH: choose when the checkpoint can be activated (e.g. costs gems).
    """
    if False:
        print("CHECKPOINT:", pad.x, pad.y, state.respawn_at)

    # TODO(student): update respawn_at AND checkpoint_name.
    pass


def update_sprint_energy(state, controls, seconds):
    """MISSION 5 -- Give sprinting an energy bar that can run out.

    Sprinting with Shift already works for free; the state.stamina bar
    starts at 100 and never decreases until you implement this mission.
    The engine sprints only while Shift is held AND stamina is above 0.

    INPUTS: controls.sprint is True when Shift is held;
    state.stamina is a number 0..100; seconds is this frame's duration.

    1. Hold Shift and print the stamina value. It stays at 100.
    2. While sprinting, subtract e.g. ``25 * seconds`` from stamina.
    3. While NOT sprinting, add e.g. ``15 * seconds`` back.
    4. Clamp between 0 and 100 with ``max(0, ...)`` and ``min(100, ...)``.
    5. Test holding Shift until sprint stops, then releasing to recover.

    SUCCESS: the green bar shrinks during sprint and refills while resting.
    STRETCH: wait one second before it starts refilling.
    """
    if False and controls.sprint:
        print("STAMINA:", round(state.stamina, 1), round(seconds, 3))

    # TODO(student): decrease or refill stamina, keeping it in [0, 100].
    pass


def move_lift(lift, seconds):
    """MISSION 6 -- Move a hovering platform sideways to make a ferry.

    The blue lift near the north garden is ALREADY a platform, and the
    player can land on it. The engine carries a player standing on it
    when the platform's x/y change. You add the movement.

    INPUTS: lift.x, lift.left_limit, lift.right_limit, lift.speed,
    lift.direction (+1 = right, -1 = left), seconds.

    1. Find the lift by the balconies. Turn on the print and inspect x.
    2. Move it a short distance: lift.x += lift.direction * lift.speed * seconds
    3. At the right limit, set lift.direction to -1; at the left limit +1.
    4. Clamp x back inside its two limits.
    5. Stand on it, release WASD, and see if you travel with it.

    SUCCESS: the platform goes back and forth without falling off its path.
    STRETCH: make another lift, or change its speed based on nearby players.
    """
    if False:
        print("LIFT:", lift.name, lift.x, lift.left_limit, lift.right_limit)

    # TODO(student): change lift.x and reverse at the boundaries.
    pass


def curator_line(state, event):
    """BONUS: personalize messages from the vault's invisible Curator.

    This hook IS already working. A string returned here replaces the
    default message on-screen when an event occurs. ``None`` uses the
    default message instead. The engine tells you what event occurred.

    Examples: 'core', 'bonus', 'jump', 'hurt', 'respawn', 'portal', 'win'.
    Start by changing one line. Then add an if statement based on
    state.cores_collected, state.hearts, or state.time_left.

    Think: if the SAME event happens twice, how would you tell those
    two situations apart? That's what state variables are for.
    """
    if False:
        print("CURATOR EVENT:", event, "prisms=", state.cores_collected)

    if event == "portal":
        return "The constellation is whole. Find the north gate."
    if event == "win":
        return "Vault cleared! The Curator grudgingly approves."
    if event == "hurt" and state.hearts == 1:
        return "The vault advises you to stop touching red things."
    return None


def guardian_markov(guardian, seconds):
    """MISSION 7 -- Give the clockwork robot a little decision-making brain.

    Find the purple-and-gold ROBOT near the south side of the vault. It is
    ALREADY drawn, stands still, and hurts you if you touch it. You don't
    need any 3D drawing or collision code to make it walk.

    THE IMPORTANT IDEA: A Markov chain has a CURRENT STATE and a rule for
    choosing the NEXT STATE based on the current one. This is one way to
    make a character wander without giving it a fixed scripted route.

    INPUTS AND MEMORY:
      guardian.mode          current state (starts as "idle")
      guardian.decision_timer seconds until we make another decision
      guardian.rng           a seeded Python random-number generator
      guardian.move_x/y      YOUR requested walking direction this frame
      seconds                elapsed frame time

    WALKTHROUGH:
    1. Enable the print below; the guard begins in the 'idle' state.
    2. Choose the possible states: 'idle', 'north', 'south', 'east', 'west'.
       Create a list with those five strings (order is your choice).
    3. Count the timer down each frame: subtract seconds from it.
       When it reaches zero, choose a NEW state and reset the timer to
       perhaps 1.0 or 2.0 seconds. The state persists on other frames.
    4. Try ``guardian.rng.choice(states)`` as a first experiment.
       For a real Markov-style rule, make the CHANCES depend on the old
       state. Example: staying 'idle' could be more likely if already
       idle. ``guardian.rng.choices(states, weights=weights)[0]`` lets
       you specify relative probabilities (e.g. [4, 1, 1, 1, 1]).
    5. Translate your chosen state into movement requests. For example,
       north means move_y = +1, south -1, east means move_x = +1.
       Idle means both directions should be 0 (the engine resets them
       to zero before calling you each frame).
    6. You should NOT directly change x/y. The engine already applies
       speed * seconds, restricts the robot to the room, and draws it.

    TEST: the guard sometimes pauses and sometimes changes direction.
    Restarting the game gives the same random pattern at the same times.
    STRETCH: prefer turns over reversals; avoid getting near walls; give
    each old state a different list of transition probabilities.
    """
    if False and guardian.decision_timer <= 0:
        print("GUARD BRAIN:", guardian.name,
              "state=", guardian.mode,
              "timer=", round(guardian.decision_timer, 2))

    # TODO 1: count down decision_timer and pick a state when it expires.
    # TODO 2: choose probabilities that depend on the previous mode.
    # TODO 3: set move_x and move_y based on the chosen mode.
    pass


def guardian_chase(guardian, player, seconds):
    """MISSION 8 -- Chase the player, but ONLY inside a detection radius.

    This exercise works independently of Mission 7. If you return True,
    the engine will use YOUR chase movement; if False, it runs the
    Markov/patrol mission instead. That gives the robot two behaviors.

    INPUTS:
      guardian.x/y, player.x/y: their positions on the floor
      guardian.detection_radius: how near the player must be
      guardian.move_x/y: desired direction, not a world position

    WALKTHROUGH:
    1. Turn on the debug print. Stand far away, then walk near the guard.
       Notice how dx and dy (differences between the two positions) change.
    2. Compute dx = player.x - guardian.x and dy similarly.
       The distance between them is ``(dx**2 + dy**2)**0.5``.
    3. Compare distance with guardian.detection_radius. If farther away,
       return False so Mission 7 is allowed to control movement.
    4. If close enough, request movement TOWARD the player by setting
       move_x and move_y. Try dx and dy directly first. The engine
       normalizes the direction and applies the chase speed.
    5. Return True in the chase case. Don't forget to return False in the
       non-chase case, or the guard will never switch to patrol mode.

    TEST: the robot remains still outside the radius if Mission 7 is
    unfinished, but follows you when you come close. Running away makes
    it stop chasing again. The player can still evade it by jumping.
    STRETCH: have it stop when very close, lose sight behind obstacles,
    or remember your last position for two seconds after you escape.
    """
    if False:
        dx = player.x - guardian.x
        dy = player.y - guardian.y
        distance = (dx * dx + dy * dy)**0.5
        print("GUARD CHASE:", guardian.name,
              "distance=", round(distance, 2),
              "range=", guardian.detection_radius,
              "dx=", round(dx, 2), "dy=", round(dy, 2))

    # TODO: if the player is nearby, set movement toward them and return True.
    # TODO: when they are far away, return False for ordinary patrol behavior.
    return False
