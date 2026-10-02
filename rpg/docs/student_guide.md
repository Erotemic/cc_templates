# Student Guide: Build Your Own Battle Game

The goal of this project is not to understand the entire engine before you are allowed
to make something. Start in `student_game/`, make visible changes, and move deeper as your
questions become more ambitious.

## Level 1 — Change something and see it

Pick one:

- change a character's `hp`, `attack`, `magic`, or `speed` in `student_game/characters.py`;
- change a palette color in `student_game/art.py`;
- swap the order of two characters in a team in `student_game/battles.py`;
- change a sound's `frequency` or `waveform` in `student_game/audio.py`.

Before running the program, predict what will change.

Then run:

```bash
python main.py --check
python main.py
```

## Level 2 — Compose existing objects

Python variables can refer to other objects. The game uses that directly.

Try:

- give the Knight `moves.sine_wave`;
- put `characters.mage` on `default_player`;
- make a battle use `audio.d_minor_jam`;
- give a move a different `effects.*` animation.

Notice that you are not coordinating string IDs by hand. The object you name is the
object the game uses.

## Level 3 — Make a new move

Copy a short move in `student_game/moves.py` and change it:

```python
meteor = Move(
    "Meteor",
    kind="magical",
    power=16,
    animation=effects.ember,
    sound=audio.ember,
    effects=[status("burn", turns=3, chance=0.50)],
)
```

Add `meteor` to the `MOVES` list, then give it to a character.

Things to experiment with:

- `kind="physical"` versus `kind="magical"`;
- `target="all_enemies"`;
- `accuracy=0.75`;
- buffs with `stat_change("speed", 2)`;
- status effects with different probabilities and durations.

## Level 4 — Make a new character

Characters are compositions of things you already understand:

```python
comet_witch = Character(
    "Comet Witch",
    role="mage",
    hp=45,
    attack=4,
    defense=5,
    magic=13,
    speed=8,
    sprite=art.moon_mage,
    moves=[moves.meteor, moves.mist_veil, moves.strike],
)
```

Add the character to `CHARACTERS`, then add it to a team in `student_game/battles.py`.

At first it is fine to reuse another character's sprite. Drawing a new one can be a
separate project.

## Level 5 — Program a move with `if`

`student_game/moves.py` contains `desperate_strike_logic`, an example where an ordinary Python
function changes the rule:

```python
def desperate_strike_logic(ctx):
    if ctx.user.hp_ratio < 0.5:
        return damage(18)
    return damage(8)
```

`ctx.user` is a read-only view of the character using the move. `ctx.target` is the
first target. Useful facts include:

- `name`
- `hp`
- `max_hp`
- `hp_ratio`
- `attack`, `defense`, `magic`, `speed`
- `statuses`

A custom move returns commands such as:

```python
damage(12)
heal(10, target="user")
add_status("burn", turns=2)
change_stat("speed", 2, target="user")
```

It can return a list when several things should happen.

Challenges:

- do extra damage when the target is below half HP;
- heal the user after dealing damage;
- make a move that buffs itself on even-numbered rounds;
- check `"burn" in ctx.target.statuses` and react differently.

The function chooses the behavior. The engine still handles battle state, messages,
knockouts, replacement characters, and presentation.

## Level 6 — Draw a character from geometry

`student_game/art.py` builds sprites from primitives:

```python
my_sprite = Sprite("My Sprite", my_palette)
my_sprite.circle((0, 0), 40, fill="body")
my_sprite.polygon([(-25, -20), (0, -60), (25, -20)], fill="accent")
my_sprite.face(-8)
```

Preview just the character instead of replaying a battle:

```bash
python render_character.py knight
```

Try building a sprite using only circles, then only polygons. Think about coordinates,
symmetry, and how changing one number moves a shape.

## Level 7 — Program a mathematical spell path

Preset path effects include sine, square, staircase, and zigzag/triangle shapes.
`student_game/effects.py` also contains `classroom_wave`, which is a normal Python function:

```python
def classroom_wave(x):
    envelope = 1.0 - 0.45 * x
    return math.sin(x * math.tau * 3) * 30 * envelope
```

The renderer samples `x` from 0 to 1 and uses the returned value as the vertical
offset of the effect.

Ideas:

- change the frequency;
- multiply two waves;
- add harmonics;
- make a parabola;
- damp the wave toward zero;
- create your own piecewise function with `if`.

Preview effects with:

```bash
python render_effect.py sine_wave
python render_effect.py classroom_wave
```

## Level 8 — Design a battle

A `Team` holds characters. A `Battle` combines two teams, the number of active
characters, and music.

Build something with a design goal rather than random stats:

- a fast glass-cannon team;
- a defensive attrition team;
- a single boss against three heroes;
- two teams built around status effects;
- a boss with a custom conditional move.

Playtest it and adjust one variable at a time.

## Level 9 — Explore the engine

When you want to know *why* something happens, follow it into `src/rpg_battle/`.
Good paths are:

```text
student_game/moves.py
  -> rpg_battle.api.Move
  -> core.models.MoveSpec
  -> core.rules.resolve_action
  -> battle/battle_scene.py
```

or:

```text
student_game/art.py
  -> rpg_battle.api.Sprite
  -> GameContent.sprites
  -> render/sprite_actor.py
  -> render/primitives.py
```

At this point the engine is no longer mysterious library code: it is the implementation
of the objects and rules you have already been using.

## Debugging

First run:

```bash
python main.py --check
```

For more battle-flow logging:

```bash
RPG_BATTLE_LOG_LEVEL=DEBUG python main.py
```

A syntax error or `NameError` is a normal Python programming error and will still show
a traceback. Content-relationship mistakes are collected by the game validator so you
can fix several at once.
