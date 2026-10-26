# Miracode Text NF v16 / local release 1.16

V16 keeps the original complete !/? bodies exactly at capital height. They are
neither shortened nor raised. Their tops and body paths match the v13 source.

Only their dots are resized to make the requested geometry fit. Diamond radii
are 128 Regular / 144 Bold, with bottom tips aligned to the text and period at
y=288 / 228. This leaves gaps of 256 / 224 units above the dots. Relative to
the text-sized v11 punctuation, the dots are about 27% / 33% narrower. They remain
sharp, four-point vector diamonds. Larger trials crowded the bodies at some
reading sizes in Windows, so this version uses the smaller pair.

Only !/? outlines differ from v15. The large raised period, other punctuation,
letters/accents, list symbols, advances and GSUB remain exact. Line spacing and
clipping metrics are unchanged. Monospacing and multi-cell ligatures remain.

Four linked styles: Regular, Bold, Italic, Bold Italic. Italics are 12-degree
obliques; added icons remain upright. Earlier installed families are retained.
Source checks cover cap height, complete body height, aligned dot bottoms and
clearance. Independent source/package comparisons require exact original v13
body contours in all four styles and unchanged outlines for every other glyph.

Font/OFL, generator/GPL and Nerd Fonts 3.5.1 icon attribution still apply.
Local derivative; no public publication or upstream acceptance is claimed.
AI assistance: OpenAI Codex (GPT-6.1).
