"""Assert pronounced period diamonds and a separated, single-cell ellipsis."""
import sys
from fontTools.ttLib import TTFont

for path in sys.argv[1:]:
    font=TTFont(path);bold=font['OS/2'].usWeightClass==700;cmap=font.getBestCmap()
    for code,count,radius in [(46,1,384 if bold else 352),(0x2026,3,248 if bold else 240)]:
        glyph=font['glyf'][cmap[code]]
        points,ends,flags=glyph.getCoordinates(font['glyf'])
        assert len(ends)==count and all(flag&1 for flag in flags)
        start=0;boxes=[]
        for end in ends:
            contour=list(points[start:end+1]);start=end+1
            assert len(contour)==4
            xs,ys=zip(*contour)
            assert max(xs)-min(xs)==max(ys)-min(ys)==radius*2
            expected_center = (228 if bold else 288) + radius if code == 46 else 384
            assert min(ys)+max(ys)==2 * expected_center
            boxes.append((min(xs),max(xs)))
        assert font['hmtx'][cmap[code]][0]==1536
        if code==0x2026:
            boxes.sort();assert boxes[0][0]>=0 and boxes[-1][1]<=1536
            assert all(a[1]<b[0] for a,b in zip(boxes,boxes[1:]))
    print(f'{path}: PASS, stronger vector periods; ellipsis diamonds stay separate inside one cell')
