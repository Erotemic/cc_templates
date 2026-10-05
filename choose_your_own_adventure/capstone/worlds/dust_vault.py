"""Generated from the original version8.py world.

Do not hand-edit existing records when checking fidelity.  Students can add
rooms and simple ``choices`` records directly; the engine fills in omitted
optional fields.
"""

WORLD_DATA = {'source_version': 'version8.py',
 'name': 'Dust Vault',
 'start_location': 'berth',
 'player': {'max_hp': 100,
            'attack_min': 6,
            'attack_max': 10,
            'defense': 1,
            'gold': 5,
            'inventory': ['utility_knife'],
            'equipment': {'weapon': 'utility_knife', 'armor': None, 'charm': None},
            'flags': ['game_started']},
 'items': {'utility_knife': {'type': 'Item',
                             'item_id': 'utility_knife',
                             'name': 'Utility Knife',
                             'description': 'A serviceable field blade issued to disposable crew.',
                             'slot': 'weapon',
                             'power_bonus': 1,
                             'defense_bonus': 0,
                             'hp_bonus': 0,
                             'healing': 0,
                             'set_flags_on_pickup': [],
                             'tags': []},
           'spoofer': {'type': 'Item',
                       'item_id': 'spoofer',
                       'name': 'Port Spoofer',
                       'description': 'A handshake spoofer for old security panels.',
                       'slot': None,
                       'power_bonus': 0,
                       'defense_bonus': 0,
                       'hp_bonus': 0,
                       'healing': 0,
                       'set_flags_on_pickup': [],
                       'tags': []},
           'payroll_shard': {'type': 'Item',
                             'item_id': 'payroll_shard',
                             'name': 'Payroll Shard',
                             'description': 'The encrypted payroll archive your crew was hired to '
                                            'steal.',
                             'slot': None,
                             'power_bonus': 0,
                             'defense_bonus': 0,
                             'hp_bonus': 0,
                             'healing': 0,
                             'set_flags_on_pickup': ['has_payroll_shard'],
                             'tags': []},
           'survey_canister': {'type': 'Item',
                               'item_id': 'survey_canister',
                               'name': 'Survey Canister',
                               'description': 'A sealed field canister tagged with a dead world '
                                              'survey code.',
                               'slot': None,
                               'power_bonus': 0,
                               'defense_bonus': 0,
                               'hp_bonus': 0,
                               'healing': 0,
                               'set_flags_on_pickup': [],
                               'tags': []},
           'cutter_rifle': {'type': 'Item',
                            'item_id': 'cutter_rifle',
                            'name': 'Cutter Rifle',
                            'description': 'A compact industrial carbine cut down for boarding '
                                           'work.',
                            'slot': 'weapon',
                            'power_bonus': 5,
                            'defense_bonus': 0,
                            'hp_bonus': 0,
                            'healing': 0,
                            'set_flags_on_pickup': [],
                            'tags': []},
           'pressure_weave': {'type': 'Item',
                              'item_id': 'pressure_weave',
                              'name': 'Pressure Weave',
                              'description': 'Layered expedition armor rated for thin air and '
                                             'stone spray.',
                              'slot': 'armor',
                              'power_bonus': 0,
                              'defense_bonus': 2,
                              'hp_bonus': 12,
                              'healing': 0,
                              'set_flags_on_pickup': [],
                              'tags': []},
           'claim_marker': {'type': 'Item',
                            'item_id': 'claim_marker',
                            'name': 'Claim Marker',
                            'description': 'A brass marker used to stamp discovered ground as '
                                           'owned.',
                            'slot': 'charm',
                            'power_bonus': 0,
                            'defense_bonus': 1,
                            'hp_bonus': 0,
                            'healing': 0,
                            'set_flags_on_pickup': [],
                            'tags': []},
           'line_spool': {'type': 'Item',
                          'item_id': 'line_spool',
                          'name': 'Line Spool',
                          'description': 'A powered anchor line for crossing broken industrial '
                                         'gaps.',
                          'slot': None,
                          'power_bonus': 0,
                          'defense_bonus': 0,
                          'hp_bonus': 0,
                          'healing': 0,
                          'set_flags_on_pickup': [],
                          'tags': []},
           'coldlamp': {'type': 'Item',
                        'item_id': 'coldlamp',
                        'name': 'Cold Lamp',
                        'description': 'A harsh white lamp that cuts through dust and dead '
                                       'tunnels.',
                        'slot': None,
                        'power_bonus': 0,
                        'defense_bonus': 0,
                        'hp_bonus': 0,
                        'healing': 0,
                        'set_flags_on_pickup': [],
                        'tags': []},
           'locator_chart': {'type': 'Item',
                             'item_id': 'locator_chart',
                             'name': 'Locator Chart',
                             'description': 'A triangulation chart recovered from an old survey '
                                            'mast.',
                             'slot': None,
                             'power_bonus': 0,
                             'defense_bonus': 0,
                             'hp_bonus': 0,
                             'healing': 0,
                             'set_flags_on_pickup': ['found_locator'],
                             'tags': []},
           'vault_cipher': {'type': 'Item',
                            'item_id': 'vault_cipher',
                            'name': 'Vault Cipher',
                            'description': 'A drill-yard cipher rod keyed to the buried access '
                                           'seals.',
                            'slot': None,
                            'power_bonus': 0,
                            'defense_bonus': 0,
                            'hp_bonus': 0,
                            'healing': 0,
                            'set_flags_on_pickup': [],
                            'tags': []},
           'grave_core': {'type': 'Item',
                          'item_id': 'grave_core',
                          'name': 'Grave Core',
                          'description': 'A dense, warm machine core that hums with buried '
                                         'authority.',
                          'slot': None,
                          'power_bonus': 0,
                          'defense_bonus': 0,
                          'hp_bonus': 0,
                          'healing': 0,
                          'set_flags_on_pickup': ['has_grave_core'],
                          'tags': []},
           'med_patch': {'type': 'Item',
                         'item_id': 'med_patch',
                         'name': 'Med Patch',
                         'description': 'A quick seal patch full of painkillers and clotting foam.',
                         'slot': None,
                         'power_bonus': 0,
                         'defense_bonus': 0,
                         'hp_bonus': 0,
                         'healing': 20,
                         'set_flags_on_pickup': [],
                         'tags': ['consumable']},
           'stim_dose': {'type': 'Item',
                         'item_id': 'stim_dose',
                         'name': 'Stim Dose',
                         'description': 'A stronger injector used when your hands start to shake.',
                         'slot': None,
                         'power_bonus': 0,
                         'defense_bonus': 0,
                         'hp_bonus': 0,
                         'healing': 34,
                         'set_flags_on_pickup': [],
                         'tags': ['consumable']}},
 'rooms': {'berth': {'key': 'berth',
                     'name': 'Ring Berth Three',
                     'description': 'A freight berth on a tired transfer ring. Cargo nets sway '
                                    'over scarred deck plating while your crew pretends this is '
                                    'just another routine lift.',
                     'exits': [{'type': 'Exit',
                                'direction': 'east',
                                'destination': 'lounge',
                                'requires_item': None,
                                'requires_flag': None,
                                'blocked': False,
                                'blocked_text': 'That path is blocked.',
                                'warning_text': None,
                                'on_attempt_effect': None,
                                'on_blocked_effect': None,
                                'on_success_effect': None}],
                     'items': [],
                     'npcs': [],
                     'features': [],
                     'choices': []},
           'lounge': {'key': 'lounge',
                      'name': 'Crew Cubicle',
                      'description': 'A rented crew room with cracked lockers, stale coffee, and a '
                                     'table full of disposable mission tablets.',
                      'exits': [{'type': 'Exit',
                                 'direction': 'west',
                                 'destination': 'berth',
                                 'requires_item': None,
                                 'requires_flag': None,
                                 'blocked': False,
                                 'blocked_text': 'That path is blocked.',
                                 'warning_text': None,
                                 'on_attempt_effect': None,
                                 'on_blocked_effect': None,
                                 'on_success_effect': None},
                                {'type': 'Exit',
                                 'direction': 'north',
                                 'destination': 'service',
                                 'requires_item': None,
                                 'requires_flag': None,
                                 'blocked': False,
                                 'blocked_text': 'That path is blocked.',
                                 'warning_text': None,
                                 'on_attempt_effect': None,
                                 'on_blocked_effect': None,
                                 'on_success_effect': None}],
                      'items': [],
                      'npcs': [{'type': 'NPC',
                                'name': 'Rafe Mercer',
                                'base_stats': {'type': 'Stats',
                                               'max_hp': 34,
                                               'attack_min': 5,
                                               'attack_max': 8,
                                               'defense': 1},
                                'location': 'lounge',
                                'health': 34,
                                'gold': 10,
                                'inventory': ['med_patch'],
                                'equipment': {'weapon': None, 'armor': None, 'charm': None},
                                'description': 'Crew lead, well dressed for a thief, and always '
                                               'measuring people by how much noise they make.',
                                'tags': [],
                                'aggression': 25,
                                'courage': 60,
                                'willingness_to_trade': 0,
                                'hostile': False,
                                'dialogue_topics': [{'type': 'DialogueTopic',
                                                     'key': 'job_pitch',
                                                     'title': 'Ask about the job',
                                                     'lines': ['Simple lift. Payroll shard out of '
                                                               'a dead annex, no bodies, no '
                                                               'heroics.',
                                                               'Do it clean and I stop calling you '
                                                               'the new hand.'],
                                                     'required_flags': [],
                                                     'blocked_flags': ['act1_started'],
                                                     'required_items': [],
                                                     'once': True,
                                                     'outcome_effect': {'type': 'CompositeEffect',
                                                                        'effects': [{'type': 'GivePlayerItemEffect',
                                                                                     'item_ids': ['spoofer']},
                                                                                    {'type': 'SetFlagEffect',
                                                                                     'flags': ['act1_started']}]}},
                                                    {'type': 'DialogueTopic',
                                                     'key': 'after_start',
                                                     'title': 'Ask what comes after the lift',
                                                     'lines': ['If the shard sells, we eat well. '
                                                               'If the side archive log is real, '
                                                               'we might eat for a year.',
                                                               'Dead survey worlds hide expensive '
                                                               'mistakes.'],
                                                     'required_flags': ['act1_started'],
                                                     'blocked_flags': ['act2_started'],
                                                     'required_items': [],
                                                     'once': False,
                                                     'outcome_effect': None}],
                                'trade_offers': [],
                                'riddle': None,
                                'surrender_at_ratio': None,
                                'surrender_lines': [],
                                'surrender_trade_offers': [],
                                'peaceful_after_surrender': True,
                                'surrender_accept_lines': [],
                                'surrender_reject_lines': [],
                                'surrender_accept_effect': None,
                                'defeat_lines': [],
                                'reward_items': [],
                                'reward_flags': [],
                                'reward_gold': 0,
                                'persistent': True,
                                'used_topics': [],
                                'completed_trades': [],
                                'surrendered': False,
                                'riddle_solved': False,
                                'defeated': False},
                               {'type': 'NPC',
                                'name': 'Mina Voss',
                                'base_stats': {'type': 'Stats',
                                               'max_hp': 28,
                                               'attack_min': 4,
                                               'attack_max': 7,
                                               'defense': 0},
                                'location': 'lounge',
                                'health': 28,
                                'gold': 0,
                                'inventory': [],
                                'equipment': {'weapon': None, 'armor': None, 'charm': None},
                                'description': 'The slicer on the crew. Her tools are neat, her '
                                               'hands are not.',
                                'tags': [],
                                'aggression': 5,
                                'courage': 35,
                                'willingness_to_trade': 20,
                                'hostile': False,
                                'dialogue_topics': [{'type': 'DialogueTopic',
                                                     'key': 'mina_advice',
                                                     'title': 'Ask for advice',
                                                     'lines': ['The panel at archive access still '
                                                               'speaks antique station. Use the '
                                                               'spoofer and do not get curious '
                                                               'about the red locker.',
                                                               'Curiosity is how cheap jobs become '
                                                               'hard ones.'],
                                                     'required_flags': [],
                                                     'blocked_flags': [],
                                                     'required_items': [],
                                                     'once': False,
                                                     'outcome_effect': None},
                                                    {'type': 'DialogueTopic',
                                                     'key': 'mina_patch',
                                                     'title': 'Ask if she has anything useful',
                                                     'lines': ['Take this patch and stop leaking '
                                                               'on the consoles.'],
                                                     'required_flags': [],
                                                     'blocked_flags': ['mina_helped'],
                                                     'required_items': [],
                                                     'once': True,
                                                     'outcome_effect': {'type': 'CompositeEffect',
                                                                        'effects': [{'type': 'GivePlayerItemEffect',
                                                                                     'item_ids': ['med_patch']},
                                                                                    {'type': 'SetFlagEffect',
                                                                                     'flags': ['mina_helped']}]}}],
                                'trade_offers': [],
                                'riddle': None,
                                'surrender_at_ratio': None,
                                'surrender_lines': [],
                                'surrender_trade_offers': [],
                                'peaceful_after_surrender': True,
                                'surrender_accept_lines': [],
                                'surrender_reject_lines': [],
                                'surrender_accept_effect': None,
                                'defeat_lines': [],
                                'reward_items': [],
                                'reward_flags': [],
                                'reward_gold': 0,
                                'persistent': True,
                                'used_topics': [],
                                'completed_trades': [],
                                'surrendered': False,
                                'riddle_solved': False,
                                'defeated': False}],
                      'features': [{'type': 'ScriptedFeature',
                                    'name': 'crew locker',
                                    'verb': 'Search',
                                    'required_flags': [],
                                    'blocked_text': 'Nothing happens.',
                                    'once_flag': 'locker_searched',
                                    'first_effect': {'type': 'CompositeEffect',
                                                     'effects': [{'type': 'PrintEffect',
                                                                  'lines': ['You crack your own '
                                                                            'locker and take what '
                                                                            'should already have '
                                                                            'been issued.',
                                                                            'The crew never spends '
                                                                            'good money on people '
                                                                            'they can replace.']},
                                                                 {'type': 'GivePlayerItemEffect',
                                                                  'item_ids': ['med_patch']}]},
                                    'repeat_effect': {'type': 'PrintEffect',
                                                      'lines': ['The locker is empty except for '
                                                                'old meal wrappers.']}}],
                      'choices': []},
           'service': {'key': 'service',
                       'name': 'Service Spine',
                       'description': 'A narrow maintenance artery running behind customs walls '
                                      'and freight lifts.',
                       'exits': [{'type': 'Exit',
                                  'direction': 'south',
                                  'destination': 'lounge',
                                  'requires_item': None,
                                  'requires_flag': None,
                                  'blocked': False,
                                  'blocked_text': 'That path is blocked.',
                                  'warning_text': None,
                                  'on_attempt_effect': None,
                                  'on_blocked_effect': None,
                                  'on_success_effect': None},
                                 {'type': 'Exit',
                                  'direction': 'north',
                                  'destination': 'annex',
                                  'requires_item': None,
                                  'requires_flag': None,
                                  'blocked': False,
                                  'blocked_text': 'That path is blocked.',
                                  'warning_text': None,
                                  'on_attempt_effect': None,
                                  'on_blocked_effect': None,
                                  'on_success_effect': None},
                                 {'type': 'Exit',
                                  'direction': 'east',
                                  'destination': 'shuttle',
                                  'requires_item': None,
                                  'requires_flag': None,
                                  'blocked': False,
                                  'blocked_text': 'That path is blocked.',
                                  'warning_text': None,
                                  'on_attempt_effect': None,
                                  'on_blocked_effect': None,
                                  'on_success_effect': None}],
                       'items': [],
                       'npcs': [],
                       'features': [],
                       'choices': []},
           'annex': {'key': 'annex',
                     'name': 'Archive Access',
                     'description': 'A pressure door, a dead camera cluster, and a security panel '
                                    'older than the station itself.',
                     'exits': [{'type': 'Exit',
                                'direction': 'south',
                                'destination': 'service',
                                'requires_item': None,
                                'requires_flag': None,
                                'blocked': False,
                                'blocked_text': 'That path is blocked.',
                                'warning_text': None,
                                'on_attempt_effect': None,
                                'on_blocked_effect': None,
                                'on_success_effect': None},
                               {'type': 'Exit',
                                'direction': 'north',
                                'destination': 'archive',
                                'requires_item': None,
                                'requires_flag': 'archive_opened',
                                'blocked': False,
                                'blocked_text': 'The archive door is deadlocked. You need to spoof '
                                                'the panel first.',
                                'warning_text': None,
                                'on_attempt_effect': None,
                                'on_blocked_effect': None,
                                'on_success_effect': None}],
                     'items': [],
                     'npcs': [{'type': 'GuardNPC',
                               'name': 'Marshal Sorn',
                               'base_stats': {'type': 'Stats',
                                              'max_hp': 45,
                                              'attack_min': 6,
                                              'attack_max': 9,
                                              'defense': 2},
                               'location': 'annex',
                               'health': 45,
                               'gold': 15,
                               'inventory': ['pressure_weave', 'med_patch'],
                               'equipment': {'weapon': None,
                                             'armor': 'pressure_weave',
                                             'charm': None},
                               'description': 'A station marshal posted to a job too quiet to stay '
                                              'honest for long.',
                               'tags': ['guard', 'law'],
                               'aggression': 40,
                               'courage': 85,
                               'willingness_to_trade': 0,
                               'hostile': False,
                               'dialogue_topics': [{'type': 'DialogueTopic',
                                                    'key': 'marshal_bluff',
                                                    'title': 'Ask who still uses this annex',
                                                    'lines': ['Claims division, when it wants '
                                                              'something forgotten instead of '
                                                              'processed.',
                                                              'That should tell you enough to turn '
                                                              'around.'],
                                                    'required_flags': [],
                                                    'blocked_flags': [],
                                                    'required_items': [],
                                                    'once': False,
                                                    'outcome_effect': None}],
                               'trade_offers': [],
                               'riddle': None,
                               'surrender_at_ratio': None,
                               'surrender_lines': [],
                               'surrender_trade_offers': [],
                               'peaceful_after_surrender': True,
                               'surrender_accept_lines': ['Down. Hands where I can see them.',
                                                          'You can try again after you cool off in '
                                                          'the brig.'],
                               'surrender_reject_lines': [],
                               'surrender_accept_effect': {'type': 'CompositeEffect',
                                                           'effects': [{'type': 'SetFlagEffect',
                                                                        'flags': ['jailed']},
                                                                       {'type': 'SetBountyEffect',
                                                                        'amount': 0},
                                                                       {'type': 'MovePlayerEffect',
                                                                        'destination': 'brig',
                                                                        'text': 'Marshal Sorn '
                                                                                'knocks the fight '
                                                                                'out of you and '
                                                                                'drops you in the '
                                                                                'transit brig.'}]},
                               'defeat_lines': [],
                               'reward_items': [],
                               'reward_flags': [],
                               'reward_gold': 0,
                               'persistent': True,
                               'used_topics': [],
                               'completed_trades': [],
                               'surrendered': False,
                               'riddle_solved': False,
                               'defeated': False}],
                     'features': [{'type': 'ScriptedFeature',
                                   'name': 'security panel',
                                   'verb': 'Spoof',
                                   'required_flags': ['act1_started'],
                                   'blocked_text': 'You do not even have a job yet.',
                                   'once_flag': 'archive_opened',
                                   'first_effect': {'type': 'ConditionalEffect',
                                                    'required_flags': [],
                                                    'blocked_flags': [],
                                                    'required_items': ['spoofer'],
                                                    'success_effect': {'type': 'CompositeEffect',
                                                                       'effects': [{'type': 'PrintEffect',
                                                                                    'lines': ['You '
                                                                                              'jack '
                                                                                              'the '
                                                                                              'spoofer '
                                                                                              'into '
                                                                                              'the '
                                                                                              'old '
                                                                                              'panel.',
                                                                                              'The '
                                                                                              'archive '
                                                                                              'lock '
                                                                                              'chatters, '
                                                                                              'hesitates, '
                                                                                              'and '
                                                                                              'finally '
                                                                                              'rolls '
                                                                                              'open.']},
                                                                                   {'type': 'SetFlagEffect',
                                                                                    'flags': ['archive_opened']}]},
                                                    'failure_effect': {'type': 'PrintEffect',
                                                                       'lines': ['You need the '
                                                                                 'port spoofer '
                                                                                 'Mina promised '
                                                                                 'before this '
                                                                                 'panel will do '
                                                                                 'anything '
                                                                                 'useful.']}},
                                   'repeat_effect': {'type': 'PrintEffect',
                                                     'lines': ['The archive lock is already '
                                                               'hanging open.']}}],
                     'choices': []},
           'archive': {'key': 'archive',
                       'name': 'Black Archive',
                       'description': 'A temperature-controlled records vault full of payroll '
                                      'wafers, claim ledgers, and sealed survey debris no one was '
                                      'meant to notice.',
                       'exits': [{'type': 'Exit',
                                  'direction': 'south',
                                  'destination': 'annex',
                                  'requires_item': None,
                                  'requires_flag': None,
                                  'blocked': False,
                                  'blocked_text': 'That path is blocked.',
                                  'warning_text': None,
                                  'on_attempt_effect': None,
                                  'on_blocked_effect': None,
                                  'on_success_effect': None}],
                       'items': ['payroll_shard'],
                       'npcs': [],
                       'features': [{'type': 'ScriptedFeature',
                                     'name': 'red locker',
                                     'verb': 'Crack',
                                     'required_flags': ['archive_opened'],
                                     'blocked_text': 'You should get inside the archive properly '
                                                     'first.',
                                     'once_flag': 'red_locker_hit',
                                     'first_effect': {'type': 'CompositeEffect',
                                                      'effects': [{'type': 'PrintEffect',
                                                                   'lines': ['You force the red '
                                                                             'locker and sweep the '
                                                                             'contents into your '
                                                                             'bag.',
                                                                             'A silent trip wakes '
                                                                             'somewhere in the '
                                                                             'wall. You have what '
                                                                             'you wanted, but the '
                                                                             'job is no longer '
                                                                             'clean.']},
                                                                  {'type': 'GivePlayerItemEffect',
                                                                   'item_ids': ['survey_canister']},
                                                                  {'type': 'ChangeGoldEffect',
                                                                   'amount': 12,
                                                                   'target': 'player',
                                                                   'reason': 'Loose station credit '
                                                                             'and bonded scrip'},
                                                                  {'type': 'ChangeBountyEffect',
                                                                   'amount': 45,
                                                                   'reason': 'You tripped the '
                                                                             'archive side '
                                                                             'locker'}]},
                                     'repeat_effect': {'type': 'PrintEffect',
                                                       'lines': ['You already stripped the red '
                                                                 'locker.']}},
                                    {'type': 'ScriptedFeature',
                                     'name': 'sealed terminal',
                                     'verb': 'Read',
                                     'required_flags': [],
                                     'blocked_text': 'Nothing happens.',
                                     'once_flag': 'saw_suppressed_log',
                                     'first_effect': {'type': 'PrintEffect',
                                                      'lines': ['A suppressed log flashes up '
                                                                'before the terminal wipes itself.',
                                                                'Survey World MV-241. Deep '
                                                                'anomaly. All crew claims frozen. '
                                                                'Site sealed by order of claims '
                                                                'division.',
                                                                'Someone buried a find on this '
                                                                'world and then buried the record '
                                                                'of finding it.']},
                                     'repeat_effect': {'type': 'PrintEffect',
                                                       'lines': ['The terminal is blank now, but '
                                                                 'you still remember the world '
                                                                 'code.']}}],
                       'choices': []},
           'shuttle': {'key': 'shuttle',
                       'name': 'Extraction Pad',
                       'description': 'A utility skiff waits on mag clamps beside a yawning lock '
                                      'and a view of black space.',
                       'exits': [{'type': 'Exit',
                                  'direction': 'west',
                                  'destination': 'service',
                                  'requires_item': None,
                                  'requires_flag': None,
                                  'blocked': False,
                                  'blocked_text': 'That path is blocked.',
                                  'warning_text': None,
                                  'on_attempt_effect': None,
                                  'on_blocked_effect': None,
                                  'on_success_effect': None}],
                       'items': [],
                       'npcs': [],
                       'features': [{'type': 'ScriptedFeature',
                                     'name': 'extraction skiff',
                                     'verb': 'Board',
                                     'required_flags': ['has_payroll_shard'],
                                     'blocked_text': 'There is no point running for extraction '
                                                     'before you have the payroll shard.',
                                     'once_flag': 'left_station',
                                     'first_effect': {'type': 'BranchOnBountyEffect',
                                                      'clean_effect': {'type': 'CompositeEffect',
                                                                       'effects': [{'type': 'PrintEffect',
                                                                                    'lines': ['Rafe '
                                                                                              'checks '
                                                                                              'the '
                                                                                              'shard, '
                                                                                              'studies '
                                                                                              'you '
                                                                                              'for '
                                                                                              'a '
                                                                                              'second, '
                                                                                              'and '
                                                                                              'almost '
                                                                                              'smiles.',
                                                                                              'Clean '
                                                                                              'lift. '
                                                                                              'No '
                                                                                              'alarms '
                                                                                              'worth '
                                                                                              'caring '
                                                                                              'about. '
                                                                                              'He '
                                                                                              'promotes '
                                                                                              'you '
                                                                                              'on '
                                                                                              'the '
                                                                                              'spot '
                                                                                              'and '
                                                                                              'hands '
                                                                                              'you '
                                                                                              'a '
                                                                                              'proper '
                                                                                              'field '
                                                                                              'assignment.',
                                                                                              'The '
                                                                                              'side '
                                                                                              'log '
                                                                                              'from '
                                                                                              'the '
                                                                                              'archive '
                                                                                              'mentioned '
                                                                                              'a '
                                                                                              'dead '
                                                                                              'survey '
                                                                                              'world. '
                                                                                              'Rafe '
                                                                                              'wants '
                                                                                              'first '
                                                                                              'rights '
                                                                                              'to '
                                                                                              'whatever '
                                                                                              'was '
                                                                                              'buried '
                                                                                              'there, '
                                                                                              'and '
                                                                                              'now '
                                                                                              'you '
                                                                                              'are '
                                                                                              'trusted '
                                                                                              'enough '
                                                                                              'to '
                                                                                              'go '
                                                                                              'look.']},
                                                                                   {'type': 'GivePlayerItemEffect',
                                                                                    'item_ids': ['cutter_rifle',
                                                                                                 'pressure_weave',
                                                                                                 'claim_marker',
                                                                                                 'med_patch']},
                                                                                   {'type': 'ChangeGoldEffect',
                                                                                    'amount': 18,
                                                                                    'target': 'player',
                                                                                    'reason': 'Promotion '
                                                                                              'cut '
                                                                                              'and '
                                                                                              'expedition '
                                                                                              'advance'},
                                                                                   {'type': 'SetBountyEffect',
                                                                                    'amount': 0},
                                                                                   {'type': 'SetFlagEffect',
                                                                                    'flags': ['promoted',
                                                                                              'act2_started',
                                                                                              'heard_artifact_tip']},
                                                                                   {'type': 'MovePlayerEffect',
                                                                                    'destination': 'survey_pad',
                                                                                    'text': 'Hours '
                                                                                            'later '
                                                                                            'the '
                                                                                            'skiff '
                                                                                            'sets '
                                                                                            'down '
                                                                                            'on a '
                                                                                            'survey '
                                                                                            'pad '
                                                                                            'under '
                                                                                            'a '
                                                                                            'hard '
                                                                                            'white '
                                                                                            'sky.'}]},
                                                      'hot_effect': {'type': 'CompositeEffect',
                                                                     'effects': [{'type': 'PrintEffect',
                                                                                  'lines': ['Rafe '
                                                                                            'clocks '
                                                                                            'the '
                                                                                            'heat '
                                                                                            'before '
                                                                                            'you '
                                                                                            'even '
                                                                                            'make '
                                                                                            'the '
                                                                                            'ramp.',
                                                                                            'He '
                                                                                            'says '
                                                                                            'nothing '
                                                                                            'on '
                                                                                            'the '
                                                                                            'ride '
                                                                                            'down '
                                                                                            'to '
                                                                                            'the '
                                                                                            'surface. '
                                                                                            'When '
                                                                                            'the '
                                                                                            'skiff '
                                                                                            'drops '
                                                                                            'through '
                                                                                            'dust '
                                                                                            'over '
                                                                                            'the '
                                                                                            'survey '
                                                                                            'world, '
                                                                                            'the '
                                                                                            'crew '
                                                                                            'shoves '
                                                                                            'you '
                                                                                            'into '
                                                                                            'an '
                                                                                            'emergency '
                                                                                            'coffin '
                                                                                            'with '
                                                                                            'your '
                                                                                            'knife '
                                                                                            'and '
                                                                                            'not '
                                                                                            'much '
                                                                                            'else.',
                                                                                            'You '
                                                                                            'hit '
                                                                                            'the '
                                                                                            'ground '
                                                                                            'alone. '
                                                                                            'The '
                                                                                            'skiff '
                                                                                            'never '
                                                                                            'comes '
                                                                                            'back.']},
                                                                                 {'type': 'SetBountyEffect',
                                                                                  'amount': 0},
                                                                                 {'type': 'SetFlagEffect',
                                                                                  'flags': ['stranded',
                                                                                            'act2_started',
                                                                                            'heard_artifact_tip']},
                                                                                 {'type': 'DamageCharacterEffect',
                                                                                  'target': 'player',
                                                                                  'amount': 12,
                                                                                  'text': None},
                                                                                 {'type': 'MovePlayerEffect',
                                                                                  'destination': 'crash_gully',
                                                                                  'text': 'You '
                                                                                          'wake in '
                                                                                          'broken '
                                                                                          'fiberglass '
                                                                                          'and '
                                                                                          'dust on '
                                                                                          'a world '
                                                                                          'you '
                                                                                          'were '
                                                                                          'never '
                                                                                          'meant '
                                                                                          'to '
                                                                                          'see.'}]},
                                                      'threshold': 0},
                                     'repeat_effect': {'type': 'PrintEffect',
                                                       'lines': ['The station is behind you '
                                                                 'now.']}}],
                       'choices': []},
           'brig': {'key': 'brig',
                    'name': 'Transit Brig',
                    'description': 'A narrow holding box bolted beside the docking arms. It smells '
                                   'of coolant, bruises, and bad judgment.',
                    'exits': [],
                    'items': [],
                    'npcs': [],
                    'features': [{'type': 'ScriptedFeature',
                                  'name': 'brig bench',
                                  'verb': 'Wait on',
                                  'required_flags': ['jailed'],
                                  'blocked_text': 'No one is holding you here right now.',
                                  'once_flag': None,
                                  'first_effect': {'type': 'CompositeEffect',
                                                   'effects': [{'type': 'PrintEffect',
                                                                'lines': ['You let the station '
                                                                          'clock grind away your '
                                                                          'temper.',
                                                                          'Eventually a bored '
                                                                          'deputy vents you back '
                                                                          'toward the freight '
                                                                          'decks.']},
                                                               {'type': 'SetBountyEffect',
                                                                'amount': 0},
                                                               {'type': 'ClearFlagEffect',
                                                                'flags': ['jailed']},
                                                               {'type': 'MovePlayerEffect',
                                                                'destination': 'berth',
                                                                'text': 'You are dumped back at '
                                                                        'Ring Berth Three.'},
                                                               {'type': 'HealPlayerEffect',
                                                                'amount': 999,
                                                                'heal_text': 'Time and water do '
                                                                             'some repair.',
                                                                'full_text': 'You are already '
                                                                             'steady enough.'}]},
                                  'repeat_effect': None}],
                    'choices': []},
           'survey_pad': {'key': 'survey_pad',
                          'name': 'Survey Pad',
                          'description': 'A prefab landing pad baked hard by years of dust. The '
                                         'horizon is all rock, wind, and abandoned equipment.',
                          'exits': [{'type': 'Exit',
                                     'direction': 'south',
                                     'destination': 'windbreak',
                                     'requires_item': None,
                                     'requires_flag': None,
                                     'blocked': False,
                                     'blocked_text': 'That path is blocked.',
                                     'warning_text': None,
                                     'on_attempt_effect': None,
                                     'on_blocked_effect': None,
                                     'on_success_effect': None}],
                          'items': ['med_patch'],
                          'npcs': [],
                          'features': [],
                          'choices': []},
           'crash_gully': {'key': 'crash_gully',
                           'name': 'Crash Gully',
                           'description': 'A twisted escape coffin lies cracked open between stone '
                                          'ribs and drifting dust.',
                           'exits': [{'type': 'Exit',
                                      'direction': 'east',
                                      'destination': 'windbreak',
                                      'requires_item': None,
                                      'requires_flag': None,
                                      'blocked': False,
                                      'blocked_text': 'That path is blocked.',
                                      'warning_text': None,
                                      'on_attempt_effect': None,
                                      'on_blocked_effect': None,
                                      'on_success_effect': None}],
                           'items': ['med_patch'],
                           'npcs': [],
                           'features': [],
                           'choices': []},
           'windbreak': {'key': 'windbreak',
                         'name': 'Windbreak Camp',
                         'description': 'A lean-to camp built from survey panels and rover doors. '
                                        'Someone here survived by becoming harder than the planet.',
                         'exits': [{'type': 'Exit',
                                    'direction': 'north',
                                    'destination': 'survey_pad',
                                    'requires_item': None,
                                    'requires_flag': None,
                                    'blocked': False,
                                    'blocked_text': 'That path is blocked.',
                                    'warning_text': None,
                                    'on_attempt_effect': None,
                                    'on_blocked_effect': None,
                                    'on_success_effect': None},
                                   {'type': 'Exit',
                                    'direction': 'west',
                                    'destination': 'crash_gully',
                                    'requires_item': None,
                                    'requires_flag': None,
                                    'blocked': False,
                                    'blocked_text': 'That path is blocked.',
                                    'warning_text': None,
                                    'on_attempt_effect': None,
                                    'on_blocked_effect': None,
                                    'on_success_effect': None},
                                   {'type': 'Exit',
                                    'direction': 'east',
                                    'destination': 'habitat',
                                    'requires_item': None,
                                    'requires_flag': None,
                                    'blocked': False,
                                    'blocked_text': 'That path is blocked.',
                                    'warning_text': None,
                                    'on_attempt_effect': None,
                                    'on_blocked_effect': None,
                                    'on_success_effect': None},
                                   {'type': 'Exit',
                                    'direction': 'west',
                                    'destination': 'pump',
                                    'requires_item': None,
                                    'requires_flag': None,
                                    'blocked': False,
                                    'blocked_text': 'That path is blocked.',
                                    'warning_text': None,
                                    'on_attempt_effect': None,
                                    'on_blocked_effect': None,
                                    'on_success_effect': None},
                                   {'type': 'Exit',
                                    'direction': 'north',
                                    'destination': 'relay',
                                    'requires_item': None,
                                    'requires_flag': None,
                                    'blocked': False,
                                    'blocked_text': 'That path is blocked.',
                                    'warning_text': None,
                                    'on_attempt_effect': None,
                                    'on_blocked_effect': None,
                                    'on_success_effect': None}],
                         'items': [],
                         'npcs': [{'type': 'MerchantNPC',
                                   'name': 'Orla Quist',
                                   'base_stats': {'type': 'Stats',
                                                  'max_hp': 35,
                                                  'attack_min': 4,
                                                  'attack_max': 6,
                                                  'defense': 1},
                                   'location': 'windbreak',
                                   'health': 35,
                                   'gold': 40,
                                   'inventory': ['line_spool',
                                                 'med_patch',
                                                 'med_patch',
                                                 'stim_dose'],
                                   'equipment': {'weapon': None, 'armor': None, 'charm': None},
                                   'description': 'A scavenger-mechanic who has made a life out of '
                                                  'dead survey hardware and careful distrust.',
                                   'tags': [],
                                   'aggression': 10,
                                   'courage': 40,
                                   'willingness_to_trade': 90,
                                   'hostile': False,
                                   'dialogue_topics': [{'type': 'DialogueTopic',
                                                        'key': 'orla_intro',
                                                        'title': 'Ask how she survived here',
                                                        'lines': ['By staying useful and never '
                                                                  'standing where companies last '
                                                                  'saw me.',
                                                                  'This world eats plans. Learn to '
                                                                  'travel with spares.'],
                                                        'required_flags': [],
                                                        'blocked_flags': [],
                                                        'required_items': [],
                                                        'once': False,
                                                        'outcome_effect': None},
                                                       {'type': 'DialogueTopic',
                                                        'key': 'orla_tip',
                                                        'title': 'Ask about the buried site',
                                                        'lines': ['People came here for ore and '
                                                                  'left whispering about a hollow '
                                                                  'under the plateau.',
                                                                  'Whatever they found, claims '
                                                                  'division buried the hole and '
                                                                  'the workers with the '
                                                                  'paperwork.'],
                                                        'required_flags': ['act2_started'],
                                                        'blocked_flags': [],
                                                        'required_items': [],
                                                        'once': False,
                                                        'outcome_effect': None}],
                                   'trade_offers': [{'type': 'TradeOffer',
                                                     'title': 'Buy Line Spool for 5 gold',
                                                     'wants_items': [],
                                                     'gives_items': ['line_spool'],
                                                     'wants_gold': 5,
                                                     'gives_gold': 0,
                                                     'repeatable': False,
                                                     'required_flags': [],
                                                     'blocked_flags': []},
                                                    {'type': 'TradeOffer',
                                                     'title': 'Buy Med Patch for 6 gold',
                                                     'wants_items': [],
                                                     'gives_items': ['med_patch'],
                                                     'wants_gold': 6,
                                                     'gives_gold': 0,
                                                     'repeatable': True,
                                                     'required_flags': [],
                                                     'blocked_flags': []},
                                                    {'type': 'TradeOffer',
                                                     'title': 'Buy Stim Dose for 11 gold',
                                                     'wants_items': [],
                                                     'gives_items': ['stim_dose'],
                                                     'wants_gold': 11,
                                                     'gives_gold': 0,
                                                     'repeatable': True,
                                                     'required_flags': [],
                                                     'blocked_flags': []}],
                                   'riddle': None,
                                   'surrender_at_ratio': None,
                                   'surrender_lines': [],
                                   'surrender_trade_offers': [],
                                   'peaceful_after_surrender': True,
                                   'surrender_accept_lines': [],
                                   'surrender_reject_lines': [],
                                   'surrender_accept_effect': None,
                                   'defeat_lines': [],
                                   'reward_items': [],
                                   'reward_flags': [],
                                   'reward_gold': 0,
                                   'persistent': True,
                                   'used_topics': [],
                                   'completed_trades': [],
                                   'surrendered': False,
                                   'riddle_solved': False,
                                   'defeated': False}],
                         'features': [{'type': 'ScriptedFeature',
                                       'name': 'field stove',
                                       'verb': 'Rest at',
                                       'required_flags': [],
                                       'blocked_text': 'Nothing happens.',
                                       'once_flag': None,
                                       'first_effect': {'type': 'HealPlayerEffect',
                                                        'amount': 18,
                                                        'heal_text': 'You sit by the stove and let '
                                                                     'your hands stop shaking.',
                                                        'full_text': 'You already feel as rested '
                                                                     'as this camp can make you.'},
                                       'repeat_effect': None},
                                      {'type': 'ScriptedFeature',
                                       'name': 'landing beacon',
                                       'verb': 'Answer',
                                       'required_flags': ['has_grave_core', 'rafe_offer_heard'],
                                       'blocked_text': 'No one is waiting for your answer yet.',
                                       'once_flag': 'ending_corporate',
                                       'first_effect': {'type': 'EndGameEffect',
                                                        'lines': ["You answer Rafe's beacon and "
                                                                  'hand over the grave core for '
                                                                  'extraction, pay, and a promised '
                                                                  'place higher up the chain.',
                                                                  'Within weeks the survey world '
                                                                  'is fenced, drilled, and '
                                                                  'stripped. Everyone who helped '
                                                                  'you is bought off, pushed out, '
                                                                  'or buried under paperwork and '
                                                                  'private security.',
                                                                  'You got exactly what a '
                                                                  'successful heist is supposed to '
                                                                  'buy: a future. It just was not '
                                                                  'a future anyone else here got '
                                                                  'to share.',
                                                                  'Ending: Sell the vault.'],
                                                        'flags': ['ending_corporate', 'game_won']},
                                       'repeat_effect': {'type': 'PrintEffect',
                                                         'lines': ['The beacon has already done '
                                                                   'its work.']}}],
                         'choices': []},
           'relay': {'key': 'relay',
                     'name': 'Relay Ridge',
                     'description': 'A ridge line crowned by a dead survey mast and snapped '
                                    'antenna spars.',
                     'exits': [{'type': 'Exit',
                                'direction': 'south',
                                'destination': 'windbreak',
                                'requires_item': None,
                                'requires_flag': None,
                                'blocked': False,
                                'blocked_text': 'That path is blocked.',
                                'warning_text': None,
                                'on_attempt_effect': None,
                                'on_blocked_effect': None,
                                'on_success_effect': None}],
                     'items': [],
                     'npcs': [],
                     'features': [{'type': 'ScriptedFeature',
                                   'name': 'survey mast',
                                   'verb': 'Align',
                                   'required_flags': [],
                                   'blocked_text': 'Nothing happens.',
                                   'once_flag': 'relay_aligned',
                                   'first_effect': {'type': 'CompositeEffect',
                                                    'effects': [{'type': 'PrintEffect',
                                                                 'lines': ['You wrestle the dead '
                                                                           'mast into one last '
                                                                           'sweep.',
                                                                           'A locator chart spills '
                                                                           'across the cracked '
                                                                           'screen, along with a '
                                                                           'lamp cached for '
                                                                           'emergency descent '
                                                                           'work.']},
                                                                {'type': 'GivePlayerItemEffect',
                                                                 'item_ids': ['locator_chart',
                                                                              'coldlamp']}]},
                                   'repeat_effect': {'type': 'PrintEffect',
                                                     'lines': ['The mast has already given you '
                                                               'everything it had left.']}}],
                     'choices': []},
           'habitat': {'key': 'habitat',
                       'name': 'Habitat Shell',
                       'description': 'An abandoned habitat ring slumps into the dust, half buried '
                                      'but still full of airless rooms and old voices.',
                       'exits': [{'type': 'Exit',
                                  'direction': 'west',
                                  'destination': 'windbreak',
                                  'requires_item': None,
                                  'requires_flag': None,
                                  'blocked': False,
                                  'blocked_text': 'That path is blocked.',
                                  'warning_text': None,
                                  'on_attempt_effect': None,
                                  'on_blocked_effect': None,
                                  'on_success_effect': None},
                                 {'type': 'Exit',
                                  'direction': 'north',
                                  'destination': 'crater',
                                  'requires_item': 'vault_cipher',
                                  'requires_flag': 'found_locator',
                                  'blocked': False,
                                  'blocked_text': 'Without the locator chart and a matching '
                                                  'cipher, the crater is just another dead hole in '
                                                  'the ground.',
                                  'warning_text': None,
                                  'on_attempt_effect': None,
                                  'on_blocked_effect': None,
                                  'on_success_effect': None}],
                       'items': ['claim_marker'],
                       'npcs': [{'type': 'ElderNPC',
                                 'name': 'Juno Hale',
                                 'base_stats': {'type': 'Stats',
                                                'max_hp': 40,
                                                'attack_min': 4,
                                                'attack_max': 7,
                                                'defense': 0},
                                 'location': 'habitat',
                                 'health': 40,
                                 'gold': 5,
                                 'inventory': ['med_patch'],
                                 'equipment': {'weapon': None, 'armor': None, 'charm': None},
                                 'description': 'A former survey geologist who stayed when the '
                                                'company wrote the planet off. Dust has taken the '
                                                'softness out of her voice, not the memory.',
                                 'tags': [],
                                 'aggression': 5,
                                 'courage': 20,
                                 'willingness_to_trade': 15,
                                 'hostile': False,
                                 'dialogue_topics': [{'type': 'DialogueTopic',
                                                      'key': 'juno_planet',
                                                      'title': 'Ask what the survey team found',
                                                      'lines': ['Not ore. Not a ruin exactly. A '
                                                                'machine complex sealed under the '
                                                                'plateau like the world had grown '
                                                                'around it.',
                                                                'Claims division froze the '
                                                                'reports, killed the dig, and told '
                                                                'us to forget where we had '
                                                                'drilled.'],
                                                      'required_flags': [],
                                                      'blocked_flags': ['truth_known'],
                                                      'required_items': [],
                                                      'once': True,
                                                      'outcome_effect': {'type': 'SetFlagEffect',
                                                                         'flags': ['truth_known']}},
                                                     {'type': 'DialogueTopic',
                                                      'key': 'juno_canister',
                                                      'title': 'Show the survey canister',
                                                      'lines': ['I remember this casing. It held '
                                                                'the first field core they pulled '
                                                                'out before they resealed the '
                                                                'shaft.',
                                                                'The artifact is not the prize. It '
                                                                'is the key they used to wake the '
                                                                'rest of the place.'],
                                                      'required_flags': [],
                                                      'blocked_flags': ['canister_discussed'],
                                                      'required_items': ['survey_canister'],
                                                      'once': True,
                                                      'outcome_effect': {'type': 'SetFlagEffect',
                                                                         'flags': ['truth_known',
                                                                                   'canister_discussed']}},
                                                     {'type': 'DialogueTopic',
                                                      'key': 'juno_end',
                                                      'title': 'Ask what to do with the grave core',
                                                      'lines': ['If you hand it back to the kind '
                                                                'of people who bury worlds, they '
                                                                'will own this place before the '
                                                                'dust settles.',
                                                                'If you show everyone what it is, '
                                                                'the lies stop, but the scramble '
                                                                'begins. Frontier truth is '
                                                                'expensive that way.'],
                                                      'required_flags': ['has_grave_core'],
                                                      'blocked_flags': [],
                                                      'required_items': [],
                                                      'once': False,
                                                      'outcome_effect': None}],
                                 'trade_offers': [],
                                 'riddle': None,
                                 'surrender_at_ratio': None,
                                 'surrender_lines': [],
                                 'surrender_trade_offers': [],
                                 'peaceful_after_surrender': True,
                                 'surrender_accept_lines': [],
                                 'surrender_reject_lines': [],
                                 'surrender_accept_effect': None,
                                 'defeat_lines': [],
                                 'reward_items': [],
                                 'reward_flags': [],
                                 'reward_gold': 0,
                                 'persistent': True,
                                 'used_topics': [],
                                 'completed_trades': [],
                                 'surrendered': False,
                                 'riddle_solved': False,
                                 'defeated': False}],
                       'features': [{'type': 'ScriptedFeature',
                                     'name': 'archive uplink',
                                     'verb': 'Broadcast through',
                                     'required_flags': ['has_grave_core', 'truth_known'],
                                     'blocked_text': 'Without the grave core and the truth of what '
                                                     'this place is, the uplink is just a dead '
                                                     'frame.',
                                     'once_flag': 'ending_broadcast',
                                     'first_effect': {'type': 'EndGameEffect',
                                                      'lines': ['You wire the grave core into the '
                                                                'habitat uplink and flood every '
                                                                'claims relay you can reach with '
                                                                'the buried archive.',
                                                                'By dawn the planet is no longer a '
                                                                'rumor. It is evidence, territory, '
                                                                'scandal, and war all at once.',
                                                                'The company cannot bury the find '
                                                                'again, but the people still '
                                                                'living here will now endure the '
                                                                'kind of attention that kills more '
                                                                'slowly than a bullet.',
                                                                'Ending: Broadcast the truth.'],
                                                      'flags': ['ending_broadcast', 'game_won']},
                                     'repeat_effect': {'type': 'PrintEffect',
                                                       'lines': ['The uplink is already screaming '
                                                                 'the truth into the void.']}}],
                       'choices': []},
           'pump': {'key': 'pump',
                    'name': 'Pump House',
                    'description': 'A concrete utility bunker feeding ancient lines into the '
                                   'plateau. Its machinery knocks like a failing heart.',
                    'exits': [{'type': 'Exit',
                               'direction': 'east',
                               'destination': 'windbreak',
                               'requires_item': None,
                               'requires_flag': None,
                               'blocked': False,
                               'blocked_text': 'That path is blocked.',
                               'warning_text': None,
                               'on_attempt_effect': None,
                               'on_blocked_effect': None,
                               'on_success_effect': None},
                              {'type': 'Exit',
                               'direction': 'north',
                               'destination': 'ravine',
                               'requires_item': None,
                               'requires_flag': 'bridge_powered',
                               'blocked': False,
                               'blocked_text': 'The access bridge has no power. The ravine is too '
                                               'wide to cross by foot.',
                               'warning_text': None,
                               'on_attempt_effect': None,
                               'on_blocked_effect': None,
                               'on_success_effect': None}],
                    'items': ['med_patch'],
                    'npcs': [],
                    'features': [{'type': 'ScriptedFeature',
                                  'name': 'bridge control',
                                  'verb': 'Start',
                                  'required_flags': [],
                                  'blocked_text': 'Nothing happens.',
                                  'once_flag': 'bridge_powered',
                                  'first_effect': {'type': 'CompositeEffect',
                                                   'effects': [{'type': 'PrintEffect',
                                                                'lines': ['You kick the old pumps '
                                                                          'awake and route power '
                                                                          'into the ravine bridge.',
                                                                          'Somewhere out in the '
                                                                          'dust, metal begins to '
                                                                          'move again.']},
                                                               {'type': 'SetFlagEffect',
                                                                'flags': ['bridge_powered']}]},
                                  'repeat_effect': {'type': 'PrintEffect',
                                                    'lines': ['The bridge control is already '
                                                              'humming.']}}],
                    'choices': []},
           'ravine': {'key': 'ravine',
                      'name': 'Glass Ravine',
                      'description': 'A cut of fused stone and brittle mineral sheets. Every step '
                                     'sounds like something ready to break.',
                      'exits': [{'type': 'Exit',
                                 'direction': 'south',
                                 'destination': 'pump',
                                 'requires_item': None,
                                 'requires_flag': None,
                                 'blocked': False,
                                 'blocked_text': 'That path is blocked.',
                                 'warning_text': None,
                                 'on_attempt_effect': None,
                                 'on_blocked_effect': None,
                                 'on_success_effect': None},
                                {'type': 'Exit',
                                 'direction': 'east',
                                 'destination': 'drill',
                                 'requires_item': 'line_spool',
                                 'requires_flag': None,
                                 'blocked': False,
                                 'blocked_text': 'The far side is reachable only with an anchor '
                                                 'line.',
                                 'warning_text': 'The glass shelves crack under every step. Cross '
                                                 'anyway?',
                                 'on_attempt_effect': None,
                                 'on_blocked_effect': None,
                                 'on_success_effect': {'type': 'ChanceEffect',
                                                       'chance': 0.35,
                                                       'success_effect': {'type': 'CompositeEffect',
                                                                          'effects': [{'type': 'PrintEffect',
                                                                                       'lines': ['The '
                                                                                                 'shelf '
                                                                                                 'snaps '
                                                                                                 'under '
                                                                                                 'you '
                                                                                                 'for '
                                                                                                 'half '
                                                                                                 'a '
                                                                                                 'breath '
                                                                                                 'before '
                                                                                                 'the '
                                                                                                 'line '
                                                                                                 'catches. '
                                                                                                 'Stone '
                                                                                                 'and '
                                                                                                 'glass '
                                                                                                 'rake '
                                                                                                 'your '
                                                                                                 'arms '
                                                                                                 'as '
                                                                                                 'you '
                                                                                                 'swing '
                                                                                                 'across.']},
                                                                                      {'type': 'DamageCharacterEffect',
                                                                                       'target': 'player',
                                                                                       'amount': 7,
                                                                                       'text': None}]},
                                                       'failure_effect': {'type': 'PrintEffect',
                                                                          'lines': ['You clip the '
                                                                                    'line and '
                                                                                    'cross the '
                                                                                    'ravine '
                                                                                    'without '
                                                                                    'incident.']}}}],
                      'items': [],
                      'npcs': [],
                      'features': [],
                      'choices': []},
           'drill': {'key': 'drill',
                     'name': 'Drill Site Theta',
                     'description': 'A stripped drill yard surrounds a collapsed bore and a crane '
                                    'frozen mid-lift.',
                     'exits': [{'type': 'Exit',
                                'direction': 'west',
                                'destination': 'ravine',
                                'requires_item': None,
                                'requires_flag': None,
                                'blocked': False,
                                'blocked_text': 'That path is blocked.',
                                'warning_text': None,
                                'on_attempt_effect': None,
                                'on_blocked_effect': None,
                                'on_success_effect': None}],
                     'items': [],
                     'npcs': [{'type': 'BanditNPC',
                               'name': 'Cade Voss',
                               'base_stats': {'type': 'Stats',
                                              'max_hp': 28,
                                              'attack_min': 5,
                                              'attack_max': 9,
                                              'defense': 1},
                               'location': 'drill',
                               'health': 28,
                               'gold': 18,
                               'inventory': ['vault_cipher', 'med_patch'],
                               'equipment': {'weapon': 'utility_knife',
                                             'armor': None,
                                             'charm': None},
                               'description': 'A rival salvage runner stripping the drill yard for '
                                              'anything portable and profitable.',
                               'tags': [],
                               'aggression': 70,
                               'courage': 35,
                               'willingness_to_trade': 10,
                               'hostile': False,
                               'dialogue_topics': [{'type': 'DialogueTopic',
                                                    'key': 'cade_claim',
                                                    'title': 'Ask what he found here',
                                                    'lines': ['A cipher rod, a dead crane, and '
                                                              'proof that everyone on this rock is '
                                                              "late to somebody else's score.",
                                                              'You want the rod, bring money or '
                                                              'bring blood.'],
                                                    'required_flags': [],
                                                    'blocked_flags': [],
                                                    'required_items': [],
                                                    'once': False,
                                                    'outcome_effect': None}],
                               'trade_offers': [{'type': 'TradeOffer',
                                                 'title': 'Buy Vault Cipher for 12 gold',
                                                 'wants_items': [],
                                                 'gives_items': ['vault_cipher'],
                                                 'wants_gold': 12,
                                                 'gives_gold': 0,
                                                 'repeatable': False,
                                                 'required_flags': [],
                                                 'blocked_flags': []}],
                               'riddle': None,
                               'surrender_at_ratio': 0.25,
                               'surrender_lines': ['All right. Enough. I am not dying for a cipher '
                                                   'rod.',
                                                   'Take the rod or trade for it. I am done '
                                                   'bleeding over survey junk.'],
                               'surrender_trade_offers': [{'type': 'TradeOffer',
                                                           'title': 'Take Vault Cipher for 5 gold',
                                                           'wants_items': [],
                                                           'gives_items': ['vault_cipher'],
                                                           'wants_gold': 5,
                                                           'gives_gold': 0,
                                                           'repeatable': False,
                                                           'required_flags': [],
                                                           'blocked_flags': []}],
                               'peaceful_after_surrender': True,
                               'surrender_accept_lines': [],
                               'surrender_reject_lines': [],
                               'surrender_accept_effect': None,
                               'defeat_lines': [],
                               'reward_items': [],
                               'reward_flags': [],
                               'reward_gold': 8,
                               'persistent': True,
                               'used_topics': [],
                               'completed_trades': [],
                               'surrendered': False,
                               'riddle_solved': False,
                               'defeated': False}],
                     'features': [],
                     'choices': []},
           'crater': {'key': 'crater',
                      'name': 'Burial Crater',
                      'description': 'An excavation bowl ringed with abandoned charges and survey '
                                     'flags. Something was opened here and then hurriedly covered '
                                     'again.',
                      'exits': [{'type': 'Exit',
                                 'direction': 'south',
                                 'destination': 'habitat',
                                 'requires_item': None,
                                 'requires_flag': None,
                                 'blocked': False,
                                 'blocked_text': 'That path is blocked.',
                                 'warning_text': None,
                                 'on_attempt_effect': None,
                                 'on_blocked_effect': None,
                                 'on_success_effect': None},
                                {'type': 'Exit',
                                 'direction': 'down',
                                 'destination': 'gallery',
                                 'requires_item': 'coldlamp',
                                 'requires_flag': None,
                                 'blocked': False,
                                 'blocked_text': 'The shaft below is lightless and deep. You need '
                                                 'a proper lamp.',
                                 'warning_text': None,
                                 'on_attempt_effect': None,
                                 'on_blocked_effect': None,
                                 'on_success_effect': None}],
                      'items': [],
                      'npcs': [],
                      'features': [{'type': 'ScriptedFeature',
                                    'name': 'collapse charges',
                                    'verb': 'Arm',
                                    'required_flags': ['has_grave_core'],
                                    'blocked_text': 'You would only do that if you had already '
                                                    'taken the core.',
                                    'once_flag': 'ending_bury',
                                    'first_effect': {'type': 'EndGameEffect',
                                                     'lines': ['You sink the grave core into the '
                                                               'old charge well and trigger the '
                                                               'crater collapse.',
                                                               'Stone folds in on the shaft. The '
                                                               'vault, the machine records, and '
                                                               'the promise of profit vanish under '
                                                               'a landslide of dust and bad luck.',
                                                               'No one gets rich. No one learns '
                                                               'enough. The planet goes back to '
                                                               'keeping its own counsel.',
                                                               'Ending: Bury it again.'],
                                                     'flags': ['ending_bury', 'game_won']},
                                    'repeat_effect': {'type': 'PrintEffect',
                                                      'lines': ['The crater is already coming '
                                                                'down.']}}],
                      'choices': []},
           'gallery': {'key': 'gallery',
                       'name': 'Lower Gallery',
                       'description': 'Dust hangs unmoving in a buried machine corridor cut with '
                                      'geometric precision far older than the survey camp above.',
                       'exits': [{'type': 'Exit',
                                  'direction': 'up',
                                  'destination': 'crater',
                                  'requires_item': None,
                                  'requires_flag': None,
                                  'blocked': False,
                                  'blocked_text': 'That path is blocked.',
                                  'warning_text': None,
                                  'on_attempt_effect': None,
                                  'on_blocked_effect': None,
                                  'on_success_effect': None},
                                 {'type': 'Exit',
                                  'direction': 'north',
                                  'destination': 'vault',
                                  'requires_item': None,
                                  'requires_flag': None,
                                  'blocked': False,
                                  'blocked_text': 'That path is blocked.',
                                  'warning_text': None,
                                  'on_attempt_effect': None,
                                  'on_blocked_effect': None,
                                  'on_success_effect': None}],
                       'items': [],
                       'npcs': [],
                       'features': [],
                       'choices': []},
           'vault': {'key': 'vault',
                     'name': 'Vault Heart',
                     'description': 'A colossal chamber surrounds a suspended core cradle. The air '
                                    'is still, warm, and charged with old intent.',
                     'exits': [{'type': 'Exit',
                                'direction': 'south',
                                'destination': 'gallery',
                                'requires_item': None,
                                'requires_flag': None,
                                'blocked': False,
                                'blocked_text': 'That path is blocked.',
                                'warning_text': None,
                                'on_attempt_effect': None,
                                'on_blocked_effect': None,
                                'on_success_effect': None}],
                     'items': [],
                     'npcs': [{'type': 'GuardianNPC',
                               'name': 'Custodian Echo',
                               'base_stats': {'type': 'Stats',
                                              'max_hp': 38,
                                              'attack_min': 7,
                                              'attack_max': 11,
                                              'defense': 2},
                               'location': 'vault',
                               'health': 38,
                               'gold': 0,
                               'inventory': ['grave_core', 'stim_dose'],
                               'equipment': {'weapon': None, 'armor': None, 'charm': None},
                               'description': 'A voice distributed through the chamber, speaking '
                                              'from nowhere human-sized.',
                               'tags': [],
                               'aggression': 50,
                               'courage': 90,
                               'willingness_to_trade': 0,
                               'hostile': False,
                               'dialogue_topics': [{'type': 'DialogueTopic',
                                                    'key': 'echo_warning',
                                                    'title': 'Ask what this place is',
                                                    'lines': ['A registry of deep claims and '
                                                              'deeper dead. A vault built to '
                                                              'remember extraction long after '
                                                              'extractors were gone.',
                                                              'Your kind returns to every grave '
                                                              'with scales and flags.'],
                                                    'required_flags': [],
                                                    'blocked_flags': ['custodian_cleared'],
                                                    'required_items': [],
                                                    'once': False,
                                                    'outcome_effect': None},
                                                   {'type': 'DialogueTopic',
                                                    'key': 'echo_after',
                                                    'title': 'Ask what the grave core does',
                                                    'lines': ['It names ownership, wakes dormant '
                                                              'routes, and proves this world was '
                                                              'catalogued before your survey ships '
                                                              'were born.',
                                                              'In smaller hands it is a key. In '
                                                              'larger hands it becomes a deed.'],
                                                    'required_flags': ['custodian_cleared'],
                                                    'blocked_flags': [],
                                                    'required_items': [],
                                                    'once': False,
                                                    'outcome_effect': None}],
                               'trade_offers': [],
                               'riddle': {'type': 'Riddle',
                                          'question': 'What is the first tool of every claim '
                                                      'jumper?',
                                          'answers': ['lie', 'a lie', 'lies'],
                                          'intro_lines': ['Answer plainly. What comes before every '
                                                          'stolen claim?'],
                                          'success_lines': ['Correct. Your species teaches that '
                                                            'lesson early.'],
                                          'failure_lines': ['No. The blade comes later.'],
                                          'repeat_lines': ['The chamber has judged you already. '
                                                           'Take what you came for.'],
                                          'damage_on_failure': 10,
                                          'set_flags_on_success': ['custodian_cleared']},
                               'surrender_at_ratio': None,
                               'surrender_lines': [],
                               'surrender_trade_offers': [],
                               'peaceful_after_surrender': True,
                               'surrender_accept_lines': [],
                               'surrender_reject_lines': [],
                               'surrender_accept_effect': None,
                               'defeat_lines': ['The chamber voice fractures into a thousand quiet '
                                                'tones and finally falls still.'],
                               'reward_items': [],
                               'reward_flags': ['custodian_cleared'],
                               'reward_gold': 0,
                               'persistent': True,
                               'used_topics': [],
                               'completed_trades': [],
                               'surrendered': False,
                               'riddle_solved': False,
                               'defeated': False}],
                     'features': [],
                     'choices': []}},
 'encounters': [{'name': 'service_patrol',
                 'locations': ['annex', 'service', 'shuttle'],
                 'chance': 1.0,
                 'required_flags': ['act1_started'],
                 'blocked_flags': ['act2_started', 'patrol_drone_seen'],
                 'once_flag': 'patrol_drone_seen',
                 'handler': 'handle_station_patrol',
                 'predicate': '<lambda>'},
                {'name': 'glass_maw',
                 'locations': ['ravine'],
                 'chance': 0.3,
                 'required_flags': [],
                 'blocked_flags': ['act3_started'],
                 'once_flag': None,
                 'handler': 'handle_glass_maw',
                 'predicate': '<lambda>'},
                {'name': 'rafe_offer',
                 'locations': ['crater', 'windbreak'],
                 'chance': 1.0,
                 'required_flags': ['has_grave_core'],
                 'blocked_flags': ['game_won', 'rafe_offer_heard'],
                 'once_flag': 'rafe_offer_heard',
                 'handler': 'handle_rafe_offer',
                 'predicate': None}]}

# ---------------------------------------------------------------------------
# STUDENT EXTENSION ZONE
# ---------------------------------------------------------------------------
# Add rooms here instead of editing the preserved original records above.
# A simple room needs only a name, description, exits, and optional choices.
# The engine treats omitted items, NPCs, and features as empty.
EXTRA_ROOMS = {}

# Add simple choices to an existing room without changing engine code. A
# choice can also move into one of your extra rooms. For example:
# EXTRA_ROOMS = {
#     "weather_station": {
#         "name": "Abandoned Weather Station",
#         "description": "A cracked antenna clicks slowly in the dust.",
#         "exits": [{"direction": "back", "destination": "windbreak"}],
#         "choices": [
#             {
#                 "text": "Check the old forecast terminal",
#                 "result": ["The final forecast simply reads: DUST."],
#             },
#         ],
#     },
# }
# EXTRA_CHOICES = {
#     "windbreak": [
#         {"text": "Follow the cable to the weather station", "go": "weather_station"},
#     ],
# }
EXTRA_CHOICES = {}

WORLD_DATA["rooms"].update(EXTRA_ROOMS)
for _room_key, _choices in EXTRA_CHOICES.items():
    WORLD_DATA["rooms"][_room_key].setdefault("choices", []).extend(_choices)
