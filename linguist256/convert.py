"""
Approximate 24bit color to 8bit
"""

import math
import yaml

from os import path

wd = path.realpath(path.dirname(__file__))

with open(path.join(wd, 'lut.yml'), 'r') as f:
    lut = yaml.load(f.read())


def __get_delta(a, b):
    r = (a[0] - b[0]) ** 2
    g = (a[1] - b[1]) ** 2
    b = (a[2] - b[2]) ** 2
    return math.sqrt(r + g + b)


def torgb(color: str):
    """covert hex color to rgb tuple"""
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def to8bit(color: str):
    """covert 24bit hex color to 8bit terminal color"""
    color = color.lstrip('#')

    if len(color) != 6:
        return None

    rgb = torgb(color)
    min_delta = math.inf
    ans = None

    for c in lut:
        delta = __get_delta(rgb, torgb(c))
        if delta < min_delta:
            min_delta = delta
            ans = c

    return lut[ans]
