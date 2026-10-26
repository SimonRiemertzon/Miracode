"""Assert v13's visible punctuation and sharp, hollow/filled list diamonds."""
import sys
from fontTools.ttLib import TTFont

def parts(font, code):
    p, ends, flags = font['glyf'][font.getBestCmap()[code]].getCoordinates(font['glyf'])
    result, start = [], 0
    for end in ends:
        result.append([(x, y, int(f)) for (x, y), f in zip(p[start:end + 1], flags[start:end + 1])])
        start = end + 1
    return result

def bounds(points):
    xs, ys, flags = zip(*points)
    return min(xs), min(ys), max(xs), max(ys)

def diamond(points):
    x0, y0, x1, y1 = bounds(points)
    return len(points) == 4 and all(f & 1 for x, y, f in points) and set((x, y) for x, y, f in points) == {
        (x0, (y0 + y1) / 2), ((x0 + x1) / 2, y1), (x1, (y0 + y1) / 2), ((x0 + x1) / 2, y0)}

for path in sys.argv[1:]:
    font = TTFont(path)
    bold = font['OS/2'].usWeightClass == 700
    radius = 384 if bold else 352
    for char, count in [('.', 1), ('·', 1), (':', 2), (';', 1), ('!', 1), ('?', 1), ('¡', 1), ('¿', 1)]:
        dots = [p for p in parts(font, ord(char)) if diamond(p)]
        assert len(dots) == count, (char, len(dots))
        expected_radius = (320 if bold else 304) if char in '!?¡¿' else radius
        assert all(bounds(p)[2] - bounds(p)[0] == expected_radius * 2 for p in dots), char
    for code in (0x2022, 0x25C6, 0x25E6, 0x25C7):
        shapes = parts(font, code)
        assert all(diamond(p) for p in shapes), hex(code)
        assert all(bounds(p)[1] + bounds(p)[3] == 2304 for p in shapes)
        assert len(shapes) == (2 if code in (0x25E6, 0x25C7) else 1)
        outer = max(shapes, key=lambda p: bounds(p)[2] - bounds(p)[0])
        expected = (576 if bold else 544) if len(shapes) == 2 else (528 if bold else 480)
        assert bounds(outer)[2] - bounds(outer)[0] == expected * 2
        assert bounds(outer)[0] >= 0 and bounds(outer)[2] <= 1536
    print(f'{path}: PASS, larger punctuation and list diamonds, sharp tips and centered markers')
