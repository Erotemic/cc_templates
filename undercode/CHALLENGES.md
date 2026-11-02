# Beyond the supplied hooks

Choose a player-visible goal. Locate the state and update/drawing code yourself;
these projects intentionally have no prewired student function. A small complete
version is better than starting several features. You can invent another goal.

For each project, write a prediction, identify the state owner, implement one
step, demonstrate a counterexample, and explain the input → state → picture path.
Use the engine guide to navigate, not as a list of files you are allowed to edit.

## Overworld projects

- **A pressure plate:** a gate stays open only while someone stands on a plate.
  Decide how entry differs from continued occupancy and departure. Standing
  still should hold the door open; leaving should close it again.
- **A patrolling neighbor:** a person moves between two landmarks, pauses, and
  remains interactable while moving. Decide what is definition data and what
  changes during play. How does collision use the new position?
- **Stamina:** sprinting consumes a resource that recovers while walking. Predict
  behavior with zero stamina and a key held down. Test different frame times.
- **A new terrain:** add a surface with a gameplay effect, such as ice or slow
  water. Find each place the new terrain must be recognized, including drawing.
- **A second view frame:** animate walking differently from idle, in all four
  directions, without making collision depend on the picture.

## Encounter projects

- **A new player technique:** invent a timing sequence and connect it as a Weapon.
  A no-input attempt must finish. Explain what prevents repeated presses from
  earning the same target's points twice.
- **A new ACT effect:** invent a rule beyond a fixed understanding gain. Decide
  what information belongs on an Act, where its effect happens, and how its
  result can be shown without putting rules inside drawing code.
- **A changing arena:** shrink, move or reshape the defense playfield. Explain
  which coordinates represent local gameplay and which represent display layout.
- **A multi-stage opponent:** make a transition respond to health or understanding.
  Consider whether timers reset, what warnings remain readable, and how a
  peaceful ending interacts with the stages.

## Connecting the systems

- **A remembered favor:** an encounter outcome changes a later room, person or
  route. Use a stable person ID and explain who writes and reads the outcome.
- **A companion:** another character follows in the world and participates in an
  encounter. Decide what is shared progress and what belongs to each mode.
- **Saving progress:** design a versioned save format and decide which state must
  survive. Consider what happens when a map or person ID changes between versions.
- **Remappable controls:** let a player choose their keys while leaving world and
  encounter rules independent of pygame's key constants.

## Code-detective questions

1. Which line makes an invitation press unable to choose FIGHT immediately?
2. Can drawing the same frame twice change HP, facing, dialogue or random state?
3. Which object is the authoritative owner of health? Prove it with a short test.
4. Where is an input press changed into a lasting story fact?
5. What happens if a fast projectile crosses the player between two frames?
6. Why does a new defense turn need a fresh pattern instance?
7. Can a story-only NPC exist without any opponent definition? Demonstrate it.
8. What would break if every spawn marker were on its arrival door?

When showing your feature, explain both the part you reused and the rule you
added. If your project needs a new engine connection, make it explicit and add a
short example or regression check that would catch a real mistake in that rule.
