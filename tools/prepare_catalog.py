"""Prepare a local Nerd Fonts catalog candidate, with honest source provenance."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--catalog',type=Path,required=True)
args=parser.parse_args();repo=args.catalog
target=repo/'src/unpatched-fonts/MiracodeText';target.mkdir(parents=True,exist_ok=True)
for style,name in [('Regular','Miracode.ttf'),('Bold','Miracode-Bold.ttf')]:
    shutil.copyfile(ROOT/'dist/v10-source'/name,target/('MiracodeText-'+style+'.ttf'))
shutil.copyfile(ROOT/'LICENSE',target/'LICENSE.txt')
shutil.copyfile(ROOT/'tools/fix_win_bounds.py',target/'fix_win_bounds.py')
(target/'fix_win_bounds.py').chmod(0o755)
shutil.copyfile(ROOT/'COPYING-GENERATOR',target/'COPYING-postprocessor')
(target/'config.cfg').write_text('[Config]\ncommandline = --careful --metrics TYPO --name postscript --makegroups 1 --postprocess src/unpatched-fonts/MiracodeText/fix_win_bounds.py\nabort-mono-patch = True\n')
(target/'README.md').write_text('''# Miracode Text

Local OFL derivative of [Miracode](https://github.com/IdreesInc/Miracode),
an angular vector typeface by Idrees Hassan based on Monocraft.
Version 1.10, local v10 candidate. This is not an official upstream release.

Filled diamonds replace Ä/Ö/ä/ö/i/j dots and matching aliases/word dots.
Other accents, quotes, commas and punctuation remain unchanged. Capital
diaereses share the unchanged Å-ring bottom; lowercase
marks retain their original centers. Filled/hollow diamond bullets are centered
on the capital body; hollow tips match the unchanged å ring. Source Regular/Bold,
complete letter bodies,
monospaced advances, liga/calt programming operators, liga-only word logos,
centered literal list symbols and the prior accent/dash fixes are included.
Application numbering conventions remain application behavior.

License: SIL Open Font License 1.1, no Reserved Font Name declaration.
The generator's GPL-3.0-or-later license is separate.

Exact source: the contributor's local feature/all-diamond-dots-v10 branch
in the local source checkout. A source archive and checksum accompany the
review package. Before public submission, publish the source and replace this
local provenance with an immutable reachable URL. Source maintenance and the
derivative name must be reviewed with the existing Miracode proposals.
Update the existing Nerd Fonts draft #2098; do not create a duplicate proposal.

Build: pinned FontForge 20230101 and fontTools 4.63.0,
python tools/build.py --with-bold --base-only. The flat directory contains
unpatched Regular/Bold source fonts only; never commit patched font binaries.
The separate installed four-face local family includes 12-degree obliques.

Config chooses postscript naming because parsing the full name treats Text as
a weight. Forced Mono is disabled: it collapses multi-cell ligature widths.
Stock Normal/Propo remain available. A single-width-icons build without
--mono preserves source ligatures, and is used by the local installed family.
The stock patcher deliberately overlaps box/Powerline joins outside hhea.
The postprocess hook expands only Windows clipping bounds and SFNT checksums;
glyphs, layout tables and typographic spacing remain byte-identical. It uses
only Python's standard library and is GPL-3.0-or-later (COPYING-postprocessor);
font files remain OFL-1.1. Future forced-Mono support needs maintainer review.

AI assistance: OpenAI Codex (GPT-6.1). This candidate is prepared by an AI agent
and remains subject to human source/publication and Nerd Fonts review.
''')
(target/'README.md').write_text((target/'README.md').read_text()+'\nLocal source commit: '+subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()+' (not yet published).\n')
path=repo/'bin/scripts/lib/fonts.json';data=json.loads(path.read_text())
data['fonts']=[f for f in data['fonts'] if f['folderName']!='MiracodeText']
entry=dict(unpatchedName='Miracode Text',licenseId='OFL-1.1-no-RFN',RFN=False,version='1.10',patchedName='MiracodeText',folderName='MiracodeText',imagePreviewFont='MiracodeText Nerd Font',imagePreviewFontSource='MiracodeText/MiracodeText-Regular.ttf',linkPreviewFont=False,caskName='miracode-text',repoRelease=False,isMonospaced=True,description='Angular vector Miracode derivative with programming ligatures, diamond dots and centered filled/hollow diamond bullets')
index=next(i for i,f in enumerate(data['fonts']) if f['folderName'].casefold()>'miracodetext')
data['fonts'].insert(index,entry);path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
path=repo/'readme.md';text=path.read_text();anchor='| [Monaspice Nerd Font]'
assert anchor in text
row='| [MiracodeText Nerd Font][p-miracodetext]          | [Miracode Text][f-miracodetext]        | 1.10       | YES  |'
lines=text.splitlines();existing=next((i for i,line in enumerate(lines) if line.startswith('| [MiracodeText Nerd Font]')),None)
if existing is not None:
    lines[existing]=row;text='\n'.join(lines)+'\n'
else:
    text=text.replace(anchor,row+'\n'+anchor,1)
if '[p-miracodetext]:' not in text:
    text+='\n[p-miracodetext]:patched-fonts/MiracodeText\n[f-miracodetext]:https://github.com/IdreesInc/Miracode\n'
path.write_text(text)
print(target)
