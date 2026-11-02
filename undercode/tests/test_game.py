"""Rules and extensions, exercised without a window or an audio device."""

import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
from undercode.overworld.maps import compile_rooms
from undercode.student_world import LEVELS

ROOMS = compile_rooms(definitions=LEVELS)

from undercode.app import Game, Scene
from undercode.encounters.arena import Arena, DefensePattern, Mode, Vec
from undercode.encounters.attacks import TimingStrike, RhythmStrike
from undercode.encounters.encounter import Encounter as Battle, Phase
from undercode.encounters.content import OPPONENTS, WEAPONS, PATTERNS
from undercode.controls import Controls
from undercode.model import Player, Session
from undercode.contracts import Outcome, EncounterRequest
from undercode.encounters.model import TurnContext
from undercode.encounters.validate import validate_encounters
from undercode.overworld.world import World, tile_center


class QuietPattern(DefensePattern):
    duration = 1.0

    def update(self, *, arena, seconds):
        pass


def run_for(game, seconds, controls=Controls()):
    for _ in range(round(seconds * 60)):
        game.update(seconds=1 / 60, controls=controls)


def finish_message(battle):
    while battle.phase == Phase.MESSAGE:
        battle.update(seconds=0, controls=Controls(confirm_pressed=True))


class AttackTests(unittest.TestCase):
    def test_focus_strike_center_edge_and_timeout(self):
        strike = TimingStrike()
        strike.update(seconds=strike.duration / 2, controls=Controls(confirm_pressed=True))
        self.assertTrue(strike.done)
        self.assertAlmostEqual(strike.score, 1)
        strike.update(seconds=1, controls=Controls(confirm_pressed=True))
        self.assertAlmostEqual(
            strike.score, 1, msg="A finished strike cannot be changed by another press"
        )
        miss = TimingStrike()
        miss.update(seconds=0.01, controls=Controls(confirm_pressed=True))
        self.assertEqual(miss.score, 0)
        timeout = TimingStrike()
        timeout.update(seconds=2, controls=Controls())
        self.assertTrue(timeout.done)
        self.assertEqual(timeout.score, 0)

    def test_rhythm_counts_three_distinct_beats_not_spam(self):
        strike = RhythmStrike()
        for _ in range(3):
            strike.update(seconds=0.6, controls=Controls(confirm_pressed=True))
        self.assertTrue(strike.done)
        self.assertAlmostEqual(strike.score, 1)
        spam = RhythmStrike()
        spam.update(seconds=0.6, controls=Controls(confirm_pressed=True))
        for _ in range(20):
            spam.update(seconds=0, controls=Controls(confirm_pressed=True))
        self.assertEqual(len(spam.hits), 1)
        self.assertAlmostEqual(spam.score, 1 / 3)
        spam.update(seconds=4, controls=Controls())
        self.assertTrue(spam.done)


class ArenaTests(unittest.TestCase):
    def test_free_movement_normalizes_diagonals_and_stays_inside(self):
        straight, diagonal = (
            Arena(pattern=QuietPattern(), player=Player(hp=20, max_hp=20)),
            Arena(pattern=QuietPattern(), player=Player(hp=20, max_hp=20)),
        )
        start = straight.soul.position.copy()
        straight.update(seconds=0.2, controls=Controls(move_x=1))
        diagonal.update(seconds=0.2, controls=Controls(move_x=1, move_y=-1))
        self.assertAlmostEqual(
            straight.soul.position.distance_to(start), diagonal.soul.position.distance_to(start)
        )
        straight.update(seconds=0.8, controls=Controls(move_x=1))
        self.assertLessEqual(straight.soul.position.x, straight.width - straight.soul.radius)

    def test_swept_projectile_collision_and_invulnerability(self):
        arena = Arena(pattern=QuietPattern(), player=Player(hp=20, max_hp=20))
        y = arena.soul.position.y
        arena.spawn(x=0, y=y, vx=6000, vy=0)
        arena.update(seconds=0.1, controls=Controls())
        self.assertEqual(arena.hp, 18, "A fast bullet must not tunnel through the soul")
        self.assertEqual(arena.hits, 1)
        arena.spawn(x=arena.soul.position.x, y=y, vx=0, vy=0)
        arena.update(seconds=0.1, controls=Controls())
        self.assertEqual(arena.hp, 18, "Overlapping hazards must respect the damage cooldown")
        arena.update(seconds=0.7, controls=Controls())
        arena.spawn(x=arena.soul.position.x, y=y, vx=0, vy=0)
        arena.update(seconds=0.01, controls=Controls())
        self.assertEqual(arena.hp, 16)

    def test_gravity_jump_lands_and_cannot_jump_again_in_midair(self):
        pattern = QuietPattern()
        pattern.mode = Mode.GRAVITY
        pattern.duration = 3
        arena = Arena(pattern=pattern, player=Player(hp=20, max_hp=20))
        floor = arena.soul.position.y
        arena.update(seconds=1 / 60, controls=Controls(confirm_pressed=True))
        self.assertLess(arena.soul.position.y, floor)
        first_speed = arena.soul.vertical_speed
        arena.update(seconds=1 / 60, controls=Controls(confirm_pressed=True))
        self.assertGreater(arena.soul.vertical_speed, first_speed)
        for _ in range(90):
            arena.update(seconds=1 / 60, controls=Controls())
        self.assertTrue(arena.soul.grounded)
        self.assertAlmostEqual(arena.soul.position.y, floor)

    def test_shield_blocks_only_the_faced_direction(self):
        pattern = QuietPattern()
        pattern.mode = Mode.SHIELD
        arena = Arena(pattern=pattern, player=Player(hp=20, max_hp=20))
        x, y = arena.soul.position
        arena.spawn(x=x, y=0, vx=0, vy=1000)
        arena.update(seconds=0.1, controls=Controls(move_y=-1))
        self.assertEqual(arena.blocks, 1)
        self.assertEqual(arena.hp, 20)
        arena.spawn(x=0, y=y, vx=4000, vy=0)
        arena.update(seconds=0.1, controls=Controls(move_y=-1))
        self.assertEqual(arena.hp, 18)
        self.assertEqual(arena.blocks, 1)

    def test_warnings_are_safe_until_active_and_expire(self):
        arena = Arena(pattern=QuietPattern(), player=Player(hp=20, max_hp=20))
        x, y = arena.soul.position
        arena.beam(x=x - 15, y=0, width=30, height=arena.height, warmup=0.5, duration=0.2)
        arena.update(seconds=0.3, controls=Controls())
        self.assertEqual(arena.hp, 20)
        arena.update(seconds=0.25, controls=Controls())
        self.assertEqual(arena.hp, 18)
        arena.update(seconds=0.2, controls=Controls())
        self.assertEqual(arena.beams, [])
        delayed = Arena(pattern=QuietPattern(), player=Player(hp=20, max_hp=20))
        delayed.spawn(x=x, y=y, vx=0, vy=0, warmup=0.5)
        delayed.update(seconds=0.3, controls=Controls())
        self.assertEqual(delayed.hp, 20)
        delayed.update(seconds=0.21, controls=Controls())
        self.assertEqual(delayed.hp, 18)

    def test_end_of_turn_and_invalid_student_hazards(self):
        arena = Arena(pattern=QuietPattern(), player=Player(hp=20, max_hp=20))
        arena.update(seconds=1.1, controls=Controls())
        self.assertTrue(arena.done)
        state = (arena.elapsed, arena.hp, arena.soul.position.copy())
        arena.update(seconds=0.1, controls=Controls(move_x=1))
        self.assertEqual((arena.elapsed, arena.hp, arena.soul.position), state)
        with self.assertRaises(ValueError):
            arena.spawn(x=float("nan"), y=0, vx=0, vy=0)
        with self.assertRaises(ValueError):
            arena.beam(x=0, y=0, width=10, height=0)
        with self.assertRaises(ValueError):
            arena.update(seconds=-1, controls=Controls())


class BattleTests(unittest.TestCase):
    def make_encounter(self):
        return Battle(opponent=OPPONENTS[0], player=Player(), weapon=WEAPONS[0], seed=19)

    def test_intro_submenus_and_cancel_do_not_accidentally_take_turns(self):
        battle = self.make_encounter()
        self.assertEqual(battle.phase, Phase.MESSAGE)
        battle.update(seconds=0, controls=Controls(confirm_pressed=True))
        self.assertEqual(battle.phase, Phase.MESSAGE, "First confirm reveals, next advances")
        finish_message(battle)
        battle.selection = 1
        battle.update(seconds=0, controls=Controls(confirm_pressed=True))
        self.assertEqual(battle.phase, Phase.ACT)
        battle.update(seconds=0, controls=Controls(cancel_pressed=True))
        self.assertEqual(battle.phase, Phase.MENU)
        self.assertEqual(battle.turn, 0)

    def test_act_defend_spare_route_without_attacking(self):
        battle = self.make_encounter()
        finish_message(battle)
        for _ in range(2):
            battle.selection = 1
            battle.choose()  # ACT submenu
            battle.selection = 0
            battle.choose()  # Listen, calm +2
            finish_message(battle)
            self.assertEqual(battle.phase, Phase.DEFEND)
            # For this route test, use an empty practice pattern; physics is
            # tested separately and real content factories are simulated below.
            battle.arena = Arena(
                pattern=QuietPattern(), player=Player(hp=battle.player.hp, max_hp=battle.player.hp)
            )
            battle.update(seconds=1, controls=Controls())
            finish_message(battle)
            self.assertEqual(battle.phase, Phase.MENU)
        self.assertTrue(battle.spare_ready)
        self.assertEqual(battle.opponent_hp, battle.opponent.max_hp)
        battle.selection = 3
        battle.choose()
        battle.choose()
        self.assertEqual(battle.outcome, Outcome.SPARED)
        finish_message(battle)
        self.assertEqual(battle.phase, Phase.FINISHED)

    def test_attack_damage_and_combat_result(self):
        battle = self.make_encounter()
        battle.opponent_hp = 4
        battle.set_phase(phase=Phase.ATTACK)
        battle.update(seconds=0.725, controls=Controls(confirm_pressed=True))
        self.assertEqual(battle.opponent_hp, 0)
        self.assertEqual(battle.outcome, Outcome.DEFEATED)
        self.assertEqual(battle.last_damage, 13)

    def test_item_clamps_health_and_empty_inventory_returns_to_menu(self):
        battle = self.make_encounter()
        battle.player.hp = 18
        battle.set_phase(phase=Phase.ITEM)
        battle.choose()
        self.assertEqual(battle.player.hp, 20)
        self.assertEqual(battle.player.snacks, 1)
        battle.player.snacks = 0
        battle.set_phase(phase=Phase.ITEM)
        battle.choose()
        finish_message(battle)
        self.assertEqual(battle.phase, Phase.MENU)

    def test_leave_practice_and_loss_are_distinct_outcomes(self):
        battle = self.make_encounter()
        battle.set_phase(phase=Phase.MERCY)
        battle.selection = 1
        battle.choose()
        self.assertEqual(battle.outcome, Outcome.LEFT)
        lost = self.make_encounter()
        lost.set_phase(phase=Phase.DEFEND)
        lost.arena.hp = 0
        lost.update(seconds=0.01, controls=Controls())
        self.assertEqual(lost.player.hp, 0)
        self.assertEqual(lost.outcome, Outcome.LOST)

    def test_long_dialogue_is_paged_and_no_page_takes_a_turn(self):
        battle = self.make_encounter()
        battle.say(message="A long student story. " * 40, then=Phase.MENU)
        self.assertGreater(len(battle.pages), 2)
        finish_message(battle)
        self.assertEqual(battle.phase, Phase.MENU)
        self.assertEqual(battle.turn, 0)


class WorldAndSceneTests(unittest.TestCase):
    def test_world_to_battle_transition_freezes_input_and_returns_to_position(self):
        game = Game()
        run_for(game, 0.42, Controls(move_y=-1))
        game.update(seconds=0, controls=Controls(confirm_pressed=True))
        self.assertEqual(game.world.talking.key, "folio")
        game.update(seconds=0, controls=Controls(confirm_pressed=True))
        before = game.world.position.copy()
        self.assertIsNotNone(game.transition)
        run_for(game, 0.4, Controls(move_x=1, confirm_pressed=True))
        self.assertEqual(game.scene, Scene.ENCOUNTER)
        self.assertEqual(game.encounter.phase, Phase.MESSAGE)
        self.assertEqual(game.world.position, before)
        run_for(game, 0.4)
        game.encounter.finish(outcome=Outcome.SPARED, message="A peaceful finish.")
        finish_message(game.encounter)
        game.update(seconds=0)
        run_for(game, 0.8)
        self.assertEqual(game.scene, Scene.WORLD)
        self.assertEqual(game.session.resolved["folio"], Outcome.SPARED)
        self.assertEqual(game.world.position, before)

    def test_loss_restores_player_and_flee_preserves_unresolved_encounter(self):
        game = Game()
        game.apply_request(request=EncounterRequest(encounter_id="folio", person_id="folio"))
        game.session.player.hp = 0
        game.session.player.snacks = 0
        game.encounter.finish(outcome=Outcome.LOST, message="Rest.")
        finish_message(game.encounter)
        game.update(seconds=0)
        run_for(game, 0.8)
        self.assertEqual(game.session.player.hp, 20)
        self.assertEqual(game.session.player.snacks, 2)
        self.assertFalse(game.session.resolved)
        self.assertEqual(game.world.position, tile_center(tile=(7, 12)))
        game.begin_transition(request=EncounterRequest(encounter_id="folio", person_id="folio"))
        run_for(game, 0.8)
        game.encounter.finish(outcome=Outcome.LEFT, message="Later.")
        finish_message(game.encounter)
        game.update(seconds=0)
        run_for(game, 0.8)
        self.assertFalse(game.session.resolved)

    def test_wall_collision_does_not_tunnel_and_diagonal_speed_matches(self):
        a, b = (
            World(rooms=ROOMS, session=Session(), room_key="courtyard", spawn="camp"),
            World(rooms=ROOMS, session=Session(), room_key="courtyard", spawn="camp"),
        )
        start = a.position.copy()
        a.move(direction=Vec(1, 0), seconds=0.1)
        b.move(direction=Vec(1, -1), seconds=0.1)
        self.assertAlmostEqual(a.position.distance_to(start), b.position.distance_to(start))
        a.position = tile_center(tile=(1, 1))
        a.move(direction=Vec(-1, 0), seconds=3)
        self.assertGreaterEqual(a.position.x, 41)
        self.assertTrue(a.passable(position=a.position))

    def test_doors_fountain_help_pause_and_weapon_selection(self):
        game = Game()
        game.world.position = tile_center(tile=(14, 1))
        run_for(game, 0.5)
        run_for(game, 0.15, Controls(move_y=-1))
        run_for(game, 0.8)
        self.assertEqual(game.world.room_key, "garden")
        self.assertEqual(game.world.position, tile_center(tile=(14, 13)))
        game.world.position = tile_center(tile=game.world.room.rest_tile)
        game.session.player.hp = 2
        game.session.player.snacks = 0
        game.update(seconds=0, controls=Controls(confirm_pressed=True))
        self.assertEqual(game.session.player.hp, 20)
        self.assertEqual(game.session.player.snacks, 2)
        old = game.world.position.copy()
        game.help_open = True
        run_for(game, 0.5, Controls(move_x=1))
        self.assertEqual(game.world.position, old)
        game.help_open = False
        game.change_weapon()
        self.assertEqual(game.session.player.weapon, 1)


class ExtensionTests(unittest.TestCase):
    def test_all_real_content_factories_and_rooms_validate(self):
        self.assertEqual(
            validate_encounters(characters=OPPONENTS, weapons=WEAPONS, patterns=PATTERNS), []
        )

    def test_student_pattern_is_registered_and_playable_without_engine_changes(self):
        from undercode.student_encounters import ECHO, RippleLanes

        pattern = ECHO.choose_pattern(
            context=TurnContext(turn=0, opponent_hp=20, opponent_max_hp=20, calm=0)
        )
        self.assertIsInstance(pattern, RippleLanes)
        game = Game(practice="ripples")
        self.assertEqual(game.encounter.phase, Phase.DEFEND)
        run_for(game, 1)
        self.assertGreater(len(game.encounter.arena.bullets), 0)
        self.assertEqual(game.encounter.arena.pattern.name, pattern.name)

    def test_seeds_repeat_spawns_and_separate_instances_do_not_share_clocks(self):
        first, second = (
            Arena(pattern=PATTERNS["pages"](), player=Player(hp=20, max_hp=20), seed=11),
            Arena(pattern=PATTERNS["pages"](), player=Player(hp=20, max_hp=20), seed=11),
        )
        for _ in range(30):
            first.update(seconds=1 / 60, controls=Controls())
            second.update(seconds=1 / 60, controls=Controls())
        self.assertEqual(
            [tuple(b.position) for b in first.bullets], [tuple(b.position) for b in second.bullets]
        )
        self.assertIsNot(first.pattern, second.pattern)
        first.update(seconds=0.1, controls=Controls())
        self.assertNotEqual(first.elapsed, second.elapsed)


class CompleteRouteTests(unittest.TestCase):
    def test_each_character_can_be_spared_through_real_defense_patterns(self):
        for character in OPPONENTS:
            with self.subTest(opponent=character.key):
                battle = Battle(opponent=character, player=Player(), weapon=WEAPONS[0], seed=7)
                finish_message(battle)
                while not battle.spare_ready:
                    battle.selection = 1
                    battle.choose()
                    battle.selection = max(
                        range(len(character.acts)), key=lambda i: character.acts[i].calm
                    )
                    battle.choose()
                    finish_message(battle)
                    while battle.phase == Phase.DEFEND:
                        battle.update(seconds=1 / 60, controls=Controls())
                    self.assertIsNone(
                        battle.outcome, "The introductory peaceful route should be forgiving"
                    )
                    finish_message(battle)
                battle.selection = 3
                battle.choose()
                battle.choose()
                self.assertEqual(battle.outcome, Outcome.SPARED)
                self.assertEqual(battle.opponent_hp, character.max_hp)

    def test_each_character_can_be_defeated_with_real_strikes_and_a_counterturn(self):
        for character in OPPONENTS:
            with self.subTest(opponent=character.key):
                battle = Battle(opponent=character, player=Player(), weapon=WEAPONS[0], seed=7)
                finish_message(battle)
                while battle.outcome is None:
                    battle.selection = 0
                    battle.choose()
                    battle.update(seconds=0.725, controls=Controls(confirm_pressed=True))
                    if battle.outcome:
                        break
                    finish_message(battle)
                    while battle.phase == Phase.DEFEND:
                        battle.update(seconds=1 / 60, controls=Controls())
                    finish_message(battle)
                self.assertEqual(battle.outcome, Outcome.DEFEATED)


if __name__ == "__main__":
    unittest.main()
