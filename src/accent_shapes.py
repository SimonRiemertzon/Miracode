"""Optical source designs for Swedish accents at small text sizes.

SPDX-License-Identifier: GPL-3.0-or-later
"""
import fontforge

def drawSwedishAccent(glyph, code, characters, diacritics, draw, bold=False):
    capital = code != 0xE5
    ring = code != 0xC4
    source = fontforge.font()
    try:
        def component(name, data, stroke):
            part = source.createChar(-1, name)
            draw(data, part, part.glyphPen(), stroke=stroke)
            return part

        base = characters[65 if capital else 97]
        body = component('body', base, 312 if bold else 192)
        opening = None
        if capital and bold:
            regular = component('regular', base, 192)
            opening = next(c.dup() for c in regular.foreground if not c.isClockwise())
        layer = fontforge.layer()
        for contour in body.foreground:
            contour = opening.dup() if opening is not None and not contour.isClockwise() else contour.dup()
            if capital and ring:
                # Shorten the vertical legs below the arch. Translate the
                # entire upper opening unchanged instead of squeezing it.
                for point in contour:
                    if point.y >= 1152:
                        point.y -= 192
            layer += contour

        accent_name = 'ring_above' if ring else 'diaeresis'
        # Keep the capital ring at its existing height and lower the small
        # ring by half a source pixel, as in the personal repaired build.
        data = {'pixels': diacritics[accent_name]['pixels'],
                'descent': -7 if capital and ring else (-5.5 if ring else -8)}
        accent = component('accent', data, 192 if ring else (312 if bold else 192))
        for contour in accent.foreground:
            contour = contour.dup()
            if ring and bold and not contour.isClockwise():
                # Retain the regular outer ring, widening its hole from240
                # to384 units. A full312-unit stroke nearly closes this hole.
                center_y = 2432 if capital else 2048
                for point in contour:
                    point.x = 640 + (point.x - 640) * 1.6
                    point.y = center_y + (point.y - center_y) * 1.6
            layer += contour
        glyph.foreground = layer
        glyph.round()
    finally:
        source.close()
