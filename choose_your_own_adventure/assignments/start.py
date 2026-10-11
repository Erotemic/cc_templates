"""Copy a fresh, self-contained game into a private assignment work file.

From choose_your_own_adventure/:
    python assignments/start.py B01
    python assignments/work/B01.py
"""

import argparse
import shutil

from catalog import ASSIGNMENTS, PROJECT, ROOT, work_file


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("assignment", choices=sorted(ASSIGNMENTS), help="worksheet ID")
    args = parser.parse_args(argv)

    source, worksheet = ASSIGNMENTS[args.assignment]
    destination = work_file(args.assignment)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shown = destination.relative_to(PROJECT) if destination.is_relative_to(PROJECT) else destination
    if destination.exists():
        parser.exit(1, f"Already exists, NOT overwritten: {shown}\n")

    # Exclusive creation means even simultaneous invocations cannot overwrite work.
    with destination.open("x", encoding="utf-8") as output:
        with (PROJECT / source).open(encoding="utf-8") as original:
            shutil.copyfileobj(original, output)

    print(f"Created {shown} from {source}")
    print(f"Read {ROOT.joinpath(worksheet).relative_to(PROJECT)}")
    print(f"Play:  python assignments/work/{args.assignment}.py")
    print(f"Check: python assignments/check.py {args.assignment}")


if __name__ == "__main__":
    main()
