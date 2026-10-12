"""Real-engine checks for the classroom team-controller tournament.

Avoid assertions about student-facing worksheet wording: only test combat
behavior, CLI handling, game fairness, and safe starter-file creation.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from student_game import CONTENT
from team_arena.cli import (
    BUILTIN,
    PREFABS,
    PLAYERS,
    REQUIRED_SCORE,
    _score,
    builtin_names,
    bounded_pair,
    controller_for,
    make_parser,
    run,
)
from team_arena.engine import (
    ARENA_ID,
    GUARDIAN,
    MAGE,
    content_for_match,
    compare,
    single_match,
)

ROOT = Path(__file__).resolve().parents[1]


def test_teams_are_symmetric_and_story_content_unchanged():
    before_encounters = frozenset(CONTENT.encounters)
    content = content_for_match("left", controller_for("first_target"),
                                "right", controller_for("heavy_hitter"))
    match = content.encounters[ARENA_ID]
    assert match.player_team.members == match.enemy_team.members == (
        GUARDIAN.char_id, MAGE.char_id)
    assert match.active_limits == (2, 2)
    assert match.player_team.strategy is not match.enemy_team.strategy
    assert frozenset(CONTENT.encounters) == before_encounters
    assert ARENA_ID not in CONTENT.encounters
    assert not content.validate_structure()


def test_prefabs_are_valid_strategies_in_actual_battles():
    for name in builtin_names():
        match = single_match(name, controller_for(name), "first_target",
                             controller_for("first_target"), seed=19)
        assert match.winner in (0, 1, None)
        assert match.events


def test_side_swaps_seeds_and_deterministic_replay():
    left = controller_for("crowd_control")
    right = controller_for("heavy_hitter")
    a = compare("crowd_control", left, "heavy_hitter", right, runs=5, seed=8)
    b = compare("crowd_control", left, "heavy_hitter", right, runs=5, seed=8)
    assert a.matches == 10
    assert (a.wins, a.losses, a.draws) == (b.wins, b.losses, b.draws)
    assert a.first_result is not None
    assert a.first_result.rounds == b.first_result.rounds


def test_sample_baselines_can_be_beaten_with_legal_moves():
    # A legitimate, minimal role-aware experiment can outperform an
    # intentionally weak prefab. Project 4's full solution is not shipped.
    def chooses_different_known_moves(turn):
        if "arena_crush" in turn.available_move_ids:
            return turn.use("arena_crush", target=turn.enemies[0])
        return turn.use("arena_spark", target=turn.enemies[0])

    result = compare("example", chooses_different_known_moves,
                     "first_target", controller_for("first_target"),
                     runs=4, seed=0)
    assert result.score >= REQUIRED_SCORE


def test_score_counts_draws_as_half():
    assert _score({"wins": 1, "losses": 1, "draws": 2}) == 0.5


def test_example_files_have_a_single_callable_interface():
    for name in builtin_names():
        if name != BUILTIN:
            assert callable(controller_for(name))
            assert (PREFABS / f"{name}.py").is_file()
    assert (PLAYERS / "my_team.py").is_file()


def test_new_command_copies_a_prefab_but_does_not_overwrite(tmp_path, monkeypatch):
    import team_arena.cli as cli

    monkeypatch.setattr(cli, "PLAYERS", tmp_path)
    monkeypatch.setattr(cli, "ROOT", tmp_path)
    args = make_parser().parse_args(["new", "fresh_bot", "--from", "first_target"])
    assert run(args) == 0
    target = tmp_path / "fresh_bot.py"
    assert target.read_text() == (PREFABS / "first_target.py").read_text()
    target.write_text("untouched")
    with pytest.raises(ValueError, match="already exists"):
        run(args)
    assert target.read_text() == "untouched"
    with pytest.raises(ValueError):
        run(make_parser().parse_args(["new", "../escape"]))


def test_bounded_worker_accepts_printing_student_controller():
    name = "test_temporary_printer"
    file = PLAYERS / f"{name}.py"
    assert not file.exists()
    try:
        file.write_text('def choose_action(turn):\n    print("I am deciding")\n'
                        '    return turn.use("arena_tap", target=turn.enemies[0])\n')
        record = bounded_pair(name, "first_target", runs=1, seed=0,
                              max_steps=300, timeout=10)
        assert sum(record[k] for k in ("wins", "losses", "draws")) == 2
    finally:
        file.unlink(missing_ok=True)


def test_invalid_action_causes_failure_not_a_counted_loss():
    name = "test_temporary_invalid"
    file = PLAYERS / f"{name}.py"
    assert not file.exists()
    try:
        file.write_text('def choose_action(turn):\n'
                        '    return turn.use("not_a_move", target=turn.enemies[0])\n')
        with pytest.raises(RuntimeError, match="not_a_move"):
            bounded_pair(name, "first_target", runs=1, seed=0,
                         max_steps=100, timeout=10)
    finally:
        file.unlink(missing_ok=True)


def test_infinite_loop_can_be_stopped_by_parent_timeout():
    name = "test_temporary_infinite"
    file = PLAYERS / f"{name}.py"
    assert not file.exists()
    try:
        file.write_text('def choose_action(turn):\n    while True:\n        pass\n')
        with pytest.raises(RuntimeError, match="exceeded"):
            bounded_pair(name, "first_target", runs=1, seed=0,
                         max_steps=100, timeout=1.0)
    finally:
        file.unlink(missing_ok=True)


def test_cli_tournament_writes_rankable_csv(tmp_path):
    args = [sys.executable, str(ROOT / "arena.py"), "tournament", "first_target",
            "heavy_hitter", "--runs", "2", "--csv", str(tmp_path / "results.csv")]
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True,
                            timeout=30, check=False)
    assert result.returncode == 0, result.stderr
    assert "STANDINGS" in result.stdout
    data = (tmp_path / "results.csv").read_text()
    assert "name,wins,losses,draws,games,score" in data
    assert "first_target" in data
    assert "heavy_hitter" in data
