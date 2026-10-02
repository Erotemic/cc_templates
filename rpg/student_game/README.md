# Build the game here

If you are a student, this directory is the main project.

A useful order is:

1. `characters.py` — change stats or swap a move.
2. `moves.py` — invent a move, then write a move function.
3. `art.py` — recolor or redraw a character with shapes.
4. `battles.py` — create a team, enemy lineup, or boss battle.
5. `effects.py` — change graph-shaped attack paths or write a math function.
6. `audio.py` — tune sound waves and swap generated music.
7. `catalog.py` — see how all of those objects become one complete game.

After an edit, run:

```bash
python main.py --check
```

The lists at the bottom of these files (`MOVES`, `CHARACTERS`, `TEAMS`, and so on)
are ordinary Python lists. If you create something new that should be available to
the game or preview tools, add the object to the appropriate list.

The `src/rpg_battle/` directory is not forbidden. It is the next layer down. Go there
when you want to understand or change how the engine itself works.
