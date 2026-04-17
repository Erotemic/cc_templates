from rpg_battle.content.audio import DEFAULT_BATTLE_TRACK, MUSIC_TRACKS, SOUND_EFFECTS
from rpg_battle.content.moves import MOVES


def test_default_track_exists() -> None:
    assert DEFAULT_BATTLE_TRACK in MUSIC_TRACKS


def test_every_move_sound_exists() -> None:
    for move in MOVES.values():
        assert move.sound_id
        assert move.sound_id in SOUND_EFFECTS
