"""Build the four unpatched Miracode Text 1.16 contribution faces.

SPDX-License-Identifier: GPL-3.0-or-later
Uses the accepted v16 source and the installed package's 12-degree transform.
Requires the pinned FontForge/fontTools environment from requirements-build.txt.
"""
import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]


def build(output):
    output.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ, SOURCE_DATE_EPOCH='1707523200', PYTHONHASHSEED='0')
    subprocess.run([sys.executable, str(ROOT / 'tools/build.py'), '--with-bold',
                    '--base-only', '--output', str(output / 'base')],
                   env=environment, check=True)
    base_manifest = json.loads((output / 'base/manifest.json').read_text())
    records = []
    shear = math.tan(math.radians(12))
    for style in ('Regular', 'Bold', 'Oblique', 'BoldOblique'):
        bold, oblique = style.startswith('Bold'), 'Oblique' in style
        source = output / 'base' / ('Miracode-Bold.ttf' if bold else 'Miracode.ttf')
        font = TTFont(source, recalcTimestamp=False)
        if oblique:
            original = copy.deepcopy(font)
            glyphs = original.getGlyphSet()
            for name in original.getGlyphOrder():
                pen = TTGlyphPen(glyphs)
                glyphs[name].draw(TransformPen(pen, (1, 0, shear, 1, -shear * 1152, 0)))
                font['glyf'][name] = pen.glyph()
                font['glyf'][name].recalcBounds(font['glyf'])
                font['hmtx'][name] = (original['hmtx'][name][0],
                                     getattr(font['glyf'][name], 'xMin', 0))
        # Retain the same four-face RIBBI linking used by the approved package.
        # Oblique is an accurate design name; the Italic bit aids legacy linking.
        font['OS/2'].fsSelection = 128 | (32 if bold else 0) | (1 if oblique else 0)
        if not bold and not oblique:
            font['OS/2'].fsSelection |= 64
        font['head'].macStyle = (1 if bold else 0) | (2 if oblique else 0)
        font['head'].fontRevision = 1.16
        font['post'].italicAngle = -12 if oblique else 0
        font['hhea'].caretSlopeRise = 1000 if oblique else 1
        font['hhea'].caretSlopeRun = round(shear * 1000) if oblique else 0
        display = 'Bold Oblique' if style == 'BoldOblique' else style
        prefix = 'MiracodeText-' + style
        names = {1: 'Miracode Text', 2: display,
                 3: prefix + ';1.16;' + base_manifest['sourceSha256'][:12],
                 4: 'Miracode Text ' + display, 5: 'Version 1.16; local derivative',
                 6: prefix, 16: 'Miracode Text', 17: display}
        for name_id in (18, 21, 22):
            font['name'].removeNames(nameID=name_id)
        for name_id, value in names.items():
            font['name'].removeNames(nameID=name_id)
            for platform, encoding in ((3, 1), (1, 0)):
                font['name'].setName(value, name_id, platform, encoding,
                                     0x409 if platform == 3 else 0)
        target = output / (prefix + '.ttf')
        font.save(target)
        records.append({'file': target.name, 'style': display,
                        'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
    manifest = {'family': 'Miracode Text', 'version': '1.16',
                'status': 'Local contribution candidate; publication pending',
                'sourceSha256': base_manifest['sourceSha256'],
                'sourceDateEpoch': 1707523200, 'fontforge': base_manifest['fontforge'],
                'fonttools': base_manifest['fonttools'], 'unpatched': True,
                'obliqueDegrees': 12, 'files': records}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist/v16-contribution')
    build(parser.parse_args().output.resolve())
