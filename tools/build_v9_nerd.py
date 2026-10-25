"""Build stock Nerd Fonts outputs without forced-Mono ligature collapse."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--patcher',type=Path,required=True)
parser.add_argument('--fontforge',type=Path,required=True)
parser.add_argument('--output',type=Path,default=ROOT/'dist/v9-nerd')
args=parser.parse_args()
args.output.mkdir(parents=True,exist_ok=True)
records=[]
for variant,flags in (('Single',['--single-width-glyphs']),('Normal',[]),('Propo',['--variable-width-glyphs'])):
    for style in ('Regular','Bold'):
        source=ROOT/'dist/v9-source'/('Miracode-Bold.ttf' if style=='Bold' else 'Miracode.ttf')
        target=args.output/variant/style;target.mkdir(parents=True,exist_ok=True)
        command=[str(args.fontforge),'-quiet','-script',str(args.patcher/'font-patcher'),str(source),'--complete','--careful','--metrics','TYPO','--name','postscript','--no-progressbars','--outputdir',str(target),*flags]
        result=subprocess.run(command,cwd=args.patcher,env=os.environ.copy(),capture_output=True,text=True)
        (target/'patcher.log').write_text(result.stdout+result.stderr)
        result.check_returncode()
        files=list(target.glob('*.ttf'));assert len(files)==1
        records.append(dict(variant=variant,style=style,file=str(files[0].relative_to(args.output)),sha256=hashlib.sha256(files[0].read_bytes()).hexdigest(),command=command))
        (args.output/'manifest.json').write_text(json.dumps(dict(files=records,stockPatcher=True,forceMono=False),indent=2)+'\n')
        print(json.dumps(dict(variant=variant,style=style,file=files[0].name)),flush=True)
