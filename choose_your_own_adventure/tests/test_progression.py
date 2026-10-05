from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
ADVANCED = ROOT / "advanced"


def run_script(relative_path: str, user_input: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / relative_path)],
        input=user_input,
        text=True,
        capture_output=True,
        cwd=ROOT,
        timeout=10,
        check=False,
    )


def load_module(relative_path: str, module_name: str):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


TINY_VERSIONS = [
    "beginner/version1.py",
    "beginner/version2.py",
    "intermediate/version1.py",
    "intermediate/version2.py",
]


@pytest.mark.parametrize("relative_path", TINY_VERSIONS)
def test_tiny_versions_have_same_winning_path(relative_path):
    # village -> forest -> stump -> cave -> chest
    result = run_script(relative_path, "1\n3\n2\n2\n")
    assert result.returncode == 0, result.stderr
    assert "You win" in result.stdout


@pytest.mark.parametrize("relative_path", TINY_VERSIONS)
def test_zero_is_rejected_instead_of_selecting_last_choice(relative_path):
    result = run_script(relative_path, "0\nquit\n")
    assert result.returncode == 0, result.stderr
    assert "menu numbers" in result.stdout or "not one of the choices" in result.stdout
    assert "You win" not in result.stdout


def play(game, actions):
    for action in actions:
        legal = {choice.action for choice in game.choices()}
        assert action in legal, (action, sorted(legal), game.describe())
        game.apply(action)
    return game


def star_crystal_solution(game):
    return play(
        game,
        [
            "talk_elder",
            "go:crossroads",
            "go:forest",
            "take_herb",
            "go:crossroads",
            "go:lake",
            "talk_fisher",
            "go:crossroads",
            "go:ruins",
            "fight_spider",
            "combat:attack",
            "combat:attack",
            "go:tower",
            "take_crystal",
        ],
    )


def test_intermediate_richer_game_has_scriptable_backend():
    module = load_module("intermediate/version3.py", "cya_test_intermediate_v3")
    game = star_crystal_solution(module.Game())
    assert game.won
    assert "tower key" in game.player.inventory
    assert "spider_defeated" in game.player.flags


def test_shared_star_crystal_world_can_be_completed():
    sys.path.insert(0, str(ADVANCED))
    try:
        from adventure.worlds.star_crystal import make_star_crystal_game

        game = star_crystal_solution(make_star_crystal_game())
    finally:
        sys.path.remove(str(ADVANCED))
    assert game.won
    assert game.ending.startswith("You recovered")


def test_dust_vault_reuses_engine_and_can_be_completed():
    sys.path.insert(0, str(ADVANCED))
    try:
        from adventure.core import AdventureGame
        from adventure.worlds.dust_vault import make_dust_vault_game

        game = make_dust_vault_game()
        assert isinstance(game, AdventureGame)
        play(
            game,
            [
                "read_contract",
                "go:market",
                "buy_code",
                "go:tunnels",
                "fight_drone",
                "combat:attack",
                "combat:attack",
                "take_cell",
                "go:market",
                "go:vault_door",
                "go:vault",
                "recover_maps",
            ],
        )
    finally:
        sys.path.remove(str(ADVANCED))
    assert game.won
    assert game.player.has("vault code")
    assert game.player.has("power cell")


def test_core_has_no_terminal_io_or_textual_dependency():
    source = (ADVANCED / "adventure" / "core.py").read_text()
    tree = ast.parse(source)

    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert "input" not in called_names
    assert "print" not in called_names
    assert "textual" not in imported_roots


def test_textual_frontend_does_not_bridge_legacy_blocking_io():
    source = (ADVANCED / "adventure" / "ui" / "textual_app.py").read_text()
    assert "threading" not in source
    assert "redirect_stdout" not in source
    assert "builtins.input" not in source
    assert "queue.Queue" not in source
    assert "game.apply(action)" in source


def test_advanced_versions_are_examples_not_copied_engines():
    for name in ["version1.py", "version2.py", "version3.py", "version4.py"]:
        lines = (ADVANCED / name).read_text().splitlines()
        assert len(lines) < 80, f"advanced/{name} grew into another copied engine"


def test_level_boundaries_are_visible_in_the_filesystem():
    assert not (ROOT / "adventure").exists()
    assert not list(ROOT.glob("version*.py"))
    assert (ADVANCED / "adventure" / "core.py").is_file()

    beginner_source = "\n".join(path.read_text() for path in (ROOT / "beginner").glob("version*.py"))
    intermediate_source = "\n".join(path.read_text() for path in (ROOT / "intermediate").glob("version*.py"))
    assert "from adventure" not in beginner_source
    assert "from adventure" not in intermediate_source
