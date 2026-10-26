"""Check vector diamond marks, lowercase heights, counters and punctuation.

SPDX-License-Identifier: GPL-3.0-or-later
"""
import sys
import argparse
from fontTools.ttLib import TTFont

def parts(font, code):
    p, ends, flags = font['glyf'][font.getBestCmap()[code]].getCoordinates(font['glyf'])
    start, result = 0, []
    for end in ends:
        result.append([(x, y, int(f)) for (x, y), f in zip(p[start:end+1], flags[start:end+1])])
        start = end + 1
    return result

def bounds(p):
    return min(x for x,y,f in p), min(y for x,y,f in p), max(x for x,y,f in p), max(y for x,y,f in p)

def diamond(p):
    x0,y0,x1,y1 = bounds(p)
    return len(p)==4 and all(f&1 for x,y,f in p) and { (x,y) for x,y,f in p } == {(x0,(y0+y1)/2),((x0+x1)/2,y1),(x1,(y0+y1)/2),((x0+x1)/2,y0)}

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--punctuation-dots',choices=('original','basic','extended'),default='extended')
parser.add_argument('fonts',nargs='+')
args=parser.parse_args()
selected=set('.:…' if args.punctuation_dots=='basic' else '.:;!?…·¡¿' if args.punctuation_dots=='extended' else '')
for path in args.fonts:
    font=TTFont(path);bold=font['OS/2'].usWeightClass==700
    for char in 'ÄÖäöij':
        marks=sorted(parts(font,ord(char)),key=lambda p: bounds(p)[1],reverse=True)[:(1 if char in 'ij' else 2)]
        assert all(diamond(p) for p in marks),char
        if char in 'ÄÖ':
            assert all(bounds(p)[1]==2208 for p in marks),char
        elif char in 'ij':
            assert all(bounds(p)[1]+bounds(p)[3]==(4160 if bold else 4032) for p in marks),char
    for char, count in [('.',1),(':',2),('!',1),('?',1),('…',3)]:
        dots=[p for p in parts(font,ord(char)) if diamond(p)]
        assert len(dots)==(count if char in selected else 0),(char,len(dots))
    for code in (0x2022,0x25C6):
        assert len(parts(font,code))==1 and diamond(parts(font,code)[0])
    for code in (0x25E6,0x25C7):
        contours=parts(font,code)
        assert sorted(map(len,contours))==[4,4]
        def area(p):return sum(x*v-u*y for (x,y,f),(u,v,g) in zip(p,p[1:]+p[:1]))
        assert area(contours[0])*area(contours[1])<0,'Hollow counter must have opposite winding'
    print(f'{path}: PASS, requested letter dots are vector diamonds; punctuation policy={args.punctuation_dots}; hollow bullets have real counters')
