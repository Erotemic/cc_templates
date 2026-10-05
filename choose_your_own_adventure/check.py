"""Fast repository sanity check that does not require Textual."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
ADVANCED = ROOT / "advanced"


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
    # The first object-oriented example is still a standalone file.
    tiny_module = load_module("intermediate/version2.py", "cya_intermediate_v2")
    tiny = tiny_module.Game()
    require(tiny.player.location == "village", "intermediate version2 should start in the village")
    require(tiny.choices(), "intermediate version2 should offer choices")

    richer_module = load_module("intermediate/version3.py", "cya_intermediate_v3")
    richer = richer_module.Game()
    require(richer.choices(), "intermediate version3 should offer choices")

    # The advanced package intentionally lives inside advanced/. Add that level
    # to the import path only for this repository-level check.
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

    require(not (ROOT / "adventure").exists(), "the shared library belongs under advanced/")
    require(not list(ROOT.glob("version*.py")), "numbered examples belong inside level folders")

    print("choose_your_own_adventure check: OK")
    print("  beginner examples: standalone")
    print("  intermediate examples: standalone")
    print("  advanced library: shared by multiple examples/worlds")


if __name__ == "__main__":
    main()
