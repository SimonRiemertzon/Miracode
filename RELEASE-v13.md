# Miracode Text NF v13 / local release 1.13

This variant increases diamond punctuation and list-marker outlines. The four
separately named styles coexist with previous releases.

- Period, middle dot, colon and semicolon dot radii: 352 Regular / 384 Bold.
- Exclamation/question dots, including inverted forms: 304 / 320, retaining
  clearance from their heavier strokes. Punctuation dots in NOTE:/TODO: match.
- Ellipsis radii: 240 / 248. Three separated diamonds still fit one 1536-unit cell.
- Filled list diamonds (U+2022/U+25C6) radii: 480 / 528. Hollow diamonds
  (U+25E6/U+25C7) have sharp outer tips, radii 544 / 576 and counters 352 / 320.
  All remain centered at y=1152.

Letter outlines, Swedish accent shapes and positions, quotes, commas, circular
and square list glyphs, all advances, and GSUB are preserved from v12. Ligatures
retain their multiple-cell advances. The font is already monospaced; do not force
Nerd Fonts `--mono`, which collapses those advances.

Unordered lists require an application or stylesheet change to remove numeric
prefixes. The matching Zen customization is scoped to hosted T3 chat/composer.
It shows symbols only on unordered rows and parent paths on ordered rows, while
retaining task checkboxes. The comparison uses real font glyphs for bullets.

Build with the existing pinned toolchain and `tools/build.py --with-bold`.
`tests/check_large_diamonds.py` checks the new source geometry. Prior optical,
accent, fixed-width and ligature checks also apply. The local four-face package
includes true linked styles; italic faces are 12-degree obliques with upright
added icons. Font and icon licenses accompany the package.

Local derivative; no public publication or Nerd Fonts acceptance is claimed.
AI assistance: OpenAI Codex (GPT-6.1).
