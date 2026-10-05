# Advanced adventures

This folder introduces a shared Python package because there is now something
real to reuse. The earlier levels deliberately avoid this machinery.

```text
advanced/
    version1.py
    version2.py
    version3.py
    version4.py

    adventure/
        core.py
        art.py
        worlds/
        ui/
```

Modularization should **not** make ordinary world-building harder. `Room` still
owns exits and `RoomChoice` values. A student can add a new room and simple
choices in a world file without changing `adventure/core.py`.

## Version 1 — extract reusable modules

```bash
python advanced/version1.py
```

Compare this with `../intermediate/version3.py`. Reusable mechanics, Star
Crystal content, and terminal I/O now live in separate modules.

## Version 2 — second frontend

```bash
python advanced/version2.py
```

Textual calls the same `describe()`, `choices()`, and `apply()` API as the
console frontend. There are no worker threads, redirected stdout, monkey-patched
`input()`, or queues just to connect the UI to the game.

## Version 3 — presentation only

```bash
python advanced/version3.py
```

ASCII art observes game state but does not control game rules.

## Version 4 — prove the reuse

```bash
python advanced/version4.py
```

Dust Vault is a different teaching-sized world while reusing the same engine
and console UI.

To build another advanced game, copy a file in `adventure/worlds/`, not
`adventure/core.py`. Use `RoomChoice` for simple story interactions; add
world-specific Python logic only when the story needs behavior beyond a simple
result.

When students want the complete original worlds rather than teaching-sized
examples, continue to `../capstone/`.
