# Lesson 4 — Find and Repair Bugs

**Prerequisites:** Lessons 1–3.

Make each mistake one at a time, observe the feedback, then repair it.

## Syntax error

Temporarily remove the colon after an `if` statement. What part of Python's
message points to the problem?

## Runtime/API error

Temporarily write:

```python
return heal(10, target="usr")
```

Run `python main.py --check`. The RPG should reject the target instead of
silently healing somebody else.

## Logic error

Change the Power Strike comparison in a way that still runs but produces the
opposite behavior from the specification. The checker cannot know your intent;
use boundary scenarios to find the mistake.

## Independent task

Create a bug in one of your own functions, give only the behavior specification
to a partner, and ask them to diagnose it.

## Explain / transfer

Classify one example as a syntax error, one as a runtime/API error, and one as a
logic error. Explain why each needs a different debugging strategy.
