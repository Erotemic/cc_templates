from __future__ import annotations

"""Assemble the student-authored modules into one validated game."""

from rpg_battle.api import (
    BobMotion,
    CharacterMotionSet,
    FallMotion,
    Game,
    GamePresentation,
    LungeMotion,
    ShakeMotion,
)

from student_game import (
    art,
    audio,
    battles,
    characters,
    effects,
    moves,
    workshop,
    workshop_assets,
    workshop_battles,
)



# A static frame still feels alive because these motions transform the whole
# drawing. Students can tune these numbers before they ever draw a second frame.
DEFAULT_CHARACTER_MOTION = CharacterMotionSet(
    idle=BobMotion(height=3, period=2.85),
    attack=LungeMotion(distance=18, duration=0.25),
    hurt=ShakeMotion(distance=6, duration=0.30, cycles=2),
    faint=FallMotion(
        distance=110,
        duration=0.90,
        rotation=180,
        rotation_duration=0.24,
        show_x_eyes=True,
    ),
)

GAME = Game(
    title="RPG Battle Classroom Project",
    palettes=[*art.PALETTES, *workshop_assets.PALETTES],
    art_assets=[*art.ART_ASSETS, *workshop_assets.ART_ASSETS],
    effects=[*effects.EFFECTS, *workshop_assets.EFFECTS],
    sounds=[*audio.SOUNDS, *workshop_assets.SOUNDS],
    music=[*audio.MUSIC, *workshop_assets.MUSIC],
    moves=[*moves.MOVES, *workshop.MOVES],
    characters=[*characters.CHARACTERS, *workshop.CHARACTERS],
    teams=[*battles.TEAMS, *workshop_battles.TEAMS],
    battles=[*battles.BATTLES, *workshop_battles.BATTLES],
    presentation=GamePresentation(
        basic_attack=moves.strike,
        menu_move_sound=audio.menu_move,
        menu_confirm_sound=audio.menu_confirm,
        menu_back_sound=audio.menu_back,
        damage_sound=audio.damage_tick,
        heal_sound=audio.heal_chime,
        ko_sound=audio.ko,
        switch_sound=audio.switch,
        defend_sound=audio.defend,
        heal_effect=effects.heal_pulse,
        character_motion=DEFAULT_CHARACTER_MOTION,
    ),
    default_battle=battles.DEFAULT_BATTLE,
    default_battle_music=audio.bluesy_overhaul,
    victory_music=audio.victory_fanfare,
    defeat_music=audio.defeat_lament,
)

CONTENT = GAME.compile()
