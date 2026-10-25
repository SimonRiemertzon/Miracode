"""Run the official one-font outlined SVG preview with isolated fontconfig."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
from xml.sax.saxutils import escape

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--catalog',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--inkscape-runtime',type=Path,required=True)
args=parser.parse_args();OUT=args.output;OUT.mkdir(parents=True,exist_ok=True)
scripts=OUT/'preview-build/bin/scripts';(scripts/'lib').mkdir(parents=True,exist_ok=True)
generator=(args.catalog/'bin/scripts/generate-font-image-previews.sh').read_text()
(scripts/'generate-font-image-previews.sh').write_text(generator.replace('first_step=TRUE','first_step=FALSE'))
for name in ('template-font-preview.svg','template-font-preview2.svg'):shutil.copyfile(args.catalog/'bin/scripts/lib'/name,scripts/'lib'/name)
registry=json.loads((args.catalog/'bin/scripts/lib/fonts.json').read_text());registry['fonts']=[f for f in registry['fonts'] if f['folderName']=='MiracodeText'];assert len(registry['fonts'])==1
(scripts/'lib/fonts.json').write_text(json.dumps(registry,indent=2)+'\n')
fontconfig=OUT/'preview-fontconfig.xml'
fontconfig.write_text('<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd"><fontconfig><dir>'+escape(str(args.catalog/'check-fonts/MiracodeText'))+'</dir><cachedir>'+escape(str(OUT/'preview-fontconfig-cache'))+'</cachedir></fontconfig>')
runtime=args.inkscape_runtime
env=dict(os.environ,PATH=str(runtime/'usr/bin')+':'+os.environ['PATH'],LD_LIBRARY_PATH=str(runtime/'usr/lib/x86_64-linux-gnu'),INKSCAPE_DATADIR=str(runtime/'usr/share/inkscape'),FONTCONFIG_FILE=str(fontconfig))
resolved=subprocess.check_output(['fc-match','MiracodeText Nerd Font','-f','%{file}'],env=env,text=True)
assert Path(resolved)==args.catalog/'check-fonts/MiracodeText/MiracodeTextNerdFont-Regular.ttf'
run=subprocess.run(['bash','generate-font-image-previews.sh'],cwd=scripts,env=env,capture_output=True,text=True)
(OUT/'official-preview-build.log').write_text(run.stdout+run.stderr);run.check_returncode()
preview=OUT/'preview-build/assets/img/previews/MiracodeText Nerd Font.svg'
assert '<path' in preview.read_text() and '<text' not in preview.read_text()
shutil.copyfile(preview,OUT/preview.name)
print(json.dumps(dict(passChecks=True,officialGenerator=True,outlinedSvg=True)))
