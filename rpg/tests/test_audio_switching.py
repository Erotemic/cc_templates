from __future__ import annotations

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from rpg_battle.battle.battle_scene import BattleScene
from rpg_battle.content.audio import (
    DEFAULT_BATTLE_TRACK,
    DEFAULT_DEFEAT_TRACK,
    DEFAULT_VICTORY_TRACK,
)
from rpg_battle.content.encounters import ENCOUNTERS


class StubAudio:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def play_music(self, track_id: str, loops: int = -1) -> None:
        self.calls.append(("play_music", track_id))

    def stop_music(self) -> None:
        self.calls.append(("stop_music", ""))

    def play_sfx(self, sound_id: str) -> None:
        self.calls.append(("play_sfx", sound_id))


def test_battle_scene_plays_only_encounter_track_when_present() -> None:
    pygame.init()
    try:
        audio = StubAudio()
        scene = BattleScene(
            pygame.Rect(0, 0, 1280, 720),
            audio=audio,
            encounter=ENCOUNTERS["boss_ai_slop"],
        )
        assert scene.controller.encounter.music_track_id == "boss_battle_frenzy"
        assert audio.calls[0] == ("play_music", "boss_battle_frenzy")
        assert all(
            track != DEFAULT_BATTLE_TRACK for kind, track in audio.calls if kind == "play_music"
        )
    finally:
        pygame.quit()


def test_battle_end_plays_victory_music_for_player_win() -> None:
    pygame.init()
    try:
        audio = StubAudio()
        scene = BattleScene(
            pygame.Rect(0, 0, 1280, 720), audio=audio, encounter=ENCOUNTERS["default"]
        )
        audio.calls.clear()
        scene._handle_battle_event({"type": "battle_end", "winner": 0, "text": "Player wins!"})
        assert ("play_music", DEFAULT_VICTORY_TRACK) in audio.calls
    finally:
        pygame.quit()


def test_battle_end_plays_defeat_music_for_player_loss() -> None:
    pygame.init()
    try:
        audio = StubAudio()
        scene = BattleScene(
            pygame.Rect(0, 0, 1280, 720), audio=audio, encounter=ENCOUNTERS["default"]
        )
        audio.calls.clear()
        scene._handle_battle_event({"type": "battle_end", "winner": 1, "text": "Enemy wins!"})
        assert ("play_music", DEFAULT_DEFEAT_TRACK) in audio.calls
    finally:
        pygame.quit()
