# Miracode Text 1.10 / local NF v10

Filled diamonds replace the requested Ä/Ö/ä/ö/i/j dots, matching Cyrillic
aliases and Miracode/Miranda word dots. Other accents, quotation marks,
commas and punctuation retain their v9 outlines. Capital Ä/Ö retain the accepted diamond design and
bottom alignment at y=2208. Lowercase ä/ö marks stay centered at y=1920;
i/j keep their original centers at y=2016/2080 in Regular/Bold. Their smaller
diamonds preserve the required dot/stem gap at 10–16px. Complete letter
bodies, Å/å rings, advances and GSUB remain unchanged from v9.

Filled U+2022/U+25C6 and hollow U+25E6/U+25C7 list diamonds share capital
center y=1152. Hollow markers follow å's flat-tip ring geometry with a real
counter. Other geometric circles/squares retain their own meanings and stay
centered. Added Nerd Fonts icon drawings retain their original designs.

The comparison alternates filled diamonds at odd unordered-list levels and
hollow diamonds at even levels, with full parent paths, hanging indents and
capital-centered vector shapes. Numeric/alphabetical/mixed paths and the
compact five-row style comparison remain available. List ancestry is app
behavior and cannot be imposed globally by installing a font.

Separate actual-font punctuation studies use --punctuation-dots basic
(. : …) or extended (. : ; ! ? … · ¡ ¿). These do not change quotes, commas
or other accents. The default release uses --punctuation-dots original.
Affected programming/word ligatures follow each optional punctuation policy.
These studies are review options, not an adopted release choice.

The source family remains Miracode Text. The local installed four-face family
is Miracode Text NF v10. Regular/Bold are source-generated; Italic/Bold Italic
are linked 12-degree obliques with upright added icons. No separate Semibold
is claimed. Programming operators support liga and calt; word logos remain
liga-only. Vector paths contain no bitmap strikes or new autohinting.

With pinned FontForge 20230101 and fontTools 4.63.0:

```sh
python tools/build.py --with-bold --base-only --output dist/v10-source
python tools/build.py --with-bold --output dist/v10-release
```

The full build uses checksum-pinned Nerd Fonts 3.5.1 and single-width icons
without forced Mono. Source and independent delta tests verify that all
non-dot contours remain exact. Windows clipping fields enclose intentional
Box/Powerline overshoots without changing typographic line spacing or paths.

tools/prepare_catalog.py prepares flat unpatched Regular/Bold, OFL, README,
config, source identity, fonts.json and the root readme. The supported Mono
guard avoids collapsing multi-cell ligatures; stock Normal/Propo variations
are verified. The standard-library clipping hook changes only OS/2 metrics
and checksums, not glyph/layout bytes. Official outlined SVG preview and
native Windows/Linux installation/rendering evidence accompany the release.

This is a local OFL derivative, not an official IdreesInc/Miracode release or
an accepted Nerd Fonts catalog entry. Before public submission, publish an
immutable reachable source reference. Derivative identity, maintenance and
config choices require maintainer review; use existing draft #2098. No public
upload is performed by the build or install workflow. Original font OFL and
separate GPL generator attribution are retained; icon licenses are packaged.

AI assistance: OpenAI Codex (GPT-6.1). AI-containing commits disclose this.
