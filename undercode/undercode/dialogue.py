"""Story conversation records and page navigation, independent of both engines.

Definitions are records that authors write. Conversation is the changing state
of reading one definition. Keeping these separate lets two people reuse writing
without sharing the same selected page. No window or audio device opens here.
"""

from dataclasses import dataclass, field
from typing import Callable
import textwrap


@dataclass(kw_only=True)
class Choice:
    """A reply: commit set_flags on selection, then display text."""

    label: str
    text: str | list[str]
    set_flags: list[str] = field(default_factory=list)
    required_flag: str | None = None


@dataclass(kw_only=True)
class Branch:
    """Use this replacement dialogue when its flag and optional Python condition pass."""

    text: str | list[str]
    required_flag: str | None = None
    when: Callable | None = None
    choices: list[Choice] = field(default_factory=list)
    set_flags: list[str] = field(default_factory=list)


@dataclass(kw_only=True)
class Dialogue:
    """Reusable writing: paragraphs, optional replies, and first-matching story branches."""

    text: str | list[str]
    choices: list[Choice] = field(default_factory=list)
    branches: list[Branch] = field(default_factory=list)
    set_flags: list[str] = field(default_factory=list)


def available(*, session, required_flag=None, when=None):
    """Read a simple flag, then an optional named condition; never parse expressions."""
    if required_flag is not None and required_flag not in session.flags:
        return False
    if when is not None and not when(session=session):
        return False
    return True


def paginate(*, text, width=48, lines_per_page=3):
    """Wrap paragraphs into small pages; widths are characters, not screen pixels."""
    paragraphs = [text] if isinstance(text, str) else text
    pages = []
    for paragraph in paragraphs:
        lines = textwrap.wrap(paragraph, width=width) or [""]
        for start in range(0, len(lines), lines_per_page):
            pages.append("\n".join(lines[start : start + lines_per_page]))
    return pages or [""]


class Conversation:
    """Track the current page and choice of one world conversation.

    World pauses walking while this object exists. update changes page/flags;
    drawing only reads them. Choosing commits immediately; closing unread text
    does not earn its completion flags. This rule is visible in finish below.
    """

    def __init__(self, *, name, dialogue, session):
        """Choose a story branch now, then start at its first page."""
        self.name = name
        self.session = session
        self.definition = dialogue
        for branch in dialogue.branches:
            if available(session=session, required_flag=branch.required_flag, when=branch.when):
                self.definition = branch
                break
        self.pages = paginate(text=self.definition.text)
        self.page = 0
        self.choices = []
        for choice in self.definition.choices:
            if available(session=session, required_flag=choice.required_flag):
                self.choices.append(choice)
        self.selection = 0
        self.finished = False
        self.cancelled = False

    @property
    def choosing(self):
        """Offer replies only after the final page of the question is visible."""
        return self.page == len(self.pages) - 1 and bool(self.choices)

    def update(self, *, controls):
        """Apply one-shot presses. One press performs exactly one page/choice action."""
        if controls.cancel_pressed:
            self.cancelled = True
            self.finished = True
            return
        if self.choosing:
            self.selection = (self.selection + controls.menu_step) % len(self.choices)
        if not controls.confirm_pressed:
            return
        if self.page + 1 < len(self.pages):
            self.page += 1
        elif self.choices:
            selected = self.choices[self.selection]
            self.session.flags.update(selected.set_flags)
            self.pages = paginate(text=selected.text)
            self.page = 0
            self.choices = []
        else:
            # Completion is an event, not a per-frame reward. World removes this
            # conversation after finished becomes True, so it cannot pay twice.
            self.session.flags.update(self.definition.set_flags)
            self.finished = True
