"""GUIDED MISSION 2 -- Give the Story Studio's light a healing effect.

Run ``python main.py --level studio``. The mint oval below the path is already
connected to warm_light through the 's' letter in studio.json. It does not heal
yet. You implement the effect; the engine handles entering/leaving the tile.
"""


def warm_light(world, obj):
    """Heal the Courier on entering the light, then show how much HP returned.

    YOUR INPUTS:
      world.session.player: the player, with hp, max_hp, and heal(amount).
      player.heal(amount) changes HP, clamps it, and RETURNS the actual gain.
      world.tell(text): show a short message in the world HUD.
      obj.data['name']: this story object's name, from its map legend.

    WALKTHROUGH:
    1. Enter the oval. Turn on the diagnostic to see HP before the effect.
    2. Store world.session.player in a variable named player.
    3. Call player.heal(3) and store its returned value in healed.
       Do not assign hp = 3: that would replace health instead of adding it.
    4. Show a message with world.tell(...). Include healed in an f-string:
       f"The light restores {healed} HP." is an example expression.
    5. Test at full HP and low HP. For a temporary low-HP experiment, add
       player.hp = 5 BEFORE the heal call, test once, then REMOVE that line.
       You can also visit after taking damage in an encounter.

    TEST IT: at 5/20 HP, entry gives 8/20. Staying still gives no extra heals.
    Leave and re-enter for 11/20. At 19/20, report 1 healed; at 20/20 report 0.
    STRETCH: require a story flag, charge a snack, or heal only once per run.
    """
    if False:
        print("LIGHT DEBUG:", obj.data["name"], "HP=", world.session.player.hp)

    # TODO: heal by 3, keep the actual gain, then show it with world.tell().
    pass


# The engine calls registry functions by their JSON name. Add your own here.
WORLD_MECHANICS = {"warm_light": warm_light}
