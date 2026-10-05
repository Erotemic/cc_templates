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

## Version 1 — extract reusable modules

```bash
python advanced/version1.py
```

Compare this with `../intermediate/version3.py`. The game behaves the same, but
reusable mechanics, Star Crystal content, and terminal I/O now live in separate
modules.

## Version 2 — second frontend

```bash
python advanced/version2.py
```

Textual calls the same `describe()`, `choices()`, and `apply()` API as the
console frontend. There are no worker threads, redirected stdout, monkey-
patched `input()`, or message queues just to connect the UI to the game.

## Version 3 — presentation only

```bash
python advanced/version3.py
```

ASCII art observes game state but does not control game rules.

## Version 4 — prove the reuse

```bash
python advanced/version4.py
```

Dust Vault is a different world with different rooms, items, quest conditions,
and combat content, while reusing the same engine and console UI.

To build another advanced game, copy a file in `adventure/worlds/`, not
`adventure/core.py`.
