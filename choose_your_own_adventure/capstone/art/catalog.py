"""Choose presentation art from game state and the latest story outcome.

This module is intentionally presentation-only.  It reads snapshots and event
text; it never changes game state or decides what actions are legal.
"""

from __future__ import annotations

from typing import Any

from .dust_vault import DUST_VAULT_ART
from .star_crystal import STAR_CRYSTAL_ART


SCENE_TITLES = {
    "ruins_stumble": "Loose footing",
    "bramble_push": "Through the brambles",
    "dark_cave_blocked": "The dark path",
    "broken_crossing": "Broken crossing",
    "tower_gate_unlock": "The tower opens",
    "forest_whisper_hint": "A forest whisper",
    "trail_reopened": "Trail reopened",
    "serve_time": "Serving time",
    "jail_release": "Released",
    "first_tower_visit": "The summit",
    "bandit_surrenders": "Bandit surrender",
    "player_surrender_accepted": "Surrender",
    "player_surrender_rejected": "Surrender refused",
    "guardian_trial_passed": "Trial passed",
    "guardian_trial_failed": "Trial failed",
    "spider_web_cleared": "Web cleared",
    "return_crystal": "The Star Crystal returns",
    "fountain_restored": "Fountain restored",
    "fountain_rest": "Rest at the fountain",
    "quest_complete_cheer": "Sunmeadow celebrates",
    "guard_arrest": "Guard arrest",
    "item_shatter": "A tonic shatters",
    "mercy_choice": "Mercy",
    "river_delivery_started": "River delivery",
    "river_crossing_blocked": "Think it through",
    "river_delivery_complete": "Delivery complete",
    "scene::station_patrol": "Station patrol",
    "scene::glass_maw_ambush": "Glass Maw ambush",
    "scene::rafe_offer": "Rafe's offer",
    "scene::archive_heist": "Black Archive",
    "scene::payroll_shard": "Payroll shard",
    "scene::shuttle_betrayal": "Extraction",
    "scene::survey_arrival": "Survey world",
    "scene::crash": "Crash gully",
    "scene::locator_found": "Locator recovered",
    "scene::bridge_lowered": "Bridge control",
    "scene::grave_core": "Grave Core",
    "scene::landing_beacon": "Landing beacon",
    "scene::ending_corporate": "Corporate ending",
    "scene::ending_broadcast": "Broadcast ending",
    "scene::ending_bury": "Burial ending",
    "scene::brig_release": "Released from the brig",
    "scene::custodian_trial_passed": "Custodian trial passed",
    "scene::custodian_trial_failed": "Custodian trial failed",
}


def _generic_npc_art(name: str, state: str) -> str:
    eyes = "x  x" if state == "dead" else "o  o"
    label = name[:28]
    lines = [
        "+--------------------------------------------------------+",
        "|" + ".------------.".center(56) + "|",
        "|" + (f"/   {eyes}   " + "\\").center(56) + "|",
        "|" + "|     ^      |".center(56) + "|",
        "|" + "|   \\___/   |".center(56) + "|",
        "|" + "'------------'".center(56) + "|",
        "|" + label.center(56) + "|",
        "+--------------------------------------------------------+",
    ]
    return "\n".join(lines)


def _generic_scene_art(title: str) -> str:
    return "\n".join([
        "+--------------------------------------------------------+",
        "|" + "*       .              .       *".center(56) + "|",
        "|" + "/\\             /\\".center(56) + "|",
        "|" + "/  \\___________/  \\".center(56) + "|",
        "|" + title[:50].center(56) + "|",
        "|" + "\\______________________________/".center(56) + "|",
        "+--------------------------------------------------------+",
    ])


def _slug(name: str) -> str:
    return name.lower().replace(" ", "_").replace("-", "_")


STAR_EVENT_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("ruins_stumble", ("loose stone gives way", "stumble")),
    ("bramble_push", ("thorns rake", "force your way through")),
    ("dark_cave_blocked", ("shadows shift in the crack", "dark path")),
    ("broken_crossing", ("gap ahead looks fatal", "crossing gives way")),
    ("tower_gate_unlock", ("gate opens", "ancient light flickers along the stairwell")),
    ("forest_whisper_hint", ("light opens the dark path", "forest has already shared its hint")),
    ("trail_reopened", ("part of the trail is cleared", "winch has already done")),
    ("serve_time", ("narrow cot and wait", "hours pass")),
    ("jail_release", ("released back into sunmeadow", "guard finally opens the cell")),
    ("first_tower_visit", ("something ancient is waiting here",)),
    # Use the distinctive event phrase, not merely the character name.  NPC
    # dialogue is prefixed with "Bandit Nox:", so matching on the name alone
    # would show surrender art during ordinary conversation.
    ("bandit_surrenders", ("surrenders.",)),
    ("player_surrender_accepted", ("binds your hands", "marches you to the village jail")),
    ("player_surrender_rejected", ("cannot be escaped", "only answered or endured")),
    ("guardian_trial_passed", ("trial is complete", "may now be taken", "correct")),
    ("guardian_trial_failed", ("not quite", "wrong answer", "think more carefully")),
    ("spider_web_cleared", ("crystal web tears apart", "safer route through the cave")),
    ("return_crystal", ("you raise the crystal above the fountain", "return the star crystal")),
    ("fountain_restored", ("water bursts upward", "light pours across the square")),
    ("fountain_rest", ("sit beside the fountain", "catch your breath")),
    ("quest_complete_cheer", ("cheers echo through the village", "valley has been saved")),
    ("guard_arrest", ("marches you to the village jail", "stand down")),
    # A normal pickup/trade line also contains "Health Tonic".  Only the
    # broken-crossing consequence should select the shatter illustration.
    ("item_shatter", ("shatters on the rocks",)),
    ("mercy_choice", ("spare", "mercy")),
    (
        "river_delivery_started",
        ("wolf, goat, and cabbage are now traveling with you",),
    ),
    (
        "river_crossing_blocked",
        ("break the delivery puzzle's safety rule",),
    ),
    (
        "river_delivery_complete",
        ("all three passengers are safely on the east bank",),
    ),
]


DUST_EVENT_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("scene::station_patrol", ("patrol drone", "stunner arc")),
    ("scene::glass_maw_ambush", ("dust predator erupts", "glass maw")),
    ("scene::rafe_offer", ("rafe's cutter hails", "landing beacon for payment")),
    ("scene::archive_heist", ("black archive", "sealed terminal", "security panel")),
    ("scene::payroll_shard", ("payroll shard",)),
    ("scene::shuttle_betrayal", ("extraction skiff", "stranded", "shakes out")),
    ("scene::survey_arrival", ("survey world is all hard light",)),
    ("scene::crash", ("crew is gone", "escape coffin")),
    ("scene::locator_found", ("locator chart", "found_locator")),
    ("scene::bridge_lowered", ("bridge", "control")),
    ("scene::grave_core", ("grave core", "grave_core")),
    ("scene::landing_beacon", ("landing beacon", "beacon online")),
    ("scene::ending_corporate", ("ending_corporate", "sold the vault", "corporate")),
    ("scene::ending_broadcast", ("ending_broadcast", "truth is out", "broadcast")),
    ("scene::ending_bury", ("ending_bury", "vault is buried", "collapse charges")),
    ("scene::brig_release", ("sentence", "released", "brig")),
    ("scene::custodian_trial_passed", ("correct. your species teaches", "may now be taken")),
    ("scene::custodian_trial_failed", ("the blade comes later",)),
]


def _event_key(text: str, rules: list[tuple[str, tuple[str, ...]]]) -> str | None:
    lowered = text.lower()
    for key, phrases in rules:
        # Most rules describe a distinctive phrase; multi-phrase rules are
        # satisfied when any strong phrase is present, not all of them.
        if any(phrase in lowered for phrase in phrases):
            return key
    return None


def _star_key(snapshot: dict[str, Any], latest_event: str) -> str:
    # A just-resolved story beat temporarily takes visual priority over the
    # person who happened to trigger it.  On the next choice the portrait
    # returns, so both scenario art and character art are actually visible.
    event_key = _event_key(latest_event, STAR_EVENT_RULES)
    if event_key is not None:
        return event_key

    focus_name = snapshot.get("focus_npc_name")
    if focus_name:
        state = snapshot.get("focus_npc_state") or "alive"
        return f"npc::{_slug(focus_name)}::{state}"

    flags = set(snapshot.get("flags", []))
    if "game_won" in flags:
        return "fountain_restored"
    return f"loc::{snapshot.get('location_key', 'village')}"


def _dust_key(snapshot: dict[str, Any], latest_event: str) -> str:
    flags = set(snapshot.get("flags", []))
    if "ending_corporate" in flags:
        return "scene::ending_corporate"
    if "ending_broadcast" in flags:
        return "scene::ending_broadcast"
    if "ending_bury" in flags:
        return "scene::ending_bury"

    event_key = _event_key(latest_event, DUST_EVENT_RULES)
    if event_key is not None:
        return event_key

    focus_name = snapshot.get("focus_npc_name")
    if focus_name:
        state = snapshot.get("focus_npc_state") or "alive"
        return f"npc::{_slug(focus_name)}::{state}"
    return f"loc::{snapshot.get('location_key', 'berth')}"


def choose_art(snapshot: dict[str, Any], latest_event: str = "") -> tuple[str, str, str]:
    """Return ``(key, title, art)`` for a capstone snapshot."""
    focus_name = snapshot.get("focus_npc_name")
    state = snapshot.get("focus_npc_state") or "alive"

    if snapshot.get("source_version") == "version8.py":
        key = _dust_key(snapshot, latest_event)
        art = DUST_VAULT_ART.get(key)
    else:
        key = _star_key(snapshot, latest_event)
        art = STAR_CRYSTAL_ART.get(key)

    if key.startswith("npc::") and focus_name:
        mood = snapshot.get("focus_npc_mood") or "unknown"
        suffix = "defeated" if state == "dead" else mood
        title = f"{focus_name} [{suffix}]"
        if art is None:
            art = _generic_npc_art(focus_name, state)
    elif key in SCENE_TITLES:
        title = SCENE_TITLES[key]
    else:
        title = snapshot.get("location") or "Scene"

    if art is None:
        art = _generic_scene_art(title)
    return key, title, art
