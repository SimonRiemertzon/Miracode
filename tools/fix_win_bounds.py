#!/usr/bin/env python3
"""Expand SFNT Windows clipping bounds without reencoding any glyph table.

SPDX-License-Identifier: GPL-3.0-or-later
Only Python's standard library is needed by the Nerd Fonts postprocess hook.
"""
import math
import os
from pathlib import Path
import struct
import sys
import tempfile

def checksum(data):
    padded=bytes(data)+bytes(-len(data)%4)
    return sum(struct.unpack('>'+str(len(padded)//4)+'I',padded)) & 0xFFFFFFFF

def protect(path):
    data=bytearray(path.read_bytes())
    assert len(data)>=12
    count=struct.unpack_from('>H',data,4)[0]
    tables={}
    for i in range(count):
        record=12+i*16
        tag,old_sum,offset,length=struct.unpack_from('>4sIII',data,record)
        assert offset+length<=len(data)
        tables[tag]=(record,offset,length)
    _,head,head_len=tables[b'head'];record,os2,os2_len=tables[b'OS/2']
    assert head_len>=54 and os2_len>=78
    ymin=struct.unpack_from('>h',data,head+38)[0]
    ymax=struct.unpack_from('>h',data,head+42)[0]
    before=struct.unpack_from('>HH',data,os2+74)
    after=(max(before[0],math.ceil(ymax/64)*64),max(before[1],math.ceil(-ymin/64)*64))
    if after==before:return
    struct.pack_into('>HH',data,os2+74,*after)
    struct.pack_into('>I',data,record+4,checksum(data[os2:os2+os2_len]))
    struct.pack_into('>I',data,head+8,0)
    struct.pack_into('>I',data,head+8,(0xB1B0AFBA-checksum(data))&0xFFFFFFFF)
    assert checksum(data)==0xB1B0AFBA
    descriptor,temp=tempfile.mkstemp(prefix=path.name+'.',dir=path.parent)
    try:
        with os.fdopen(descriptor,'wb') as stream:stream.write(data)
        os.chmod(temp,path.stat().st_mode&0o777)
        os.replace(temp,path)
    finally:
        if os.path.exists(temp):os.unlink(temp)

if __name__=='__main__':
    assert len(sys.argv)==2,'Usage: fix_win_bounds.py patched-font.ttf'
    protect(Path(sys.argv[1]))
