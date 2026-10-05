"""Complete ASCII-art catalog for the Dust Vault capstone.

The original Dust Vault version had the improved Textual UI but never received
v7's scene-art pass.  The capstone fills that gap: every authored location,
every named character, both random-combat creatures, and the major story beats
have presentation-only art.
"""

from __future__ import annotations

import textwrap


def _trim(text: str) -> str:
    lines = textwrap.dedent(text).splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(line.rstrip() for line in lines)


def _card(text: str, width: int = 56) -> str:
    lines = _trim(text).splitlines()
    inner = max(width, max((len(line) for line in lines), default=0) + 4)
    edge = "+" + "-" * inner + "+"
    body = ["|" + line.center(inner) + "|" for line in lines]
    return "\n".join([edge, *body, edge])


RAW_ART = {
    "loc::berth": r"""
          .-------------------------------.
          | RING BERTH THREE              |
      ____|____                    ____   |
 ____/  _   _  \__________________/ __ \__|____
|   |  |_| |_|  |   cargo nets   |/  \|       |
|===|===========|================|====|=======|
|___|___________|________________|____|_______|
        ||                          ||
       _||_        transfer ring   _||_
    """,
    "loc::lounge": r"""
       ______________________________________
      /  cracked locker     mission tablets  \
     |  [__][__][__]     .---------------.   |
     |                   |  LIFT / ARCHIVE |  |
     |       __          '---------------'   |
     |   ___/  \___       stale coffee       |
     |  |          |        (____)            |
     |  |  crew    |          ||              |
     |  |  table   |       ___||___           |
      \_|__________|__________________________/
    """,
    "loc::service": r"""
      __________________________________________
     /  conduit  conduit  conduit  conduit       \
    |============================================|
    |   [ ]      [ ]        [ ]       [ ]       |
    |                                            |
    |        narrow maintenance spine            |
    |  .----.                        .----.       |
    |  |lift|                        |vent|       |
    |__|____|________________________|____|_______|
    """,
    "loc::annex": r"""
          _________________________________
         /  ARCHIVE ACCESS                 \
        |  camera cluster      pressure door|
        |    (x)(x)(x)          __________  |
        |                       |  ||||  |   |
        |   security panel      |  ||||  |   |
        |   .----------.        |  ||||  |   |
        |   | 07:LOCK  |        |________|   |
         \__'----------'_____________________/
    """,
    "loc::archive": r"""
        ______________________________________
       /           BLACK ARCHIVE              \
      |  [ledger][ledger][ledger][ledger]      |
      |  [claim ][claim ][claim ][claim ]      |
      |                                        |
      |    .---------.        .------------.   |
      |    | RED     |        | SEALED     |   |
      |    | LOCKER  |        | TERMINAL   |   |
      |____'---------'________'------------'___|
    """,
    "loc::shuttle": r"""
            *                  .
                     _____________
              ______/  UTILITY    \______
             /  ___     SKIFF        ___  \
      ======/__/___\_______________/___\__\======
             \_________________________/
          ____||_____________________||____
         /       yawning air lock          \
        /___________________________________\
    """,
    "loc::brig": r"""
       ______________________________________
      | | | | | | | | | | | | | | | | | | |
      | | | | | | | | | | | | | | | | | | |
      | | | | | | | | | | | | | | | | | | |
      | | | | | | | | | | | | | | | | | | |
      | | | | | | | | | | | | | | | | | | |
      |_______________    _________________|
            _________|    |_________
           /      transit brig       \
    """,
    "loc::survey_pad": r"""
              \       |       /
               \      |      /
          ______\_____|_____/_______
         /                          /|
        /      SURVEY PAD          / |
       /__________________________/  |
       |   :: dust :: dust ::     |  /
       |__________________________| /
          _/      _/      _/      
       __/____ __/____ __/____     horizon
    """,
    "loc::crash_gully": r"""
        \                /\              /
         \__        ____/  \____       _/
            \______/            \_____/
             _______________
         ___/  ESCAPE COFFIN \___
       _/   _/\/\/\/\/\/\_     \_
      /____/______________\_______\
          /   cracked hull  \
     ____/___________________\____
    """,
    "loc::windbreak": r"""
          ______________________________
         / survey-panel windbreak       \
        /_______________________________\
        |  rover door |  stove  | tools |
        |  __________ |  (___)  | /\/\  |
        | |          ||    |    | ||||  |
        |_|__________||____|____|_||||__|
           \            dust            /
            \__________________________/
    """,
    "loc::relay": r"""
                         |
                    -----+-----
                         |
                  .------|------.
                  |      |      |
                  |      |      |
                 /|\     |     /|\
                / | \    |    / | \
       ________/__|__\___|___/__|__\________
                   RELAY RIDGE
    """,
    "loc::habitat": r"""
          _________               _________
      ___/         \_____________/         \___
     /      HABITAT SHELL   _                  \
    |   .---------.       _/ \_    dust         |
    |   | old log |      /     \                |
    |   | archive |     |       |               |
    |   '---------'      \_____/                |
     \__________________________________________/
          \\__ half buried rooms __//
    """,
    "loc::pump": r"""
       ________________________________________
      /      PUMP HOUSE                        \
     |   .----.     .----.     .----.           |
     |   |====|=====|====|=====|====|           |
     |   '----'     '----'     '----'           |
     |          KNOCK   KNOCK   KNOCK           |
     |      .-------------------------.          |
     |______| bridge control          |__________|
            '-------------------------'
    """,
    "loc::ravine": r"""
        \      /\/\         /\          /
         \____/ /\ \_______/  \________/
           /\  /  \   /\/\       /\
      ____/  \/ /\ \_/ /\ \_____/  \____
          brittle mineral shelves
      =====================================
          \      fused glass       /
           \______________________/
    """,
    "loc::drill": r"""
                         ______
                    ____/ ____ \____
             ______/    /    \     \____
            /          crane               \
       ____/______________|_________________\____
      |   [scrap]      ___|___        [scrap]    |
      |              _/       \_                 |
      |_____________/ COLLAPSED \________________|
                     \   BORE   /
                      '-------'
    """,
    "loc::crater": r"""
                 .                 .
           _________.---------._________
       ___/       .-'         '-.       \___
     _/         .'      X        '.         \_
    /     o    /    burial crater   \   o     \
   /__________/______________________\__________\
        | |         survey flags       | |
       [###]       old charges        [###]
    """,
    "loc::gallery": r"""
       ________________________________________
      /                                        \
     |   |\        /|      |\        /|         |
     |   | \______/ |      | \______/ |         |
     |   |  ______  |      |  ______  |         |
     |   |_/      \_|      |_/      \_|         |
     |       geometric machine corridor          |
      \__________________________________________/
    """,
    "loc::vault": r"""
                     .-=========-.
                 _.-'             '-._
              .-'        /\           '-.
             /          /  \             \
            |          / /\ \             |
            |         <  CORE >            |
            |          \ \/ /             |
             \          \  /             /
              '-._       \/          _.-'
                  '---._______ .---'
                       VAULT HEART
    """,

    "npc::rafe_mercer::alive": r"""
              .-==============-.
             /   _        _     \
            |   o          o     |
            |        /\          |
            |    .-"----"-.      |
             \__/  .====.  \____/
                 _/ |==| \_
            ____/ __|==|__ \____
           / tailored coat + cred \
          /________________________\
                RAFE MERCER
    """,
    "npc::rafe_mercer::dead": r"""
              .-==============-.
             /   _        _     \
            |   x          x     |
            |        --          |
            |    .-"----"-.      |
             \__/  .====.  \____/
                 _/ |==| \_
            ____/ __|==|__ \____
    """,
    "npc::mina_voss::alive": r"""
               .-============-.
              /  o        o    \
             |       .--.       |
             |    .-'_[]_'-.    |
              \___\__====__/___/
                 / / || \
          ______/_/  ||  \_ ______
         /  slicer rig  ||  probes  \
        /_______________||___________\
                 MINA VOSS
    """,
    "npc::mina_voss::dead": r"""
               .-============-.
              /  x        x    \
             |       .--.       |
             |        ----       |
              \___\__====__/___/
                 / / || \
          ______/_/  ||  \_ ______
    """,
    "npc::marshal_sorn::alive": r"""
               ____==##==____
           ___/______/\______\___
          /    .-==========-.    \
         |    /  o      o    \    |
         |   |       <>       |   |
         |   |    .-____-.    |   |
          \   \___\______/___/   /
           '.___/  ||||  \___.-'
             _/____||||____\_
            /_____/ || \_____\
               MARSHAL SORN
    """,
    "npc::marshal_sorn::dead": r"""
               ____==##==____
           ___/______/\______\___
          /    .-==========-.    \
         |    /  x      x    \    |
         |   |       --       |   |
         |   |    .-____-.    |   |
          \   \___\______/___/   /
           '.___/  ||||  \___.-'
             _/____||||____\_
    """,
    "npc::orla_quist::alive": r"""
               .-============-.
              /   o      o     \
             |        <>        |
             |    .-______-.    |
              \___/  /||\  \___/
                 _/__/||\__\_
            ____/  pack||coil \____
           /____ dusty tools + map __\
                ORLA QUIST
    """,
    "npc::orla_quist::dead": r"""
               .-============-.
              /   x      x     \
             |        --        |
             |    .-______-.    |
              \___/  /||\  \___/
                 _/__/||\__\_
            ____/  pack||coil \____
    """,
    "npc::juno_hale::alive": r"""
               .-============-.
              /   o      o     \
             |        ..        |
             |    .-\____/-.    |
              \___/ __||__ \___/
                 _/ _||||_ \_
            ____/__/ med kit\__\____
           /______ bandages + tonic _\
                 JUNO HALE
    """,
    "npc::juno_hale::dead": r"""
               .-============-.
              /   x      x     \
             |        --        |
             |    .-\____/-.    |
              \___/ __||__ \___/
                 _/ _||||_ \_
            ____/__/ med kit\__\____
    """,
    "npc::cade_voss::alive": r"""
               .-============-.
              /  o        o     \
             |       /\/\       |
             |    .-'===='-.     |
              \___/  ||||  \_____/
                 __/||||\__
           _____/ salvage belt \_____
          /______ pry bar + scrap ____\
                 CADE VOSS
    """,
    "npc::cade_voss::dead": r"""
               .-============-.
              /  x        x     \
             |       ----        |
             |    .-'===='-.     |
              \___/  ||||  \_____/
                 __/||||\__
           _____/ salvage belt \_____
    """,
    "npc::custodian_echo::alive": r"""
                   .   |   .
                .  \  |  /  .
          -----+---\ | /---+-----
           .-==\   \|/   //==-.
        .-'=====\   *   //====='-.
       <=========== /|\ ==========>
        '-.=====// / | \=====.-'
           '-==//_/__|__\_\==-'
                 /   |   \
                '    |    '
              CUSTODIAN ECHO
    """,
    "npc::custodian_echo::dead": r"""
                   .   |   .
                .  \  |  /  .
          -----+---\ | /---+-----
           .-==\   \|/   //==-.
        .-'=====\   x   //====='-.
       <=========== /-\ ==========>
        '-.=====// / | \=====.-'
           '-==//_/__|__\_\==-'
    """,
    "npc::patrol_drone::alive": r"""
                  .-======-.
              .--|  [] [] |--.
           .-'   |    <>   |   '-.
          /    __|_.-==-. _|__    \
     ----|----/  _  /||\  _  \----|----
          \__/__/ |_|  |_| \__\__/
              /_/  /_/\_\  \_\
               PATROL DRONE
    """,
    "npc::patrol_drone::dead": r"""
                  .-======-.
              .--|  xx xx |--.
           .-'   |    --   |   '-.
          /    __|_.-==-. _|__    \
     ----|----/  _  /||\  _  \----|----
          \__/__/ |_|  |_| \__\__/
    """,
    "npc::glass_maw::alive": r"""
                __..-^^^^-..__
           _.-'      /\      '-._
        .-'   .--.  / /\  .--.   '-.
       /     / oo \/ /  \/ oo \     \
      |      \____/ /_/\ \____/     |
      |          .-' /  \'-.         |
       \      _.'___/____\___'._    /
        '._.-'   _/ /\/\ \_   '-._.'
              __/__/    \__\__
                 GLASS MAW
    """,
    "npc::glass_maw::dead": r"""
                __..-^^^^-..__
           _.-'      /\      '-._
        .-'   .--.  / /\  .--.   '-.
       /     / xx \/ /  \/ xx \     \
      |      \____/ /_/\ \____/     |
      |          .-' /  \'-.         |
       \      _.'___/____\___'._    /
        '._.-'   _/ /\/\ \_   '-._.'
    """,

    "scene::station_patrol": r"""
              RED PROFILE LOCKED
             .-------------------.
             |       (  )        |
             |        \/         |
             '--------||---------'
                 _____||_____
            ____/  PATROL    \____
           /______ DRONE _________\
                 \  /\  /
                  \/  \/
    """,
    "scene::glass_maw_ambush": r"""
       brittle shelves      KRRRCH
     /\/\/\/\/\                /\/\/\
    /          \____      ____/      \
                    \____/
              .-========-.
          ___/  o      o  \___
     ----/        /\         \----
          GLASS MAW AMBUSH
    """,
    "scene::rafe_offer": r"""
                    .------.
              _____/ CUTTER \_____
          ___/_____________________\___
         /      \              /       \
        /________\____________/_________\
                    |  |  |
             .------'  |  '------.
             | BRING THE CORE.    |
             | LANDING BEACON.    |
             '--------------------'
    """,
    "scene::archive_heist": r"""
        .----------------------------------.
        | BLACK ARCHIVE : ACCESS GRANTED   |
        |                                  |
        |  [PAYROLL] [CLAIMS] [SURVEY]     |
        |        .---------------.         |
        |        | COPY IN PROGRESS|        |
        |        '---------------'         |
        '----------------------------------'
    """,
    "scene::payroll_shard": r"""
              .----------------.
              |  PAYROLL       |
              |  SHARD         |
              |  7A:F0:19      |
              |  [ENCRYPTED]   |
              '----------------'
                 \          /
                  \________/
    """,
    "scene::shuttle_betrayal": r"""
                LOCKS RELEASED
              _________||_________
         ____/                    \____
        /       EXTRACTION SKIFF       \
       /_______________________________\
             \       ||       /
              \______||______/
                     \/
            the station falls away
    """,
    "scene::survey_arrival": r"""
             *           .
        __________________________
       /       SURVEY WORLD       \
      /____________________________\
           .  .   .   .  .
       ____/\/\__/\/\__/\/\____
      / hard light and harder silence \
    """,
    "scene::crash": r"""
             WARNING // TRAJECTORY LOST
          __________________________________
       __/   \_/\_/\_/\_/\_/\_/\_/\_/   \__
      /        ESCAPE COFFIN IMPACT          \
     /________________________________________\
             *    *    *    *
          dust fills the broken sky
    """,
    "scene::locator_found": r"""
             .----------------------.
             |  SURVEY LOCATOR      |
             |       *              |
             |   *       X          |
             |      /\              |
             | ____/  \______       |
             '----------------------'
              coordinates recovered
    """,
    "scene::bridge_lowered": r"""
          LEFT BANK                 RIGHT BANK
      _____________               _____________
                   \             /
                    \___________/
                =======[===]=======
                     BRIDGE
                  CONTROL ONLINE
    """,
    "scene::grave_core": r"""
                    .-========-.
                 .-'    /\      '-.
               .'      /  \        '.
              <       < CORE >        >
               '.      \  /        .'
                 '-.    \/      .-'
                    '---..---'
                  GRAVE CORE
    """,
    "scene::landing_beacon": r"""
                        /\
                       /  \
                      / || \
                     /  ||  \
                    /___||___\
                        ||
                 .------||------.
                 | BEACON ONLINE |
                 '---------------'
                    /        \
    """,
    "scene::ending_corporate": r"""
               .-----------------------.
               |     TRANSFER OK       |
               |  CORE -> CORPORATE    |
               '-----------------------'
                 ____            ____
             ___/    \__________/    \___
            /     cutter burns for orbit   \
           /_______________________________\
    """,
    "scene::ending_broadcast": r"""
                  *   *   *   *
             .--------------------.
             |  BROADCAST OPEN    |
             |  DATA -> EVERYONE  |
             '--------------------'
              \   |   |   |   /
               \  |   |   |  /
                \ |   |   | /
                 \|   |   |/
    """,
    "scene::ending_bury": r"""
                 \     |     /
                  \    |    /
              _____\___|___/_____
           __/       crater      \__
         _/   [###]         [###]  \_
        /_____________________________\
             BOOM       BOOM
          dust closes over the vault
    """,
    "scene::brig_release": r"""
          | | | | |       | | | | |
          | | | | |       | | | | |
          | | | | |  -->  | | | | |
          | | | | |       | | | | |
          |_|_|_|_|       |_|_|_|_| 
               sentence served
    """,
    "scene::custodian_trial_passed": r"""
                  .    *    .
             .----\    |    /----.
            <======\   |   /======>
             '------\  |  /------'
                    \ | /
                     \|/
                     /|\
               ACCESS GRANTED
    """,
    "scene::custodian_trial_failed": r"""
                 .---?---.
              .-'    !    '-.
             <      /_\      >
              '-.    !    .-'
                 '---+---'
                    / \
               WRONG ANSWER
    """,
}


DUST_VAULT_ART = {key: _card(value) for key, value in RAW_ART.items()}
EXPECTED_DUST_LOCATION_KEYS = frozenset(key for key in RAW_ART if key.startswith("loc::"))
EXPECTED_DUST_NPC_KEYS = frozenset(key for key in RAW_ART if key.startswith("npc::"))
EXPECTED_DUST_SCENE_KEYS = frozenset(key for key in RAW_ART if key.startswith("scene::"))
