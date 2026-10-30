"""Check the math tasks independently of Manim: python check.py 1 (or all).

The starter intentionally fails these checks until each student task is done.
This is a teaching tool, not part of the normal unit test suite.
"""

import math
import sys

import student


TOLERANCE = 1e-5


def near(a, b):
    try:
        return math.isfinite(a) and abs(a - b) <= TOLERANCE
    except (TypeError, ValueError, OverflowError):
        return False


def near_point(got, expected):
    try:
        x, y = got
        return near(x, expected[0]) and near(y, expected[1])
    except (TypeError, ValueError):
        return False


def check_1():
    return (near(student.wave_height(0), 0)
            and near(student.wave_height(math.pi / 2), 1)
            and near(student.wave_height(-math.pi / 2), -1))


def check_2():
    return (near_point(student.circle_xy(0), (1, 0))
            and near_point(student.circle_xy(math.pi / 2), (0, 1))
            and near_point(student.circle_xy(math.pi), (-1, 0)))


def check_3():
    f = lambda x: x * x + 0.5
    return (near(student.secant_slope(f, 0.5, 0.5), 1.5)
            and near(student.secant_slope(f, 0.5, 0.1), 1.1)
            and near(student.secant_slope(f, -1.0, 0.5), -1.5))


def check_4():
    f = lambda x: 0.5 + 0.2 * x * x
    return (near(student.left_sum(f, 0, 2, 4), 1.35)
            and near(student.left_sum(lambda x: 2, -3, 3, 6), 12)
            and near(student.left_sum(lambda x: x, 0, 2, 4), 1.5))


def check_5():
    m = ((0, -1), (1, 0))
    return (near_point(student.transform_xy(2, 1, m), (-1, 2))
            and near_point(student.transform_xy(1, 0, m), (0, 1))
            and near_point(student.transform_xy(1, 2, ((2, 0), (0, 3))), (2, 6)))


CHECKS = {1: check_1, 2: check_2, 3: check_3, 4: check_4, 5: check_5}
NAMES = {
    1: "function graph",
    2: "unit circle",
    3: "secant slope",
    4: "left Riemann sum",
    5: "matrix transform",
}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1 or argv[0] not in {'1', '2', '3', '4', '5', 'all'}:
        print('Usage: python check.py {1|2|3|4|5|all}')
        return 2

    requested = CHECKS if argv[0] == 'all' else {int(argv[0]): CHECKS[int(argv[0])]}
    unfinished = False
    for index, check in requested.items():
        try:
            passed = check()
        except Exception as exc:
            print(f"{index}. {NAMES[index]}: ERROR: {type(exc).__name__}: {exc}")
            unfinished = True
            continue
        if passed:
            print(f"{index}. {NAMES[index]}: PASS")
        else:
            print(f"{index}. {NAMES[index]}: NOT YET - read the mission in student.py")
            unfinished = True
    return int(unfinished)


if __name__ == '__main__':
    raise SystemExit(main())
