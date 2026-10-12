from __future__ import annotations

"""Student commands, tournament reporting, and bounded subprocess execution.

Every comparison runs in a separate process so an accidental infinite loop in
student Python can be terminated. This is NOT a security sandbox: only execute
code you trust or have reviewed.
"""

import argparse
import csv
from dataclasses import asdict
from importlib import import_module
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

from loguru import logger

ROOT = Path(__file__).resolve().parent.parent
PREFABS = Path(__file__).resolve().parent / "prefabs"
PLAYERS = Path(__file__).resolve().parent / "players"
BUILTIN = "engine_heuristic"
IDENTIFIER = re.compile(r"[a-z][a-z0-9_]{0,39}\Z")
REQUIRED_SCORE = 0.80


def builtin_names() -> list[str]:
    return sorted(path.stem for path in PREFABS.glob("*.py") if path.stem != "__init__") + [BUILTIN]


def player_names() -> list[str]:
    return sorted(
        path.stem for path in PLAYERS.glob("*.py")
        if path.stem != "__init__" and IDENTIFIER.fullmatch(path.stem)
    )


def source_for(name: str) -> Path:
    if not IDENTIFIER.fullmatch(name):
        raise ValueError("controller names must contain only lowercase letters, digits, and _")
    if name == BUILTIN:
        raise ValueError("the engine's controller has no editable source file")
    for folder in (PLAYERS, PREFABS):
        candidate = folder / f"{name}.py"
        if candidate.is_file():
            return candidate
    raise ValueError(f"Unknown controller {name!r}; run 'python arena.py list'")


def controller_for(name: str):
    if name == BUILTIN:
        return None
    source = source_for(name)
    package = "players" if source.parent == PLAYERS else "prefabs"
    module = import_module(f"team_arena.{package}.{name}")
    fn = getattr(module, "choose_action", None)
    if not callable(fn):
        raise ValueError(f"{source.relative_to(ROOT)} needs a choose_action(turn) function")
    return fn


def worker_pair(left: str, right: str, runs: int, seed: int, max_steps: int) -> dict:
    from team_arena.engine import compare

    result = compare(left, controller_for(left), right, controller_for(right),
                     runs=runs, seed=seed, max_steps=max_steps)
    return asdict(result)


def bounded_pair(
    left: str, right: str, *, runs: int, seed: int,
    max_steps: int, timeout: float,
) -> dict:
    """Stop runaway student loops and return a useful error instead of hanging."""
    command = [
        sys.executable, str(ROOT / "arena.py"), "__worker",
        left, right, "--runs", str(runs), "--seed", str(seed),
        "--max-steps", str(max_steps),
    ]
    env = dict(os.environ, PYTHONHASHSEED="0", PYTHONDONTWRITEBYTECODE="1")
    try:
        completed = subprocess.run(
            command, cwd=ROOT, env=env, capture_output=True, text=True,
            timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            f"Match {left} vs {right} exceeded {timeout:g} seconds. "
            "Check for a controller loop that never returns."
        ) from exc
    if completed.returncode:
        message = completed.stderr.strip().splitlines()
        tail = "\n".join(message[-12:])
        raise RuntimeError(
            f"Match {left} vs {right} failed:\n{tail or '(no diagnostic output)'}"
        )
    try:
        return json.loads(next(
            line[len("ARENA_RESULT_JSON:"):] for line in reversed(completed.stdout.splitlines())
            if line.startswith("ARENA_RESULT_JSON:")
        ))
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Match {left} vs {right} produced unexpected output: "
            f"{completed.stdout[:300]!r}"
        ) from exc


def _shared_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--runs", type=int, default=12, help="seeds per side (two games per seed)")
    parser.add_argument("--seed", type=int, default=0, help="first random seed")
    parser.add_argument("--max-steps", type=int, default=300, help="turn-engine step limit per game")
    parser.add_argument("--timeout", type=float, default=30, help="seconds allowed per paired fixture")


def _check_limits(args: argparse.Namespace) -> None:
    if not 1 <= args.runs <= 500:
        raise ValueError("--runs must be from 1 to 500")
    if not 1 <= args.max_steps <= 10000:
        raise ValueError("--max-steps must be from 1 to 10000")
    if not 1 <= args.timeout <= 1800:
        raise ValueError("--timeout must be from 1 to 1800 seconds")


def _pair(args: argparse.Namespace, left: str, right: str, *, runs: int | None = None) -> dict:
    return bounded_pair(left, right, runs=runs if runs is not None else args.runs,
                        seed=args.seed, max_steps=args.max_steps, timeout=args.timeout)


def _print_row(row: dict) -> None:
    games = row["wins"] + row["losses"] + row["draws"]
    score = (row["wins"] + row["draws"] / 2) / games
    print(
        f"  {row['left']:<19} vs {row['right']:<19} "
        f"W {row['wins']:>3}  L {row['losses']:>3}  D {row['draws']:>3} "
        f"score {score:>5.1%}"
    )


def _score(row: dict) -> float:
    count = row["wins"] + row["losses"] + row["draws"]
    return (row["wins"] + 0.5 * row["draws"]) / count


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Algorithm Arena: create, compete, and compare RPG team controllers."
    )
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("list", help="show prebuilt and student controllers")
    sub.add_parser("moves", help="inspect the two fighters and their actions")

    start = sub.add_parser("new", help="copy an example into your personal controller file")
    start.add_argument("name", help="new lowercase controller name, e.g. smart_team")
    start.add_argument("--from", dest="from_name", default="first_target",
                       help="example/controller to copy, default first_target")

    battle = sub.add_parser("battle", help="play a reproducible headless battle on both sides")
    battle.add_argument("left")
    battle.add_argument("right")
    battle.add_argument("--log", action="store_true", help="show an event-by-event sample game")
    _shared_options(battle)

    challenge = sub.add_parser("challenge", help="test one student AI against every prebuilt bot")
    challenge.add_argument("name")
    _shared_options(challenge)

    tournament = sub.add_parser("tournament", help="round-robin between named controllers")
    tournament.add_argument("names", nargs="*", help="default: all prefabs and all student files")
    tournament.add_argument("--csv", type=Path, help="save standings to a CSV file")
    _shared_options(tournament)

    worker = sub.add_parser("__worker", help=argparse.SUPPRESS)
    worker.add_argument("left")
    worker.add_argument("right")
    worker.add_argument("--runs", type=int, required=True)
    worker.add_argument("--seed", type=int, required=True)
    worker.add_argument("--max-steps", type=int, required=True)
    return parser


def run(args: argparse.Namespace) -> int:
    if args.action == "__worker":
        logger.remove()
        print("ARENA_RESULT_JSON:" + json.dumps(worker_pair(
            args.left, args.right, args.runs, args.seed, args.max_steps)))
        return 0

    if args.action == "list":
        print("Example controllers:")
        for name in builtin_names():
            print("  " + name)
        print("\nStudent controllers:")
        for name in player_names():
            print("  " + name)
        print("\nRun 'python arena.py moves' for the arena rules.")
        return 0

    if args.action == "moves":
        from team_arena.engine import friendly_description
        print(friendly_description())
        return 0

    if args.action == "new":
        name = args.name
        if not IDENTIFIER.fullmatch(name) or name == BUILTIN:
            raise ValueError("use a lowercase Python name such as 'clever_team'")
        target = PLAYERS / f"{name}.py"
        if name in builtin_names() or target.exists():
            raise ValueError(f"{name!r} already exists; choose a different name")
        shutil.copyfile(source_for(args.from_name), target)
        print(f"Created {target.relative_to(ROOT)}; edit choose_action(turn).")
        print(f"Try: python arena.py battle {name} first_target --log")
        return 0

    _check_limits(args)

    if args.action == "battle":
        row = _pair(args, args.left, args.right)
        print(f"{2 * args.runs} battles (each seed plays with seats swapped):")
        _print_row(row)
        if args.log:
            print("\nSample battle (first match, left controller on team 0):")
            for event in row["first_result"]["events"]:
                if event.get("type") in {"turn_start", "move", "damage", "heal", "defend", "ko", "battle_end"}:
                    print("  " + event.get("text", event["type"]))
        return 0

    if args.action == "challenge":
        if args.name not in player_names():
            raise ValueError("challenge expects a student file in team_arena/players/")
        rows = [_pair(args, args.name, name) for name in builtin_names()]
        print(f"{args.name}: {args.runs} seeds, both sides, against each prefab")
        for row in rows:
            _print_row(row)
        passed = all(_score(row) >= REQUIRED_SCORE for row in rows)
        print(f"\nGoal: score at least {REQUIRED_SCORE:.0%} against EACH prefab (draws count half).")
        print("CHALLENGE PASSED" if passed else "Not yet: revise your controller and try again.")
        return 0 if passed else 1

    if args.action == "tournament":
        entrants = args.names or [*builtin_names(), *player_names()]
        if len(set(entrants)) != len(entrants):
            raise ValueError("each controller can enter only once")
        if not 2 <= len(entrants) <= 30:
            raise ValueError("choose between 2 and 30 controllers")
        for name in entrants:
            if name != BUILTIN:
                source_for(name)
        scores = {name: {"name": name, "wins": 0, "losses": 0, "draws": 0,
                         "score": 0.0, "games": 0} for name in entrants}
        for index, left in enumerate(entrants):
            for right in entrants[index + 1:]:
                row = _pair(args, left, right)
                _print_row(row)
                for name, w, l in (
                    (left, row["wins"], row["losses"]),
                    (right, row["losses"], row["wins"]),
                ):
                    scores[name]["wins"] += w
                    scores[name]["losses"] += l
                    scores[name]["draws"] += row["draws"]
        standings = []
        for data in scores.values():
            data["games"] = data["wins"] + data["losses"] + data["draws"]
            data["score"] = round((data["wins"] + data["draws"] / 2) / data["games"], 4)
            standings.append(data)
        standings.sort(key=lambda data: (-data["score"], -data["wins"], data["name"]))
        print("\nSTANDINGS (score = wins + half of draws):")
        for rank, data in enumerate(standings, start=1):
            print(f"{rank:>2}. {data['name']:<19} {data['score']:>6.1%} "
                  f"({data['wins']}W {data['losses']}L {data['draws']}D)")
        if args.csv is not None:
            destination = args.csv.resolve()
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open("w", newline="", encoding="utf8") as file:
                writer = csv.DictWriter(file, fieldnames=["name", "wins", "losses", "draws", "games", "score"])
                writer.writeheader()
                writer.writerows(standings)
            print(f"Saved {destination}")
        return 0

    raise AssertionError(f"unexpected command {args.action}")


def main() -> None:
    parser = make_parser()
    args = parser.parse_args()
    try:
        raise_code = run(args)
    except (ValueError, RuntimeError, OSError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")
    raise SystemExit(raise_code)
