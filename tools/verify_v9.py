"""Verify accepted v9 geometry, full-font integrity and catalog outputs."""
import argparse
import json
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--package',type=Path,required=True)
parser.add_argument('--catalog',type=Path)
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--baseline-source',type=Path,default=ROOT.parent/'miracode-v8/dist/centered-diaereses-v8')
args=parser.parse_args()

def parts(font,name):
    c,e,f=font['glyf'][name].getCoordinates(font['glyf'])
    return [[(x,y,int(flag)) for (x,y),flag in zip(c[(0 if i==0 else e[i-1]+1):end+1],f[(0 if i==0 else e[i-1]+1):end+1])] for i,end in enumerate(e)]
def box(p):return [min(x for x,y,f in p),min(y for x,y,f in p),max(x for x,y,f in p),max(y for x,y,f in p)]
def canonical(p):return min(tuple(p[i:]+p[:i]) for i in range(len(p)))
def outline(font,name):
    glyphs=font.getGlyphSet();pen=DecomposingRecordingPen(glyphs);glyphs[name].draw(pen);return pen.value

records=[]
manifest=json.loads((args.package/'manifest.json').read_text())
for entry in manifest['files']:
    path=args.package/entry['file'];font=TTFont(path);style=entry['style'];bold=style.startswith('Bold');cmap=font.getBestCmap()
    assert 'glyf' in font and not {'EBDT','EBLC','EBSC','CBDT','CBLC','sbix'}&set(font.keys())
    assert font['name'].getDebugName(1)==manifest['family']
    assert font['OS/2'].usWeightClass==(700 if bold else 400)
    expected={196:(352 if not bold else 432),214:(352 if not bold else 432)}
    marks={}
    for code in (196,214,105,106):
        count=2 if code in (196,214) else 1
        ps=sorted(parts(font,cmap[code]),key=lambda p:box(p)[1],reverse=True)
        dots=ps[:count];marks[str(code)]=[box(p) for p in dots]
        assert all(len(p)==4 for p in dots)
        if count==2:
            assert all(box(p)[1]==2208 and box(p)[3]-box(p)[1]==expected[code] for p in dots)
        else:
            assert all(box(p)[1]+box(p)[3]==(4160 if bold else 4032) for p in dots)
    for code in (0x2022,0x25E6,0x25AA,0x25A0,0x25CF,0x25CB,0x25A1):
        g=font['glyf'][cmap[code]];assert g.yMin+g.yMax==2304
    outside=[]
    reverse={name:code for code,name in cmap.items()}
    for name in font.getGlyphOrder():
        glyph=font['glyf'][name];glyph.recalcBounds(font['glyf'])
        assert getattr(glyph,'yMax',0)<=font['OS/2'].usWinAscent
        assert getattr(glyph,'yMin',0)>=-font['OS/2'].usWinDescent
        if getattr(glyph,'yMax',0)>font['hhea'].ascent or getattr(glyph,'yMin',0)<font['hhea'].descent:
            code=reverse.get(name,0)
            assert 0x2500<=code<=0x259F or 0xE0A0<=code<=0xE0D7,(name,code)
            outside.append(hex(code))
    web=TTFont(args.package/'webfonts'/path.with_suffix('.woff2').name)
    assert font.getBestCmap()==web.getBestCmap()
    assert font['hmtx'].metrics==web['hmtx'].metrics
    assert font.getTableData('GSUB')==web.getTableData('GSUB')
    for name in font.getGlyphOrder():assert outline(font,name)==outline(web,name),(style,name)
    records.append(dict(style=style,marks=marks,vectorOutlines=True,webRoundTripExact=True,capitalMarkersCentered=True,joiningOvershootsPreserved=outside,windowsBounds=[font['OS/2'].usWinAscent,-font['OS/2'].usWinDescent]))

source_records=[]
for style in ('Regular','Bold'):
    new=TTFont(ROOT/'dist/v9-source'/('Miracode-Bold.ttf' if style=='Bold' else 'Miracode.ttf'))
    old=TTFont(args.baseline_source/('Miracode-Bold.ttf' if style=='Bold' else 'Miracode.ttf'))
    changed={n for n in old.getGlyphOrder() if outline(old,n)!=outline(new,n)}
    allowed={old.getBestCmap()[c] for c in (196,214,105,106,0x456,0x458,0x25CF)}|{'miracode','miranda'}
    assert changed==allowed,(style,changed)
    assert set(new.getBestCmap())-set(old.getBestCmap())=={0x25AA,0x25A0}
    assert all(new['hmtx'][n][0]==old['hmtx'][n][0] for n in old.getGlyphOrder())
    for code,base in ((196,65),(214,79)):
        body=[p for p in parts(new,new.getBestCmap()[code]) if box(p)[1]<2208]
        assert sorted(canonical(p) for p in body)==sorted(canonical(p) for p in parts(new,new.getBestCmap()[base]))
    source_records.append(dict(style=style,onlyIntendedOutlinesChanged=True,addedMarkers=['U+25AA','U+25A0'],fullBodiesAndAaUnchanged=True))

catalog_records=[]
if args.catalog:
    files=sorted((args.catalog/'check-fonts/MiracodeText').glob('*.ttf'));assert len(files)==4,len(files)
    for path in files:
        font=TTFont(path);bold=font['OS/2'].usWeightClass==700
        base=TTFont(ROOT/'dist/v9-source'/('Miracode-Bold.ttf' if bold else 'Miracode.ttf'))
        cmap=font.getBestCmap();old=base.getBestCmap()
        assert set(old)<=set(cmap)
        for code,name in old.items():
            assert font['hmtx'][cmap[code]][0]==base['hmtx'][name][0]
            assert outline(font,cmap[code])==outline(base,name),(path.name,code)
        def ligs(f):
            return sorted((first,tuple(v.Component),f['hmtx'][v.LigGlyph][0]) for lookup in f['GSUB'].table.LookupList.Lookup for sub in lookup.SubTable for first,values in getattr(sub,'ligatures',{}).items() for v in values)
        assert ligs(font)==ligs(base)
        assert font['name'].getDebugName(2) in ('Regular','Bold')
        assert font['name'].getDebugName(1) in ('MiracodeText Nerd Font','MiracodeText Nerd Font Propo')
        for name in font.getGlyphOrder():
            glyph=font['glyf'][name]
            assert getattr(glyph,'yMax',0)<=font['OS/2'].usWinAscent
            assert getattr(glyph,'yMin',0)>=-font['OS/2'].usWinDescent
        catalog_records.append(dict(file=path.name,sourceOutlinesAdvancesAndLigaturesExact=True,properFamilyAndStyleNames=True))
result=dict(passChecks=True,source=source_records,installedPackage=records,catalog=catalog_records)
args.output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(passChecks=True,packageFaces=len(records),catalogFaces=len(catalog_records),vector=True,ligaturesPreserved=True)))
