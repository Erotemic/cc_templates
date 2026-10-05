"""Fast repository sanity check that does not require Textual."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
ADVANCED = ROOT / "advanced"
CAPSTONE = ROOT / "capstone"


def load_module(relative_path: str, module_name: str):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    # Intermediate remains self-contained even after it gains objects.
    tiny_module = load_module("intermediate/version2.py", "cya_intermediate_v2")
    tiny = tiny_module.Game()
    require(tiny.player.location == "village", "intermediate version2 should start in the village")
    require(tiny.choices(), "intermediate version2 should offer choices")

    larger_module = load_module("intermediate/version3.py", "cya_intermediate_v3")
    larger = larger_module.Game()
    require(larger.choices(), "intermediate version3 should offer choices")

    # The advanced teaching package lives inside advanced/ and is reused by two
    # intentionally small worlds.
    sys.path.insert(0, str(ADVANCED))
    try:
        from adventure.worlds.dust_vault import make_dust_vault_game
        from adventure.worlds.star_crystal import make_star_crystal_game

        star = make_star_crystal_game()
        dust = make_dust_vault_game()
        require(star.world is not dust.world, "the two advanced worlds should be distinct")
        require(type(star) is type(dust), "the two advanced worlds should reuse one engine")
    finally:
        sys.path.remove(str(ADVANCED))

    # Capstone has a separate, descriptively named engine because it supports
    # the complete original worlds rather than the teaching-sized examples.
    sys.path.insert(0, str(CAPSTONE))
    try:
        from art.dust_vault import DUST_VAULT_ART
        from art.star_crystal import STAR_CRYSTAL_ART
        from engine.game import AdventureGame
        from engine.validation import validate_state, validate_world
        from worlds.dust_vault import WORLD_DATA as DUST_VAULT
        from worlds.star_crystal import WORLD_DATA as STAR_CRYSTAL

        require(len(STAR_CRYSTAL["rooms"]) >= 11, "full Star Crystal world should be present")
        require(len(DUST_VAULT["rooms"]) >= 18, "full Dust Vault world should be present")
        require(len(STAR_CRYSTAL["items"]) >= 12, "full Star Crystal item set should be present")
        require(len(DUST_VAULT["items"]) >= 14, "full Dust Vault item set should be present")
        require(not validate_world(STAR_CRYSTAL), "capstone Star Crystal world data should validate")
        require(not validate_world(DUST_VAULT), "capstone Dust Vault world data should validate")
        star_game = AdventureGame(STAR_CRYSTAL)
        dust_game = AdventureGame(DUST_VAULT)
        require(star_game.choices(), "capstone Star Crystal should be playable")
        require(dust_game.choices(), "capstone Dust Vault should be playable")
        require(not validate_state(star_game), "capstone Star Crystal initial state should validate")
        require(not validate_state(dust_game), "capstone Dust Vault initial state should validate")
        require(len(STAR_CRYSTAL_ART) >= 50, "all original Star Crystal art states should be present")
        require("npc::elder_mira::alive" in STAR_CRYSTAL_ART, "Elder Mira art should be present")
        require("loc::river_west" in STAR_CRYSTAL_ART, "the river quest should have presentation art")
        require("river_crossing" in STAR_CRYSTAL, "the capstone should include the river state machine")
        require(
            all(f"loc::{key}" in DUST_VAULT_ART for key in DUST_VAULT["rooms"]),
            "every Dust Vault location should have art",
        )
        require((CAPSTONE / "engine" / "textual_app.py").is_file(), "capstone Textual UI should be present")
        require((CAPSTONE / "tests" / "test_state_machine.py").is_file(), "capstone should teach state-machine testing")
        require((CAPSTONE / "simulate.py").is_file(), "capstone should include a headless simulator")
    finally:
        sys.path.remove(str(CAPSTONE))

    require(not (ROOT / "adventure").exists(), "shared libraries belong inside their teaching level")
    require(not list(ROOT.glob("version*.py")), "numbered examples belong inside level folders")
    require(not (CAPSTONE / "rich.py").exists(), "capstone modules should be named by responsibility")
    require(not (CAPSTONE / "engine" / "rich.py").exists(), "capstone modules should be named by responsibility")

    print("choose_your_own_adventure check: OK")
    print("  beginner examples: standalone")
    print("  intermediate examples: standalone and easy to extend with room choices")
    print("  advanced library: shared by multiple teaching-sized worlds")
    print("  capstone: full worlds + presentation + validation/simulation testing")


if __name__ == "__main__":
    main()
