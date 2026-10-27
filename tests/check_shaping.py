"""Exercise actual OpenType shaping, including positive/negative heart contexts.

SPDX-License-Identifier: GPL-3.0-or-later
Requires the system HarfBuzz shared library and fontTools.
"""
import argparse
import ctypes as c
import json
from pathlib import Path

from fontTools.ttLib import TTFont

OPERATORS = ['==', '===', '!=', '!==', '<=', '>=', '<-', '->', '=>', '<=>', '+=', '-=', '/**', '*/']
WORDS = ['Miracode', 'Miranda', 'NOTE:', 'TODO:']
POSITIVE = {'Miracode': 1, 'Miracode Diamond': 1, '(Miracode)': 1, 'Miracode!': 1,
            '->Miracode': 1, 'Miracode->': 1, 'Miranda Miracode': 1,
            'Miracode.Miracode': 2, 'Miracode\u00a0Diamond': 1, 'Miracode-Miracode': 2}
NEGATIVE = ['MyMiracodeTool', 'MiracodeDiamond', 'Miracodes', '_Miracode', 'Miracode_',
            '1Miracode', 'Miracode2', 'éMiracode', 'Miracodeå', 'ЖMiracode', 'MiracodeЖ',
            'MirandaMiracode', 'MiracodeMiranda', 'MiracodeMiracode', 'miracode', 'MIRACODE']
hb = c.CDLL('libharfbuzz.so.0')


def bind(name, result, *arguments):
    function = getattr(hb, name)
    function.restype, function.argtypes = result, list(arguments)
    return function


ptr, uint, integer = c.c_void_p, c.c_uint, c.c_int
blob_create = bind('hb_blob_create_from_file_or_fail', ptr, c.c_char_p)
face_create = bind('hb_face_create', ptr, ptr, uint)
font_create = bind('hb_font_create', ptr, ptr)
ot_funcs = bind('hb_ot_font_set_funcs', None, ptr)
buffer_create = bind('hb_buffer_create', ptr)
buffer_add = bind('hb_buffer_add_utf8', None, ptr, c.c_char_p, integer, uint, integer)
guess = bind('hb_buffer_guess_segment_properties', None, ptr)


class Feature(c.Structure):
    _fields_ = [(name, uint) for name in ('tag', 'value', 'start', 'end')]


class Info(c.Structure):
    _fields_ = [(name, uint) for name in ('codepoint', 'mask', 'cluster', 'var1', 'var2')]


class Position(c.Structure):
    _fields_ = [(name, integer) for name in ('x_advance', 'y_advance', 'x_offset', 'y_offset', 'var')]


feature_parse = bind('hb_feature_from_string', integer, c.c_char_p, integer, c.POINTER(Feature))
shape = bind('hb_shape', None, ptr, ptr, c.POINTER(Feature), uint)
infos = bind('hb_buffer_get_glyph_infos', c.POINTER(Info), ptr, c.POINTER(uint))
positions = bind('hb_buffer_get_glyph_positions', c.POINTER(Position), ptr, c.POINTER(uint))
destroy = {kind: bind('hb_' + kind + '_destroy', None, ptr) for kind in ('blob', 'face', 'font', 'buffer')}


def check(path):
    font = TTFont(path)
    blob = blob_create(str(path).encode())
    assert blob
    face = face_create(blob, 0)
    hf = font_create(face)
    ot_funcs(hf)

    def run(text, liga, calt):
        buffer = buffer_create()
        encoded = text.encode()
        buffer_add(buffer, encoded, len(encoded), 0, len(encoded))
        guess(buffer)
        flags = (Feature * 2)()
        for index, value in enumerate((f'liga={liga}', f'calt={calt}')):
            assert feature_parse(value.encode(), -1, c.byref(flags[index]))
        shape(hf, buffer, flags, 2)
        length = uint()
        data = infos(buffer, c.byref(length))
        names = [font.getGlyphName(data[index].codepoint) for index in range(length.value)]
        pos = positions(buffer, c.byref(length))
        advance = sum(pos[index].x_advance for index in range(length.value))
        destroy['buffer'](buffer)
        return names, advance

    for sequence in OPERATORS:
        off, width = run(sequence, 0, 0)
        assert len(off) == len(sequence)
        for liga, calt in ((1, 0), (0, 1), (1, 1)):
            on, joined_width = run(sequence, liga, calt)
            assert len(on) == 1 and on[0] != '.notdef', (path.name, sequence, liga, calt, on)
            assert joined_width == width == len(sequence) * 1536
    for word in WORDS:
        on, width = run(word, 1, 0)
        off, plain_width = run(word, 0, 0)
        contextual, _ = run(word, 0, 1)
        assert len(on) == 1 and width == plain_width == len(word) * 1536
        assert contextual == off, (path.name, word)
    contexts = []
    for liga, calt in ((1, 0), (1, 1)):
        for text, count in [*POSITIVE.items(), *((text, 0) for text in NEGATIVE)]:
            names, advance = run(text, liga, calt)
            assert names.count('miracode') == count, (path.name, text, liga, calt, names)
            assert '.notdef' not in names, (path.name, text, names)
            contexts.append({'text': text, 'liga': liga, 'calt': calt,
                             'hearts': names.count('miracode'), 'advance': advance})
    for composed, decomposed in [('Ä', 'A\u0308'), ('Ö', 'O\u0308'), ('Å', 'A\u030a'),
                                 ('ä', 'a\u0308'), ('ö', 'o\u0308'), ('å', 'a\u030a')]:
        assert run(composed, 1, 1) == run(decomposed, 1, 1)
    for kind, value in [('font', hf), ('face', face), ('blob', blob)]:
        destroy[kind](value)
    return {'file': path.name, 'pass': True, 'operatorSequences': 14, 'wordSequences': 4,
            'positiveContexts': len(POSITIVE), 'negativeContexts': len(NEGATIVE),
            'featureModes': ['liga', 'calt', 'both', 'off'], 'contexts': contexts}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('fonts', nargs='+', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = {'pass': True, 'fonts': [check(path) for path in args.fonts]}
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'pass': True, 'fonts': len(report['fonts']),
                      'heartContextsPerFont': (len(POSITIVE) + len(NEGATIVE)) * 2}))
