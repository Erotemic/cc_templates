from __future__ import annotations

"""Assemble the student-authored modules into one validated game."""

from rpg_battle.api import Game, GamePresentation

from student_game import art, audio, battles, characters, effects, moves

GAME = Game(
    title="RPG Battle Classroom Project",
    palettes=art.PALETTES,
    sprites=art.SPRITES,
    effects=effects.EFFECTS,
    sounds=audio.SOUNDS,
    music=audio.MUSIC,
    moves=moves.MOVES,
    characters=characters.CHARACTERS,
    teams=battles.TEAMS,
    battles=battles.BATTLES,
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
    ),
    default_battle=battles.DEFAULT_BATTLE,
    default_battle_music=audio.bluesy_overhaul,
    victory_music=audio.victory_fanfare,
    defeat_music=audio.defeat_lament,
)

CONTENT = GAME.compile()
