# Based on either User Inputs (e.g. game_modes, other_games)
# or Function keys (e.g. topics, gp roles)

ROLES = {
    'game_modes': {
        'crucible': ['crucible', 'c'],
        'gambit': ['gambit', 'g'],
        'raid': ['raid', 'r'],
        'strike-nf-pve': ['strike-nf-pve', 's', 'nf', 'pve', 'strike', 'nightfall']
    },
    'other_games': {
        'og-ac': ['animal crossing', 'ac', 'animal crossing new horizons'],
        'og-ant': ['anthem', 'ant'],
        'og-apex': ['apex legends', 'apex', 'apex: legends'],
        'og-au': ['among us', 'au'],
        'og-bl': ['borderlands', 'bl', 'borderlands 2', 'borderlands 3'],
        'og-cod': ['call of duty', 'cod', 'mw', 'modern warfare'],
        'og-c77': ['cyberpunk 2077', 'c77', 'cp77', 'cyberpunk'],
        'og-drg': ['deep rock galactic', 'drg', 'deep rock'],
        'og-div2': ['division 2', 'div2', 'td2', 'division', 'the division 2'],
        'og-dl': ['dying light', 'dl'],
        'og-dota': ['dota 2', 'dota', 'defense of the ancients 2'],
        'og-eft': ['escape from tarkov', 'eft', 'tarkov'],
        'og-f76': ['fallout 76', 'f76', 'fallout', 'fallout online'],
        'og-ffxiv': ['final fantasy xiv', 'ffxiv'],
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
        'og-rage': ['rage 2', 'rage'],
        'og-r6s': ['rainbow six siege', 'r6s', 'rss', 'rainbow', 'siege', 'rainbow six', 'rainbow six: siege'],
        'og-rdo': ['red dead online', 'rdo', 'red dead redemption 2', 'red dead'],
        'og-rem': ['remnant', 'rem'],
        'og-ror2': ['risk of rain', 'ror', 'ror2', 'risk of rain 2'],
        'og-smash': ['super smash bros', 'smash', 'ssb', 'ssbu'],
        'og-sd': ['stardew valley', 'sd', 'stardew'],
        'og-sot': ['sea of thieves', 'sot'],
        'og-steep': ['steep'],
        'og-stel': ['stellaris', 'stel'],
        'og-sts': ['slay the spire', 'sts'],
        'og-switch': ['nintendo switch', 'switch'],
        'og-va': ['valorant', 'va'],
        'og-val': ['valheim', 'val'],
        'og-warf': ['warframe', 'wf', 'warf'],
        'og-wow': ['world of warcraft', 'wow', 'warcraft'],
    },
    'raid_leads': {
        'sherpa': ['sherpa', 'teach']
    },
    'rythm_dj': {
        'DJ': ['dj', 'rythm', 'rhythm']
    },
    'nsfw': {
        'nsfw': ['nsfw']
    },
    'pronouns': {
        'she': ['she/her'],
        'he': ['he/him'],
        'they': ['they/them'],
        'any': ['any/all'],
        'ask': ['ask']
    },
    'toggle_roles': {
        'pride': ['pride']  # 🌈  # U+1F308  \u1F308
    },
    'topics': {
        'current-events': ['current events', 'ce', 'current-events', 'politics', 'news'],
        'stonks': ['stonks', 'stocks', 'finances', 'financial'],
        'vog': ['vog', 'vault', 'glass', 'vault of glass']
    },
    'ghost_proxy_roles': {
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
    'ghost_proxy_elevated_roles': {
        'ghost-proxy-vanguard': ['vanguard', 'gp-vanguard', 'ghost-proxy-vanguard'],
        'ghost-proxy-veteran': ['gpv', 'gp-veteran', 'ghost-proxy-veteran'],
        'ghost-proxy-archivist': ['gpa', 'gp-archivist', 'ghost-proxy-archivist']
    },
    'ghost_proxy_protected_roles': {
        'founder': ['founder', 'gp-founder', 'ghost-proxy-founder'],
        'ghost-proxy-gatekeeper': ['gatekeeper', 'gp-gatekeeper', 'ghost-proxy-gatekeeper']
    }
}
