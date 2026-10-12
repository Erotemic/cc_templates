from __future__ import annotations

"""Small command-line interface for the classroom AI/team-controller arena.

Every student controller executes in a time-limited subprocess. This protects
against accidental endless loops, but is NOT a sandbox for untrusted Python.
"""

import argparse
import csv
from contextlib import redirect_stdout
from dataclasses import asdict
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import traceback

from loguru import logger

ROOT = Path(__file__).resolve().parent.parent
PACKAGE = Path(__file__).resolve().parent
PREFABS = PACKAGE / "prefabs"
PLAYERS = Path(os.environ.get("RPG_ARENA_PLAYERS_DIR", str(PACKAGE / "players"))).resolve()
BUILTIN = "engine_heuristic"
IDENTIFIER = re.compile(r"[a-z][a-z0-9_]{0,39}\Z")
REQUIRED_SCORE = 0.80
# A new teaching example must not silently change the published challenge.
CHALLENGE_OPPONENTS = (
    "first_target", "weakest_first", "cautious", "rotating",
    "heavy_hitter", "crowd_control", BUILTIN,
)
RESULT_PREFIX = "ARENA_RESULT_JSON:"
ERROR_PREFIX = "ARENA_ERROR_JSON:"


def builtin_names() -> list[str]:
    return sorted(p.stem for p in PREFABS.glob("*.py") if p.stem != "__init__") + [BUILTIN]


def player_names() -> list[str]:
    return sorted(
        p.stem for p in PLAYERS.glob("*.py")
        if p.stem != "__init__" and IDENTIFIER.fullmatch(p.stem)
        and p.stem not in builtin_names()
    )


def source_for(name: str) -> Path:
    if not IDENTIFIER.fullmatch(name):
        raise ValueError("Controller names use lowercase letters, digits, and _ only")
    if name == BUILTIN:
        raise ValueError("The engine's heuristic AI has no student-editable file")
    # A prefab cannot be shadowed by a student file of the same name.
    if (PREFABS / f"{name}.py").is_file():
        return PREFABS / f"{name}.py"
    if (PLAYERS / f"{name}.py").is_file():
        return PLAYERS / f"{name}.py"
    raise ValueError(f"No controller named {name!r}; run 'python arena.py list'")


def controller_for(name: str):
    if name == BUILTIN:
        return None
    source = source_for(name)
    # Load by its exact file, so tests can use a temporary student directory,
    # and every worker sees newly saved student code rather than a cached import.
    spec = importlib.util.spec_from_file_location(f"arena_controller_{name}", source)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot load {source}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    fn = getattr(module, "choose_action", None)
    if not callable(fn):
        raise ValueError(f"{source.name} must define: def choose_action(turn):")
    return fn


def worker_pair(left: str, right: str, runs: int, seed: int, max_steps: int,
                *, include_log: bool = False) -> dict:
    from team_arena.engine import compare
    result = asdict(compare(left, controller_for(left), right, controller_for(right),
                            runs=runs, seed=seed, max_steps=max_steps))
    if not include_log:
        # No need to serialize an entire event tape for each tournament fixture.
        result["first_result"] = None
    return result


def _error_details(exc: Exception) -> dict[str, str | int | None]:
    """Extract the actionable student source location instead of a huge traceback."""
    current: BaseException = exc
    while current.__cause__ is not None:
        current = current.__cause__
    filename = None
    line = None
    code = None
    if isinstance(current, SyntaxError):
        filename, line, code = current.filename, current.lineno, current.text
    else:
        for frame in reversed(traceback.extract_tb(current.__traceback__)):
            file = Path(frame.filename).resolve()
            if file.parent in (PLAYERS, PREFABS):
                filename, line, code = frame.filename, frame.lineno, frame.line
                break
    if filename is not None:
        source = Path(filename)
        try:
            name = str(source.relative_to(ROOT))
        except ValueError:
            name = str(source)
        message = f"{name}, line {line}: {type(current).__name__}: {current}"
        if code:
            message += f"\n    {code.strip()}"
        message += "\nEdit that line, save the file, and rerun the match."
    else:
        message = f"{type(exc).__name__}: {exc}"
    return {"message": message}


def _worker_error(stdout: str, stderr: str) -> str:
    for line in reversed(stdout.splitlines()):
        if line.startswith(ERROR_PREFIX):
            try:
                return json.loads(line[len(ERROR_PREFIX):])["message"]
            except (ValueError, KeyError, TypeError):
                break
    return "\n".join(stderr.strip().splitlines()[-10:]) or "No diagnostic output"


def _tail(stream, limit: int = 80000) -> str:
    """Read only the last bytes, even when a student printed gigabytes."""
    stream.seek(0, 2)
    size = stream.tell()
    stream.seek(max(0, size - limit))
    return stream.read().decode("utf8", errors="replace")


def _run_worker(command: list[str], *, timeout: float, description: str) -> str:
    env = dict(os.environ, PYTHONHASHSEED="0", PYTHONDONTWRITEBYTECODE="1")
    # File-backed output avoids holding unbounded stdout/stderr in memory.
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        try:
            completed = subprocess.run(
                [sys.executable, str(ROOT / "arena.py"), *command],
                cwd=ROOT, env=env, stdout=stdout, stderr=stderr,
                timeout=timeout, check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                f"{description} exceeded {timeout:g} seconds. "
                "Look for a loop in choose_action(turn) that never returns."
            ) from exc
        output = _tail(stdout)
        errors = _tail(stderr)
    if completed.returncode:
        raise RuntimeError(f"{description} failed:\n{_worker_error(output, errors)}")
    return output


def bounded_pair(left: str, right: str, *, runs: int, seed: int,
                 max_steps: int, timeout: float, include_log: bool = False) -> dict:
    arguments = ["__worker", left, right, "--runs", str(runs), "--seed", str(seed),
                 "--max-steps", str(max_steps)]
    if include_log:
        arguments.append("--include-log")
    output = _run_worker(
        arguments,
        timeout=timeout, description=f"Match {left} vs {right}",
    )
    for line in reversed(output.splitlines()):
        if line.startswith(RESULT_PREFIX):
            try:
                return json.loads(line[len(RESULT_PREFIX):])
            except json.JSONDecodeError as exc:
                raise RuntimeError("Invalid match result from the worker") from exc
    raise RuntimeError("Match worker returned no result")


def bounded_record(left: str, right: str, *, seed: int, max_steps: int,
                   timeout: float) -> dict:
    with tempfile.TemporaryDirectory(prefix="rpg-arena-record-") as folder:
        destination = Path(folder) / "match.json"
        _run_worker(
            ["__record", left, right, "--seed", str(seed),
             "--max-steps", str(max_steps), "--output", str(destination)],
            timeout=timeout, description=f"Recording {left} vs {right}",
        )
        if not destination.is_file():
            raise RuntimeError("Recorder did not produce a battle recording")
        record = json.loads(destination.read_text(encoding="utf8"))
        from team_arena.recording import verify_replay
        verify_replay(record)
        return record


def _shared_options(parser: argparse.ArgumentParser, *, runs: int = 12) -> None:
    parser.add_argument("--runs", type=int, default=runs,
                        help="seed count; each seed is played with seats swapped")
    parser.add_argument("--seed", type=int, default=0, help="first random seed")
    parser.add_argument("--max-steps", type=int, default=300, help="steps per battle")
    parser.add_argument("--timeout", type=float, default=30, help="seconds per pairing")


def _check_limits(args: argparse.Namespace) -> None:
    if not 1 <= getattr(args, "runs", 1) <= 500:
        raise ValueError("--runs must be between 1 and 500")
    if not 1 <= args.max_steps <= 10000:
        raise ValueError("--max-steps must be between 1 and 10000")
    if not 1 <= args.timeout <= 1800:
        raise ValueError("--timeout must be between 1 and 1800 seconds")


def _pair(args: argparse.Namespace, left: str, right: str) -> dict:
    return bounded_pair(left, right, runs=args.runs, seed=args.seed,
                        max_steps=args.max_steps, timeout=args.timeout,
                        include_log=args.action == "battle" and args.log)


def _games(row: dict) -> int:
    return row["wins"] + row["losses"] + row["draws"] + row.get("unfinished", 0)


def _score(row: dict) -> float:
    games = _games(row)
    return (row["wins"] + 0.5 * row["draws"]) / games if games else 0.0


def _print_row(row: dict) -> None:
    print(f"  {row['left']:<19} vs {row['right']:<19} "
          f"W {row['wins']:>3}  L {row['losses']:>3}  "
          f"D {row['draws']:>3}  U {row.get('unfinished', 0):>3} "
          f"score {_score(row):>5.1%}", flush=True)


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="AI Team Arena: code a team controller, watch it fight, improve it."
    )
    sub = parser.add_subparsers(dest="action")
    sub.add_parser("list", help="list starter bots and student controllers")
    sub.add_parser("moves", help="explain fighters, moves and legal actions")

    new = sub.add_parser("new", help="copy a starter bot without overwriting work")
    new.add_argument("name", help="name for your new controller")
    new.add_argument("--from", dest="from_name", default="first_target")

    watch = sub.add_parser("watch", help="watch animated match, prints, and source labels")
    watch.add_argument("left", nargs="?", default="my_team")
    watch.add_argument("right", nargs="?", default="first_target")
    watch.add_argument("--seed", type=int, default=3)
    watch.add_argument("--speed", type=float, default=1.0)
    watch.add_argument("--max-steps", type=int, default=300)
    watch.add_argument("--timeout", type=float, default=20)

    battle = sub.add_parser("battle", help="quick non-graphical win/loss comparison")
    battle.add_argument("left", nargs="?", default="my_team")
    battle.add_argument("right", nargs="?", default="first_target")
    battle.add_argument("--log", action="store_true")
    _shared_options(battle)

    challenge = sub.add_parser("challenge", help="score against the fixed prefab roster")
    challenge.add_argument("name", nargs="?", default="my_team")
    _shared_options(challenge, runs=20)

    tournament = sub.add_parser("tournament", help="round robin across student controllers")
    tournament.add_argument("names", nargs="*", help="default: student files, not prefabs")
    tournament.add_argument("--include-prefabs", action="store_true",
                            help="also enter all built-in example controllers")
    tournament.add_argument("--csv", type=Path, help="save standings for the instructor")
    _shared_options(tournament, runs=2)

    for name in ("__worker", "__record"):
        worker = sub.add_parser(name, help=argparse.SUPPRESS)
        worker.add_argument("left")
        worker.add_argument("right")
        worker.add_argument("--seed", type=int, required=True)
        worker.add_argument("--max-steps", type=int, required=True)
        if name == "__worker":
            worker.add_argument("--runs", type=int, required=True)
            worker.add_argument("--include-log", action="store_true")
        else:
            worker.add_argument("--output", type=Path, required=True)
    return parser


def run(args: argparse.Namespace) -> int:
    if args.action is None:
        return run(make_parser().parse_args(["watch"]))
    if args.action in ("__worker", "__record"):
        logger.remove()
        try:
            if args.action == "__worker":
                from team_arena.recording import LimitedOutput
                with redirect_stdout(LimitedOutput()):
                    result = worker_pair(args.left, args.right, args.runs,
                                         args.seed, args.max_steps,
                                         include_log=args.include_log)
                print(RESULT_PREFIX + json.dumps(result))
            else:
                from team_arena.recording import record_match
                result = record_match(args.left, args.right, seed=args.seed,
                                      max_steps=args.max_steps)
                args.output.write_text(json.dumps(result), encoding="utf8")
        except Exception as exc:
            print(ERROR_PREFIX + json.dumps(_error_details(exc)), flush=True)
            return 2
        return 0

    if args.action == "list":
        print("Example controllers:", ", ".join(builtin_names()))
        print("Student controllers:", ", ".join(player_names()) or "(none yet)")
        print("Open team_arena/players/my_team.py, then run 'python arena.py'.")
        return 0
    if args.action == "moves":
        from team_arena.engine import friendly_description
        print(friendly_description())
        return 0
    if args.action == "new":
        name = args.name
        if not IDENTIFIER.fullmatch(name) or name == BUILTIN:
            raise ValueError("Choose a lowercase name such as 'clever_team'")
        if name in builtin_names() or (PLAYERS / f"{name}.py").exists():
            raise ValueError(f"{name!r} already exists; nothing was overwritten")
        source = source_for(args.from_name)
        PLAYERS.mkdir(parents=True, exist_ok=True)
        target = PLAYERS / f"{name}.py"
        # 'x' mode closes the race if two students try the same name.
        with target.open("x", encoding="utf8") as stream:
            stream.write(source.read_text(encoding="utf8"))
        print(f"Created {target}. Edit choose_action(turn), then:")
        print(f"  python arena.py watch {name} first_target")
        return 0

    _check_limits(args)
    if args.action == "watch":
        if not 0.25 <= args.speed <= 8.0:
            raise ValueError("--speed must be between 0.25 and 8")
        if importlib.util.find_spec("pygame") is None:
            raise RuntimeError(
                "Animated battles require pygame. From the rpg directory, run "
                "python -m pip install -e '.[classroom]'\n"
                "You can still use 'python arena.py battle' without graphics."
            )
        record = bounded_record(args.left, args.right, seed=args.seed,
                                max_steps=args.max_steps, timeout=args.timeout)
        print(f"Watch: {args.left} vs {args.right} (seed {args.seed})", flush=True)
        from team_arena.viewer import watch
        watch(record, speed=args.speed,
              reload_recording=lambda: bounded_record(
                  args.left, args.right, seed=args.seed,
                  max_steps=args.max_steps, timeout=args.timeout))
        return 0
    if args.action == "battle":
        row = _pair(args, args.left, args.right)
        print(f"{2 * args.runs} battles, with swapped team positions:")
        _print_row(row)
        if args.log:
            print("\nFirst battle:")
            for event in row["first_result"]["events"]:
                if event.get("type") in {
                    "turn_start", "move", "damage", "heal", "defend", "ko", "battle_end"
                }:
                    print("  " + event.get("text", event["type"]))
        return 0
    if args.action == "challenge":
        if args.name not in player_names():
            raise ValueError("The challenge needs a student controller under team_arena/players/")
        rows = [_pair(args, args.name, name) for name in CHALLENGE_OPPONENTS]
        print(f"{args.name}: {args.runs} seeds, both seats, against each prefab")
        for row in rows:
            _print_row(row)
        passed = all(_score(row) >= REQUIRED_SCORE and row["unfinished"] == 0
                     for row in rows)
        print(f"\nGoal: {REQUIRED_SCORE:.0%} vs EACH opponent, no unfinished matches.")
        print("CHALLENGE PASSED" if passed else "Not yet: revise your controller and try again.")
        return 0 if passed else 1
    if args.action == "tournament":
        entrants = (args.names or player_names())[:]
        if args.include_prefabs:
            entrants += [name for name in builtin_names() if name not in entrants]
        if not args.names and len(entrants) < 2 and not args.include_prefabs:
            entrants.append("first_target")
        if len(set(entrants)) != len(entrants):
            raise ValueError("Each controller can enter only once")
        if len(entrants) < 2:
            raise ValueError("Enter at least two controllers")
        for name in entrants:
            if name != BUILTIN:
                source_for(name)
        fixture_count = len(entrants) * (len(entrants) - 1) // 2
        print(f"Tournament: {len(entrants)} controllers, {fixture_count} pairings, "
              f"{2 * args.runs * fixture_count} games", flush=True)
        scores = {name: {"name": name, "wins": 0, "losses": 0,
                         "draws": 0, "unfinished": 0, "score": 0.0, "games": 0}
                  for name in entrants}
        match_no = 0
        for index, left in enumerate(entrants):
            for right in entrants[index + 1:]:
                match_no += 1
                print(f"Fixture {match_no}/{fixture_count}:", end="", flush=True)
                row = _pair(args, left, right)
                _print_row(row)
                for name, wins, losses in (
                    (left, row["wins"], row["losses"]),
                    (right, row["losses"], row["wins"]),
                ):
                    data = scores[name]
                    data["wins"] += wins
                    data["losses"] += losses
                    data["draws"] += row["draws"]
                    data["unfinished"] += row["unfinished"]
        standings = []
        for item in scores.values():
            item["games"] = _games(item)
            item["score"] = _score(item)
            standings.append(item)
        standings.sort(key=lambda item: (-item["score"], -item["wins"], item["name"]))
        print("\nSTANDINGS (U = unfinished; no points awarded for unfinished games):")
        for rank, item in enumerate(standings, start=1):
            print(f"{rank:>2}. {item['name']:<19} {item['score']:>6.1%} "
                  f"({item['wins']}W {item['losses']}L {item['draws']}D "
                  f"{item['unfinished']}U)")
        if args.csv:
            destination = args.csv.resolve()
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open("w", newline="", encoding="utf8") as stream:
                writer = csv.DictWriter(stream, fieldnames=[
                    "name", "wins", "losses", "draws", "unfinished", "games", "score",
                ])
                writer.writeheader()
                writer.writerows(standings)
            print(f"Saved {destination}")
        return 0
    raise AssertionError(f"Unknown action {args.action}")


def main() -> None:
    parser = make_parser()
    args = parser.parse_args()
    try:
        code = run(args)
    except (ValueError, RuntimeError, OSError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")
    raise SystemExit(code)
