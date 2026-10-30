"""Movement, level reachability, and ready-to-implement guard exercises.

No Panda3D import is needed. Tests verify the ENGINE, not any particular
student solution; every behavior hook can be replaced with a new solution.
"""

from __future__ import annotations

from math import hypot
from unittest import TestCase
from unittest.mock import patch

from fpx3d import engine, settings, student, world


class GeometryTests(TestCase):
    def test_only_perimeter_walls_block_horizontal_motion(self):
        names = {box.name for box in world.WALK_BLOCKERS}
        self.assertEqual(names, {"north wall", "south wall",
                                 "east wall", "west wall"})
        self.assertTrue(all(box.solid for box in world.WALK_BLOCKERS))
        self.assertTrue(all(box.top >= settings.EYE_HEIGHT
                            for box in world.WALK_BLOCKERS))

    def test_raised_balconies_can_be_walked_under_and_landed_on(self):
        state = engine.State()
        for name in ("moss balcony", "azure balcony"):
            balcony = next(box for box in world.LANDING_PLATFORMS
                           if box.name == name)
            self.assertGreater(balcony.bottom, settings.PLAYER_HEIGHT)
            # Camera height is safely UNDER the balcony: there should be
            # neither a hidden movement obstacle nor eye-level clipping.
            state.player.x, state.player.y, state.player.z = (
                balcony.x, balcony.y - balcony.depth / 2 - 1, 0.0)
            state.player.on_ground = True
            for _ in range(70):
                engine.step(state, engine.Controls(forward=1), 1 / 60)
            self.assertGreater(state.player.y,
                               balcony.y + balcony.depth / 2)

            state.player.x, state.player.y = balcony.x, balcony.y
            state.player.z = balcony.top + 1.0
            state.player.vz = -2
            state.player.on_ground = False
            for _ in range(120):
                engine.step(state, engine.Controls(), 1/60)
                if state.player.on_ground:
                    break
            self.assertAlmostEqual(state.player.z, balcony.top)

    def test_circle_collision_is_not_a_square_at_corners(self):
        box = world.Box("sample", 0, 0, 1, 2, 2, 2, (1, 1, 1, 1))
        # The old square expansion blocked this point, but a circle does
        # not touch the corner at (1,1): sqrt(.3**2 + .3**2) > .42.
        self.assertFalse(engine._circle_touches_box(1.3, 1.3, .42, box))
        self.assertTrue(engine._circle_touches_box(1.2, 1.2, .42, box))
        self.assertFalse(engine._circle_touches_box(2.5, 0.0, .42, box))

    def test_perimeter_slides_and_recovers_from_outside_spawn(self):
        state = engine.State()
        state.player.x = settings.MAP_EDGE - settings.PLAYER_RADIUS - .02
        state.player.y = -12.0
        for _ in range(18):
            engine.step(state, engine.Controls(forward=1, sideways=1), .05)
        self.assertLessEqual(state.player.x,
                             settings.MAP_EDGE - settings.PLAYER_RADIUS + 1e-6)
        self.assertGreater(state.player.y, -12.0)  # Slides along wall.

        state.player.x = 30  # Accidental bad position while student edits.
        state.player.y = 30
        engine.step(state, engine.Controls(sideways=-1), 0.05)
        self.assertLess(state.player.x, settings.MAP_EDGE)
        self.assertLess(state.player.y, settings.MAP_EDGE)

    def test_portal_and_prisms_are_not_trapped_by_interior_art(self):
        state = engine.State()
        for pickup in world.CORES:
            self.assertFalse(engine._collides_laterally(state, pickup.x,
                                                       pickup.y), pickup.name)
        self.assertFalse(engine._collides_laterally(
            state, settings.EXIT[0], settings.EXIT[1]))
        self.assertFalse(engine._collides_laterally(
            state, settings.START[0], settings.START[1]))

    def test_recovery_key_keeps_progress(self):
        state = engine.State()
        state.collected.add(world.CORES[0].name)
        state.time_left = 81.0
        state.respawn_at = (4.0, -7.0, 0.0)
        state.player.x, state.player.y = 19.0, 19.0
        engine.recover_position(state)
        self.assertEqual((state.player.x, state.player.y, state.player.z),
                         state.respawn_at)
        self.assertEqual(state.cores_collected, 1)
        self.assertEqual(state.time_left, 81.0)
        self.assertIn('respawn', state.events)


class GuardianTests(TestCase):
    def test_guardian_exists_in_safe_visible_space(self):
        state = engine.State()
        self.assertGreaterEqual(len(state.guardians), 1)
        for guard in state.guardians:
            self.assertTrue(guard.name)
            self.assertGreater(guard.detection_radius, 1)
            self.assertFalse(engine._blocked_at(guard.x, guard.y,
                                                guard.radius, 0, guard.height))
            self.assertGreater(hypot(guard.x - state.player.x,
                                     guard.y - state.player.y),
                               settings.PLAYER_RADIUS + guard.radius + 1)

    def test_default_stationary_engine_if_student_does_nothing(self):
        state = engine.State()
        guard = state.guardians[0]
        initial = guard.x, guard.y
        with patch.object(student, 'guardian_chase', return_value=False), \
             patch.object(student, 'guardian_markov', return_value=None):
            for _ in range(180):
                engine.step(state, engine.Controls(), 1/60)
        self.assertEqual((guard.x, guard.y), initial)
        self.assertEqual(guard.mode, 'idle')

    def test_markov_hook_can_drive_walk_intent(self):
        state = engine.State()
        guard = state.guardians[0]
        initial = (guard.x, guard.y)
        def walk_east(g, dt):
            g.mode = 'east'
            g.move_x = 1.0
            g.move_y = 0.0
        with patch.object(student, 'guardian_chase', return_value=False), \
             patch.object(student, 'guardian_markov', side_effect=walk_east) as hook:
            for _ in range(20):
                engine.step(state, engine.Controls(), .05)
        self.assertEqual(hook.call_count, 20)
        self.assertAlmostEqual(guard.x - initial[0], guard.walk_speed)
        self.assertAlmostEqual(guard.y, initial[1])
        self.assertEqual(guard.mode, 'east')

    def test_chase_hook_overrides_patrol_and_has_faster_speed(self):
        state = engine.State()
        guard = state.guardians[0]
        state.player.x = guard.x - 2.0
        state.player.y = guard.y
        initial = guard.x
        def chase(g, player, dt):
            distance = hypot(player.x - g.x, player.y - g.y)
            if distance < g.detection_radius:
                g.move_x = player.x - g.x
                g.move_y = player.y - g.y
                return True
            return False
        with patch.object(student, 'guardian_chase', side_effect=chase), \
             patch.object(student, 'guardian_markov') as patrol:
            engine.step(state, engine.Controls(), .05)
            patrol.assert_not_called()
            self.assertTrue(guard.chasing)
            self.assertAlmostEqual(initial - guard.x,
                                   guard.chase_speed * .05)

            state.player.x, state.player.y = 0.0, 19.0  # far away
            engine.step(state, engine.Controls(), .05)
            self.assertFalse(guard.chasing)
            patrol.assert_called_once()

    def test_guardian_movement_cannot_escape_room(self):
        state = engine.State()
        guard = state.guardians[0]
        guard.x = settings.MAP_EDGE - guard.radius - .01
        guard.y = 18.0
        def run_walls(g, dt):
            g.move_x = 1.0
            g.move_y = 1.0
        with patch.object(student, 'guardian_chase', return_value=False), \
             patch.object(student, 'guardian_markov', side_effect=run_walls):
            for _ in range(100):
                engine.step(state, engine.Controls(), .05)
        self.assertLessEqual(guard.x, settings.MAP_EDGE - guard.radius + 1e-6)
        self.assertLessEqual(guard.y, settings.MAP_EDGE - guard.radius + 1e-6)

    def test_touching_guardian_hurts_once_during_cooldown(self):
        state = engine.State()
        guard = state.guardians[0]
        state.player.x, state.player.y = guard.x, guard.y
        with patch.object(student, 'guardian_chase', return_value=False), \
             patch.object(student, 'guardian_markov', return_value=None):
            engine.step(state, engine.Controls(), 0)
            self.assertEqual(state.hearts, settings.MAX_HEARTS - 1)
            self.assertIn('hurt', state.events)
            engine.step(state, engine.Controls(), 0)
            self.assertEqual(state.hearts, settings.MAX_HEARTS - 1)

    def test_restart_resets_guardian_state_and_random_generator(self):
        state = engine.State()
        guard = state.guardians[0]
        expected = guard.rng.random()
        guard.x += 10
        guard.mode = 'west'
        guard.decision_timer = 7
        guard.rng.random()
        state.restart()
        restored = state.guardians[0]
        self.assertEqual((restored.x, restored.y),
                         (restored.home_x, restored.home_y))
        self.assertEqual(restored.mode, 'idle')
        self.assertEqual(restored.decision_timer, 0)
        self.assertEqual(restored.rng.random(), expected)
