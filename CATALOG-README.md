# Miracode Diamond

Version **1.16**. Maintained by **SimonRiemertzon**, based on
[Miracode by Idrees Hassan](https://github.com/IdreesInc/Miracode).
Original Miracode is the source of the angular design and programming ligatures.
This separately named derivative is not an official upstream release.

Four unpatched faces: Regular, Bold, Oblique and Bold Oblique. The obliques use
the accepted 12-degree transform; `--has-no-italic` keeps the four-face family
linked correctly. No separate true Italic design is supplied.

The approved v16 diamond letter/punctuation dots, accent/dash repairs, complete
cap-height !/? bodies, aligned dot/period bottoms and centered literal symbols
are preserved. All 18 original ligature sequences and 13 literal Unicode arrows
remain. Programming operators work through liga/calt; four special words use
liga. Only the complete word **Miracode** has the original heart-bearing i.
Miranda and ordinary i keep their diamond dots. Letters, numbers, combining
marks and underscore prevent a match inside a larger identifier. Context is
limited to one shaping run; application token/fallback splits can affect it.

All supported features are built into the font. Nerd Fonts adds icons and
preserves these rules; applications control feature activation. There is no
new autohinting. The optional Zen list cycle and 12% marker enlargement are
separate application configuration, not font features.

Font: SIL OFL 1.1, no Reserved Font Name declaration; original attribution is
retained in LICENSE.txt. The generator/build tools and this metadata hook are
separately GPL-3.0-or-later; see COPYING-postprocessor for the hook's license.

Exact local source commit: `SOURCE_COMMIT`. The baseline design was accepted
at `7152f7b2c3a84fdd22ce01bfde92dfec58567edf`; the new source adds the selected
name, restored Miracode heart and whole-word matching. Complete source archives,
reproducible builds and checksums accompany the local review package.
Intended fork location: SimonRiemertzon/Miracode-Diamond. Rename/publication has
not occurred. Replace this local provenance with the actual immutable reachable
source URL before public submission. No upstream endorsement or Nerd Fonts
catalog acceptance is claimed.

Build all four unpatched faces with `python tools/build_contribution.py`, using
FontForge 20230101 Python bindings and fontTools 4.63.0. A separate
`tools/build_release.py` creates base and complete Nerd Font packages; do not
commit its patched fonts here.

Configuration uses postscript naming for standard Nerd Fonts family names,
TYPO metrics for accepted text spacing, and a narrow Windows clipping hook.
The hook changes only OS/2 clipping bounds and SFNT checksums, retaining glyph,
layout and typographic spacing bytes. Intentional box/Powerline overlap stays.
Forced Mono is guarded because it collapses multi-cell ligature advances.
Stock Normal/Propo are supported; single-width icons without forced Mono are
used in the separate installable release. Stock catalog pitch metadata and
configuration/hook policy remain integration review points.

Keep focused original Miracode repair proposals separate from this maintained
derivative. Existing Nerd Fonts draft #2098 can be refreshed only after source
publication and explicit authorization. No public changes accompany this candidate.

AI assistance: OpenAI Codex (GPT-6.1), running in T3 Code. Visual decisions were
confirmed by the user; independent human source review is not claimed.
