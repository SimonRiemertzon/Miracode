"""Prepare the isolated Miracode Diamond Nerd Fonts catalog candidate.

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
parser.add_argument('--source', type=Path, default=ROOT / 'dist/diamond-source')
args = parser.parse_args()
repo = args.catalog.resolve()
target = repo / 'src/unpatched-fonts/MiracodeDiamond'
target.mkdir(parents=True, exist_ok=True)
manifest = json.loads((args.source / 'manifest.json').read_text())
assert manifest['unpatched'] and manifest['family'] == 'Miracode Diamond'
assert manifest['version'] == '1.16' and len(manifest['files']) == 4
for old in target.glob('MiracodeText-*.ttf'):
    old.unlink()
for entry in manifest['files']:
    shutil.copyfile(args.source / entry['file'], target / entry['file'])
shutil.copyfile(ROOT / 'LICENSE', target / 'LICENSE.txt')
shutil.copyfile(ROOT / 'COPYING-GENERATOR', target / 'COPYING-postprocessor')
shutil.copyfile(ROOT / 'tools/fix_win_bounds.py', target / 'fix_win_bounds.py')
(target / 'fix_win_bounds.py').chmod(0o755)
(target / 'config.cfg').write_text(
    '[Config]\ncommandline = --careful --metrics TYPO --name postscript --makegroups 1 '
    '--has-no-italic --postprocess src/unpatched-fonts/MiracodeDiamond/fix_win_bounds.py\n'
    'abort-mono-patch = True\n')
commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
(target / 'README.md').write_text((ROOT / 'CATALOG-README.md').read_text().replace('SOURCE_COMMIT', commit))
path = repo / 'bin/scripts/lib/fonts.json'
registry = json.loads(path.read_text())
entry = next(font for font in registry['fonts'] if font['folderName'] in ('MiracodeText', 'MiracodeDiamond'))
entry.update(unpatchedName='Miracode Diamond', patchedName='MiracodeDiamond',
             folderName='MiracodeDiamond', version='1.16', repoRelease=False,
             imagePreviewFont='MiracodeDiamond Nerd Font',
             imagePreviewFontSource='MiracodeDiamond/MiracodeDiamond-Regular.ttf',
             caskName='miracode-diamond',
             description='Maintained Miracode derivative with diamond dots, whole-word heart logo, coding ligatures and four faces')
path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + '\n')
path = repo / 'readme.md'
text = path.read_text().replace('MiracodeText Nerd Font', 'MiracodeDiamond Nerd Font')
text = text.replace('Miracode Text', 'Miracode Diamond').replace('miracodetext', 'miracodediamond')
text = text.replace('src/unpatched-fonts/MiracodeText', 'src/unpatched-fonts/MiracodeDiamond')
text = text.replace('patched-fonts/MiracodeText', 'patched-fonts/MiracodeDiamond')
path.write_text(text)
print(target)
