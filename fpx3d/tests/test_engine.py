"""Regressions for the playable baseline, without a Panda3D installation."""

from __future__ import annotations

from math import hypot
from unittest import TestCase
from unittest.mock import patch

from fpx3d import engine, settings, student, world


class WorldTests(TestCase):
    def test_unique_required_pickups_and_reachable_ground_positions(self):
        self.assertGreaterEqual(len(world.CORES), 3)
        self.assertEqual(len({p.name for p in world.PICKUPS}), len(world.PICKUPS))
        for item in world.CORES:
            self.assertLess(abs(item.x), settings.MAP_EDGE - 1)
            self.assertLess(abs(item.y), settings.MAP_EDGE - 1)
            self.assertLess(item.z, 1.5)
            for box in world.SOLIDS:
                # No solid wall goes THROUGH a required ground crystal.
                self.assertFalse(box.top > .5 and box.bottom < 1.2
                                 and box.under(item.x, item.y, .4),
                                 (item, box))

    def test_required_prisms_and_exit_are_connected_on_the_floor(self):
        # Reachability is a level-design requirement, not just a physics
        # requirement. One prism hidden *inside* a platform breaks the game.
        from collections import deque
        state = engine.State()
        start = (round(settings.START[0]), round(settings.START[1]))
        queue = deque([start])
        reachable = {start}
        while queue:
            x, y = queue.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if not (-20 <= xx <= 20 and -20 <= yy <= 20):
                    continue
                candidate = (xx, yy)
                if candidate in reachable or engine._collides_laterally(state, xx, yy):
                    continue
                reachable.add(candidate)
                queue.append(candidate)
        for pickup in world.CORES:
            self.assertIn((round(pickup.x), round(pickup.y)), reachable,
                          f"Unreachable required pickup: {pickup.name}")
        self.assertIn((round(settings.EXIT[0]), round(settings.EXIT[1])), reachable)

    def test_solid_collision_geometry_matches_box_dimensions(self):
        for box in world.SOLIDS:
            self.assertTrue(box.under(box.x, box.y))
            self.assertFalse(box.under(box.x + box.width, box.y))
            self.assertGreater(box.top, box.bottom)

    def test_nearest_core_changes_with_collection(self):
        first = world.CORES[0]
        near = world.nearest_core(first.x, first.y, set())
        self.assertEqual(near.name, first.name)
        after = world.nearest_core(first.x, first.y, {near.name})
        self.assertNotEqual(after.name, near.name)
        self.assertIsNone(world.nearest_core(0, 0, {p.name for p in world.CORES}))


class EngineTests(TestCase):
    def test_initial_state(self):
        state = engine.State()
        self.assertTrue(state.player.on_ground)
        self.assertEqual(state.cores_collected, 0)
        self.assertFalse(state.gate_open)
        self.assertEqual(state.hearts, settings.MAX_HEARTS)
        self.assertIn("prism", engine.objective_hint(state).lower())

    def test_forward_motion_and_diagonal_normalization(self):
        a = engine.State()
        b = engine.State()
        engine.step(a, engine.Controls(forward=1), .05)
        engine.step(b, engine.Controls(forward=1, sideways=1), .05)
        expected = settings.WALK_SPEED * .05
        self.assertAlmostEqual(a.player.y - settings.START[1], expected)
        self.assertAlmostEqual(hypot(b.player.x, b.player.y - settings.START[1]),
                               expected)

    def test_boundary_walls_cannot_be_walked_through(self):
        state = engine.State()
        state.player.x = 19.3
        for _ in range(60):
            engine.step(state, engine.Controls(sideways=1), 1/60)
        self.assertLess(state.player.x, 20)

    def test_jump_lands_and_does_not_repeat_while_airborne(self):
        state = engine.State()
        engine.step(state, engine.Controls(jump_pressed=True), 1/60)
        self.assertGreater(state.player.z, 0)
        self.assertFalse(state.player.on_ground)
        vy = state.player.vz
        engine.step(state, engine.Controls(jump_pressed=True), 1/60)
        self.assertLess(state.player.vz, vy)
        for _ in range(100):
            engine.step(state, engine.Controls(), 1/60)
        self.assertTrue(state.player.on_ground)
        self.assertAlmostEqual(state.player.z, 0)

    def test_player_can_land_on_a_balcony(self):
        balcony = next(box for box in world.SOLIDS
                       if box.name == "moss balcony")
        state = engine.State()
        state.player.x, state.player.y = balcony.x, balcony.y
        state.player.z = balcony.top + 2
        state.player.vz = -2
        state.player.on_ground = False
        for _ in range(120):
            engine.step(state, engine.Controls(), 1/60)
            if state.player.on_ground:
                break
        self.assertTrue(state.player.on_ground)
        self.assertAlmostEqual(state.player.z, balcony.top)

    def test_first_prism_can_be_collected_by_walking(self):
        state = engine.State()
        for _ in range(100):
            engine.step(state, engine.Controls(forward=1), 1/60)
            if world.CORES[0].name in state.collected:
                break
        self.assertIn(world.CORES[0].name, state.collected)

    def test_walkthrough_pickup_and_gate(self):
        state = engine.State()
        state.player.x, state.player.y = world.CORES[0].x, world.CORES[0].y
        engine.step(state, engine.Controls(), 0)
        self.assertEqual(state.cores_collected, 1)
        self.assertIn("core", state.events)
        for item in world.CORES[1:]:
            state.player.x, state.player.y = item.x, item.y
            engine.step(state, engine.Controls(), 0)
        self.assertTrue(state.gate_open)
        self.assertIn("portal", state.events)
        state.player.x, state.player.y = settings.EXIT[:2]
        engine.step(state, engine.Controls(), 0)
        self.assertTrue(state.won)
        self.assertIn("win", state.events)

    def test_portal_is_locked_until_prisms_collected(self):
        state = engine.State()
        state.player.x, state.player.y = settings.EXIT[:2]
        engine.step(state, engine.Controls(), 0)
        self.assertFalse(state.won)

    def test_red_pad_can_hurt_but_has_cooldown(self):
        state = engine.State()
        hazard = next(p for p in world.PADS if p.kind == "danger")
        state.player.x, state.player.y = hazard.x, hazard.y
        engine.step(state, engine.Controls(), 0)
        self.assertEqual(state.hearts, settings.MAX_HEARTS - 1)
        engine.step(state, engine.Controls(), 0)
        self.assertEqual(state.hearts, settings.MAX_HEARTS - 1)

    def test_spring_pad_launches_player(self):
        state = engine.State()
        spring = next(p for p in world.PADS if p.kind == "spring")
        state.player.x, state.player.y = spring.x, spring.y
        engine.step(state, engine.Controls(), 0)
        self.assertEqual(state.player.vz, settings.SPRING_SPEED)
        self.assertIn("spring", state.events)

    def test_timeout_and_restart(self):
        state = engine.State(time_left=.01)
        engine.step(state, engine.Controls(), .02)
        self.assertTrue(state.lost)
        old_elapsed = state.elapsed
        engine.step(state, engine.Controls(forward=1), .04)
        self.assertEqual(state.elapsed, old_elapsed)
        state.restart()
        self.assertFalse(state.lost)
        self.assertEqual(state.cores_collected, 0)
        self.assertEqual(state.player.y, settings.START[1])

    def test_bonus_reward_student_hook_runs_once(self):
        state = engine.State()
        bonus = world.BONUSES[2]  # An easy-to-reach ground bonus.
        state.player.x, state.player.y = bonus.x, bonus.y
        with patch.object(student, "bonus_reward") as hook:
            engine.step(state, engine.Controls(), 0)
            engine.step(state, engine.Controls(), 0)
        hook.assert_called_once_with(state, bonus)
        self.assertIn(bonus.name, state.collected)

    def test_drone_patrol_student_hook_changes_position(self):
        state = engine.State()
        drone = state.drones[0]
        first = drone.x
        with patch.object(student, "move_drone",
                          side_effect=lambda item, dt: setattr(item, 'x', item.x + dt)):
            engine.step(state, engine.Controls(), .03)
        self.assertAlmostEqual(drone.x, first + .03)

    def test_scanner_hook_controls_hazard(self):
        state = engine.State()
        state.player.x, state.player.y = world.SCANNER_CENTER
        with patch.object(student, "update_scanner",
                          side_effect=lambda scanner, dt: setattr(scanner, 'active', True)):
            engine.step(state, engine.Controls(), 0)
        self.assertEqual(state.hearts, settings.MAX_HEARTS - 1)

    def test_checkpoint_student_hook_controls_respawn(self):
        state = engine.State()
        pad = next(p for p in world.PADS if p.kind == "checkpoint")
        state.player.x, state.player.y = pad.x, pad.y
        def save_checkpoint(state, pad):
            state.respawn_at = (pad.x, pad.y, 0.0)
            state.checkpoint_name = f"{pad.x},{pad.y}"
        with patch.object(student, "activate_checkpoint", save_checkpoint):
            engine.step(state, engine.Controls(), 0)
        self.assertEqual(state.respawn_at, (pad.x, pad.y, 0))
        self.assertEqual(state.checkpoint_name, f"{pad.x},{pad.y}")

    def test_stamina_student_hook_changes_sprint_capacity(self):
        state = engine.State()
        def drain(state, controls, dt):
            state.stamina = max(0, state.stamina - 100 * dt)
        with patch.object(student, "update_sprint_energy", drain):
            engine.step(state, engine.Controls(sprint=True, forward=1), .05)
        self.assertEqual(state.stamina, 95)

    def test_moving_lift_student_hook_carries_player(self):
        state = engine.State()
        lift = state.lifts[0]
        state.player.x, state.player.y, state.player.z = lift.x, lift.y, lift.top
        state.player.on_ground = True
        def move(lift, dt):
            lift.x += 2 * dt
        with patch.object(student, "move_lift", move):
            engine.step(state, engine.Controls(), .05)
        self.assertAlmostEqual(state.player.x, lift.x)
        self.assertAlmostEqual(state.player.z, lift.top)

    def test_curator_hook_overrides_message(self):
        state = engine.State()
        first = world.CORES[0]
        state.player.x, state.player.y = first.x, first.y
        with patch.object(student, "curator_line", return_value="Custom line"):
            engine.step(state, engine.Controls(), 0)
        self.assertEqual(state.notice, "Custom line")

    def test_distant_hint_points_toward_core(self):
        state = engine.State()
        first = world.CORES[0]
        state.collected.update(p.name for p in world.CORES[1:])
        state.player.x, state.player.y = first.x, first.y - 4
        self.assertIn("AHEAD", engine.objective_hint(state))
        state.player.heading = 180
        self.assertIn("BEHIND", engine.objective_hint(state))

    def test_headless_engine_import_does_not_pull_in_panda3d(self):
        import subprocess
        import sys
        result = subprocess.run(
            [sys.executable, '-c',
             'import fpx3d.engine, sys; assert "panda3d" not in sys.modules'],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
