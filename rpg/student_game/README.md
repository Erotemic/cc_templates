# Build the game here

If you are a student, **start with `workshop.py`**.

It is deliberately small, but it is not a fake tutorial version of the RPG. Its
move, character, enemy strategy, and practice battle are registered in the same
catalog and run through the same engine as every other character and boss.

Try this first:

```bash
python main.py --check
python main.py --encounter workshop
```

Then use the deterministic move laboratory:

```bash
python lab.py move workshop_power_strike --user-hp 50
python lab.py move workshop_power_strike --user-hp 10
```

Those two commands run the same Python function with different input values. The
lab prints the function, the read-only battle facts it received, the command it
returned, and the real engine events that followed.

## When you want more room

The rest of this directory is the complete shipped game and a library for your
workshop code:

1. `workshop.py` — **start here**: conditionals, loops, a character, an AI strategy, and a practice battle.
2. `characters.py` — the complete character roster.
3. `moves.py` — the complete move library and more custom move examples.
4. `art.py` — procedural sprites and palettes.
5. `battles.py` — larger teams, encounters, and bosses.
6. `effects.py` — graph-shaped attacks and mathematical path functions.
7. `audio.py` — synthesized sound effects and generated music.
8. `catalog.py` — where the workshop and full game are assembled into one `Game`.

The lists at the bottom of the full-game files (`MOVES`, `CHARACTERS`, `TEAMS`,
and so on) are ordinary Python lists. `catalog.py` combines those lists with the
small lists from `workshop.py`.

## Three feedback loops

Use whichever loop matches what you are learning:

```bash
# Does my content fit together?
python main.py --check

# What exactly did one move function do?
python lab.py move workshop_chain_lightning \
    --target spirit --target guardian --target-status 2:burn

# What does it feel like in the game?
python main.py --encounter workshop --teach
```

`--teach` prints readable execution facts when a custom move function or custom
AI strategy runs.

For balance experiments, run battles without pygame:

```bash
python simulate.py --encounter workshop --runs 100 --seed 0
```

Changing a number and rerunning the same seeds gives you an experiment rather
than an impression.

The `src/rpg_battle/` directory is not forbidden. It is the next layer down. Go
there when you want to understand or change how the engine itself works.
