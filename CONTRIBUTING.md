# Contributing to Miracode Diamond

Miracode Diamond is maintained by SimonRiemertzon as a separate derivative of
Idrees Hassan's Miracode. Keep original attribution and license notices intact.
The [original guidance](docs/UPSTREAM-CONTRIBUTING.md) is retained for context;
changes to this derivative do not imply approval by the original author.

Preserve source coverage, fixed text advances, full multi-cell ligature widths,
approved letter/punctuation geometry and four-face style linking. Add focused
regression checks for changed behavior, including positive and negative word
contexts. Keep application layout/settings and broad patcher changes separate.

Use the pinned build environment documented in README.md. The build runs source
geometry/style tests and actual HarfBuzz checks. For release work, compare the
four base and patched fonts against the accepted v16 baseline, regenerate the
official Nerd Fonts preview and document actual application test limits.

Do not commit generated patched font binaries to the Nerd Fonts catalog.
Disclose AI assistance accurately in relevant commits and pull request text.
Keep focused proposals to original Miracode separate from derivative releases.
