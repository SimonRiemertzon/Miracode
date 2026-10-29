# Miracode Diamond

**Version 1.16 · maintained by SimonRiemertzon.**

A derivative of [Miracode](https://github.com/IdreesInc/Miracode), the angular
programming font by **Idrees Hassan**. Miracode Diamond keeps the original
character and ligature coverage and adds the approved diamond-dot design,
source Bold and linked 12-degree obliques. The upstream for this fork and its
focused original-project contributions is **IdreesInc/Miracode**.

This source is prepared locally. The planned fork is
`SimonRiemertzon/Miracode-Diamond`; it has not yet been renamed or published.
No official Miracode endorsement or Nerd Fonts catalog acceptance is claimed.

## Fonts

- **Miracode Diamond**: unpatched base, Regular/Bold/Oblique/Bold Oblique.
- **MiracodeDiamond Nerd Font**: the same four text faces with the complete
  Nerd Fonts 3.5.1 icon set. The installable package keeps single-width icons
  without forcing multi-cell text ligatures to one cell. Its selected family
  name is distinct from the stock catalog Normal/Propo build variants.
- The version is stored separately as **1.16**. Releases can be called
  Miracode Diamond v1.16 and Miracode Diamond v1.16 Nerd Font.

The approved v16 punctuation, Swedish accents, diamond letter dots, centered
literal symbols and text advances are preserved. The complete word **Miracode**
uses the original heart-bearing i. `Miracode Diamond` therefore has that heart;
`MyMiracodeTool`, `MiracodeDiamond`, `Miranda` and ordinary i do not.

All 18 original ligature sequences remain. Programming operators work through
liga and calt; the four special words use liga. Applications control which
built-in features are enabled. Word context is evaluated within a shaping run;
syntax-token or fallback-font boundaries can affect it. The optional Zen list
cycle and marker-size stylesheet is separate application configuration.

## Design history and Swedish accents

The Swedish accent work was developed in the source generator for small text
sizes. Regular uses a 192-unit source stroke and Bold uses 312 units. A, Å and
Ä share identical full A bodies within each weight, and Ö retains the full O
body. Bold preserves the Regular A's upper opening rather than closing it
while increasing the stroke weight. Character advances, programming ligatures
and family line metrics stay consistent across the weights.

The Å ring was separated from the A body so the shapes remain distinct. Its
counter remains open in Bold; Regular has a larger counter and a lighter ring.
The small å ring was lowered slightly. These changes preserve the full base
letters rather than shrinking them to make room for accents.

An earlier revision aligned the Ä/Ö mark centers with the accepted Å ring
center at y=2560. The later accepted design uses filled diamond diaereses with
their bottom tips aligned to the unchanged Å ring bottom at y=2208. The full
A/O bodies and accepted ring design remain intact. That bottom-aligned diamond
design, recorded in [the v9 release notes](RELEASE-v9.md), is preserved in the
current v16 geometry; the earlier center-alignment description is historical.

The same text-size work centered the bullet on capitals and refined the i/j
dots and their Cyrillic references. Later revisions developed the accepted
diamond letter and punctuation dots. Earlier Miracode/Miranda wordmarks reused
the ordinary i; version 1.16 restores the original heart only for the complete
word Miracode, as described above. Miranda keeps its diamond dot. No automatic
hinting is added.

These are font-outline changes. Applications that draw their own list markers
control their positions separately. The [accent regressions](tests/check_accent_spacing.py)
check identical A/O bodies, preserved openings, ring separation and weight,
accepted diamond placement and bullet centering. The
[v16 release notes](RELEASE-v16.md) document the later punctuation work and
preservation of the accent outlines.

## Reproducible builds

Use Python with **FontForge 20230101** Python bindings and **fontTools 4.63.0**
in the same environment. HarfBuzz's system shared library is required for the
shaping checks. The build checks the pinned versions and uses a fixed timestamp.

For the four unpatched faces, run from the repository root:

```sh
python tools/build_contribution.py
```

For both complete release packages, provide the official Nerd Fonts 3.5.1
FontPatcher.zip (SHA256
`42bcb32145499a35732274c7fc48deb434ad0d2e0e118f98527c1479c6fa251a`):

```sh
python tools/build_release.py --patcher-archive /path/to/FontPatcher.zip
```

The build produces eight fonts, licenses, manifests, checksums, two ZIPs and
shaping results in `dist/diamond-release`. Repeat with `--output` pointing to
a second directory to check binary identity on the same pinned toolchain.
The release builder fixes its timestamp at 2024-02-10 UTC and normalizes generated
identifiers. Reproducibility has been verified on the recorded Linux toolchain
and compression runtime; identical bytes across different platforms or toolchain
builds are not assumed. The older Regular-only and experimental Bold commands
in historical release records are superseded by the four-face build above.
No font installation or application-setting change is part of the build.

Use `tools/prepare_contribution_catalog.py --catalog /path/to/nerd-fonts` to
prepare an isolated Nerd Fonts candidate. It copies only unpatched fonts,
license/config/README material, and updates the registry/root README. Patched
fonts must not be committed to the catalog. Publish exact source provenance
and complete integration review before submitting this local candidate.

## Attribution and licenses

Idrees Hassan's original font attribution and SIL OFL 1.1 are retained in
[LICENSE](LICENSE). Generator/build code is GPL-3.0-or-later;
see [COPYING-GENERATOR](COPYING-GENERATOR). Nerd Font packages include the
original icon-set license and attribution files. The metadata-only clipping
hook has its own GPL notice and does not alter font outlines or text spacing.

Original background is preserved in [docs/UPSTREAM-README.md](docs/UPSTREAM-README.md).
Versioned older release notes/tools are historical evidence. Start with the
build commands above for this derivative.

AI assistance: OpenAI Codex (GPT-6.1), running in T3 Code. The user confirmed
the design and maintenance plan; independent human source review is not claimed.
