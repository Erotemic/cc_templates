"""Smoke-check beginner games and behavior-check intermediate features.

Run from choose_your_own_adventure/:
    python assignments/check.py B01
    python assignments/check.py I07

Checks avoid depending on narrative wording. They intentionally test stable action
IDs, item names, and state contracts documented in intermediate worksheets.
"""

import argparse
import ast
import importlib.util
from pathlib import Path
import subprocess
import sys

from catalog import ASSIGNMENTS, PROJECT, work_file


class CheckFailure(Exception):
    """A student-facing explanation of an unmet gameplay contract."""


def require(condition, explanation):
    if not condition:
        raise CheckFailure(explanation)


def actions(choices):
    return {choice.action for choice in choices}


def lines_contain(lines, term):
    return term.lower() in "\n".join(lines).lower()


def check_syntax(path):
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def check_quit(path):
    result = subprocess.run(
        [sys.executable, str(path)],
        cwd=PROJECT,
        input="quit\n",
        capture_output=True,
        text=True,
        timeout=8,
        check=False,
    )
    require(
        result.returncode == 0,
        "The game failed to start and quit cleanly. "
        f"Exit status: {result.returncode}. Error: {result.stderr.strip()[-1000:]}",
    )


def load_game_module(path, assignment_id):
    module_name = f"cyoa_assignment_{assignment_id}_student"
    spec = importlib.util.spec_from_file_location(module_name, path)
    require(spec is not None and spec.loader is not None, "Cannot import the game file.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module  # Required by @dataclass on Python 3.10.
    spec.loader.exec_module(module)
    return module


# Intermediate v1 exposes function dispatch rather than Game.
def v1_state():
    return {"key_taken": False, "game_won": False, "berry_taken": False}


def v1_actions(module, player, state):
    return {action for _label, action in module.build_choices(player, state)}


def v1_do(module, player, state, action):
    require(
        action in v1_actions(module, player, state),
        f"{action!r} should be an available choice in {player.location!r}.",
    )
    return module.handle_action(action, player, state)


def check_original_v1(module):
    player, state = module.Player(), v1_state()
    for action in ("go:forest", "search_stump", "go:cave", "open_chest"):
        v1_do(module, player, state, action)
    require(state["game_won"], "The original tiny treasure story must still be winnable.")


def check_original_v2(module):
    game = module.Game()
    for action in ("go:forest", "search_stump", "go:cave", "open_chest"):
        require(action in actions(game.choices()), f"Original action {action!r} is unavailable.")
        game.apply(action)
    require(game.won, "The original tiny treasure story must still be winnable.")


def check_original_v3(module):
    game = module.Game()
    solution = (
        "talk_elder", "go:crossroads", "go:forest", "take_herb",
        "go:crossroads", "go:lake", "talk_fisher", "go:crossroads",
        "go:ruins", "fight_spider", "combat:attack", "combat:attack",
        "go:tower", "take_crystal",
    )
    for action in solution:
        require(action in actions(game.choices()), f"Original story action {action!r} is unavailable.")
        game.apply(action)
    require(game.won, "The original Star Crystal ending must remain reachable.")


def check_i01(module):
    require("lookout" in module.ROOMS, "Add a room with key 'lookout' to ROOMS.")
    room = module.ROOMS["lookout"]
    require(
        any(dest == "forest" for _label, dest in room["exits"]),
        "The lookout needs an exit back to the forest.",
    )
    story_choices = [
        (index, spec) for index, spec in enumerate(room["choices"])
        if "action" not in spec and spec.get("result")
    ]
    require(story_choices, "The lookout needs a story-only telescope choice with a nonempty result.")
    player = module.Player(location="forest")
    state = v1_state()
    v1_do(module, player, state, "go:lookout")
    require(player.location == "lookout", "The forest exit should reach the lookout.")
    index, _spec = story_choices[0]
    result = v1_do(module, player, state, f"room:{index}")
    require(result and all(isinstance(item, str) for item in result),
            "The lookout's room choice should return story lines.")
    require(player.location == "lookout", "Inspecting the telescope should not move the player.")
    v1_do(module, player, state, "go:forest")
    require(player.location == "forest", "The return exit should reach the forest.")


def check_i02(module):
    for action in ("pick_berry", "trade_berry"):
        require(action in module.ACTION_HANDLERS, f"Register {action!r} in ACTION_HANDLERS.")
    state = v1_state()
    player = module.Player()
    v1_do(module, player, state, "trade_berry")
    require("lucky charm" not in player.inventory,
            "Trading without a wild berry must not award a charm.")
    v1_do(module, player, state, "go:forest")
    v1_do(module, player, state, "pick_berry")
    require(player.inventory.count("wild berry") == 1,
            "The first pickup should award exactly one 'wild berry'.")
    require(state["berry_taken"], "Record berry_taken=True after the first pickup.")
    if "pick_berry" in v1_actions(module, player, state):
        v1_do(module, player, state, "pick_berry")
    require(player.inventory.count("wild berry") == 1,
            "Revisiting or repeating the pickup must not produce extra berries.")
    v1_do(module, player, state, "go:village")
    v1_do(module, player, state, "trade_berry")
    require("wild berry" not in player.inventory, "Trading should consume the berry.")
    require(player.inventory.count("lucky charm") == 1,
            "Trading should give one 'lucky charm'.")
    if "trade_berry" in v1_actions(module, player, state):
        v1_do(module, player, state, "trade_berry")
    require(player.inventory.count("lucky charm") == 1,
            "Repeated trading must not duplicate charms.")


def check_i03(module):
    game = module.Game()
    require(hasattr(game, "visited") and isinstance(game.visited, set),
            "Game needs a visited set that it owns.")
    require(game.visited == {"village"}, "The initial visited set should be {'village'}.")
    require("journal" in actions(game.choices()), "Add a 'journal' action in every room.")
    before = (game.player.location, set(game.visited))
    result = game.apply("journal")
    require(lines_contain(result, "village"), "The journal should mention the starting village.")
    require((game.player.location, game.visited) == before,
            "Reading the journal must not change location or visit history.")
    game.apply("go:forest")
    game.apply("go:cave")
    game.apply("go:forest")
    require(game.visited == {"village", "forest", "cave"},
            "The journal should record each distinct entered room exactly once.")
    require("journal" in actions(game.choices()), "The journal must be available away from the village.")
    notes = game.apply("journal")
    for room in ("village", "forest", "cave"):
        require(lines_contain(notes, room), f"The journal needs to mention {room!r}.")
    require(game.player.location == "forest", "Reading field notes must not move the player.")


def check_i04(module):
    require("watchtower" in module.ROOMS, "Add the 'watchtower' Room to ROOMS.")
    room = module.ROOMS["watchtower"]
    require(room.choices, "The watchtower should have at least one RoomChoice.")
    require("forest" in room.exits.values(), "The watchtower needs a return exit to the forest.")
    game = module.Game()
    game.apply("go:forest")
    require("go:watchtower" not in actions(game.choices()),
            "The watchtower exit must be hidden before learning the secret trail.")
    try:
        game.apply("go:watchtower")
    except ValueError:
        pass
    else:
        raise CheckFailure("An illegal watchtower action must raise ValueError.")
    game.apply("go:village")
    game.apply("talk_villager")
    game.apply("go:forest")
    require("go:watchtower" in actions(game.choices()),
            "Speaking to the villager should unlock the forest watchtower exit.")
    game.apply("go:watchtower")
    require(game.player.location == "watchtower", "The unlocked exit must lead to the watchtower.")
    require("room:0" in actions(game.choices()),
            "The watchtower should offer its data-only RoomChoice.")
    story = game.apply("room:0")
    require(story and all(isinstance(line, str) for line in story),
            "The watchtower choice should return a line of story text.")
    require("go:forest" in actions(game.choices()), "Provide a return action to the forest.")
    game.apply("go:forest")
    require("go:watchtower" in actions(game.choices()),
            "The unlocked route should remain known after returning.")


def check_i05(module):
    game = module.Game()
    game.apply("go:crossroads")
    game.apply("go:forest")
    require("take_potion" in actions(game.choices()), "Offer 'take_potion' in the forest.")
    game.apply("take_potion")
    require(game.player.inventory.count("healing potion") == 1,
            "Taking the potion should add exactly one 'healing potion'.")
    if "take_potion" in actions(game.choices()):
        game.apply("take_potion")
    require(game.player.inventory.count("healing potion") == 1,
            "There must be only one forest potion.")
    require("drink_potion" not in actions(game.choices()),
            "The player shouldn't be able to drink a potion at full HP.")
    game.player.hp -= 4
    require("drink_potion" in actions(game.choices()),
            "An injured player with a potion should be able to drink it.")
    game.apply("drink_potion")
    require(game.player.hp == game.player.max_hp, "Healing must stop at max_hp.")
    require("healing potion" not in game.player.inventory, "Drinking must consume a potion.")
    require("drink_potion" not in actions(game.choices()),
            "The drink action shouldn't remain when no potion is held.")
    game.player.inventory.append("healing potion")
    game.player.hp = 1
    game.start_combat("ruin_spider")
    require("drink_potion" not in actions(game.choices()),
            "Drinking must not be legal during combat.")
    game.apply("combat:run")
    require("drink_potion" in actions(game.choices()),
            "Drinking should become available again outside combat.")
    game.apply("drink_potion")
    require(game.player.hp == 7, "Drinking should restore exactly 6 HP when far from max_hp.")


def check_i06(module):
    game = module.Game()
    require("combat:defend" not in actions(game.choices()),
            "Defend must not be offered outside combat.")
    game.apply("go:crossroads")
    game.apply("go:ruins")
    game.apply("fight_spider")
    require("combat:defend" in actions(game.choices()),
            "Add a 'combat:defend' action while fighting the spider.")
    before_hp, before_enemy_hp = game.player.hp, game.combat_hp
    game.apply("combat:defend")
    require(game.player.hp == before_hp - 1,
            "Defend should reduce the spider's attack from 2 to 1 for that turn.")
    require(game.combat_hp == before_enemy_hp,
            "Defending should not damage the enemy.")
    game.apply("combat:attack")
    require(game.player.hp == before_hp - 3,
            "A later Attack should still receive the normal 2 damage retaliation.")
    require(game.combat_hp == before_enemy_hp - game.player.attack,
            "Normal Attack should still damage the enemy.")
    game.apply("combat:attack")
    require("spider_defeated" in game.player.flags,
            "The player should still be able to defeat the spider normally.")


def check_i07(module):
    game = module.Game()
    game.apply("go:crossroads")
    game.apply("go:forest")
    require("take_bait" in actions(game.choices()), "Offer 'take_bait' in the forest.")
    game.apply("take_bait")
    require(game.player.inventory.count("spider bait") == 1,
            "Taking bait should give exactly one 'spider bait'.")
    if "take_bait" in actions(game.choices()):
        game.apply("take_bait")
    require(game.player.inventory.count("spider bait") == 1,
            "The forest bait must be collectible only once.")
    game.apply("go:crossroads")
    game.apply("go:ruins")
    require("calm_spider" in actions(game.choices()),
            "Offer 'calm_spider' at the ruins when holding bait.")
    game.apply("calm_spider")
    require("spider_pacified" in game.player.flags,
            "Pacifying the spider should set the 'spider_pacified' flag.")
    require("spider bait" not in game.player.inventory, "Pacifying should consume the bait.")
    require(game.combat_enemy is None and "spider_defeated" not in game.player.flags,
            "Pacifying is not fighting: it should not start combat or mark the spider defeated.")
    require("fight_spider" not in actions(game.choices()),
            "Don't offer the fight after the spider has been pacified.")
    require("go:tower" not in actions(game.choices()),
            "Pacifying alone must not bypass the tower key requirement.")
    game.apply("go:crossroads")
    game.apply("go:forest")
    game.apply("take_herb")
    game.apply("go:crossroads")
    game.apply("go:lake")
    game.apply("talk_fisher")
    require("tower key" in game.player.inventory,
            "The original herb-for-key trade must still work.")
    game.apply("go:crossroads")
    game.apply("go:ruins")
    require("go:tower" in actions(game.choices()),
            "With key and pacified spider, the tower should open.")
    game.apply("go:tower")
    game.apply("take_crystal")
    require(game.won, "The peaceful path must be able to win the game.")


def check_i08(module):
    require("lake_crab" in module.ENEMIES, "Add 'lake_crab' to ENEMIES.")
    spec = module.ENEMIES["lake_crab"]
    require(spec.hp == 8 and spec.attack == 1,
            "The lake crab must have 8 HP and attack for 1 damage.")
    game = module.Game()
    game.apply("go:crossroads")
    game.apply("go:lake")
    require("fight_crab" in actions(game.choices()), "Offer 'fight_crab' at the lake.")
    starting_gold = game.player.gold
    game.apply("fight_crab")
    require(game.combat_enemy == "lake_crab", "The action must start combat with lake_crab.")
    require(game.combat_hp == 8, "The lake crab should start at 8 HP.")
    game.apply("combat:attack")
    require(game.player.hp == game.player.max_hp - 1,
            "The crab should deal 1 retaliation damage after surviving a hit.")
    game.apply("combat:attack")
    require(game.combat_enemy is None, "The crab should be defeated by two normal hits.")
    require("crab_defeated" in game.player.flags, "Record the crab's defeat separately.")
    require("spider_defeated" not in game.player.flags,
            "Defeating the crab must NOT mark the spider defeated.")
    require(game.player.gold == starting_gold + 3, "The crab should award exactly 3 gold.")
    require("fight_crab" not in actions(game.choices()),
            "The crab fight must disappear after the crab is defeated.")
    game.apply("go:crossroads")
    game.apply("go:forest")
    game.apply("take_herb")
    game.apply("go:crossroads")
    game.apply("go:lake")
    game.apply("talk_fisher")
    game.apply("go:crossroads")
    game.apply("go:ruins")
    require("go:tower" not in actions(game.choices()),
            "A crab kill and a tower key must not open the spider's gate.")
    require("fight_spider" in actions(game.choices()),
            "The spider still needs to be present after defeating the crab.")


CHECKS = {
    "I01": (check_i01, check_original_v1),
    "I02": (check_i02, check_original_v1),
    "I03": (check_i03, check_original_v2),
    "I04": (check_i04, check_original_v2),
    "I05": (check_i05, check_original_v3),
    "I06": (check_i06, check_original_v3),
    "I07": (check_i07, check_original_v3),
    "I08": (check_i08, check_original_v3),
}


def verify(path, assignment_id):
    require(path.is_file(), f"Missing work file: {path}. Run: python assignments/start.py {assignment_id}")
    check_syntax(path)
    print("PASS: Python syntax")
    check_quit(path)
    print("PASS: game starts and quits")

    if assignment_id.startswith("B"):
        print("NEXT: play the 'Done when' steps in the worksheet to check your feature.")
        print("NOTE: Beginner features have NOT been automatically checked.")
        return

    module = load_game_module(path, assignment_id)
    feature, original = CHECKS[assignment_id]
    feature(module)
    print(f"PASS: {assignment_id} feature behavior")
    original(module)
    print("PASS: original game winning route")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("assignment", choices=sorted(ASSIGNMENTS))
    parser.add_argument("--file", type=Path, help="Check an existing file instead of assignments/work/ID.py")
    args = parser.parse_args(argv)
    path = (args.file if args.file is not None else work_file(args.assignment)).resolve()
    try:
        verify(path, args.assignment)
    except (CheckFailure, SyntaxError, OSError, subprocess.TimeoutExpired,
            KeyError, AttributeError, IndexError, TypeError, ValueError) as exc:
        parser.exit(1, f"FAIL: {exc}\n")


if __name__ == "__main__":
    main()
