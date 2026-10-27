"""Ordinary i dots remain diamonds; only the Miracode wordmark has a heart.

SPDX-License-Identifier: GPL-3.0-or-later
"""
import sys
from fontTools.ttLib import TTFont

def contours(font, name):
    points, ends, flags = font['glyf'][name].getCoordinates(font['glyf'])
    start = 0
    result = []
    for end in ends:
        result.append([(x, y, int(flag)) for (x, y), flag in zip(points[start:end+1], flags[start:end+1])])
        start = end + 1
    return result

def check(path):
    font = TTFont(path)
    base = font.getBestCmap()[ord('i')]
    ordinary = max(contours(font, base), key=lambda p: min(y for x, y, flag in p))
    failures = []
    for latin, cyrillic in ((ord('i'), 0x456), (ord('j'), 0x458)):
        cmap = font.getBestCmap()
        if contours(font, cmap[latin]) != contours(font, cmap[cyrillic]):
            failures.append('Cyrillic dotted reference differs from its Latin source')
    for character in ('i', 'j'):
        parts = contours(font, font.getBestCmap()[ord(character)])
        dot = max(parts, key=lambda p: min(y for x,y,flag in p))
        stem_top = max(y for p in parts if p is not dot for x,y,flag in p)
        gap = min(y for x,y,flag in dot) - stem_top
        if gap < 350:
            failures.append(f'{character}: dot/stem gap {gap} is too small for 10px text')
    for word in ('miranda',):
        if word not in font.getGlyphOrder():
            continue
        shift = font['hmtx'].metrics[font.getBestCmap()[ord('M')]][0]
        candidates = [p for p in contours(font, word) if min(y for x,y,f in p) > 1600 and min(x for x,y,f in p) > shift and max(x for x,y,f in p) < shift*2]
        if len(candidates) != 1:
            failures.append(f'{word}: expected one detached i dot, found {len(candidates)}')
            continue
        normalized = [(x-shift,y,flag) for x,y,flag in candidates[0]]
        if normalized != ordinary:
            failures.append(f'{word}: i dot differs from standalone i (notched word-logo dot)')
    if failures:
        raise AssertionError('; '.join(failures))
    heart = [p for p in contours(font, 'miracode')
             if min(y for x,y,f in p) > 1600 and min(x for x,y,f in p) > shift
             and max(x for x,y,f in p) < shift*2]
    if len(heart) != 1 or len(heart[0]) != 8:
        failures.append('Miracode: expected the original detached eight-point heart')
    if failures:
        raise AssertionError('; '.join(failures))
    print(f'{path}: PASS, ordinary/alias/Miranda dots preserved; Miracode heart present')

if __name__ == '__main__':
    for argument in sys.argv[1:]:
        check(argument)
