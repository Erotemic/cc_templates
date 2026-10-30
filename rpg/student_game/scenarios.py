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

# FOUR GUIDED MISSIONS. Named starting states make experiments repeatable.
# The battles themselves are assembled in student_game/guided_battles.py;
# the incomplete decision functions live in student_game/student.py.
healer_injured = TeachingScenario(
    scenario_id="healer_injured",
    title="Mission 1: Injured teammate, confused healer",
    description="Battered Shieldbearer begins at 14/68 HP, but the healer attacks.",
    encounter_id="lesson_healer_battle",
    inspect_mode="strategy",
    hp_by_character=(("lesson_shieldbearer", 14),),
)
healer_healthy = TeachingScenario(
    scenario_id="healer_healthy",
    title="Mission 1: Healthy teammate comparison",
    description="Everyone is healthy. Should the healer waste a healing spell?",
    encounter_id="lesson_healer_battle",
    inspect_mode="strategy",
)
coward_low_hp = TeachingScenario(
    scenario_id="coward_low_hp",
    title="Mission 2: Coward on the ropes",
    description="Timid Wisp has 18/52 HP and attacks instead of defending.",
    encounter_id="lesson_coward_battle",
    inspect_mode="strategy",
    hp_by_character=(("lesson_coward", 18),),
)
coward_healthy = TeachingScenario(
    scenario_id="coward_healthy",
    title="Mission 2: Coward at full strength",
    description="Timid Wisp has full HP, so it has no reason to defend yet.",
    encounter_id="lesson_coward_battle",
    inspect_mode="strategy",
)
sword_low_hp = TeachingScenario(
    scenario_id="sword_low_hp",
    title="Mission 3: Cursed Sword, wielder injured",
    description="The swordfighter has 18/62 HP; a possible curse condition.",
    encounter_id="lesson_sword_battle",
    move_id="lesson_cursed_sword",
    user_char_id="lesson_swordfighter",
    target_char_ids=("spirit",),
    hp_by_character=(("lesson_swordfighter", 18),),
)
sword_healthy = TeachingScenario(
    scenario_id="sword_healthy",
    title="Mission 3: Cursed Sword, wielder healthy",
    description="The swordfighter has 55/62 HP; compare to the injured case.",
    encounter_id="lesson_sword_battle",
    move_id="lesson_cursed_sword",
    user_char_id="lesson_swordfighter",
    target_char_ids=("spirit",),
    hp_by_character=(("lesson_swordfighter", 55),),
)
boss_low_hp = TeachingScenario(
    scenario_id="boss_low_hp",
    title="Mission 4: Boss under half health",
    description="Phase Warden starts at 44/105 HP but still attacks normally.",
    encounter_id="lesson_boss_battle",
    inspect_mode="strategy",
    hp_by_character=(("lesson_boss", 44),),
)
boss_healthy = TeachingScenario(
    scenario_id="boss_healthy",
    title="Mission 4: Boss at full health",
    description="Phase Warden has full HP. Compare its decisions with the low-HP battle.",
    encounter_id="lesson_boss_battle",
    inspect_mode="strategy",
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
        healer_injured,
        healer_healthy,
        coward_low_hp,
        coward_healthy,
        sword_low_hp,
        sword_healthy,
        boss_low_hp,
        boss_healthy,
    )
}
