"""Rules and extensions, exercised without a window or an audio device."""

import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
from undercode.app import Game, Scene
from undercode.arena import Arena, DefensePattern, Mode, Vec
from undercode.attacks import TimingStrike, RhythmStrike
from undercode.battle import Battle, Phase
from undercode.content import CHARACTERS, WEAPONS, PATTERNS, ROOMS
from undercode.controls import Controls
from undercode.model import Outcome, Player, Session, TurnContext
from undercode.validate import validate_content
from undercode.world import World, tile_center


class QuietPattern(DefensePattern):
    duration = 1.0

    def update(self, arena, dt):
        pass


def run_for(game, seconds, controls=Controls()):
    for _ in range(round(seconds * 60)):
        game.update(1 / 60, controls)


def finish_message(battle):
    while battle.phase == Phase.MESSAGE:
        battle.update(0, Controls(confirm=True))


class AttackTests(unittest.TestCase):
    def test_focus_strike_center_edge_and_timeout(self):
        strike = TimingStrike()
        strike.update(strike.duration / 2, Controls(confirm=True))
        self.assertTrue(strike.done)
        self.assertAlmostEqual(strike.score, 1)
        strike.update(1, Controls(confirm=True))
        self.assertAlmostEqual(
            strike.score, 1, msg="A finished strike cannot be changed by another press"
        )
        miss = TimingStrike()
        miss.update(0.01, Controls(confirm=True))
        self.assertEqual(miss.score, 0)
        timeout = TimingStrike()
        timeout.update(2, Controls())
        self.assertTrue(timeout.done)
        self.assertEqual(timeout.score, 0)

    def test_rhythm_counts_three_distinct_beats_not_spam(self):
        strike = RhythmStrike()
        for _ in range(3):
            strike.update(0.6, Controls(confirm=True))
        self.assertTrue(strike.done)
        self.assertAlmostEqual(strike.score, 1)
        spam = RhythmStrike()
        spam.update(0.6, Controls(confirm=True))
        for _ in range(20):
            spam.update(0, Controls(confirm=True))
        self.assertEqual(len(spam.hits), 1)
        self.assertAlmostEqual(spam.score, 1 / 3)
        spam.update(4, Controls())
        self.assertTrue(spam.done)


class ArenaTests(unittest.TestCase):
    def test_free_movement_normalizes_diagonals_and_stays_inside(self):
        straight, diagonal = Arena(QuietPattern(), 20), Arena(QuietPattern(), 20)
        start = straight.soul.position.copy()
        straight.update(0.2, Controls(x=1))
        diagonal.update(0.2, Controls(x=1, y=-1))
        self.assertAlmostEqual(
            straight.soul.position.distance_to(start), diagonal.soul.position.distance_to(start)
        )
        straight.update(0.8, Controls(x=1))
        self.assertLessEqual(straight.soul.position.x, straight.width - straight.soul.radius)

    def test_swept_projectile_collision_and_invulnerability(self):
        arena = Arena(QuietPattern(), 20)
        y = arena.soul.position.y
        arena.spawn(0, y, 6000, 0)
        arena.update(0.1, Controls())
        self.assertEqual(arena.hp, 18, "A fast bullet must not tunnel through the soul")
        self.assertEqual(arena.hits, 1)
        arena.spawn(arena.soul.position.x, y, 0, 0)
        arena.update(0.1, Controls())
        self.assertEqual(arena.hp, 18, "Overlapping hazards must respect the damage cooldown")
        arena.update(0.7, Controls())
        arena.spawn(arena.soul.position.x, y, 0, 0)
        arena.update(0.01, Controls())
        self.assertEqual(arena.hp, 16)

    def test_gravity_jump_lands_and_cannot_jump_again_in_midair(self):
        pattern = QuietPattern()
        pattern.mode = Mode.GRAVITY
        pattern.duration = 3
        arena = Arena(pattern, 20)
        floor = arena.soul.position.y
        arena.update(1 / 60, Controls(confirm=True))
        self.assertLess(arena.soul.position.y, floor)
        first_speed = arena.soul.vertical_speed
        arena.update(1 / 60, Controls(confirm=True))
        self.assertGreater(arena.soul.vertical_speed, first_speed)
        for _ in range(90):
            arena.update(1 / 60, Controls())
        self.assertTrue(arena.soul.grounded)
        self.assertAlmostEqual(arena.soul.position.y, floor)

    def test_shield_blocks_only_the_faced_direction(self):
        pattern = QuietPattern()
        pattern.mode = Mode.SHIELD
        arena = Arena(pattern, 20)
        x, y = arena.soul.position
        arena.spawn(x, 0, 0, 1000)
        arena.update(0.1, Controls(y=-1))
        self.assertEqual(arena.blocks, 1)
        self.assertEqual(arena.hp, 20)
        arena.spawn(0, y, 4000, 0)
        arena.update(0.1, Controls(y=-1))
        self.assertEqual(arena.hp, 18)
        self.assertEqual(arena.blocks, 1)

    def test_warnings_are_safe_until_active_and_expire(self):
        arena = Arena(QuietPattern(), 20)
        x, y = arena.soul.position
        arena.beam(x - 15, 0, 30, arena.height, warmup=0.5, duration=0.2)
        arena.update(0.3, Controls())
        self.assertEqual(arena.hp, 20)
        arena.update(0.25, Controls())
        self.assertEqual(arena.hp, 18)
        arena.update(0.2, Controls())
        self.assertEqual(arena.beams, [])
        delayed = Arena(QuietPattern(), 20)
        delayed.spawn(x, y, 0, 0, warmup=0.5)
        delayed.update(0.3, Controls())
        self.assertEqual(delayed.hp, 20)
        delayed.update(0.21, Controls())
        self.assertEqual(delayed.hp, 18)

    def test_end_of_turn_and_invalid_student_hazards(self):
        arena = Arena(QuietPattern(), 20)
        arena.update(1.1, Controls())
        self.assertTrue(arena.done)
        state = (arena.elapsed, arena.hp, arena.soul.position.copy())
        arena.update(0.1, Controls(x=1))
        self.assertEqual((arena.elapsed, arena.hp, arena.soul.position), state)
        with self.assertRaises(ValueError):
            arena.spawn(float("nan"), 0, 0, 0)
        with self.assertRaises(ValueError):
            arena.beam(0, 0, 10, 0)
        with self.assertRaises(ValueError):
            arena.update(-1, Controls())


class BattleTests(unittest.TestCase):
    def make_battle(self):
        return Battle(CHARACTERS[0], Player(), WEAPONS[0], seed=19)

    def test_intro_submenus_and_cancel_do_not_accidentally_take_turns(self):
        battle = self.make_battle()
        self.assertEqual(battle.phase, Phase.MESSAGE)
        battle.update(0, Controls(confirm=True))
        self.assertEqual(battle.phase, Phase.MESSAGE, "First confirm reveals, next advances")
        finish_message(battle)
        battle.selection = 1
        battle.update(0, Controls(confirm=True))
        self.assertEqual(battle.phase, Phase.ACT)
        battle.update(0, Controls(cancel=True))
        self.assertEqual(battle.phase, Phase.MENU)
        self.assertEqual(battle.turn, 0)

    def test_act_defend_spare_route_without_attacking(self):
        battle = self.make_battle()
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
            battle.arena = Arena(QuietPattern(), battle.player.hp)
            battle.update(1, Controls())
            finish_message(battle)
            self.assertEqual(battle.phase, Phase.MENU)
        self.assertTrue(battle.spare_ready)
        self.assertEqual(battle.enemy_hp, battle.character.max_hp)
        battle.selection = 3
        battle.choose()
        battle.choose()
        self.assertEqual(battle.outcome, Outcome.SPARED)
        finish_message(battle)
        self.assertEqual(battle.phase, Phase.FINISHED)

    def test_attack_damage_and_combat_result(self):
        battle = self.make_battle()
        battle.enemy_hp = 4
        battle.set_phase(Phase.ATTACK)
        battle.update(0.725, Controls(confirm=True))
        self.assertEqual(battle.enemy_hp, 0)
        self.assertEqual(battle.outcome, Outcome.DEFEATED)
        self.assertEqual(battle.last_damage, 13)

    def test_item_clamps_health_and_empty_inventory_returns_to_menu(self):
        battle = self.make_battle()
        battle.player.hp = 18
        battle.set_phase(Phase.ITEM)
        battle.choose()
        self.assertEqual(battle.player.hp, 20)
        self.assertEqual(battle.player.snacks, 1)
        battle.player.snacks = 0
        battle.set_phase(Phase.ITEM)
        battle.choose()
        finish_message(battle)
        self.assertEqual(battle.phase, Phase.MENU)

    def test_leave_practice_and_loss_are_distinct_outcomes(self):
        battle = self.make_battle()
        battle.set_phase(Phase.MERCY)
        battle.selection = 1
        battle.choose()
        self.assertEqual(battle.outcome, Outcome.LEFT)
        lost = self.make_battle()
        lost.set_phase(Phase.DEFEND)
        lost.arena.hp = 0
        lost.update(0.01, Controls())
        self.assertEqual(lost.player.hp, 0)
        self.assertEqual(lost.outcome, Outcome.LOST)

    def test_long_dialogue_is_paged_and_no_page_takes_a_turn(self):
        battle = self.make_battle()
        battle.say("A long student story. " * 40, Phase.MENU)
        self.assertGreater(len(battle.pages), 2)
        finish_message(battle)
        self.assertEqual(battle.phase, Phase.MENU)
        self.assertEqual(battle.turn, 0)


class WorldAndSceneTests(unittest.TestCase):
    def test_world_to_battle_transition_freezes_input_and_returns_to_position(self):
        game = Game()
        run_for(game, 0.42, Controls(y=-1))
        game.update(0, Controls(confirm=True))
        self.assertEqual(game.world.talking.key, "folio")
        game.update(0, Controls(confirm=True))
        before = game.world.position.copy()
        self.assertIsNotNone(game.transition)
        run_for(game, 0.4, Controls(x=1, confirm=True))
        self.assertEqual(game.scene, Scene.BATTLE)
        self.assertEqual(game.battle.phase, Phase.MESSAGE)
        self.assertEqual(game.world.position, before)
        run_for(game, 0.4)
        game.battle.finish(Outcome.SPARED, "A peaceful finish.")
        finish_message(game.battle)
        game.update(0)
        run_for(game, 0.8)
        self.assertEqual(game.scene, Scene.WORLD)
        self.assertEqual(game.session.resolved["folio"], Outcome.SPARED)
        self.assertEqual(game.world.position, before)

    def test_loss_restores_player_and_flee_preserves_unresolved_encounter(self):
        game = Game(encounter="folio")
        game.session.player.hp = 0
        game.session.player.snacks = 0
        game.battle.finish(Outcome.LOST, "Rest.")
        finish_message(game.battle)
        game.update(0)
        run_for(game, 0.8)
        self.assertEqual(game.session.player.hp, 20)
        self.assertEqual(game.session.player.snacks, 2)
        self.assertFalse(game.session.resolved)
        self.assertEqual(game.world.position, tile_center((7, 12)))
        game.encounter(ROOMS["courtyard"].people[0])
        run_for(game, 0.8)
        game.battle.finish(Outcome.LEFT, "Later.")
        finish_message(game.battle)
        game.update(0)
        run_for(game, 0.8)
        self.assertFalse(game.session.resolved)

    def test_wall_collision_does_not_tunnel_and_diagonal_speed_matches(self):
        a, b = World(ROOMS, Session()), World(ROOMS, Session())
        start = a.position.copy()
        a.move(Vec(1, 0), 0.1)
        b.move(Vec(1, -1), 0.1)
        self.assertAlmostEqual(a.position.distance_to(start), b.position.distance_to(start))
        a.position = tile_center((1, 1))
        a.move(Vec(-1, 0), 3)
        self.assertGreaterEqual(a.position.x, 41)
        self.assertTrue(a.passable(a.position))

    def test_doors_fountain_help_pause_and_weapon_selection(self):
        game = Game()
        game.world.position = tile_center((14, 1))
        run_for(game, 0.5)
        run_for(game, 0.15, Controls(y=-1))
        run_for(game, 0.8)
        self.assertEqual(game.world.room_key, "garden")
        self.assertEqual(game.world.position, tile_center((14, 13)))
        game.world.position = tile_center(game.world.room.rest_tile)
        game.session.player.hp = 2
        game.session.player.snacks = 0
        game.update(0, Controls(confirm=True))
        self.assertEqual(game.session.player.hp, 20)
        self.assertEqual(game.session.player.snacks, 2)
        old = game.world.position.copy()
        game.help_open = True
        run_for(game, 0.5, Controls(x=1))
        self.assertEqual(game.world.position, old)
        game.help_open = False
        game.change_weapon()
        self.assertEqual(game.session.player.weapon, 1)


class ExtensionTests(unittest.TestCase):
    def test_all_real_content_factories_and_rooms_validate(self):
        self.assertEqual(validate_content(CHARACTERS, WEAPONS, PATTERNS, ROOMS), [])

    def test_student_pattern_is_registered_and_playable_without_engine_changes(self):
        from undercode.student import ECHO, RippleLanes

        pattern = ECHO.choose_pattern(TurnContext(0, 20, 20, 0))
        self.assertIsInstance(pattern, RippleLanes)
        game = Game(practice="ripples")
        self.assertEqual(game.battle.phase, Phase.DEFEND)
        run_for(game, 1)
        self.assertGreater(len(game.battle.arena.bullets), 0)
        self.assertEqual(game.battle.arena.pattern.name, pattern.name)

    def test_seeds_repeat_spawns_and_separate_instances_do_not_share_clocks(self):
        first, second = Arena(PATTERNS["pages"](), 20, 11), Arena(PATTERNS["pages"](), 20, 11)
        for _ in range(30):
            first.update(1 / 60, Controls())
            second.update(1 / 60, Controls())
        self.assertEqual(
            [tuple(b.position) for b in first.bullets], [tuple(b.position) for b in second.bullets]
        )
        self.assertIsNot(first.pattern, second.pattern)
        first.update(0.1, Controls())
        self.assertNotEqual(first.elapsed, second.elapsed)


class CompleteRouteTests(unittest.TestCase):
    def test_each_character_can_be_spared_through_real_defense_patterns(self):
        for character in CHARACTERS:
            with self.subTest(character=character.key):
                battle = Battle(character, Player(), WEAPONS[0], seed=7)
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
                        battle.update(1 / 60, Controls())
                    self.assertIsNone(
                        battle.outcome, "The introductory peaceful route should be forgiving"
                    )
                    finish_message(battle)
                battle.selection = 3
                battle.choose()
                battle.choose()
                self.assertEqual(battle.outcome, Outcome.SPARED)
                self.assertEqual(battle.enemy_hp, character.max_hp)

    def test_each_character_can_be_defeated_with_real_strikes_and_a_counterturn(self):
        for character in CHARACTERS:
            with self.subTest(character=character.key):
                battle = Battle(character, Player(), WEAPONS[0], seed=7)
                finish_message(battle)
                while battle.outcome is None:
                    battle.selection = 0
                    battle.choose()
                    battle.update(0.725, Controls(confirm=True))
                    if battle.outcome:
                        break
                    finish_message(battle)
                    while battle.phase == Phase.DEFEND:
                        battle.update(1 / 60, Controls())
                    finish_message(battle)
                self.assertEqual(battle.outcome, Outcome.DEFEATED)


if __name__ == "__main__":
    unittest.main()
