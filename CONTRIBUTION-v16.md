# Miracode Text 1.16 contribution source

Historical preparation record. The confirmed Miracode Diamond plan and current
build commands in README.md supersede provisional naming and maintenance below.

This local candidate preserves the approved v16 font design from commit
7152f7b2c3a84fdd22ce01bfde92dfec58567edf. It adds a reproducible, unpatched
four-face build for Nerd Fonts review. It is not an official release of
IdreesInc/Miracode or an accepted Nerd Fonts entry.

Provisional public identity: **Miracode Text 1.16**. Public source location and
maintenance responsibility remain unconfirmed. No publication is implied.

Use FontForge 20230101 Python bindings and fontTools 4.63.0, installed together
in the same Python environment. From the repository root:

```sh
python tools/build_contribution.py
```

The output is `dist/v16-contribution/MiracodeText-{Regular,Bold,Oblique,BoldOblique}.ttf`.
Only these four unpatched faces belong in the Nerd Fonts source directory.
Repeat the build to a different output directory to compare their SHA256 hashes.
The source timestamp is fixed at 2024-02-10 UTC. Binary reproducibility is
verified on the recorded Linux toolchain, not promised across different runtimes.

Regular/Bold come from the accepted vector generator. Obliques use the same
12-degree shear about y=1152 as the approved installed v16 package, with the
same integer rounding. Their design is accurately named Oblique; legacy Italic
style bits retain four-face application linking. Nerd Fonts uses
`--has-no-italic` so these join the Regular/Bold RIBBI family correctly.
No icons are present in these unpatched sources; icons added later stay upright.

The approved diamond letter/punctuation dots, cap-height complete !/? bodies,
raised period, centered literal symbols, fixed text advances and programming
ligatures are retained. No autohinting or redesign is introduced.

The optional Zen list stylesheet is application configuration, distributed
separately from the font. Neither the six-symbol list cycle nor the 12% diamond
marker enlargement is a font feature.

Font: SIL Open Font License 1.1, attribution in LICENSE, no Reserved Font Name
declaration. Generator and build tools: GPL-3.0-or-later, COPYING-GENERATOR.
The Nerd Fonts metadata-only Windows clipping hook retains its separate GPL
notice. Source publication must preserve both sets of notices.

AI assistance: OpenAI Codex (GPT-6.1), running in T3 Code. User approval of the
visual design is established; independent human source review is not claimed.
