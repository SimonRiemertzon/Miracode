"""Periods align with text bottoms; large !/? diamonds have a readable gap."""
import sys
from fontTools.ttLib import TTFont

def boxes(font, char):
    glyph=font['glyf'][font.getBestCmap()[ord(char)]]
    points, ends, flags=glyph.getCoordinates(font['glyf'])
    result=[];start=0
    for end in ends:
        xs,ys=zip(*points[start:end+1]);start=end+1
        result.append((min(xs),min(ys),max(xs),max(ys)))
    return result

failures=[]
for path in sys.argv[1:]:
    font=TTFont(path);baseline=boxes(font,'1')[0][1]
    period=boxes(font,'.')[0]
    if period[1]!=baseline:failures.append(f'{path}: period bottom {period[1]} != text bottom {baseline}')
    for char in '!?':
        dot,body=sorted(boxes(font,char),key=lambda b:b[3])
        gap=body[1]-dot[3]
        if gap<256:failures.append(f'{path}: {char} dot/body gap {gap} < 256')
        cap_top=boxes(font,'1')[0][3]
        if body[3]!=cap_top:failures.append(f'{path}: {char} body top changed')
    if not failures:print(f'{path}: PASS, period bottom {baseline}, !/? clearance >=256 units, capital tops preserved')
assert not failures,'\n'+'\n'.join(failures)
