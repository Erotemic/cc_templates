# Classroom Setup

The goal is to get from a new checkout to a validated RPG with as little setup
knowledge as possible.

## One-time setup

From the `rpg` directory, create an isolated environment:

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[classroom]"
python main.py --check
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[classroom]"
python main.py --check
```

A successful check ends with `Game content looks good` and may also print
non-fatal teaching notes explaining fields that custom Python actions override.

`main.py --check` intentionally does not require a graphical display. On the
school machines, also do this once after setup to verify that the installed
pygame/SDL_image build can decode the bundled SVG artwork:

```bash
python render_character.py moon_mage --no-show
```

That command uses the same native SVG path as the game. It does not require
Cairo.

## Daily start

Activate `.venv`, open `student_game/workshop.py`, then use one of the VS Code
Tasks or these short commands:

```bash
python main.py --check
python lab.py scenario threshold_25
python main.py --scenario threshold_25 --teach
```

For the included VS Code tasks, open the **`rpg` folder** as your workspace,
install the Python extension, and use **Python: Select Interpreter** to choose
your `.venv`. Use **Terminal → Run Task** to select Check, Lab, Play, Preview,
or Simulate. The tasks use that selected interpreter.

## Teacher reproducibility

Before a course or workshop, establish one known-good Python version and
machine image, run the complete test suite, and freeze that environment:

```bash
python -m pip freeze --local --exclude rpg-battle > classroom-lock.txt
```

Keep that lock file with the course deployment materials for the term. Rebuild
and retest it when the Python version or operating-system image changes rather
than silently upgrading packages during a class.

The project itself is excluded because an editable install can record the
teacher's local checkout path. To restore the dependencies in a fresh
environment on the same machine image, run `python -m pip install -r
classroom-lock.txt`, then `python -m pip install -e ".[classroom]"` from the
new checkout's `rpg` directory.

## Full tests

```bash
python -m pytest -q
```

The graphical tests require pygame and a usable SDL setup. On headless CI,
configure SDL's dummy video/audio drivers or run the pure engine tests
separately.
