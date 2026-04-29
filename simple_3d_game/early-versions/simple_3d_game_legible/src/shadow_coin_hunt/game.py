from __future__ import annotations

from math import sin
import random

from ursina import (
    Entity,
    Text,
    Ursina,
    Vec3,
    application,
    color,
    destroy,
    distance,
    held_keys,
    time,
    window,
)
from ursina.prefabs.first_person_controller import FirstPersonController


class ShadowCoinHunt(Entity):
    """A simple, high-contrast first-person game meant to be easy to read and learn from."""

    def __init__(self) -> None:
        super().__init__()
        self.score = 0
        self.time_left = 45
        self.game_over = False
        self.second_timer = 0.0
        self.wave_time = 0.0
        self.coins: list[Entity] = []

        self.spawn_points = [
            Vec3(-10, 1.5, -8),
            Vec3(-6, 1.5, 6),
            Vec3(0, 1.5, -2),
            Vec3(7, 1.5, 8),
            Vec3(10, 1.5, -10),
            Vec3(-12, 3.2, 10),
            Vec3(12, 3.2, 12),
            Vec3(0, 2.2, 10),
        ]

        self._configure_window()
        self._build_ui()
        self._build_world()
        self._build_player()
        self.reset_game()

    def _configure_window(self) -> None:
        window.title = "Shadow Coin Hunt"
        window.borderless = False
        window.exit_button.visible = False
        window.fps_counter.enabled = True
        # Use the window background as a calm sky color.
        window.color = color.rgb(125, 155, 210)

    def _build_ui(self) -> None:
        self.score_text = Text(
            text="Score: 0",
            position=(-0.85, 0.45),
            scale=2,
            color=color.black,
        )
        self.timer_text = Text(
            text="Time: 45",
            position=(0.62, 0.45),
            scale=2,
            color=color.black,
        )
        from ursina import camera

        self.help_back = Entity(
            parent=camera.ui,
            model="quad",
            scale=(1.0, 0.08),
            position=(0, -0.44),
            color=color.rgba(255, 255, 255, 180),
        )
        self.help_text = Text(
            parent=camera.ui,
            text="WASD move | Mouse look | Space jump | Shift sprint | R restart | Q or Esc quit",
            origin=(0, 0),
            position=(0, -0.455),
            scale=1.15,
            color=color.black,
        )
        self.message_back = Entity(
            parent=camera.ui,
            model="quad",
            scale=(0.55, 0.22),
            color=color.rgba(255, 255, 255, 170),
            enabled=False,
        )
        self.message_text = Text(
            parent=camera.ui,
            text="",
            origin=(0, 0),
            scale=2,
            color=color.black,
            y=0.02,
        )

    @property
    def camera_ui(self) -> Entity:
        # Imported lazily through Entity parenting rules to keep the import list short.
        return self.player.cursor.parent if hasattr(self, "player") else __import__("ursina").camera.ui

    def _make_block(
        self,
        position: tuple[float, float, float] | Vec3,
        scale: tuple[float, float, float],
        rgb: tuple[int, int, int],
        collider: str = "box",
    ) -> Entity:
        return Entity(
            model="cube",
            position=position,
            scale=scale,
            color=color.rgb(*rgb),
            collider=collider,
        )

    def _build_world(self) -> None:
        # Thick cube floor instead of a plane. This avoids the washed-out plane issue.
        self.floor = self._make_block(
            position=(0, -0.5, 0),
            scale=(44, 1, 44),
            rgb=(70, 150, 90),
        )

        # Border walls.
        self.walls = [
            self._make_block(position=(0, 2, 21), scale=(44, 4, 1), rgb=(60, 110, 220)),
            self._make_block(position=(0, 2, -21), scale=(44, 4, 1), rgb=(60, 110, 220)),
            self._make_block(position=(21, 2, 0), scale=(1, 4, 44), rgb=(60, 110, 220)),
            self._make_block(position=(-21, 2, 0), scale=(1, 4, 44), rgb=(60, 110, 220)),
        ]

        # A bright path down the middle helps orientation.
        self.path = [
            self._make_block(position=(0, 0.05, -12), scale=(6, 0.1, 8), rgb=(235, 225, 170), collider=None),
            self._make_block(position=(0, 0.05, -2), scale=(6, 0.1, 8), rgb=(235, 225, 170), collider=None),
            self._make_block(position=(0, 0.05, 8), scale=(6, 0.1, 8), rgb=(235, 225, 170), collider=None),
        ]

        # Corner towers make it easy to tell where you are.
        self.towers = [
            self._make_block(position=(-18, 3, -18), scale=(2, 6, 2), rgb=(220, 80, 80)),
            self._make_block(position=(18, 3, -18), scale=(2, 6, 2), rgb=(240, 170, 60)),
            self._make_block(position=(-18, 3, 18), scale=(2, 6, 2), rgb=(100, 200, 200)),
            self._make_block(position=(18, 3, 18), scale=(2, 6, 2), rgb=(180, 100, 220)),
        ]

        # Obstacles and little platforms. These are placed away from the player spawn.
        self.blocks = [
            self._make_block(position=(-8, 1, 0), scale=(3, 2, 3), rgb=(170, 85, 60)),
            self._make_block(position=(8, 1, 2), scale=(3, 2, 3), rgb=(170, 85, 60)),
            self._make_block(position=(0, 1.5, 12), scale=(4, 3, 4), rgb=(80, 90, 120)),
            self._make_block(position=(-12, 2.5, 10), scale=(4, 0.5, 4), rgb=(160, 160, 180)),
            self._make_block(position=(12, 2.5, 12), scale=(4, 0.5, 4), rgb=(160, 160, 180)),
            self._make_block(position=(0, 1.2, -6), scale=(8, 2.4, 2), rgb=(85, 130, 170)),
        ]

    def _build_player(self) -> None:
        self.player = FirstPersonController(
            position=(0, 2, -16),
            speed=6,
            jump_height=1.8,
            gravity=1,
        )
        # Start by looking slightly downward so the player immediately sees the arena.
        self.player.camera_pivot.rotation_x = 8

    def spawn_coin(self, position: Vec3 | None = None) -> None:
        spawn_position = position or random.choice(self.spawn_points)
        coin = Entity(
            model="sphere",
            position=spawn_position,
            scale=0.7,
            color=color.rgb(255, 230, 0),
            collider="box",
        )
        coin.base_y = spawn_position.y
        coin.wave_offset = random.uniform(0.0, 6.28)
        self.coins.append(coin)

    def clear_coins(self) -> None:
        for coin in self.coins:
            destroy(coin)
        self.coins.clear()

    def refill_coins(self) -> None:
        self.clear_coins()
        for position in random.sample(self.spawn_points, 6):
            self.spawn_coin(position)

    def reset_game(self) -> None:
        self.score = 0
        self.time_left = 45
        self.game_over = False
        self.second_timer = 0.0
        self.wave_time = 0.0

        self.player.position = Vec3(0, 2, -16)
        self.player.rotation = Vec3(0, 0, 0)
        self.player.camera_pivot.rotation = Vec3(8, 0, 0)

        self.score_text.text = "Score: 0"
        self.timer_text.text = "Time: 45"
        self.message_text.text = ""
        self.message_back.enabled = False
        self.refill_coins()

    def end_game(self) -> None:
        self.game_over = True
        self.message_back.enabled = True
        self.message_text.text = (
            f"Game Over!\nFinal Score: {self.score}\nPress R to restart"
        )

    def input(self, key: str) -> None:
        if key in {"q", "escape"}:
            application.quit()
            return

        if key == "r" and self.game_over:
            self.reset_game()

    def update(self) -> None:
        if self.game_over:
            return

        self.player.speed = 9 if held_keys["left shift"] or held_keys["right shift"] else 6

        self.wave_time += time.dt
        for coin in self.coins:
            coin.rotation_y += 160 * time.dt
            coin.y = coin.base_y + sin(self.wave_time * 3 + coin.wave_offset) * 0.18

        for coin in list(self.coins):
            if distance(self.player.position, coin.position) < 1.35:
                self.coins.remove(coin)
                destroy(coin)
                self.score += 1
                self.score_text.text = f"Score: {self.score}"
                self.spawn_coin()

        self.second_timer += time.dt
        if self.second_timer >= 1.0:
            self.second_timer -= 1.0
            self.time_left -= 1
            self.timer_text.text = f"Time: {self.time_left}"
            if self.time_left <= 0:
                self.end_game()

        if self.player.y < -5:
            self.player.position = Vec3(0, 2, -16)
            self.player.rotation = Vec3(0, 0, 0)
            self.player.camera_pivot.rotation = Vec3(8, 0, 0)


def main() -> None:
    app = Ursina()
    ShadowCoinHunt()
    app.run()


if __name__ == "__main__":
    main()
