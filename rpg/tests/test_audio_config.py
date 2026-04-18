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


def test_blues_track_uses_triplet_grid() -> None:
    spec = MUSIC_TRACKS["bluesy_overhaul"]
    pcm = render_generated_track(spec)
    assert len(pcm) > 0
    expected_seconds = 12 * 12 * (60.0 / 116 / 3.0)
    actual_seconds = len(pcm) / 44100
    assert abs(actual_seconds - expected_seconds) < 0.1


def test_blues_is_default_track() -> None:
    assert DEFAULT_BATTLE_TRACK == "bluesy_overhaul"


def test_chill_track_exists() -> None:
    spec = MUSIC_TRACKS["chill_exploration"]
    assert isinstance(spec, GeneratedTrackSpec)


def test_d_minor_jam_track_exists() -> None:
    spec = MUSIC_TRACKS["d_minor_jam"]
    assert isinstance(spec, GeneratedTrackSpec)


def test_d_minor_jam_track_renders() -> None:
    spec = MUSIC_TRACKS["d_minor_jam"]
    pcm = render_generated_track(spec)
    assert len(pcm) > 0
    assert pcm.shape[1] == 2


def test_d_minor_jam_uses_support_bars_and_loop_wrap() -> None:
    from rpg_battle.audio.tracks import DMinorJamTrack

    track = DMinorJamTrack()
    arrangement = track.build()
    starts = {event.start_step for event in arrangement.note_events}
    # Sparse support figures in the back half should still be present.
    assert 64 in starts
    assert 80 in starts
    assert 96 in starts
    assert 224 in starts
    assert track.wrap_loop_events is True


def test_d_minor_jam_keeps_dense_solo_sections() -> None:
    from rpg_battle.audio.tracks import DMinorJamTrack

    track = DMinorJamTrack()
    arrangement = track.build()
    starts = {event.start_step for event in arrangement.note_events if event.voice == "solo"}
    for required in [84, 88, 112, 116, 138, 144, 160, 184, 200, 216, 244, 252]:
        assert required in starts
