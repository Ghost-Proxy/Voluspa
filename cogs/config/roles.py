ROLES = {
            'game_modes': {  # Based on User Input
                'crucible': ['crucible', 'c'],
                'gambit': ['gambit', 'g'],
                'raid': ['raid', 'r'],
                'strike-nf-pve': ['strike-nf-pve', 's', 'nf', 'pve', 'strike', 'nightfall']
            },
            'other_games': {  # Based on User Input
                'og-ac': ['animal crossing', 'ac', 'animal crossing new horizons'],
                'og-ant': ['anthem', 'ant'],
                'og-apex': ['apex legends', 'apex', 'apex: legends'],
                'og-au': ['among us', 'au'],
                'og-bl': ['borderlands', 'bl', 'borderlands 2', 'borderlands 3'],
                'og-cod': ['call of duty', 'cod', 'mw', 'modern warfare'],
                'og-div2': ['division 2', 'div2', 'td2', 'division', 'the division 2'],
                'og-dl': ['dying light', 'dl'],
                'og-dota': ['dota 2', 'dota', 'defense of the ancients 2'],
                'og-eft': ['escape from tarkov', 'eft', 'tarkov'],
                'og-f76': ['fallout 76', 'f76', 'fallout', 'fallout online'],
                'og-gr': ['ghost recon', 'gr', 'grw', 'grb', 'ghost recon wildlands', 'ghost recon breakpoint'],
                'og-gtao': ['grand theft auto online', 'gtao', 'gtav', 'gta'],
                'og-gtfo': ['gtfo'],
                'og-halo': ['halo'],
                'og-hunt': ['hunt showdown', 'hunt', 'the hunt'],
                'og-kart': ['mario kart 8', 'kart', 'mario kart'],
                'og-lol': ['league of legends', 'lol', 'league'],
                'og-mc': ['minecraft', 'mc'],
                'og-mhw': ['monster hunter world', 'mh', 'mhw', 'monster', 'monster hunter'],
                'og-osu': ['osu'],
                'og-ow': ['overwatch', 'ow'],
                # 'og-rage': ['rage 2', 'rage'],
                'og-r6s': ['rainbow six siege', 'r6s', 'rss', 'rainbow', 'siege', 'rainbow six', 'rainbow six: siege'],
                'og-rdo': ['red dead online', 'rdo', 'red dead redemption 2', 'red dead'],
                'og-rem': ['remnant', 'rem'],
                'og-smash': ['super smash bros', 'smash', 'ssb', 'ssbu'],
                'og-steep': ['steep'],
                'og-sts': ['slay the spire', 'sts'],
                'og-switch': ['nintendo switch', 'switch'],
                'og-va': ['valorant', 'va'],
                'og-warf': ['warframe', 'wf', 'warf'],
                'og-wow': ['world of warcraft', 'wow', 'warcraft'],
            },
            'raid_leads': {  # Based on Function String
                'sherpa': ['sherpa', 'teach']
            },
            'rythm_dj': {  # Based on Function String
                'DJ': ['dj', 'rythm', 'rhythm']
            },
            'nsfw': {
                'nsfw': ['nsfw']
            },
            'topics': {
                'current-events': ['current events', 'ce', 'current-events', 'politics', 'news']
            },
            'ghost_proxy_roles': {  # Based on Function String
                'ghost-proxy-friend': ['gpf', 'gp-friend', 'ghost-proxy-friend'],
                'ghost-proxy-member': ['gpm', 'gp-member', 'ghost-proxy-member'],
                'ghost-proxy-legacy': ['gpl', 'gp-legacy', 'ghost-proxy-legacy'],
                'ghost-proxy-envoy': ['gpe', 'gp-envoy', 'ghost-proxy-envoy'],
                'ghost-proxy-veteran': ['gpv', 'gp-veteran', 'ghost-proxy-veteran'],
                'ghost-proxy-archivist': ['gpa', 'gp-archivist', 'ghost-proxy-archivist'],
                # Include lead roles for reset
                'raid-lead': ['raid-lead'],
                'gambit-lead': ['gambit-lead'],
                'crucible-lead': ['crucible-lead'],
                'strike-nf-pve-lead': ['strike-nf-pve-lead'],
                # And Div2 admins
                'div2-admin': ['div2-admin'],
                # Same with sherpa
                'sherpa': ['sherpa']
            },  # TODO: Figure out what the plan was with the below...
            'ghost_proxy_elevated_roles': {  # Based on Function String
                'ghost-proxy-vanguard': ['vanguard', 'gp-vanguard', 'ghost-proxy-vanguard'],
                'ghost-proxy-veteran': ['gpv', 'gp-veteran', 'ghost-proxy-veteran'],
                'ghost-proxy-archivist': ['gpa', 'gp-archivist', 'ghost-proxy-archivist']
            },
            'ghost_proxy_protected_roles': {  # Based on Function String
                'founder': ['founder', 'gp-founder', 'ghost-proxy-founder'],  # 'ghost-proxy-founder'
                'ghost-proxy-gatekeeper': ['gatekeeper', 'gp-gatekeeper', 'ghost-proxy-gatekeeper']
            }
        }
