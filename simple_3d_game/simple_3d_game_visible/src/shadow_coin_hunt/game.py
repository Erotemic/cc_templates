from __future__ import annotations

from dataclasses import dataclass
from math import sin
from random import choice, sample, uniform

from ursina import (
    BoxCollider,
    Entity,
    Sky,
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
from ursina.shaders import colored_lights_shader


ARENA_LIMIT = 18
ROUND_TIME_SECONDS = 45
START_POSITION = Vec3(0, 2, 0)


@dataclass(frozen=True)
class RgbColor:
    red: int
    green: int
    blue: int


def clamp_channel(value: int) -> int:
    return max(0, min(255, value))


def shade(rgb: RgbColor, delta: int) -> tuple[int, int, int]:
    return (
        clamp_channel(rgb.red + delta),
        clamp_channel(rgb.green + delta),
        clamp_channel(rgb.blue + delta),
    )


def apply_face_shading(entity: Entity, base: RgbColor) -> None:
    """Use Ursina's colored_lights_shader for readable face contrast."""
    entity.shader = colored_lights_shader
    entity.color = color.white
    entity.set_shader_input("top_color", color.rgb(*shade(base, 34)))
    entity.set_shader_input("bottom_color", color.rgb(*shade(base, -70)))
    entity.set_shader_input("left_color", color.rgb(*shade(base, -18)))
    entity.set_shader_input("right_color", color.rgb(*shade(base, 12)))
    entity.set_shader_input("front_color", color.rgb(*shade(base, 24)))
    entity.set_shader_input("back_color", color.rgb(*shade(base, -28)))


class ShadowCoinHunt(Entity):
    """Minimal first-person coin collector with strong contrast and simple code."""

    def __init__(self) -> None:
        super().__init__()
        self.score = 0
        self.time_left = ROUND_TIME_SECONDS
        self.game_over = False
        self.second_timer = 0.0
        self.wave_time = 0.0
        self.coins: list[Entity] = []
        self.spawn_points = [
            Vec3(-12, 1.2, -12),
            Vec3(-8, 1.2, 6),
            Vec3(-3, 1.2, -2),
            Vec3(5, 1.2, 10),
            Vec3(11, 1.2, -8),
            Vec3(13, 1.2, 12),
            Vec3(-10, 3.2, 11),
            Vec3(0, 3.2, -12),
            Vec3(12, 4.2, 11),
            Vec3(6, 2.2, 4),
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
        window.color = color.rgb(24, 30, 38)

    def _build_ui(self) -> None:
        self.score_text = Text(text="Score: 0", position=(-0.85, 0.45), scale=2)
        self.timer_text = Text(text=f"Time: {ROUND_TIME_SECONDS}", position=(0.57, 0.45), scale=2)
        self.help_text = Text(
            text="WASD move | Mouse look | Space jump | Shift sprint | R restart | Q or Esc quit",
            position=(-0.72, -0.47),
            scale=1.05,
            color=color.rgb(235, 235, 235),
        )
        self.message_text = Text(text="", origin=(0, 0), scale=2.2, y=0, color=color.rgb(250, 250, 250))

    def _build_world(self) -> None:
        self.sky = Sky(color=color.rgb(90, 130, 190))

        self.ground = Entity(
            model="plane",
            scale=(40, 1, 40),
            color=color.rgb(62, 110, 70),
            collider="box",
        )

        apply_face_shading(self.ground, RgbColor(62, 110, 70))

        wall_base = RgbColor(70, 88, 135)
        self.walls = [
            self._make_block(position=(0, 2, 20), scale=(40, 4, 1), base=wall_base),
            self._make_block(position=(0, 2, -20), scale=(40, 4, 1), base=wall_base),
            self._make_block(position=(20, 2, 0), scale=(1, 4, 40), base=wall_base),
            self._make_block(position=(-20, 2, 0), scale=(1, 4, 40), base=wall_base),
        ]

        self.level_blocks = [
            self._make_block(position=(-8, 1, -6), scale=(2, 2, 2), base=RgbColor(196, 96, 56)),
            self._make_block(position=(6, 1.5, 4), scale=(2, 3, 2), base=RgbColor(120, 86, 186)),
            self._make_block(position=(10, 2, -5), scale=(2, 4, 2), base=RgbColor(46, 154, 182)),
            self._make_block(position=(-4, 1, 8), scale=(2, 2, 2), base=RgbColor(184, 70, 120)),
            self._make_block(position=(-10, 2.5, 10), scale=(4, 0.5, 4), base=RgbColor(225, 164, 66)),
            self._make_block(position=(12, 3.5, 12), scale=(4, 0.5, 4), base=RgbColor(226, 214, 94)),
            self._make_block(position=(0, 2.5, -12), scale=(4, 0.5, 4), base=RgbColor(90, 196, 125)),
        ]

        self.landmarks = [
            self._make_block(position=(-15, 3, -15), scale=(1.5, 6, 1.5), base=RgbColor(225, 72, 72)),
            self._make_block(position=(15, 3, -15), scale=(1.5, 6, 1.5), base=RgbColor(246, 181, 68)),
            self._make_block(position=(-15, 3, 15), scale=(1.5, 6, 1.5), base=RgbColor(60, 190, 220)),
            self._make_block(position=(15, 3, 15), scale=(1.5, 6, 1.5), base=RgbColor(190, 102, 230)),
        ]

    def _make_block(self, position: tuple[float, float, float], scale: tuple[float, float, float], base: RgbColor) -> Entity:
        entity = Entity(
            model="cube",
            position=position,
            scale=scale,
            collider="box",
        )
        apply_face_shading(entity, base)
        return entity

    def _build_player(self) -> None:
        self.player = FirstPersonController(
            position=START_POSITION,
            origin_y=-0.5,
            speed=6,
            jump_height=2.2,
            gravity=1,
        )
        self.player.collider = BoxCollider(self.player, center=Vec3(0, 1, 0), size=Vec3(1, 2, 1))
        self.player.cursor.color = color.rgb(10, 10, 10)
        self.player.camera_pivot.rotation_x = -10

    def spawn_coin(self, position: Vec3 | None = None) -> None:
        spawn_position = position or choice(self.spawn_points)
        coin = Entity(
            model="sphere",
            scale=0.55,
            position=spawn_position,
            color=color.rgb(255, 214, 70),
            collider="box",
            unlit=True,
        )
        coin.base_y = spawn_position.y
        coin.wave_offset = uniform(0.0, 6.28)
        self.coins.append(coin)

    def clear_coins(self) -> None:
        for coin in self.coins:
            destroy(coin)
        self.coins.clear()

    def refill_coins(self) -> None:
        self.clear_coins()
        for spawn_position in sample(self.spawn_points, 6):
            self.spawn_coin(spawn_position)

    def reset_game(self) -> None:
        self.score = 0
        self.time_left = ROUND_TIME_SECONDS
        self.game_over = False
        self.second_timer = 0.0
        self.wave_time = 0.0

        self.player.position = START_POSITION
        self.player.rotation = Vec3(0, 0, 0)
        self.player.camera_pivot.rotation = Vec3(-10, 0, 0)

        self.score_text.text = "Score: 0"
        self.timer_text.text = f"Time: {ROUND_TIME_SECONDS}"
        self.message_text.text = ""
        self.refill_coins()

    def end_game(self) -> None:
        self.game_over = True
        self.message_text.text = (
            f"Game Over!\nFinal Score: {self.score}\nPress R to restart\nPress Q or Esc to quit"
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

        self.player.speed = 9 if (held_keys["left shift"] or held_keys["right shift"]) else 6

        self.wave_time += time.dt
        for coin in self.coins:
            coin.rotation_y += 120 * time.dt
            coin.y = coin.base_y + sin(self.wave_time * 3 + coin.wave_offset) * 0.18

        for coin in list(self.coins):
            if distance(self.player.position, coin.position) < 1.15:
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

        if self.player.y < -10:
            self.player.position = START_POSITION
            self.player.rotation = Vec3(0, 0, 0)
            self.player.camera_pivot.rotation = Vec3(-10, 0, 0)


def main() -> None:
    app = Ursina()
    ShadowCoinHunt()
    app.run()


if __name__ == "__main__":
    main()
