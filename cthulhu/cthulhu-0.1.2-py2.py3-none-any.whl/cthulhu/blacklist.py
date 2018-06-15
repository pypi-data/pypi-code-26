import numpy as np


def get_blacklist():
    return [
        # EoR-0
        "MWA001656-2559",
        "MWA005549-2621",
        "EXTmwacs13384",
        "MWA000806-2419A",
        "J002040-201934A",
        "J232021-170241A",
        "J001752-222125A",
        "J234236-443419A",

        # EoR-1
        "EXT035140-2743",
        "GLM035125-2746",
        "EXT031600-2656",
        "EXT043553-2334",
        "EXT031600-2656",
    ]


def bad_sources(sources):
    blacklist = get_blacklist()
    return np.in1d(sources, blacklist)
