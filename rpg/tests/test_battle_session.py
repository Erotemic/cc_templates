"""Contract tests for one controller-independent battle session."""

import subprocess
import sys
from pathlib import Path

import pytest

from rpg_battle.battle.session import BattleSession, DecisionRequest
from rpg_battle.core.actions import attack_action, defend_action, skill_action
from rpg_battle.core.battle_state import ensure_replacement_request, mark_fainted
from rpg_battle.core.models import CombatContent, EncounterSpec, TeamSpec
from rpg_battle.teaching.simulate import simulate_once
from student_game import CONTENT


def next_action(session):
    for _ in range(10):
        step = session.next_step()
        if step.request is not None:
            return step.request
    raise AssertionError("A battle action was not requested")


def test_round_announcements_and_pending_request_are_explicit_in_battle_state():
    session = BattleSession(content=CONTENT, seed=8)
    assert session.request is None
    first = session.next_step()
    assert [event['type'] for event in first.events] == ['round_start']
    assert first.request is None
    assert session.state.round_announced
    assert session.state.pending_turn_order
    second = session.next_step()
    assert [event['type'] for event in second.events] == ['turn_start']
    assert second.request is not None
    assert second.request.kind == 'action'
    assert second.request.actor_id == session.state.current_actor_id
    before = session.rng.getstate()
    assert session.next_step().request == second.request
    assert session.next_step().events == ()
    assert session.rng.getstate() == before


def test_invalid_decisions_do_not_consume_turn_or_randomness():
    session = BattleSession(content=CONTENT, seed=10)
    request = next_action(session)
    actor_id = request.actor_id
    assert actor_id
    state_before = session.rng.getstate()
    wrong_actor = next(cid for cid in session.state.combatants if cid != actor_id)
    with pytest.raises(ValueError, match='Wrong acting fighter'):
        session.submit(attack_action(wrong_actor))
    with pytest.raises(ValueError, match='does not know skill'):
        session.submit(skill_action(actor_id, 'not_a_real_skill'))
    with pytest.raises(TypeError, match='BattleAction'):
        session.submit('t0_c0')
    assert session.current_actor_id == actor_id
    assert session.rng.getstate() == state_before
    session.submit(defend_action(actor_id))
    assert session.request is None


@pytest.mark.parametrize('team_index', [0, 1])
def test_replacement_is_requested_for_either_team_without_auto_selecting(team_index):
    encounter = EncounterSpec(
        'replacements', 'Replacement test',
        TeamSpec('Left', ('workshop_hero', 'guardian')),
        TeamSpec('Right', ('workshop_hero', 'guardian')),
        active_limits=(1, 1),
    )
    session = BattleSession(encounter, content=CONTENT, seed=0)
    actor_id = session.state.teams[team_index].active_ids[0]
    mark_fainted(session.state, actor_id)
    ensure_replacement_request(session.state, team_index)
    request = session.next_step().request
    assert request == DecisionRequest(
        'replacement', team_index, choices=tuple(session.state.teams[team_index].reserve_ids)
    )
    before = session.rng.getstate()
    assert session.next_step().request == request
    with pytest.raises(ValueError, match='Illegal replacement'):
        session.submit('nonexistent')
    assert session.rng.getstate() == before
    assert session.request == request
    events = session.submit(request.choices[0])
    assert [event['type'] for event in events] == ['replacement_joined']
    assert request.choices[0] in session.state.teams[team_index].active_ids
    assert session.request is None


def test_action_submission_workflow_ignores_controller_type():
    # The right team is marked human; the session still merely requests a
    # decision. A caller decides whether a person or an algorithm supplies it.
    encounter = EncounterSpec(
        'two_humans', 'Human vs human',
        TeamSpec('Left', ('workshop_hero',), controller_type='human'),
        TeamSpec('Right', ('workshop_hero',), controller_type='human'),
        (1, 1),
    )
    session = BattleSession(encounter, seed=4, content=CONTENT)
    teams_seen = set()
    for _ in range(30):
        step = session.next_step()
        if step.request is not None:
            assert step.request.kind == 'action'
            teams_seen.add(step.request.team_index)
            session.submit(defend_action(step.request.actor_id))
        if teams_seen == {0, 1}:
            break
    assert teams_seen == {0, 1}


def test_core_state_only_retains_combat_definitions():
    session = BattleSession(content=CONTENT)
    assert isinstance(session.state.content, CombatContent)
    assert session.state.content.characters is CONTENT.characters
    assert session.state.content.moves is CONTENT.moves
    assert not hasattr(session.state.content, 'sprites')
    assert not hasattr(session.state.content, 'music_tracks')
    assert not hasattr(session.state.content, 'sound_effects')
    assert not hasattr(session.state.content, 'encounters')


def test_importing_core_does_not_load_the_presentation_catalog():
    root = Path(__file__).resolve().parents[1]
    script = (
        'import sys; import rpg_battle.core.battle_state; '
        'import rpg_battle.core.models; '
        'assert "rpg_battle.catalog" not in sys.modules; '
        'assert "rpg_battle.audio.library" not in sys.modules; '
        'assert "rpg_battle.render.effect_builder" not in sys.modules'
    )
    # Isolate sys.modules so this checks the imports themselves, not whichever
    # packages pytest happened to load while collecting unrelated tests.
    completed = subprocess.run(
        [sys.executable, '-c', script], cwd=root,
        capture_output=True, text=True, timeout=15,
        env={**__import__('os').environ, 'PYTHONPATH': 'src:.'},
        check=False,
    )
    assert completed.returncode == 0, completed.stderr


def test_session_results_match_headless_runner_for_fixed_decisions():
    encounter = CONTENT.encounters['workshop']
    session = BattleSession(encounter, seed=17, content=CONTENT)
    observed = []
    for _ in range(200):
        if session.finished:
            break
        step = session.next_step()
        observed.extend(step.events)
        request = step.request
        if request is not None:
            from rpg_battle.core.ai import choose_ai_action, choose_ai_replacement
            choice = (choose_ai_replacement(session.state, request.team_index)
                      if request.kind == 'replacement'
                      else choose_ai_action(session.state, request.actor_id, session.rng))
            observed.extend(session.submit(choice))
    result = simulate_once(CONTENT, encounter.encounter_id, seed=17, max_steps=200)
    assert tuple(observed) == result.events
    assert session.state.winner == result.winner
    assert session.state.outcome == result.outcome


def test_core_session_does_not_import_controller_policies():
    import ast
    source = Path(__file__).resolve().parents[1] / 'src/rpg_battle/battle/session.py'
    tree = ast.parse(source.read_text(encoding='utf8'))
    imports = [node.module for node in ast.walk(tree)
               if isinstance(node, ast.ImportFrom)]
    assert 'rpg_battle.core.ai' not in imports
    assert 'rpg_battle.battle.battle_scene' not in imports
    assert 'team_arena.viewer' not in imports
