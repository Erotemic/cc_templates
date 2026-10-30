#!/usr/bin/env python3
"""Play without installing this project: ``python main.py``."""

try:
    from platformer.game import main
except ModuleNotFoundError as error:
    if error.name == "pygame":
        raise SystemExit(
            "Missing pygame. Ask your teacher, or run: pip install pygame-ce"
        ) from error
    raise


if __name__ == "__main__":
    raise SystemExit(main())
