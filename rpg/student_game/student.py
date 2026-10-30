"""FOUR GUIDED RPG MISSIONS -- YOU write the missing decisions.

The characters, actions, art, animations, mana system, and battle setups
already work. All four functions below are called by the REAL battle engine.
You can complete any mission without editing pygame or the combat rules.

For each mission:
  1. Launch its named scenario (commands are in the docstrings).
  2. See the deliberately wrong/simple behavior.
  3. Change ``if False`` to ``if True`` briefly to inspect real battle facts.
  4. Replace the TODO's simple default with your own ``if``/loop/return.
  5. Re-run the SAME scenario and compare the result.

HOW SCRIPTS WORK:
* ``turn`` describes one fighter's turn. ``turn.user`` is that fighter,
  ``turn.allies`` are teammates (NOT including the fighter), and
  ``turn.enemies`` are opponents.
* ``turn.attack(target=...)`` attacks an opponent. ``turn.defend()``
  protects the fighter. ``turn.skill(move, target=...)`` chooses a move.
  These RETURN actions; simply calling one without returning it is not enough.
* ``turn.can_use(move_id)`` checks that a move is known and affordable.
  Attack and Defend recover mana, so they are safe fallbacks.
* ``ctx`` is different: it is used for a scripted MOVE, not to choose
  a turn. A move returns commands such as ``damage(9)`` or a LIST of
  commands. The engine applies them, animates, and updates HP.

Want less direction? Try ``student_game/challenge.py`` after these missions.
The older working examples in ``student_game/workshop.py`` are unchanged.
"""

from __future__ import annotations

from rpg_battle.api import add_status, damage


# --------------------------------------------------------------------------
# 1. THE CONFUSED HEALER -- choose WHO to help and WHEN.
# --------------------------------------------------------------------------

def healer_strategy(turn):
    """MISSION 1 -- Make the distracted healer use a healing spell.

    Try these commands, from the rpg directory:
      python lab.py scenario healer_injured
      python main.py --scenario healer_injured --teach

    The healer is on the ENEMY team with an injured shieldbearer. It knows
    the spell 'Healing Light', but initially wastes every turn attacking.

    Inputs you can use:
      turn.user: the healer (hp, max_hp, hp_ratio, mana).
      turn.allies: living friends other than the healer, possibly empty.
      turn.enemies: living opponents, possibly several.
      turn.can_use("healing_light"): True if it can afford the spell.

    WALKTHROUGH:
    1. Turn on the diagnostic and inspect the shieldbearer's HP and the
       healer's mana. Compare 'hp' with 'max_hp'.
    2. Build a collection of people who MIGHT need healing. Remember:
       turn.user is also a possible patient; turn.allies excludes it.
    3. Choose somebody to heal. One idea: the fighter with the smallest
       hp_ratio. You can use a loop and an ``if`` to keep track of the
       most injured patient.
    4. Don't waste a healing spell on a healthy teammate. Decide what
       'injured enough' means (perhaps hp_ratio < 0.60).
    5. Before casting, check turn.can_use("healing_light"). Return
       turn.skill("healing_light", target=the_patient) when appropriate.
    6. Otherwise return turn.attack(target=turn.enemies[0]) or defend.

    TEST: start the injured scenario, watch the healer cast at its ally,
    then try the healthy scenario. It should not waste magic when everyone
    is already healthy. If mana runs out, it must still do something legal.
    """
    if False:
        print("HEALER:", turn.user.name, "MP", turn.user.mana,
              "allies", [(p.name, p.hp, p.max_hp) for p in turn.allies])

    # TODO(student): choose an injured friend, check mana, cast healing.
    return turn.attack(target=turn.enemies[0])  # Wrong on purpose for now.


# --------------------------------------------------------------------------
# 2. THE COWARDLY ENEMY -- a condition changes its strategy.
# --------------------------------------------------------------------------

def coward_strategy(turn):
    """MISSION 2 -- Teach the timid creature when to protect itself.

    Try:
      python lab.py scenario coward_low_hp
      python main.py --scenario coward_low_hp --teach

    The creature starts injured but always attacks anyway. It is capable
    of Defend already -- the missing part is a decision based on its HP.

    WALKTHROUGH:
    1. Inspect turn.user.hp, .max_hp, and .hp_ratio in the diagnostic.
    2. Compare a ratio (0 to 1) with a threshold such as 0.35.
    3. When the creature is in danger, return turn.defend().
    4. When it is healthy, keep attacking an enemy with turn.attack(...).
    5. Experiment with the threshold. Does defending too early make the
       enemy easier or harder to fight?

    TEST: in coward_low_hp, the creature should DEFEND. In coward_healthy,
    it should ATTACK. These are different scenarios for the same code.
    """
    if False:
        print("COWARD:", turn.user.name, "HP", turn.user.hp, "/",
              turn.user.max_hp, "ratio", round(turn.user.hp_ratio, 2))

    # TODO(student): if low on HP, return a different action.
    return turn.attack(target=turn.enemies[0])


# --------------------------------------------------------------------------
# 3. THE CURSED SWORD -- one move can return MULTIPLE commands.
# --------------------------------------------------------------------------

def cursed_sword_logic(ctx):
    """MISSION 3 -- Give the Cursed Sword a special effect.

    Try:
      python lab.py scenario sword_low_hp
      python main.py --scenario sword_low_hp --teach

    Your hero has the Cursed Sword equipped as a move (it's in the menu).
    The animation, sound, and ordinary damage already work. At the moment
    its Python function returns only damage(9), so there is NO curse.

    Inputs you can use:
      ctx.user.hp_ratio: the user's health fraction (e.g. 0.30).
      ctx.target: the enemy the move was aimed at.
      ctx.round_number: which round of battle it is.
      ctx.targets: all chosen targets (one for this sword).

    WALKTHROUGH:
    1. Play the sword scenario and look at the attack effect.
    2. Switch the debug print on, then compare the injured and healthy
       scenarios. What health threshold will make the sword awaken?
    3. A single command ``damage(9)`` deals ordinary damage. A *list* of
       commands lets one move do two things, in order.
    4. Try making a low-health branch return ordinary damage PLUS
       add_status("burn", turns=2). Burning enemies lose HP over time.
    5. Outside that branch, return ordinary damage as before.
    6. Check that the curse affects the target, not the wielder.

    TEST: the low-HP scenario should apply a status; the healthy scenario
    should not. Make sure the sword still deals damage in BOTH cases.
    STRETCH: unlock the curse when the enemy has a different status.
    """
    if False:
        print("SWORD:", "user hp", ctx.user.hp, "/", ctx.user.max_hp,
              "target", ctx.target.name if ctx.target else "none",
              "round", ctx.round_number)

    # TODO(student): under a condition, return a LIST with a second effect.
    return damage(9)  # Ordinary strike. The interesting part is missing.


# --------------------------------------------------------------------------
# 4. BOSS PHASES -- use different moves as the boss weakens.
# --------------------------------------------------------------------------

def boss_strategy(turn):
    """MISSION 4 -- Teach a boss to change phases in the middle of battle.

    Try:
      python lab.py scenario boss_low_hp
      python main.py --scenario boss_low_hp --teach

    The boss looks imposing and knows multiple animated skills, but right
    now it only uses its basic Attack. The engine already tracks HP, MP,
    available skills, animations, effects, and battle rounds.

    Moves already available to the boss:
      "gradient_descent" -- damaging magic targeting ONE enemy.
      "regularization"  -- defensive magic targeting the boss itself.
      "artifact_burst"  -- magical attack hitting ALL enemies.

    WALKTHROUGH:
    1. Look at the boss's hp_ratio and round_number in the diagnostic.
    2. Decide on TWO phases. For example, above half HP use an ordinary
       attack; below half HP become more aggressive.
    3. Add an ``if`` for the later phase. When MP is sufficient, use
       turn.can_use("artifact_burst") and return turn.skill(...).
       The engine chooses the targets for this all-enemies skill.
    4. When mana is too low, return turn.attack(...) to recover some.
    5. OPTIONAL: a third phase might sometimes use "regularization".
       It's a SELF-targeting spell; no opponent target should be given.
    6. Change the threshold or round_number rule and replay to compare.

    TEST: boss_healthy and boss_low_hp should use different actions once
    you implement the phase conditions. Both must return a legal action.
    STRETCH: create phases based on more than just HP, or add a pattern.
    """
    if False:
        print("BOSS:", turn.user.name, "HP", turn.user.hp, "/",
              turn.user.max_hp, "MP", turn.user.mana,
              "round", turn.round_number)

    # TODO(student): use if/else and turn.can_use() to choose a phase move.
    return turn.attack(target=turn.enemies[0])
