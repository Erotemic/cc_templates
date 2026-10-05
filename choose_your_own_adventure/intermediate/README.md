# Intermediate adventures

These versions organize the program without introducing a reusable package.
Every example is still one self-contained Python file that students can copy
and modify directly.

## Version 1 — data-driven game

```bash
python intermediate/version1.py
```

New ideas:

- a `Player` dataclass;
- room data separated from action logic;
- one small function per action;
- functions stored in a dictionary.

The story is still the same tiny treasure adventure from the beginner folder.

## Version 2 — game object

```bash
python intermediate/version2.py
```

New ideas:

- `Room` and `Choice` objects;
- one `Game` object owns changing state;
- `Game.describe()`, `Game.choices()`, and `Game.apply()`;
- the console UI is separate from game rules.

A useful exercise is to write code that wins the game without calling
`input()`. That demonstrates why the boundary is useful.

## Version 3 — larger single-file game

```bash
python intermediate/version3.py
```

This is the Star Crystal game with inventory, quest flags, combat, conditional
choices, and a locked destination. The architecture stays deliberately direct.

This is a good starting point for a substantial student project that should
remain understandable in one file.

Move to `../advanced/` when the single-file version makes sense and the project
has become large enough that splitting reusable pieces into modules would
actually help.
