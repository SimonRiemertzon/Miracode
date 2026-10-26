# Miracode Text NF v15 / local release 1.15

V15 replaces the rejected shortened !/? bodies from v14 with the complete,
unchanged v13 source shapes. The large dots retain their shapes and sizes.
Both parts move by translation only; there is no shortening or scaling.

The dot bottoms align with the period and letters at y=288 Regular / 228 Bold.
Dots move upward by 208 / 164 units from v13. Complete bodies move upward by
352 / 384 units from v13, leaving a 256-unit gap above each dot. Their original
body heights of 1216 / 1336 units and stroke widths are preserved. The bodies
are deliberately taller than the capitals, reaching y=2368 / 2460, to make room
for the full-size parts and aligned baseline. Existing line/clipping metrics fit
the result without increasing line spacing.

Only ! and ? outlines differ from v14. The raised period, all other glyphs,
letter/accent geometry, six-symbol list cycle, advances and GSUB remain exact.
The font remains monospaced; multi-cell ligatures retain their advances.

Four linked styles: Regular, Bold, Italic, Bold Italic. Italics are 12-degree
obliques; added icons remain upright. Earlier installed families are preserved.
Source regression checks cover all three punctuation bottoms, complete body
heights and dot clearance. Independent source/package comparison checks the
intact v13 bodies and dots under translation, plus exact unchanged glyphs.

Font/OFL, generator/GPL and Nerd Fonts 3.5.1 icon attribution still apply.
Local derivative; no public publication or upstream acceptance is claimed.
AI assistance: OpenAI Codex (GPT-6.1).
