from __future__ import annotations

"""Deliberate starting states for lessons and reproducible experiments."""

from rpg_battle.teaching.scenarios import TeachingScenario

threshold_25 = TeachingScenario(
    scenario_id="threshold_25",
    title="Threshold: 25 / 52 HP",
    description="Power Strike just below half health; the low-health branch should run.",
    encounter_id="workshop",
    move_id="workshop_power_strike",
    user_char_id="workshop_hero",
    target_char_ids=("spirit",),
    hp_by_character=(("workshop_hero", 25),),
)

threshold_26 = TeachingScenario(
    scenario_id="threshold_26",
    title="Threshold: 26 / 52 HP",
    description="Power Strike at exactly half health; compare < with <=.",
    encounter_id="workshop",
    move_id="workshop_power_strike",
    user_char_id="workshop_hero",
    target_char_ids=("spirit",),
    hp_by_character=(("workshop_hero", 26),),
)

threshold_27 = TeachingScenario(
    scenario_id="threshold_27",
    title="Threshold: 27 / 52 HP",
    description="Power Strike just above half health; the healthy branch should run.",
    encounter_id="workshop",
    move_id="workshop_power_strike",
    user_char_id="workshop_hero",
    target_char_ids=("spirit",),
    hp_by_character=(("workshop_hero", 27),),
)

chain_lightning = TeachingScenario(
    scenario_id="chain_lightning",
    title="Chain Lightning: one burned target",
    description="Two targets make the loop visible; only Crystal Guardian starts burned.",
    encounter_id="workshop_chain",
    move_id="workshop_chain_lightning",
    user_char_id="workshop_hero",
    target_char_ids=("spirit", "guardian"),
    statuses_by_character=(("guardian", ("burn",)),),
)

target_selection = TeachingScenario(
    scenario_id="target_selection",
    title="Target Selection: HP versus HP ratio",
    description=(
        "Workshop Hero has 20/52 HP while Storm Ranger has 19/46 HP. "
        "The enemy strategy chooses the lower HP ratio, not the lower raw HP."
    ),
    encounter_id="workshop_targeting",
    inspect_mode="strategy",
    hp_by_character=(("workshop_hero", 20), ("ranger", 19)),
)

healing = TeachingScenario(
    scenario_id="healing",
    title="Healing: choose self or ally",
    description="Verdant Druid and Workshop Hero both begin injured.",
    encounter_id="workshop_healing",
    move_id="healing_light",
    user_char_id="druid",
    target_char_ids=("workshop_hero",),
    hp_by_character=(("druid", 20), ("workshop_hero", 30)),
)

balance = TeachingScenario(
    scenario_id="balance",
    title="Balance: two-versus-two comparison",
    description=(
        "A fixed 2v2 setup for comparing one code or balance change across the same seed range."
    ),
    encounter_id="workshop_balance",
    inspect_mode="simulation",
    seed=20,
)

SCENARIOS = {
    scenario.scenario_id: scenario
    for scenario in (
        threshold_25,
        threshold_26,
        threshold_27,
        chain_lightning,
        target_selection,
        healing,
        balance,
    )
}
