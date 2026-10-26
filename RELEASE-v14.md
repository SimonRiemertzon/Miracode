# Miracode Text NF v14 / local release 1.14

V14 corrects spacing around the enlarged punctuation from v13. Period diamonds
move upward by 256 Regular / 228 Bold units, aligning their bottom tip with the
letters and digits at y=288 / 228. Their sizes are unchanged.

The lower body of ! and ? ends 256 units higher, adding one source pixel of
clearance above the unchanged large dot. The gap is now 368 Regular / 292 Bold
units (previously 112 / 36). The upper part stays fixed, preserving cap height;
the lower terminal moves as a unit to retain its width and cap shape, with a
smooth positional transition in the middle of the body.

Only period, exclamation mark and question mark outlines change from v13. Every
other glyph, all advances, GSUB, letter/accent geometry and the six-symbol list
cycle remain unchanged. The font remains monospaced, with multi-cell ligatures.

Four linked styles: Regular, Bold, Italic, Bold Italic. Italics are 12-degree
obliques; added icons stay upright. Previous installed families are retained.
Use the four TTF files for Windows/Linux installation and WOFF2 for web use.

Focused checks: tests/check_punctuation_spacing.py and the existing period,
diamond, accent, fixed-width and shaping checks. Full source/package outline
comparisons must allow exactly these three glyphs and preserve every advance.
Font/OFL, generator/GPL and Nerd Fonts 3.5.1 icon attribution still apply.

Local derivative; no public publication or upstream acceptance is claimed.
AI assistance: OpenAI Codex (GPT-6.1).
