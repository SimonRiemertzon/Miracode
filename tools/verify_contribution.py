"""Verify exact approved text design, reproducibility and catalog patch outputs.

SPDX-License-Identifier: GPL-3.0-or-later
"""
import argparse
import hashlib
import io
import json
from pathlib import Path

from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.misc.xmlWriter import XMLWriter
from fontTools.ttLib import TTFont


def outline(font, name):
    glyphs = font.getGlyphSet()
    pen = DecomposingRecordingPen(glyphs)
    glyphs[name].draw(pen)
    return pen.value


def compare_text(source, other, expected_fixed_pitch=1):
    old, new = source.getBestCmap(), other.getBestCmap()
    assert set(old).issubset(new), 'missing source codepoints'
    assert all(old[code] == new[code] for code in old), 'renamed source codepoints'
    for name in source.getGlyphOrder():
        assert outline(source, name) == outline(other, name), ('outline', name)
        assert source['hmtx'][name][0] == other['hmtx'][name][0], ('advance', name)
    # Stock FontForge patching canonicalizes the source's dflt script to DFLT.
    # Compare the complete decoded GSUB, allowing only that known tag spelling.
    layouts = []
    for font in (source, other):
        stream = io.StringIO()
        font['GSUB'].toXML(XMLWriter(stream), font)
        layouts.append(stream.getvalue().replace('<ScriptTag value="dflt"/>',
                                                 '<ScriptTag value="DFLT"/>'))
    assert layouts[0] == layouts[1], 'GSUB structure changed'
    assert source['hhea'].ascent == other['hhea'].ascent
    assert source['hhea'].descent == other['hhea'].descent
    assert {other['hmtx'][new[code]][0] for code in range(32, 127)} == {1536}
    assert other['post'].isFixedPitch == expected_fixed_pitch
    assert other['OS/2'].panose.bProportion == 9
    assert source['OS/2'].usWeightClass == other['OS/2'].usWeightClass
    assert source['post'].italicAngle == other['post'].italicAngle
    return {'sourceGlyphs': len(source.getGlyphOrder()),
            'sourceCodepoints': len(old), 'allTextOutlinesExact': True,
            'allTextAdvancesExact': True,
            'gsubByteIdentical': source.getTableData('GSUB') == other.getTableData('GSUB'),
            'gsubStructureExactExceptDefaultScriptCase': True,
            'typographicSpacingExact': True,
            'postIsFixedPitch': other['post'].isFixedPitch,
            'panoseProportion': other['OS/2'].panose.bProportion}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--repeat', type=Path, required=True)
    parser.add_argument('--approved', type=Path, required=True)
    parser.add_argument('--catalog', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((args.source / 'manifest.json').read_text())
    approved = json.loads((args.approved / 'manifest.json').read_text())
    records, output_records = [], []
    for entry in manifest['files']:
        path = args.source / entry['file']
        assert path.read_bytes() == (args.repeat / entry['file']).read_bytes(), path
        source = TTFont(path)
        approved_style = entry['style'].replace('Oblique', 'Italic')
        old = next(item for item in approved['files'] if item['style'] == approved_style)
        proof = compare_text(source, TTFont(args.approved / old['file']))
        records.append({'file': path.name, 'approvedStyle': approved_style,
                        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'repeatBuildByteIdentical': True, **proof})
        if args.catalog:
            catalog_source = args.catalog / 'src/unpatched-fonts/MiracodeText' / path.name
            assert catalog_source.read_bytes() == path.read_bytes()
            for variant in ('', 'Propo'):
                patched_path = args.catalog / 'check-fonts/MiracodeText' / (
                    'MiracodeTextNerdFont' + variant + '-' + entry['style'].replace(' ', '') + '.ttf')
                patched = TTFont(patched_path)
                # Stock Normal/Propo outputs have mixed icon/ligature widths and
                # FontForge emits isFixedPitch=0. Text advances stay one cell.
                proof = compare_text(source, patched, expected_fixed_pitch=0)
                top = bottom = 0
                for name in patched.getGlyphOrder():
                    glyph = patched['glyf'][name]
                    glyph.recalcBounds(patched['glyf'])
                    top = max(top, getattr(glyph, 'yMax', 0))
                    bottom = min(bottom, getattr(glyph, 'yMin', 0))
                assert top <= patched['OS/2'].usWinAscent
                assert bottom >= -patched['OS/2'].usWinDescent
                assert patched['name'].getDebugName(1) == 'MiracodeText Nerd Font' + (' Propo' if variant else '')
                assert len(patched['name'].getDebugName(1)) <= 31
                assert patched['name'].getDebugName(2) == entry['style']
                output_records.append({'file': patched_path.name,
                                       'variant': variant or 'Normal',
                                       'family': patched['name'].getDebugName(1),
                                       'linkedStyle': patched['name'].getDebugName(2),
                                       'angle': patched['post'].italicAngle,
                                       'allGlyphsWithinWindowsClippingBounds': True,
                                       'sha256': hashlib.sha256(patched_path.read_bytes()).hexdigest(),
                                       **proof})
    if args.catalog:
        outputs = list((args.catalog / 'check-fonts/MiracodeText').glob('*.ttf'))
        assert len(outputs) == 8, [path.name for path in outputs]
        assert not any('Mono' in path.name for path in outputs)
    report = {'pass': True, 'sourceFaces': records, 'catalogOutputs': output_records,
              'publicNaming': 'provisional', 'maintenance': 'unconfirmed'}
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'pass': True, 'sourceFaces': len(records),
                      'catalogOutputs': len(output_records)}))


if __name__ == '__main__':
    main()
