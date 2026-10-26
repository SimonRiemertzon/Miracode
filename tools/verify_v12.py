"""Independently verify v12 source deltas, full package and stock catalog outputs."""
import argparse
from collections import Counter
import json
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--package',type=Path,required=True)
parser.add_argument('--catalog',type=Path)
parser.add_argument('--baseline-source',type=Path,default=ROOT.parent/'miracode-v11/dist/v11-source')
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()

def parts(font,name):
    points,ends,flags=font['glyf'][name].getCoordinates(font['glyf'])
    start,result=0,[]
    for end in ends:
        result.append([(x,y,int(f)&1) for (x,y),f in zip(points[start:end+1],flags[start:end+1])]);start=end+1
    return result
def box(p):return min(x for x,y,f in p),min(y for x,y,f in p),max(x for x,y,f in p),max(y for x,y,f in p)
def canonical(p):return min(tuple(p[i:]+p[:i]) for i in range(len(p)))
def outline(font,name):
    glyphs=font.getGlyphSet();pen=DecomposingRecordingPen(glyphs);glyphs[name].draw(pen);return pen.value
def ligs(font):
    return sorted((first,tuple(v.Component),font['hmtx'][v.LigGlyph][0]) for lookup in font['GSUB'].table.LookupList.Lookup for sub in lookup.SubTable for first,values in getattr(sub,'ligatures',{}).items() for v in values)

source_records=[]
for style in ('Regular','Bold'):
    filename='Miracode-Bold.ttf' if style=='Bold' else 'Miracode.ttf'
    new=TTFont(ROOT/'dist/v12-source'/filename);old=TTFont(args.baseline_source/filename)
    assert new.getBestCmap()==old.getBestCmap()
    assert new.getTableData('GSUB')==old.getTableData('GSUB')
    assert all(new['hmtx'][n][0]==old['hmtx'][n][0] for n in old.getGlyphOrder())
    changed={name for name in old.getGlyphOrder() if outline(old,name)!=outline(new,name)}
    expected={old.getBestCmap()[c] for c in (46,0x2026)}
    assert changed==expected,(style,changed)
    for name in old.getGlyphOrder():
        if name not in expected:assert outline(old,name)==outline(new,name),(style,name)
    for code,count in ((46,1),(0x2026,3)):
        dots=parts(new,new.getBestCmap()[code]);assert len(dots)==count
        assert all(len(p)==4 and all(flag for x,y,flag in p) for p in dots)
        assert all(box(p)[1]+box(p)[3]==768 for p in dots)
        if code==0x2026:
            boxes=sorted(box(p) for p in dots)
            assert boxes[0][0]>=0 and boxes[-1][2]<=1536
            assert all(a[2]<b[0] for a,b in zip(boxes,boxes[1:]))
    source_records.append(dict(style=style,changedGlyphs=sorted(changed),periodAndEllipsisOnly=True,allOtherContoursExact=True,allAdvancesAndGsubExact=True,ellipsisInsideOneCell=True))

manifest=json.loads((args.package/'manifest.json').read_text());records=[]
for entry in manifest['files']:
    path=args.package/entry['file'];font=TTFont(path);web=TTFont(args.package/'webfonts'/path.with_suffix('.woff2').name)
    assert font['name'].getDebugName(1)==manifest['family']
    assert not {'EBDT','EBLC','EBSC','CBDT','CBLC','sbix'}&set(font.keys())
    assert font['OS/2'].usWeightClass==(700 if entry['style'].startswith('Bold') else 400)
    assert font.getBestCmap()==web.getBestCmap() and font['hmtx'].metrics==web['hmtx'].metrics
    assert font.getTableData('GSUB')==web.getTableData('GSUB')
    for name in font.getGlyphOrder():
        assert outline(font,name)==outline(web,name),(entry['style'],name,'WOFF2 round trip')
        glyph=font['glyf'][name];glyph.recalcBounds(font['glyf'])
        assert getattr(glyph,'yMax',0)<=font['OS/2'].usWinAscent
        assert getattr(glyph,'yMin',0)>=-font['OS/2'].usWinDescent
    cmap=font.getBestCmap()
    for code in (0x2022,0x25E6,0x25C6,0x25C7,0x25AA,0x25A0,0x25CF,0x25CB,0x25A1):
        glyph=font['glyf'][cmap[code]];assert glyph.yMin+glyph.yMax==2304
    for char in 'ÄÖäöij':
        marks=sorted(parts(font,cmap[ord(char)]),key=lambda p:box(p)[1],reverse=True)[:(1 if char in 'ij' else 2)]
        assert all(len(p)==4 and all(f for x,y,f in p) for p in marks)
        if char in 'ÄÖ':assert all(box(p)[1]==2208 for p in marks)
        if char in 'ij':assert all(box(p)[1]+box(p)[3]==(4160 if entry['style'].startswith('Bold') else 4032) for p in marks)
        if char in 'äö':assert all(box(p)[1]+box(p)[3]==3840 for p in marks)
    records.append(dict(style=entry['style'],vectorOutlines=True,webRoundTripExact=True,diamondMarksAndCenters=True,allNineLiteralMarkersCentered=True,windowsBounds=[font['OS/2'].usWinAscent,-font['OS/2'].usWinDescent]))

catalog_records=[]
if args.catalog:
    files=sorted((args.catalog/'check-fonts/MiracodeText').glob('*.ttf'));assert len(files)==4
    for path in files:
        font=TTFont(path);base=TTFont(ROOT/'dist/v12-source'/('Miracode-Bold.ttf' if font['OS/2'].usWeightClass==700 else 'Miracode.ttf'))
        cmap=font.getBestCmap()
        for code,name in base.getBestCmap().items():
            assert outline(font,cmap[code])==outline(base,name),(path.name,code)
            assert font['hmtx'][cmap[code]][0]==base['hmtx'][name][0]
        assert ligs(font)==ligs(base)
        assert font['name'].getDebugName(1) in ('MiracodeText Nerd Font','MiracodeText Nerd Font Propo')
        assert font['name'].getDebugName(2) in ('Regular','Bold')
        for name in font.getGlyphOrder():
            glyph=font['glyf'][name]
            assert getattr(glyph,'yMax',0)<=font['OS/2'].usWinAscent
            assert getattr(glyph,'yMin',0)>=-font['OS/2'].usWinDescent
        catalog_records.append(dict(file=path.name,sourceOutlinesAdvancesAndLigaturesExact=True,windowsClippingBoundsPass=True))
args.output.write_text(json.dumps(dict(passChecks=True,source=source_records,installedPackage=records,catalog=catalog_records),indent=2)+'\n')
print(json.dumps(dict(passChecks=True,sourceStyles=2,packageFaces=len(records),catalogFaces=len(catalog_records),onlyDotContoursChanged=True)))
