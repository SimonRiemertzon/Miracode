"""Restrict the Miracode heart wordmark to complete words.

SPDX-License-Identifier: GPL-3.0-or-later
"""
import copy
import unicodedata

from fontTools.otlLib.builder import buildLookup
from fontTools.ttLib.tables import otTables


def restrict_wordmark(font):
    """Keep the existing ligatures; guard only the Miracode substitution.

    Letters, combining marks, numbers and connector punctuation (including _)
    count as word characters. Matching is within one font shaping run, as with
    other OpenType context rules. Application token/fallback boundaries matter.
    """
    cmap = font.getBestCmap()
    sequence = [cmap[ord(char)] for char in 'Miracode']
    gsub = font['GSUB'].table
    for record in gsub.ScriptList.ScriptRecord:
        if record.ScriptTag == 'dflt':
            record.ScriptTag = 'DFLT'
    lookups = gsub.LookupList.Lookup
    logo = None
    word_glyphs = {name for code, name in cmap.items()
                   if unicodedata.category(chr(code))[0] in 'LMN'
                   or unicodedata.category(chr(code)) == 'Pc'}
    reverse = {name: code for code, name in cmap.items()}
    for lookup in lookups:
        for subtable in lookup.SubTable:
            for first, ligatures in getattr(subtable, 'ligatures', {}).items():
                for ligature in list(ligatures):
                    inputs = [first, *ligature.Component]
                    if all(name in reverse and name in word_glyphs for name in inputs):
                        word_glyphs.add(ligature.LigGlyph)
                    if inputs == sequence:
                        assert logo is None, 'Duplicate Miracode substitution'
                        logo = copy.deepcopy(ligature)
                        ligatures.remove(ligature)
                if not ligatures:
                    del subtable.ligatures[first]
    assert logo is not None, 'Missing Miracode substitution'
    target = otTables.LigatureSubst()
    target.ligatures = {sequence[0]: [logo]}
    target_index = len(lookups)
    lookups.append(buildLookup([target]))

    def coverage(names):
        result = otTables.Coverage()
        result.glyphs = sorted(names, key=font.getGlyphID)
        return result

    def context(before=False, after=False, substitute=False):
        result = otTables.ChainContextSubst()
        result.Format = 3
        result.BacktrackCoverage = [coverage(word_glyphs)] if before else []
        result.BacktrackGlyphCount = len(result.BacktrackCoverage)
        result.InputCoverage = [coverage([name]) for name in sequence]
        result.InputGlyphCount = len(sequence)
        result.LookAheadCoverage = [coverage(word_glyphs)] if after else []
        result.LookAheadGlyphCount = len(result.LookAheadCoverage)
        result.SubstLookupRecord = []
        if substitute:
            record = otTables.SubstLookupRecord()
            record.SequenceIndex, record.LookupListIndex = 0, target_index
            result.SubstLookupRecord.append(record)
        result.SubstCount = len(result.SubstLookupRecord)
        return result

    # First match wins: a word character on either side blocks the wordmark.
    guard_index = len(lookups)
    lookups.append(buildLookup([context(before=True), context(after=True),
                                context(substitute=True)]))
    gsub.LookupList.LookupCount = len(lookups)
    feature = next(record.Feature for record in gsub.FeatureList.FeatureRecord
                   if record.FeatureTag == 'liga')
    feature.LookupListIndex.append(guard_index)
    feature.LookupCount = len(feature.LookupListIndex)
