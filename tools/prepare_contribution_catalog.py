"""Refresh an isolated Nerd Fonts catalog from the four unpatched v16 faces.

SPDX-License-Identifier: GPL-3.0-or-later
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--catalog', type=Path, required=True)
parser.add_argument('--source', type=Path, default=ROOT / 'dist/v16-contribution')
args = parser.parse_args()
repo = args.catalog.resolve()
target = repo / 'src/unpatched-fonts/MiracodeText'
target.mkdir(parents=True, exist_ok=True)
manifest = json.loads((args.source / 'manifest.json').read_text())
assert manifest['unpatched'] and manifest['version'] == '1.16'
assert len(manifest['files']) == 4
for entry in manifest['files']:
    shutil.copyfile(args.source / entry['file'], target / entry['file'])
shutil.copyfile(ROOT / 'LICENSE', target / 'LICENSE.txt')
shutil.copyfile(ROOT / 'tools/fix_win_bounds.py', target / 'fix_win_bounds.py')
(target / 'fix_win_bounds.py').chmod(0o755)
shutil.copyfile(ROOT / 'COPYING-GENERATOR', target / 'COPYING-postprocessor')
(target / 'config.cfg').write_text(
    '[Config]\n'
    'commandline = --careful --metrics TYPO --name postscript --makegroups 1 '
    '--has-no-italic --postprocess src/unpatched-fonts/MiracodeText/fix_win_bounds.py\n'
    'abort-mono-patch = True\n')
commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
(target / 'README.md').write_text('''# Miracode Text

Version **1.16**, approved v16 design; local contribution candidate.
A distinct derivative of [Miracode](https://github.com/IdreesInc/Miracode),
the angular vector typeface by Idrees Hassan based on Monocraft.
This is not an official upstream Miracode release or an accepted Nerd Fonts entry.

Four unpatched faces: Regular, Bold, Oblique and Bold Oblique. The slanted
faces are 12-degree obliques of the approved Regular/Bold designs, linked
as the Italic pair for legacy application compatibility. `--has-no-italic`
keeps the obliques in the same RIBBI family. No separate true Italic is supplied.

Filled diamonds appear in diaereses, i/j and matching aliases/word marks.
Diamond punctuation covers . : ; ! ? … · ¡ ¿. The complete !/? bodies stay
at capital height, with smaller separated diamond dots aligned to the raised
period/text bottom. Large literal list diamonds, other centered list symbols,
accepted accent/dash repairs, source-generated Bold, fixed text advances,
multi-cell ligatures, programming liga/calt and liga-only word logos are retained.
No new autohinting is applied.

The optional Zen stylesheet controls the six-symbol unordered-list cycle,
ordered parent paths and 12% diamond marker enlargement. It is separate from
this font contribution; installing a font cannot configure those behaviors.

Font license: SIL Open Font License 1.1, no Reserved Font Name declaration;
original attribution is retained in LICENSE.txt. Generator/build tools and
the metadata postprocessor are separately GPL-3.0-or-later. The postprocessor
license is COPYING-postprocessor; font outlines remain OFL-1.1.

Source provenance: approved design commit
`7152f7b2c3a84fdd22ce01bfde92dfec58567edf`, plus the contribution build commit
recorded below. Source/build archives and checksums accompany the local review.
An immutable public source URL is still pending: publish the reviewed derivative
source before public submission and replace this local-only provenance.
Public derivative naming and maintenance responsibility require confirmation.

Rebuild using FontForge 20230101 Python bindings and fontTools 4.63.0:
`python tools/build_contribution.py`. This emits all four unpatched faces.
The oblique text outlines match the approved installed v16 faces; icons are
added later by Nerd Fonts and stay upright. Do not submit the installed patched ZIP.

Config uses postscript naming because parsing the full name treats Text as a
weight. TYPO metrics preserve accepted line spacing. Forced Mono is disabled
because stock --mono collapses multi-cell ligature advances. Supported Normal
and Propo builds preserve them. A separate local single-width-icons build works
without --mono; a broader patcher fix remains a separate proposal.

The metadata-only postprocess hook expands Windows clipping bounds for
intentional box/Powerline joins. It changes OS/2 clipping bounds and SFNT
checksums only, retaining glyph/layout tables and typographic spacing byte-for-byte.
Naming, TYPO metrics, the hook and Mono policy require Nerd Fonts maintainer review.

Update existing draft ryanoasis/nerd-fonts#2098 after source publication and
authorization. Focused upstream Miracode repair proposals remain separate;
original-author acceptance of this derivative is not established.

AI assistance: OpenAI Codex (GPT-6.1), running in T3 Code. Prepared by an AI
agent using the user's approved visual design. Independent human source
review is not claimed. No public posting is authorized by this local package.
''' + '\nLocal contribution build source commit: `' + commit + '` (not yet published).\n')
path = repo / 'bin/scripts/lib/fonts.json'
registry = json.loads(path.read_text())
entry = next(font for font in registry['fonts'] if font['folderName'] == 'MiracodeText')
entry.update(version='1.16', repoRelease=False,
             description='Angular Miracode derivative with four faces, programming ligatures and diamond letter/punctuation dots')
path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + '\n')
path = repo / 'readme.md'
lines = path.read_text().splitlines()
for index, line in enumerate(lines):
    if line.startswith('| [MiracodeText Nerd Font]'):
        lines[index] = '| [MiracodeText Nerd Font][p-miracodetext]          | [Miracode Text][f-miracodetext]        | 1.16       | YES  |'
    elif line.startswith('[f-miracodetext]:'):
        lines[index] = '[f-miracodetext]:src/unpatched-fonts/MiracodeText'
path.write_text('\n'.join(lines) + '\n')
print(target)
