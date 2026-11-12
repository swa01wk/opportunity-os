# ADR-002: Remotion is the only renderer
Status: Accepted (licence tier pending: see Q-07)    Date: 2026-11-12

## Context
The Signal Motion Engine (PRD §9) needs persistent objects, frame-accurate actions at 30 fps, equation typography, captions and 1080×1920 output (R-18–R-23, R-27, R-29, NFR-16). PRD §14.2 proposed Remotion + FFmpeg with Manim only where a brief needs it. Q-07 decided: Remotion only, no Manim. The compiler must never execute generated code (NFR-05).

## Decision
- All scenes are React components in `media/scenes/`, rendered by Remotion (`@remotion/renderer`, `renderMedia`) inside the `render` container. Remotion's bundled FFmpeg does encoding and concatenation; `ffprobe` runs the media checks (R-29).
- Equations are typeset with KaTeX from a TeX string held as data, with `trust: false` and a length limit. TeX is data, not code.
- The render service accepts only a validated VideoSpec (`docs/contracts/media/video-spec.schema.json`), compiles it to component props and renders. There is no path that evaluates model-written JavaScript.
- Pinned: Remotion version, Chrome Headless Shell version (`npx remotion browser ensure` at image build), fonts, codec settings. Base image `node:*-bookworm-slim` per Remotion's Docker guidance.
- Draft preview = half resolution, lower quality; master = 1080×1920, 30 fps, H.264.

## Alternatives
- **Remotion + Manim:** a second renderer, a second component library and a Python/Cairo stack; rejected by Q-07 until a brief proves the need.
- **Manim only:** strong maths typography, weak for captions, layout tokens and Studio previews in the browser.
- **Hand-rolled canvas + FFmpeg:** we would own a renderer, against PRD §9.1 ("reuse established renderers").

## Consequences
- Easier: one component library shared by the Studio preview (Remotion Player) and the renderer; React skills apply everywhere.
- Harder: Chrome in a container is memory-hungry; scene clips must be rendered with bounded concurrency.
- Licence: Remotion is free for individuals and companies of up to three people; otherwise a company licence is needed, and automated server-side rendering most closely matches the "Automators" tier (per-render with a monthly minimum) [Remotion pricing](https://www.remotion.dev/docs/license/pricing). Which tier applies depends on who the licensee is. **Open: you confirm the licensee entity (Q-07 follow-up).** Recorded as a dependency licence in TECH_STACK.md (Stage 2b).
- Must do: an M0 render spike measures preview and master time on the odd-squares fixture (NFR-02).
