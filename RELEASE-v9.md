# Miracode Text 1.09 / local NF v9

Selected design: filled diamond diaereses on Ä/Ö, bottom-aligned to the
unchanged Å ring at y=2208. Compact square i/j dots keep their original
Regular/Bold centers at y=2016/2080. Miracode/Miranda word dots and Cyrillic
references match. Full A/O bodies, Å/å ring designs, prior dash spacing,
monospaced text advances and programming ligatures remain intact.

The source font family is distinctly named Miracode Text. The installed local
four-face package is Miracode Text NF v9. This is an OFL derivative, not an
official IdreesInc/Miracode release or an accepted Nerd Fonts catalog entry.
Original font attribution/OFL license and separate generator GPL headers
are retained. COPYING-GENERATOR supplies the generator license text.

With pinned requirements-build.txt and FontForge 20230101 bindings:

```sh
python tools/build.py --with-bold --base-only --output dist/v9-source
python tools/build.py --with-bold --output dist/v9-release
```

The full build uses checksum-pinned Nerd Fonts 3.5.1, single-width icons
without forced Mono, postscript naming and preserved vector outlines.
Intentional box/Powerline joining overlap is preserved. Windows clipping
bounds expand to enclose it while typographic line spacing stays unchanged;
icons are not scaled or shifted to satisfy an overly strict hhea test.

All programming operators are available through liga and calt; Miracode,
Miranda, NOTE: and TODO: logos remain liga-only. Literal •/◦/▪/●/○/■/□ markers
are capital-centered. List ancestry and page marker placement are controlled
by the consuming app; they cannot be imposed globally by a font file.
No Semibold is claimed. The local Italic/Bold Italic faces are real linked
12-degree oblique files, not a separately drawn cursive design.

The local four-style package contains TTFs, exact-outline WOFF2s, CSS,
checksums, source provenance and font/icon licenses. Native Windows WPF/GDI,
fontconfig, HarfBuzz and browser proofs accompany the local release review.
No automatic hinting experiment is adopted; pixel antialiasing is renderer
and display dependent.

For Nerd Fonts, tools/prepare_catalog.py prepares a flat Regular/Bold source
candidate with README, OFL, config and registry/readme changes. Config selects
--name postscript to avoid treating Text as a weight and disables forced Mono
because the stock mode collapses multi-cell ligature widths. Stock Normal
and Propo variations are validated. Source publication, derivative naming,
maintenance and the forced-Mono decision remain maintainer review items.
The catalog config uses a standard-library postprocess hook to expand only
Windows clipping fields and checksums without reencoding any glyph/layout
table. Use the existing draft #2098, not a duplicate submission.

AI assistance: OpenAI Codex (GPT-6.1). AI-containing source changes disclose
this in their commit message. No public upload is performed by these tools.
