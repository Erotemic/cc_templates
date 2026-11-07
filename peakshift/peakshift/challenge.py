"""Independent challenges: less scaffolding, more engineering decisions.

Guided missions in student.py have a function waiting for you. These do not.
Find the relevant code, change it, test it, and explain your design choices.
"""

CHALLENGES = (
    ("1. Different dash rules", "Find the dash direction and duration logic. Give the player two dashes, or make a dash bounce off walls. Explain how charges are refilled."),
    ("2. Drop-through ledges", "The = ledges already allow jumping upward through them. Add Down + Jump to deliberately drop through from above. Test both directions."),
    ("3. A real switch", "Add a switch tile that opens a door elsewhere in the room. Where should its pressed/unpressed state live?"),
    ("4. Replay ghost", "Record positions during a run, then render a translucent ghost following the last attempt. What happens after a room transition?"),
    ("5. Route choices", "Connect rooms as a branching graph instead of a simple line. How does a door choose which room to open?"),
    ("6. Your own mechanic", "Design a mechanic using at least one variable, one condition, and one function. Teach another student how to play it."),
    ("7. Collision detective", "Why does the engine handle X and Y separately? What bug appears if diagonal movement is resolved all at once?"),
    ("8. Frame-rate detective", "Why do positions change by velocity * seconds? Try running headless with step sizes 1/30, 1/60, and 1/120."),
)


def main():
    for title, description in CHALLENGES:
        print(f"{title}\n  {description}\n")


if __name__ == "__main__":
    main()
