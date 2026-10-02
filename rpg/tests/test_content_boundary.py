from __future__ import annotations

import ast
from pathlib import Path


def test_engine_does_not_import_the_shipped_game_or_legacy_content_catalogs() -> None:
    package_root = Path(__file__).parents[1] / "src" / "rpg_battle"
    engine_dirs = ["audio", "battle", "core", "render"]
    offenders: list[str] = []
    forbidden_content_ids = {
        "strike",
        "menu_move",
        "menu_confirm",
        "menu_back",
        "damage_tick",
        "heal_chime",
        "heal_pulse",
        "attack_basic",
    }

    for dirname in engine_dirs:
        for path in (package_root / dirname).glob("*.py"):
            tree = ast.parse(path.read_text(), filename=str(path))
            imported_modules: list[str] = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported_modules.extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported_modules.append(node.module)

            string_literals = {
                node.value
                for node in ast.walk(tree)
                if isinstance(node, ast.Constant) and isinstance(node.value, str)
            }

            if any(
                module == "student_game"
                or module.startswith("student_game.")
                or module == "rpg_battle.content"
                or module.startswith("rpg_battle.content.")
                for module in imported_modules
            ) or string_literals.intersection(forbidden_content_ids):
                offenders.append(str(path.relative_to(package_root)))

    assert offenders == []
