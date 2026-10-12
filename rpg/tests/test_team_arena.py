"""Behavioral regression checks for the RPG classroom team-controller arena.

Use isolated temp player directories; never create or delete student work in
team_arena/players/. These tests intentionally do not assert worksheet text.
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

from student_game import CONTENT
from team_arena import cli
from team_arena.cli import (
    BUILTIN, CHALLENGE_OPPONENTS, PREFABS, PLAYERS, REQUIRED_SCORE,
    _score, bounded_pair, bounded_record, builtin_names, controller_for,
    make_parser, run,
)
from team_arena.engine import (
    ARENA_ID, GUARDIAN, MAGE, compare, content_for_match, single_match,
)
from team_arena.recording import LimitedOutput, record_match, verify_replay

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def isolated_players(tmp_path, monkeypatch):
    """The parent AND child processes must read only test-generated players."""
    monkeypatch.setenv("RPG_ARENA_PLAYERS_DIR", str(tmp_path))
    monkeypatch.setattr(cli, "PLAYERS", tmp_path)

    def create(name: str, code: str) -> Path:
        file = tmp_path / f"{name}.py"
        file.write_text(code, encoding="utf8")
        return file

    return create


def test_symmetric_teams_do_not_modify_the_story_game():
    before = frozenset(CONTENT.encounters)
    content = content_for_match("first_target", controller_for("first_target"),
                                "heavy_hitter", controller_for("heavy_hitter"))
    encounter = content.encounters[ARENA_ID]
    assert encounter.player_team.members == encounter.enemy_team.members == (
        GUARDIAN.char_id, MAGE.char_id,
    )
    assert encounter.active_limits == (2, 2)
    assert encounter.player_team.strategy is not encounter.enemy_team.strategy
    assert frozenset(CONTENT.encounters) == before
    assert ARENA_ID not in CONTENT.encounters
    assert not content.validate_structure()


def test_prefabs_play_legal_moves_against_actual_engine():
    for name in builtin_names():
        match = single_match(name, controller_for(name), "first_target",
                             controller_for("first_target"), seed=19)
        assert match.winner in (0, 1, None)
        assert match.events


def test_repeated_comparisons_swap_sides_and_are_reproducible():
    left = controller_for("crowd_control")
    right = controller_for("heavy_hitter")
    a = compare("crowd_control", left, "heavy_hitter", right, runs=5, seed=8)
    b = compare("crowd_control", left, "heavy_hitter", right, runs=5, seed=8)
    assert a.matches == 10
    assert (a.wins, a.losses, a.draws, a.unfinished) == (
        b.wins, b.losses, b.draws, b.unfinished,
    )
    assert a.first_result.rounds == b.first_result.rounds


def test_unfinished_battles_are_not_draws_or_half_credit():
    def defend_forever(turn):
        return turn.defend()

    comparison = compare("a", defend_forever, "b", defend_forever,
                         runs=2, seed=0, max_steps=8)
    assert (comparison.wins, comparison.losses, comparison.draws) == (0, 0, 0)
    assert comparison.unfinished == comparison.matches == 4
    assert comparison.score == 0.0
    assert _score({"wins": 0, "losses": 0, "draws": 0, "unfinished": 4}) == 0.0
    assert _score({"wins": 1, "losses": 1, "draws": 2, "unfinished": 2}) == 2 / 6


def test_simple_role_aware_algorithm_can_win_first_assignment():
    # The full final challenge solution is intentionally NOT supplied in tests.
    def chooses_legal_moves_for_both_roles(turn):
        if turn.can_use("arena_crush"):
            return turn.skill("arena_crush", target=turn.enemies[0])
        if turn.can_use("arena_spark"):
            return turn.skill("arena_spark", target=turn.enemies[0])
        return turn.attack(target=turn.enemies[0])

    outcome = compare("student", chooses_legal_moves_for_both_roles,
                      "first_target", controller_for("first_target"),
                      runs=4, seed=0)
    assert outcome.score >= REQUIRED_SCORE


def test_examples_and_fixed_challenge_roster():
    assert set(CHALLENGE_OPPONENTS).issubset(builtin_names())
    for name in builtin_names():
        if name != BUILTIN:
            assert callable(controller_for(name))
            assert (PREFABS / f"{name}.py").is_file()
    assert (PLAYERS / "my_team.py").is_file()


def test_first_run_defaults_to_visual_match():
    parser = make_parser()
    assert parser.parse_args([]).action is None
    view = parser.parse_args(["watch"])
    assert (view.left, view.right) == ("my_team", "first_target")
    assert parser.parse_args(["battle"]).runs == 12
    assert parser.parse_args(["challenge"]).runs == 20
    assert parser.parse_args(["tournament"]).runs == 2


def test_new_copies_a_prefab_without_overwriting(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "PLAYERS", tmp_path)
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


def test_student_print_does_not_break_worker(isolated_players):
    isolated_players("student_print", 'def choose_action(turn):\n'
                     '    print("my move", turn.user.name)\n'
                     '    return turn.attack(target=turn.enemies[0])\n')
    result = bounded_pair("student_print", "first_target", runs=1,
                          seed=0, max_steps=300, timeout=10)
    assert sum(result[k] for k in ("wins", "losses", "draws", "unfinished")) == 2


def test_student_errors_have_source_file_and_line(isolated_players):
    isolated_players("broken_syntax", 'def choose_action(turn):\n'
                     '    if turn.user.hp <:\n'
                     '        return turn.defend()\n')
    with pytest.raises(RuntimeError) as error:
        bounded_pair("broken_syntax", "first_target", runs=1, seed=0,
                     max_steps=100, timeout=10)
    assert "broken_syntax.py, line 2" in str(error.value)
    assert "SyntaxError" in str(error.value)
    assert "Edit that line" in str(error.value)


def test_invalid_action_is_a_friendly_error_not_a_loss(isolated_players):
    isolated_players("invalid", 'def choose_action(turn):\n'
                     '    return turn.use("not_a_move", target=turn.enemies[0])\n')
    with pytest.raises(RuntimeError) as error:
        bounded_pair("invalid", "first_target", runs=1, seed=0,
                     max_steps=100, timeout=10)
    assert "not_a_move" in str(error.value)
    assert "invalid.py, line 2" in str(error.value)


def test_infinite_loop_can_be_stopped(isolated_players):
    isolated_players("endless", 'def choose_action(turn):\n    while True:\n        pass\n')
    with pytest.raises(RuntimeError, match="exceeded"):
        bounded_pair("endless", "first_target", runs=1, seed=0,
                     max_steps=100, timeout=0.6)


def test_event_tape_is_only_transferred_for_requested_logs():
    plain = bounded_pair("first_target", "heavy_hitter", runs=1, seed=0,
                         max_steps=300, timeout=10)
    detailed = bounded_pair("first_target", "heavy_hitter", runs=1, seed=0,
                            max_steps=300, timeout=10, include_log=True)
    assert plain["first_result"] is None
    assert detailed["first_result"]["events"]
    assert _score(plain) == _score(detailed)


def test_tournament_writes_standings_and_unfinished_column(tmp_path):
    cmd = [sys.executable, str(ROOT / "arena.py"), "tournament", "first_target",
           "heavy_hitter", "--runs", "2", "--csv", str(tmp_path / "results.csv")]
    completed = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                               timeout=30, check=False)
    assert completed.returncode == 0, completed.stderr
    assert "STANDINGS" in completed.stdout
    with (tmp_path / "results.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert {row["name"] for row in rows} == {"first_target", "heavy_hitter"}
    assert all("unfinished" in row and int(row["games"]) == 4 for row in rows)


def test_classroom_size_roster_and_progress(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cli, "PLAYERS", tmp_path)
    for index in range(32):
        (tmp_path / f"student_{index}.py").write_text(
            'def choose_action(turn):\n    return turn.defend()\n'
        )
    calls = []

    def fake_pair(left, right, *, runs, seed, max_steps, timeout, include_log=False):
        calls.append((left, right, runs))
        return {"left": left, "right": right, "wins": 1, "losses": 1,
                "draws": 0, "unfinished": 0}

    monkeypatch.setattr(cli, "bounded_pair", fake_pair)
    dest = tmp_path / "standings.csv"
    args = make_parser().parse_args(["tournament", "--csv", str(dest)])
    assert run(args) == 0
    assert len(calls) == 32 * 31 // 2
    assert all(runs == 2 for _, _, runs in calls)
    assert "Fixture 496/496" in capsys.readouterr().out
    with dest.open(newline="") as stream:
        assert len(list(csv.DictReader(stream))) == 32


def test_recording_replays_match_exactly_with_less_repeated_rng_data():
    for left, right, seed in (
        ("first_target", "crowd_control", 1),
        ("engine_heuristic", "heavy_hitter", 3),
        ("my_team", "first_target", 5),
    ):
        record = record_match(left, right, seed=seed)
        assert record["steps"]
        assert {step["team"] for step in record["steps"]} == {0, 1}
        assert verify_replay(record) == (
            record["winner"], record["rounds"], tuple(record["remaining_hp"]),
        )
        if left != BUILTIN and right != BUILTIN:
            assert not any("rng_state" in step for step in record["steps"])


def test_recording_captures_prints_and_reloads_edited_source(isolated_players):
    file = isolated_players("thinking", 'def choose_action(turn):\n'
                            '    print("first version")\n'
                            '    return turn.attack(target=turn.enemies[0])\n')
    old = bounded_record("thinking", "first_target", seed=1, max_steps=300, timeout=10)
    assert old["sources"][0].endswith("thinking.py")
    assert any("first version" in line for step in old["steps"]
               if step["team"] == 0 for line in step["prints"])
    file.write_text('def choose_action(turn):\n'
                    '    print("second version")\n'
                    '    return turn.defend()\n')
    new = bounded_record("thinking", "first_target", seed=1, max_steps=300, timeout=10)
    assert any("second version" in line for step in new["steps"]
               if step["team"] == 0 for line in step["prints"])
    assert all("first version" not in line for step in new["steps"]
               for line in step.get("prints", []))
    assert verify_replay(old)
    assert verify_replay(new)


def test_print_capture_has_finite_limit():
    stream = LimitedOutput(limit=12)
    assert stream.write("abc\n") == 4
    assert stream.write("defghijklmnopqrstuvwxyz") == 23
    assert stream.lines()[0] == "abc"
    assert "truncated" in stream.lines()[-1]


def test_visual_recorder_times_out_away_from_pygame(isolated_players):
    isolated_players("never_returns", 'def choose_action(turn):\n'
                     '    while True:\n        pass\n')
    with pytest.raises(RuntimeError, match="exceeded"):
        bounded_record("never_returns", "first_target", seed=1,
                       max_steps=300, timeout=0.6)


def test_pygame_replay_and_reset_when_available(monkeypatch):
    """Run this with the classroom extras and SDL dummy on a build machine."""
    pygame = pytest.importorskip("pygame")
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    monkeypatch.setenv("SDL_AUDIODRIVER", "dummy")
    from loguru import logger
    from team_arena.viewer import ArenaBattleScene
    from rpg_battle.audio.engine import AudioEngine
    logger.remove()
    record = record_match("first_target", "crowd_control", seed=1)
    content = content_for_match(record["left"], None, record["right"], None)
    pygame.init()
    try:
        screen = pygame.display.set_mode((1120, 700))
        scene = ArenaBattleScene(screen.get_rect(), record, audio=AudioEngine(content))
        scene.step_one_decision()
        for _ in range(600):
            scene.update(0.25)
            if not scene.stepping:
                break
        assert scene.paused and not scene.stepping
        assert scene.step_index == 1
        scene.paused = False
        for _ in range(2500):
            scene.update(0.25)
            if scene.controller.state.winner is not None and not scene.event_queue:
                break
        assert scene.controller.state.winner == record["winner"]
        assert scene.step_index == len(record["steps"])
        scene.draw(screen)
        scene.reset()
        assert scene.step_index == 0
    finally:
        pygame.quit()
