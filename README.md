# Miracode Diamond

**Version 1.16 · maintained by SimonRiemertzon.**

A derivative of [Miracode](https://github.com/IdreesInc/Miracode), the angular
programming font by **Idrees Hassan**, based on Monocraft. Miracode Diamond keeps
the original character and ligature coverage and adds the approved diamond-dot
design, source Bold and linked 12-degree obliques.

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
