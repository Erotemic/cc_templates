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
