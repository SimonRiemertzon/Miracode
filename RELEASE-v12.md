# Miracode Text 1.12 / local NF v12

Full-stop diamonds are more pronounced at small sizes. The period radius
changes from176 to216 Regular and216 to256 Bold, preserving its center and
1536-unit text advance. The ellipsis has three separate diamonds inside that
same advance; its earlier source extended into the following code cell.
Only period and ellipsis contours change from v11. All other contours,
advances and GSUB remain exact. Punctuation C, ÄÖäöij diamond dots, Å/å rings,
quotes, commas and other accents keep their accepted designs.

The four-face local family is Miracode Text NF v12. It is already monospaced:
ASCII advances are1536, post.isFixedPitch=1 and PANOSE proportion9. Actual
Regular/Bold/Italic/Bold Italic faces preserve cell widths and programming
ligatures; obliques are12 degrees. There is no separate Semibold. Added
icons stay upright. Outlines are vector with no bitmap strikes/new autohinting.

The standalone comparison retains parent-aware lists and the repeating
six-level ◆ ◇ ● ○ ■ □ marker cycle. Hosted T3 requires its own renderer/style
change; font installation cannot generate ancestor labels. A separate local
Zen stylesheet is tested against the real renderer and current hosted CSS.
It preserves native list ordinals and task checkboxes and is not part of the
font's behavior. Browser font-cache/selection checks are recorded separately.

With pinned FontForge20230101/fontTools4.63.0 and Nerd Fonts3.5.1:

```sh
python tools/build.py --with-bold --base-only --output dist/v12-source
python tools/build.py --with-bold --output dist/v12-release
```

Default punctuation remains extended/C. The release pipeline verifies the
two-glyph delta, period/ellipsis geometry, complete package/WOFF2 contours,
ligatures, icon advances and clipping. Source and catalog OFL/GPL attribution
are retained. Single-width icons avoid forced-Mono collapse of multi-cell
ligatures. Stock catalog Normal/Propo outputs and outlined SVG preview are
checked; the supported Mono guard and clipping hook remain unchanged.

This is a local derivative, not an official upstream or accepted Nerd Fonts
release. Immutable reachable source publication and maintainer review remain
necessary before public submission. Use existing draft2098. No public push,
upload or PR update is performed by the local release/install scripts.

AI assistance: OpenAI Codex (GPT-6.1).
