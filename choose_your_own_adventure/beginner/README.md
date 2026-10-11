# Beginner adventures

These examples teach the basic recipe for a text adventure without custom
classes or a shared library.

## Version 1 — one loop

Run from the project root:

```bash
python beginner/version1.py
```

Read the whole file from top to bottom. It demonstrates variables, lists,
dictionaries, a `while` loop, `if`/`elif`, and numbered input.

Good first changes:

- rewrite a room description;
- add a dialogue choice;
- add another flag or item;
- change what is required to open the chest.

## Version 2 — functions

```bash
python beginner/version2.py
```

The story is unchanged. Compare it directly with `version1.py` and look for
repeated jobs that became named functions.

Good changes:

- write another display helper;
- move another repeated job into a function;
- add a parameter that changes a function's behavior.

Move to `../intermediate/` when functions feel comfortable and you are ready to
organize related data and runtime state.

## Build new features in one class session

The [beginner worksheets](../assignments/README.md) add an orchard, collectible
coins, a rope-gated bridge, contextual hints, or a travel journal to **a copy**
of these games. Each takes roughly 30–60 minutes. Start with:

```bash
python assignments/start.py B01
python assignments/work/B01.py
```

Run these commands from `choose_your_own_adventure/`. Check each feature with
the worksheet's playtest steps. No new packages or custom classes are needed.
