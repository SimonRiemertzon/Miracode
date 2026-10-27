"""Build reproducible Miracode Diamond base and complete Nerd Font releases.

SPDX-License-Identifier: GPL-3.0-or-later
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

from fontTools.ttLib import TTFont

from build_contribution import build
from build import PATCHER_SHA256, PATCHER_VERSION, normalize

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def archive(directory, filename):
    destination = directory.parent / filename
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as package:
        for path in sorted(directory.rglob('*')):
            if path.is_file():
                info = zipfile.ZipInfo(directory.name + '/' + str(path.relative_to(directory)), (2024, 2, 10, 0, 0, 0))
                info.compress_type, info.create_system, info.external_attr = zipfile.ZIP_DEFLATED, 3, 0o100644 << 16
                package.writestr(info, path.read_bytes())
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist/diamond-release')
    parser.add_argument('--patcher-archive', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    assert digest(args.patcher_archive) == PATCHER_SHA256, 'Pinned patcher archive checksum mismatch'
    patcher = output / 'build/patcher'
    patcher.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.patcher_archive) as package:
        assert all(not Path(name).is_absolute() and '..' not in Path(name).parts for name in package.namelist())
        package.extractall(patcher)
    base_source = output / 'build/source'
    build(base_source)
    manifest = json.loads((base_source / 'manifest.json').read_text())
    base = output / 'Miracode-Diamond-v1.16'
    nerd = output / 'Miracode-Diamond-v1.16-Nerd-Font'
    base.mkdir(exist_ok=True)
    nerd.mkdir(exist_ok=True)
    env = dict(os.environ, SOURCE_DATE_EPOCH='1707523200', PYTHONHASHSEED='0')
    patched_weights = {}
    for entry in manifest['files']:
        source = base_source / entry['file']
        shutil.copyfile(source, base / source.name)
        target = output / 'build/patched' / entry['style'].replace(' ', '')
        target.mkdir(parents=True, exist_ok=True)
        weight = 'Bold' if entry['style'].startswith('Bold') else 'Regular'
        patch_source = base_source / 'base' / ('Miracode-Bold.ttf' if weight == 'Bold' else 'Miracode.ttf')
        command = [sys.executable, str(patcher / 'font-patcher'), str(patch_source), '--complete',
                   '--careful', '--single-width-glyphs', '--metrics', 'TYPO', '--name', 'postscript',
                   '--has-no-italic', '--makegroups', '1', '--no-progressbars', '--outputdir', str(target)]
        if weight not in patched_weights:
            run = subprocess.run(command, cwd=patcher, env=env, capture_output=True, text=True)
            (target / 'patcher.log').write_text(run.stdout + run.stderr)
            run.check_returncode()
            fonts = list(target.glob('*.ttf'))
            assert len(fonts) == 1, fonts
            patched_weights[weight] = fonts[0]
        destination = nerd / ('MiracodeDiamondNerdFont-' + entry['style'].replace(' ', '') + '.ttf')
        shutil.copyfile(patched_weights[weight], destination)
        subprocess.run([sys.executable, str(ROOT / 'tools/fix_win_bounds.py'), str(destination)], check=True)
        font = TTFont(destination)
        text = TTFont(source)
        for name in text.getGlyphOrder():
            font['glyf'][name] = copy.deepcopy(text['glyf'][name])
            font['hmtx'][name] = text['hmtx'][name]
        font['head'].macStyle = text['head'].macStyle
        font['post'].italicAngle = text['post'].italicAngle
        font['hhea'].caretSlopeRise = text['hhea'].caretSlopeRise
        font['hhea'].caretSlopeRun = text['hhea'].caretSlopeRun
        font['OS/2'].fsSelection = (font['OS/2'].fsSelection & ~(1 | 32 | 64 | 512)) | text['OS/2'].fsSelection
        # Retain the approved release's single-width icons without forced Mono.
        # This separately named release is distinct from stock catalog variants.
        family = 'MiracodeDiamond Nerd Font'
        names = {1: family, 2: entry['style'], 4: family + ' ' + entry['style'],
                 6: 'MiracodeDiamondNF-' + entry['style'].replace(' ', ''),
                 16: family, 17: entry['style']}
        for name_id, value in names.items():
            font['name'].removeNames(nameID=name_id)
            for platform, encoding in ((3, 1), (1, 0)):
                font['name'].setName(value, name_id, platform, encoding, 0x409 if platform == 3 else 0)
        font.save(destination)
        normalize(destination, 1707523200, manifest['sourceSha256'])
        font = TTFont(destination)
        assert font['name'].getDebugName(1) == 'MiracodeDiamond Nerd Font'
        assert font['post'].isFixedPitch == 1
        entry['patchedFile'] = destination.name
        entry['patchedSha256'] = digest(destination)
    for path in (patcher / 'src/glyphs').rglob('*'):
        if path.is_file() and path.name.lower().startswith(('license', 'copying', 'readme')):
            destination = nerd / 'icon-licenses' / path.relative_to(patcher / 'src/glyphs')
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, destination)
    for directory in (base, nerd):
        shutil.copyfile(ROOT / 'LICENSE', directory / 'LICENSE.txt')
        (directory / 'README.txt').write_text(
            'Miracode Diamond v1.16' + (' Nerd Font' if directory == nerd else '') + '\n\n'
            'Maintained by SimonRiemertzon; a derivative of Miracode by Idrees Hassan.\n'
            'Original: https://github.com/IdreesInc/Miracode\n'
            'Four real faces: Regular, Bold, Oblique and Bold Oblique (12-degree slant).\n'
            'Approved diamond letter/punctuation design, full coding ligatures and arrows.\n'
            'Only the complete word Miracode has the original heart; Miranda and ordinary i do not.\n'
            'Words are matched within a shaping run; token/fallback boundaries can limit context.\n'
            'The font includes all supported features. Applications control feature activation.\n'
            'The optional Zen list stylesheet is separate application configuration.\n'
            'The patched release retains single-width icons without forced Mono.\n'
            'It uses the selected release family name; stock catalog Normal/Propo are separate builds.\n'
            'No upstream endorsement or Nerd Fonts catalog acceptance is claimed.\n'
            'Font: SIL OFL 1.1; generator and build tools: GPL-3.0-or-later.\n'
            'AI assistance: OpenAI Codex (GPT-6.1), running in T3 Code.\n')
        patched = directory == nerd
        package_manifest = dict(manifest, patched=patched, unpatched=not patched,
                                family='MiracodeDiamond Nerd Font' if patched else 'Miracode Diamond',
                                maintainer='SimonRiemertzon',
                                files=[{'file': entry['patchedFile'] if patched else entry['file'],
                                        'sha256': entry['patchedSha256'] if patched else entry['sha256'],
                                        'style': entry['style']} for entry in manifest['files']])
        if directory == nerd:
            package_manifest.update(nerdFontsVersion=PATCHER_VERSION, patcherSha256=PATCHER_SHA256,
                                    forcedMono=False, singleWidthIcons=True)
        (directory / 'manifest.json').write_text(json.dumps(package_manifest, indent=2) + '\n')
        (directory / 'SHA256SUMS').write_text(''.join(digest(path) + '  ' + str(path.relative_to(directory)) + '\n'
                                                  for path in sorted(directory.rglob('*')) if path.is_file() and path.name != 'SHA256SUMS'))
    all_fonts = [*base.glob('*.ttf'), *nerd.glob('*.ttf')]
    subprocess.run([sys.executable, str(ROOT / 'tests/check_shaping.py'), *map(str, all_fonts),
                    '--output', str(output / 'shaping-verification.json')], check=True)
    archives = [archive(base, base.name + '.zip'), archive(nerd, nerd.name + '.zip')]
    (output / 'delivery.json').write_text(json.dumps({'family': 'Miracode Diamond', 'version': '1.16',
        'archives': [{'file': path.name, 'sha256': digest(path)} for path in archives]}, indent=2) + '\n')
    print(json.dumps({'pass': True, 'output': str(output), 'baseFaces': 4, 'patchedFaces': 4}))


if __name__ == '__main__':
    main()
