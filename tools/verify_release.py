"""Check release/source parity, icon coverage and approved-v16 geometry.

SPDX-License-Identifier: GPL-3.0-or-later
"""
import argparse
import hashlib
import json
from pathlib import Path

from fontTools.ttLib import TTFont
from verify_contribution import outline, compare_text

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--release', type=Path, required=True)
parser.add_argument('--approved', type=Path, required=True)
parser.add_argument('--repeat', type=Path)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
base = args.release / 'Miracode-Diamond-v1.16'
nerd = args.release / 'Miracode-Diamond-v1.16-Nerd-Font'
manifest = json.loads((nerd / 'manifest.json').read_text())
approved = json.loads((args.approved / 'manifest.json').read_text())
records = []
for entry in manifest['files']:
    patched_path = nerd / entry['file']
    source_path = base / ('MiracodeDiamond-' + entry['style'].replace(' ', '') + '.ttf')
    source, patched = TTFont(source_path), TTFont(patched_path)
    proof = compare_text(source, patched)
    old_entry = next(item for item in approved['files']
                     if item['style'] == entry['style'].replace('Oblique', 'Italic'))
    old = TTFont(args.approved / old_entry['file'])
    assert old.getBestCmap() == patched.getBestCmap()
    assert set(old.getGlyphOrder()) == set(patched.getGlyphOrder())
    differences = sorted(name for name in old.getGlyphOrder() if outline(old, name) != outline(patched, name))
    assert differences == ['miracode'], differences
    text_differences = [name for name in differences if name in source.getGlyphOrder()]
    assert text_differences == ['miracode'], text_differences
    assert {name: item[0] for name, item in old['hmtx'].metrics.items()} == {
        name: item[0] for name, item in patched['hmtx'].metrics.items()}
    assert patched['name'].getDebugName(1) == 'MiracodeDiamond Nerd Font'
    assert patched['name'].getDebugName(2) == entry['style']
    for code in (0xE0A0, 0xE0B0, 0xF07B, 0xF09B, 0xE606, 0xE73C, 0xF013, 0xF0001):
        assert patched['hmtx'][patched.getBestCmap()[code]][0] == 1536
    for name in patched.getGlyphOrder():
        glyph = patched['glyf'][name]
        glyph.recalcBounds(patched['glyf'])
        assert getattr(glyph, 'yMax', 0) <= patched['OS/2'].usWinAscent
        assert getattr(glyph, 'yMin', 0) >= -patched['OS/2'].usWinDescent
    if args.repeat:
        for directory, path in ((base, source_path), (nerd, patched_path)):
            assert path.read_bytes() == (args.repeat / directory.name / path.name).read_bytes()
    records.append({'file': patched_path.name, 'sha256': hashlib.sha256(patched_path.read_bytes()).hexdigest(),
                    'addedIconCodepoints': len(patched.getBestCmap()) - len(source.getBestCmap()),
                    'allAdvancesExactApprovedV16': True, 'allGlyphsWithinWindowsBounds': True,
                    'changedTextGlyphs': text_differences, 'changedIconGlyphs': len(differences) - 1,
                    'repeatFontBytesExact': bool(args.repeat), **proof})
report = {'pass': True, 'baseFaces': 4, 'patchedFaces': records}
args.output.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'pass': True, 'faces': len(records),
                  'iconOutlineChanges': [record['changedIconGlyphs'] for record in records]}))
