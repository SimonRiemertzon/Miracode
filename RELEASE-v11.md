# Miracode Text 1.11 / local NF v11

Adopts punctuation option C: filled diamond dots in . : ; ! ? … · ¡ ¿,
including affected programming/word ligatures. Shapes match the accepted
v10 extended-punctuation source exactly. Quotes, commas, other accents,
letter bodies, Å/å rings, glyph advances and GSUB are preserved.

ÄÖäöij and matching aliases/word dots retain v10's diamonds. Capital Ä/Ö
bottoms align with Å at y=2208. Lowercase äö remain centered at y=1920;
ij stay at y=2016/2080 Regular/Bold, retaining their text-size stem gap.

The comparison's unordered lists use a repeating six-level cycle:
filled diamond, hollow diamond, filled circle, hollow circle, filled square,
hollow square. Full parent paths, hanging indents and capital-centered
markers apply to unordered as well as ordered/alphabetical/mixed lists.
The default depth is six; levels 7–12 repeat the same cycle. Literal font
glyphs for all six shapes are also capital-centered at y=1152.
List ancestry/marker selection belongs to the consuming app and cannot be
imposed globally by a font file.

Source family: Miracode Text. Installed local family: Miracode Text NF v11.
Four actual linked faces: Regular/Bold and 12-degree obliques for
Italic/Bold Italic; added icons remain upright. No separate Semibold face.
Programming operators support liga/calt and word logos remain liga-only.
All outlines are vector; no bitmap strikes or new autohinting. Small-size
antialiasing remains renderer/display dependent.

Pinned FontForge 20230101, fontTools 4.63.0 and Nerd Fonts 3.5.1:

```sh
python tools/build.py --with-bold --base-only --output dist/v11-source
python tools/build.py --with-bold --output dist/v11-release
```

The default punctuation policy is now extended. The full build preserves
multi-cell ligatures while making added icons single-cell. Intentional
Box/Powerline overlap stays intact; only Windows clipping bounds expand.
The catalog helper prepares flat unpatched Regular/Bold, OFL, README,
config, fonts.json and root readme. Stock Normal/Propo outputs, supported
Mono guard, metadata-only clipping hook and official outlined SVG are
verified. Source font contours must exactly match accepted option C.

This is a local OFL derivative, not an official upstream release or an
accepted Nerd Fonts catalog entry. Public submission still requires an
immutable reachable source reference and maintainer review of derivative
identity, maintenance and config. Use existing draft #2098. No public
upload occurs in this build/install workflow. Font OFL, generator GPL and
icon attribution/licenses are retained.

AI assistance: OpenAI Codex (GPT-6.1). AI-containing commits disclose this.
