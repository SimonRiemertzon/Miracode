"""Independently verify v11 source deltas, full package and stock catalog outputs."""
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
parser.add_argument('--baseline-source',type=Path,default=ROOT.parent/'miracode-v10/dist/v10-source')
parser.add_argument('--punctuation-c-source',type=Path,default=ROOT.parent/'miracode-v10/dist/v10-punctuation-extended')
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
    new=TTFont(ROOT/'dist/v11-source'/filename);old=TTFont(args.baseline_source/filename)
    assert new.getBestCmap()==old.getBestCmap()
    assert new.getTableData('GSUB')==old.getTableData('GSUB')
    assert all(new['hmtx'][n][0]==old['hmtx'][n][0] for n in old.getGlyphOrder())
    markers=set()
    selected={old.getBestCmap()[ord(c)] for c in '.:;!?…·¡¿'}
    allowed=set(selected)
    for lookup in old['GSUB'].table.LookupList.Lookup:
        for sub in lookup.SubTable:
            for first,values in getattr(sub,'ligatures',{}).items():
                for lig in values:
                    if selected.intersection([first]+lig.Component):allowed.add(lig.LigGlyph)
    changed=[];dot_count=0
    for name in old.getGlyphOrder():
        before=Counter(canonical(p) for p in parts(old,name));after=Counter(canonical(p) for p in parts(new,name))
        if before==after:continue
        assert name in allowed,(style,name,'Unrequested punctuation or accent change')
        changed.append(name)
        if name in markers:continue
        removed=list((before-after).elements());added=list((after-before).elements())
        assert len(removed)==len(added),(style,name,'dot replacement count')
        expected_centers=[];actual_centers=[]
        for p in removed:
            x0,y0,x1,y1=box(p)
            square_dot=len(p)==4 and x1-x0==y1-y0 and x1-x0 in (226,284) and y0+y1 in (4032,4160)
            assert any(not f for x,y,f in p) or square_dot,(style,name,'non-dot contour changed',box(p))
            expected_centers.append((x0+x1,y0+y1))
        for p in added:
            x0,y0,x1,y1=box(p)
            assert len(p)==4 and all(f for x,y,f in p),(style,name,'non-diamond replacement')
            assert {(x,y) for x,y,f in p}=={(x0,(y0+y1)/2),((x0+x1)/2,y1),(x1,(y0+y1)/2),((x0+x1)/2,y0)}
            actual_centers.append((x0+x1,y0+y1))
        assert sorted(expected_centers)==sorted(actual_centers),(style,name,'dot center moved')
        dot_count+=len(added)
    accepted=TTFont(args.punctuation_c_source/filename)
    assert selected<=set(changed),'Every selected punctuation glyph must change'
    for name in new.getGlyphOrder():assert outline(new,name)==outline(accepted,name),(style,name,'Does not match accepted C')
    for char in 'AOÅaoåÄÖäöij\'\",éèêëü':assert outline(new,new.getBestCmap()[ord(char)])==outline(old,old.getBestCmap()[ord(char)]),char
    source_records.append(dict(style=style,changedGlyphs=changed,replacedDots=dot_count,allOtherContoursExact=True,allAdvancesAndGsubExact=True,originalRingsAndCapitalDesignExact=True,acceptedPunctuationCExact=True))

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
        font=TTFont(path);base=TTFont(ROOT/'dist/v11-source'/('Miracode-Bold.ttf' if font['OS/2'].usWeightClass==700 else 'Miracode.ttf'))
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
