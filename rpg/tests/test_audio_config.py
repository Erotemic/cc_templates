from rpg_battle.audio.library import GeneratedTrackSpec, render_generated_track
from rpg_battle.content.audio import DEFAULT_BATTLE_TRACK, MUSIC_TRACKS, SOUND_EFFECTS
from rpg_battle.content.moves import MOVES


def test_default_track_exists() -> None:
    assert DEFAULT_BATTLE_TRACK in MUSIC_TRACKS


def test_boss_track_exists() -> None:
    spec = MUSIC_TRACKS["boss_battle_frenzy"]
    assert isinstance(spec, GeneratedTrackSpec)


def test_generated_track_renders() -> None:
    spec = MUSIC_TRACKS["boss_battle_frenzy"]
    pcm = render_generated_track(spec)
    assert len(pcm) > 0
    assert pcm.shape[1] == 2


def test_every_move_sound_exists() -> None:
    for move in MOVES.values():
        assert move.sound_id
        assert move.sound_id in SOUND_EFFECTS
