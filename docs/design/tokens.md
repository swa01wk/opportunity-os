# Design tokens

Status: **Client review** (Stage 2c, step 1). Baselined at G2; after that it changes only through change control ([PROCESS.md](../PROCESS.md#tracking-and-change-control)).

This file owns two token sets:

1. **Studio UI tokens** (`ui.*`): the operator app. Used by every screen prototype in [screens/](screens/) and, per [ADR-018](../adr/ADR-018-studio-ui-kit.md), by Tailwind as CSS variables.
2. **Video house style, brand kit v1** (no prefix): what viewers see in the 1080×1920 video. Per A-31 ([QUESTIONS.md](../product/QUESTIONS.md), Q-31) this is R-23's palette, type scale, equation typography, caption placement, safe zones, transitions, narration voice, pacing and brand cue. These are the names a VideoSpec may use (`colorToken`, `styleToken`, `sizeToken`, `easing`; `common.schema.json#/$defs/Token`). A VideoSpec never holds a raw value.

Source rule: derived only from PRD §5.2 and the §10 storyboard. No reference screenshots were used. Everything here is original.

Owners of related facts: requirements [REQUIREMENTS.md](../product/REQUIREMENTS.md) (R-20, R-23, R-27) · screens and accessibility rules [UI_DESIGN.md](../product/UI_DESIGN.md) · capability catalogue and easing token list [capabilities.json](../contracts/media/capabilities.json) · flash limit NFR-08.

Reference prototype: [S-07 Storyboard and preview](screens/S-07-storyboard.html) uses both sets and renders the odd-squares fixture with the house style.

---

## Design intent

- **The video is the only bright thing.** The Studio is a quiet, cool-grey workspace. Saturated colour belongs to the video canvas, where each colour means one odd-number layer. Studio status colours are muted and always come with an icon and words, so they never compete with or get confused for layer meaning.
- **Layer colours only appear on the video canvas.** When the Studio shows a layer colour (inspector swatch, timeline lane), it sits on a small `color.canvas` chip, the same background the viewer sees it on.
- **One typeface family for legibility.** Atkinson Hyperlegible Next (Studio and video) was designed so that similar characters (1, l, I; 0, O; 3, 8) cannot be confused. That is the job of both a review tool full of hashes and a phone-size maths video.
- **Primary actions use the video canvas colour.** Solid "night" buttons tie the Studio to the canvas it controls.

---

## 1 Studio UI tokens

CSS variable = token name with dots replaced by hyphens, prefixed `--`: `ui.color.ink` → `--ui-color-ink`. Light is the default theme; dark is applied with `[data-theme="dark"]` on `<html>`, and follows `prefers-color-scheme` until the member picks one.

### 1.1 Colour

| Token | Light | Dark | Use |
|---|---|---|---|
| `ui.color.bg` | `#EEF1F4` | `#0D1526` | App background behind panels |
| `ui.color.panel` | `#FFFFFF` | `#141E33` | Panels, cards, dialogs |
| `ui.color.sunken` | `#F6F8FA` | `#0F182B` | Inset areas, table stripes, inputs |
| `ui.color.stage` | `#070D1A` | `#070D1A` | The preview stage around the video frame (both themes) |
| `ui.color.line` | `#D5DBE3` | `#26334D` | Dividers, panel edges (decorative, no contrast duty) |
| `ui.color.line.strong` | `#7D8AA0` | `#62728F` | Input and control borders (3:1) |
| `ui.color.ink` | `#172033` | `#E8EDF5` | Body text |
| `ui.color.ink.muted` | `#4B5770` | `#AAB5C8` | Secondary text |
| `ui.color.ink.subtle` | `#5F6B82` | `#8E9AB0` | Hints, timestamps (still 4.5:1) |
| `ui.color.primary` | `#101C33` | `#E8EDF5` | Primary button fill (= `color.canvas` in light) |
| `ui.color.on.primary` | `#F2F5FA` | `#101C33` | Primary button text |
| `ui.color.focus` | `#1F5FD6` | `#7FB2FF` | Focus ring, links, selected row edge |
| `ui.color.ok` / `.bg` | `#17663F` / `#E3F3EA` | `#5DD39E` / `#12301F` | Approved, passed |
| `ui.color.warn` / `.bg` | `#8A5300` / `#FFF2D9` | `#F2B84B` / `#33260A` | Awaiting review, paused, provisional |
| `ui.color.danger` / `.bg` | `#B3261E` / `#FCE8E6` | `#FF8A80` / `#3A1614` | Blocked, failed, reopened, destructive |
| `ui.color.info` / `.bg` | `#1F5FD6` / `#E6EEFC` | `#7FB2FF` / `#132647` | Running, informational |

**Status is never colour alone** (UI_DESIGN.md accessibility). Each status has a fixed icon shape and word:

| Status | Icon | Colour | Words |
|---|---|---|---|
| Not started | hollow circle | ink.subtle | "Not started" |
| Awaiting review | half-filled circle | warn | "Awaiting review" |
| Approved | check in filled circle | ok | "Approved v3 · a1b2c3d" |
| Reopened | counter-clockwise arrow | danger | "Reopened: <reason>" |
| Blocked | bar in octagon | danger | "Blocked (2)" |
| Running | three-segment ring (static when reduced motion) | info | "<step> · 3 of 6" |
| Unavailable | dashed circle | ink.subtle | "Unavailable: <reason>" (never blank, dash or zero) |

### 1.2 Typography

| Token | Value |
|---|---|
| `ui.font.sans` | `"Atkinson Hyperlegible Next", system-ui, -apple-system, "Segoe UI", sans-serif` |
| `ui.font.mono` | `"Atkinson Hyperlegible Mono", ui-monospace, "SF Mono", Menlo, monospace`. Only for machine identifiers: object and action IDs (`cell.c4r4`), hashes, request IDs. Not for labels or numbers. |
| `ui.font.numeric` | `font-variant-numeric: tabular-nums` on times, frames, money and counts |

Scale (ratio ≈ 1.2, base 14 px for a dense review tool at 1280 px+):

| Token | Size / line height | Weight | Use |
|---|---|---|---|
| `ui.text.xs` | 12 / 16 | 400 | Timeline ruler, frame ticks, captions on swatches |
| `ui.text.sm` | 13 / 18 | 400 | Table cells, metadata, chips |
| `ui.text.base` | 14 / 20 | 400 | Body, inputs, buttons (500) |
| `ui.text.md` | 16 / 24 | 500 | Panel titles, dialog body lead |
| `ui.text.lg` | 20 / 28 | 600 | Screen title, dialog title |
| `ui.text.xl` | 24 / 32 | 600 | Project title in header |
| `ui.text.2xl` | 30 / 36 | 600 | Empty-state headline only |

Sentence case everywhere; no all-caps labels. Line length ≤ 72 characters in prose panels.

### 1.3 Spacing, layout, radius, elevation

Spacing on a 4 px grid: `ui.space.1`=4, `.2`=8, `.3`=12, `.4`=16, `.5`=20, `.6`=24, `.8`=32, `.10`=40, `.12`=48.

| Token | Value | Use |
|---|---|---|
| `ui.layout.min` | 1280 px | Designed width (A-26); below it a notice and a single column |
| `ui.layout.nav` | 76 px | Left rail: icon above label |
| `ui.layout.header` | 64 px project header + 44 px gate strip | |
| `ui.target.min` | 24 × 24 px (32 px for primary controls) | WCAG 2.5.8 |
| `ui.radius.sm` | 4 px | Chips, swatches, inputs |
| `ui.radius.md` | 8 px | Buttons, scene cards |
| `ui.radius.lg` | 12 px | Panels, dialogs |
| `ui.radius.device` | 28 px | Phone-size preview frame only |
| `ui.shadow.panel` | none; panels are separated by `ui.color.line` | |
| `ui.shadow.overlay` | `0 12px 32px rgb(7 13 26 / 0.28)` | Dialogs, popovers only |

Radius follows hierarchy (chip < card < panel < device), not one value for everything.

### 1.4 Motion and focus

| Token | Value |
|---|---|
| `ui.motion.fast` | 120 ms, `cubic-bezier(0.2, 0, 0, 1)`: hover, toggles |
| `ui.motion.base` | 200 ms, same curve: dialog open, panel expand |
| `ui.motion.reduced` | With `prefers-reduced-motion: reduce`, all Studio transitions are 0 ms and the running icon is static. The video preview still plays (it is content), but autoplay is off. |
| `ui.focus.ring` | 2 px solid `ui.color.focus`, 2 px offset; never removed; not covered by sticky headers (WCAG 2.4.11) |

Studio motion only answers an action. Nothing animates on load; nothing flashes.

### 1.5 Checked contrast (WCAG 2.2 AA)

Every text pair above is ≥ 4.5:1 and every control/focus pair ≥ 3:1, in both themes. Lowest values: light `ui.color.info` on `info.bg` 4.91:1, `line.strong` on panel 3.49:1, focus ring on stage 3.39:1; dark `line.strong` on panel 3.42:1. Checked with the WCAG relative-luminance formula on 2026-11-13 (48 pairs, 0 failures). Re-check any change before merge.

---

## 2 Video house style: brand kit v1

Format pinned by the contracts: 1080 × 1920 px, 30 fps. All sizes below are in video pixels; the Studio phone-size preview is 360 × 640 (÷3).

### 2.1 Palette

| Token | Value | Meaning |
|---|---|---|
| `color.canvas` | `#101C33` | "Night": the dark canvas (§5.2). Deep blue, not black, so bright layers read as light on ink. |
| `color.canvas.raised` | `#1B2A47` | Empty grid slots, caption plate base |
| `color.chalk` | `#F2F5FA` | Question, operators, totals, captions, takeaway |
| `color.chalk.muted` | `#A7B3C9` | Brand cue, secondary labels |
| `color.outline` | `#5C6E92` | Faint outlines (hook's empty square), unit guides |
| `color.layer.1` | `#FFE04A` sun | First odd-number layer (1 cell) |
| `color.layer.2` | `#94C8F5` sky | Second layer (3 cells) |
| `color.layer.3` | `#FF6A45` ember | Third layer (5 cells) |
| `color.layer.4` | `#3EF0B4` mint | Fourth layer (7 cells) |
| `color.layer.5` | `#B477FF` violet | Fifth layer (9 cells) |
| `color.layer.6`–`.8` | reserved | Added only by a brand-kit version when a brief needs more than five; must pass the same checks |

**Rules (R-20).**
- A colour token means one thing for the whole video. Once `sum.t3` and `layer.3` are ember, nothing else is ember (the compiler's `COLOR_MEANING_CHANGED`).
- Colour is never the only cue: every coloured group also has a label (the layer's odd number in its corner cell) and a stable position, and the matching equation term is highlighted at the same moment.
- Numerals and labels on a layer fill use `color.canvas` text.

**Checks.** Every layer colour and `color.chalk.muted` is ≥ 4.5:1 on `color.canvas` (lowest: violet 5.68:1, ember 5.99:1), so they work as text as well as fills; `color.outline` is 3.32:1 (graphic). Minimum CIE76 ΔE between any two layer colours: 66 normal vision, 29 deuteranopia, 36 protanopia, 25 tritanopia (Machado 2009 simulation). The five were chosen jointly for that separation; adjacent layers (which touch on screen) are the most distinct.

### 2.2 Typography

| Token | Family | Size / line height | Weight | Use |
|---|---|---|---|---|
| `type.question` | Atkinson Hyperlegible Next | 64 / 76 | 700 | Opening question |
| `type.term` | Atkinson Hyperlegible Next, tabular | 96 / 104 | 800 | Sequence terms (`sum.t1`…) and operators (operators 600, `color.chalk`) |
| `type.total` | Atkinson Hyperlegible Next, tabular | 104 / 112 | 800 | Running total (its label in `type.label`, `color.chalk.muted`) |
| `type.equation` | KaTeX Main and Math | 72 / 88 | 400 (variables italic) | MathExpression |
| `type.label` | Atkinson Hyperlegible Next, tabular | 44 / 48 | 700 | Cell and dimension labels |
| `type.caption` | Atkinson Hyperlegible Next | 54 / 64 | 600 | Narration captions |
| `type.takeaway` | Atkinson Hyperlegible Next | 56 / 64 | 700 | Closing insight, at most 2 lines |
| `type.brandcue` | Atkinson Hyperlegible Next | 30 / 36, tracking +0.04 em | 600 | Brand cue wordmark |

Minimum video text size is 40 px (≈ 13 px at phone size). Sentence case. Numbers are lining and tabular so a changing total does not shift sideways.

**Equation typography.** TeX terms render with KaTeX fonts: variables italic (*n*, *k*), numerals and operators upright, `−` (U+2212) not hyphen, thin space around binary operators, superscripts at 60 % size. A term linked to an object (`linkedObjectIds`) takes that object's colour token; unlinked terms are `color.chalk`. Equations sit on one line at phone size. The reference formula `1+3+5+⋯+(2n−1) = n²` is about 850 px wide at 72 px, inside the 936 px content width above y = 760. If an equation would not fit, the compiler reports `LABEL_OVERFLOW`; it never shrinks below 64 px.

**Fonts and rights.** Atkinson Hyperlegible Next and Mono: SIL OFL 1.1 (Braille Institute; reserved names "Atkinson", "Hyperlegible", so no modified copies under that name). KaTeX fonts: SIL OFL 1.1. Each font file is registered in the rights ledger with its hash and licence before first use (R-55, PRD §5.2), and pinned by version so renders reproduce (PRD §9.3). Prototypes fall back to system fonts.

### 2.3 Layout and safe zones

Union of the YouTube Shorts and Instagram Reels overlays, kept conservative. Provisional: `media.qa` checks against these numbers, and they are re-measured when platform overlays change.

| Token | Rectangle (x, y, w, h) | Rule |
|---|---|---|
| `zone.content` | 72, 140, 936, 1460, minus `zone.obstructed.right` | All question, equation, object and caption content stays inside: 936 px wide above y = 760, x ≤ 948 below it |
| `zone.obstructed.top` | 0, 0, 1080, 96 | Nothing |
| `zone.brand` | 72, 96, 936, 44 | Brand cue only (centred) |
| `zone.obstructed.right` | 948, 760, 132, 840 | Nothing (platform action buttons) |
| `zone.obstructed.bottom` | 0, 1600, 1080, 320 | Nothing (title, channel, progress bar) |
| `zone.caption.bottom` | 132, 1440, 816, 160 | Default caption band (centred on x = 540) |
| `zone.caption.top` | 132, 160, 816, 160 | Alternate band when the bottom band would cover an active object |

Vertical bands for single-subject explainers (the odd-squares fixture anchors follow them): question 130–290 · sequence and equation 300–530 · main stage 540–1170 · total 1175–1290 · takeaway 1295–1430 · caption 1440–1600. Content is centred on x = 540, so centred text below y = 760 is at most 816 px wide. Grid unit for GeometricArrangement: 120 px cells drawn 108 × 108 px with 12 px gutters and 14 px corner radius.

### 2.4 Captions

- Phrase-segmented from measured alignment (R-26, R-27), never from estimates.
- At most 2 lines, at most 28 characters per line, at most 17 characters per second, at least 30 frames on screen.
- `color.chalk` on a plate of `color.canvas` at 88 % opacity, 16 px radius, 16 px × 28 px padding, at most 816 px wide, bottom edge on y = 1600 (or top edge on y = 160 in the top band).
- Never overlaps an object, label or equation that is active (revealed or highlighted) during the caption's frames. If both bands would, the compiler reports `CAPTION_OVERLAP` naming the scene and object; it never shrinks or moves content silently.

### 2.5 Motion and transitions

Easing tokens (the list in capabilities.json):

| Token | Curve |
|---|---|
| `ease.standard` | `cubic-bezier(0.2, 0, 0, 1)` |
| `ease.enter` | `cubic-bezier(0, 0, 0.2, 1)` |
| `ease.exit` | `cubic-bezier(0.4, 0, 1, 1)` |
| `ease.linear` | linear (progress bars and counters only) |

Durations in frames at 30 fps: `dur.quick` 10 (hide, dim, undim) · `dur.reveal` 15–20 · `dur.map` 20 (mapTerms) · `dur.stagger` 4–6 per cell · `dur.hold` ≥ 30 after the last reveal of an idea before the next idea starts.

How each catalogue op looks (one meaning per treatment, distinguishable without colour):

| Op | Treatment |
|---|---|
| `reveal` | Opacity 0 → 1 and scale 0.9 → 1 from the cell centre; text also rises 12 px. Staggered cells reveal in reading order (row, then column). |
| `hide` | Opacity → 0, no movement |
| `highlight` | Solid 6 px `color.chalk` ring, 6 px outside the target's bounds |
| `outline` | Dashed 6 px ring (18 on, 12 off). `color.chalk` on cells; `color.outline` for the hook's faint empty square |
| `emphasize` | Scale to 108 % and a solid ring, once; no repeat pulse |
| `dim` / `undim` | Opacity 0.3 / 1. Dimmed items keep their label. |
| `mapTerms` | Old value moves up 16 px and fades; new value enters from 16 px below; 20 frames. The change is explicit, never a jump cut. |
| `showText` / `hideText` | As reveal / hide for text |
| `move`, `rotate`, `scale`, `regroup` | Straight paths with `ease.standard`; regrouped items keep colour until the regroup completes, then take the new group's token |

Transitions between scenes: a **continuity cut**. Scenes share one stage, the next scene's entry state equals the previous exit state (R-22), so the cut is invisible. No wipes, zooms, camera moves or decorative motion. `transition.fade` (10 frames to `color.canvas`) is reserved for a scene that starts a new stage. No luminance change repeats more than 3 times a second (NFR-08); there is no flashing op.

### 2.6 Pacing

Provisional, calibrated against the R0 baseline:
- One idea per beat; a beat is never shorter than 60 frames (2 s).
- Hook states the question within the first 30 frames and shows the full sum within 4 s (PRD §10.2).
- Narration about 150–165 words per minute; the measured take sets the timing (R-26). A take that no longer fits is shown as a pacing change, never sped up.
- Closure holds the completed picture at least 45 frames after the takeaway appears.
- Target 45 s (1,350 frames) for the reference story; catalogue bounds 900–2,700 frames.

### 2.7 Narration voice

One licensed narrator for the house brand (ADR-013, R-03). Character: calm, curious and plain-spoken; explains rather than performs; no hype, no fake surprise; a short pause before the answer to the opening question. Notation is read the same way every time and kept in the pronunciation list (R-25): "n squared", "two k minus one", "one plus three plus five". The voice and motion reference clips follow in M0 (A-31, PRD OOS-003).

### 2.8 Brand cue

- Wordmark "Signal Motion" in `type.brandcue`, `color.chalk.muted`, in `zone.brand`, preceded by the mark.
- The mark is a 2 × 2 square of cells: one `color.layer.1` cell and an L of three `color.chalk.muted` cells. It is the first step of the house idea (small things adding up to a whole), drawn 30 × 30 px.
- Shown only in the closure beat, after the takeaway (fixture action `a.close.brand`), at most 4 s. Never in the hook or during an explanation (R-23 AC2), never animated beyond a fade.
- A voluntary AI-production identity, not a fact-check claim (PRD §5.2). Platform disclosure is assessed separately on S-11.

### 2.9 Token index for VideoSpecs

`color.canvas`, `color.canvas.raised`, `color.chalk`, `color.chalk.muted`, `color.outline`, `color.layer.1`–`color.layer.5` · `type.question`, `type.term`, `type.total`, `type.equation`, `type.label`, `type.caption`, `type.takeaway`, `type.brandcue` · `ease.standard`, `ease.enter`, `ease.exit`, `ease.linear` · `zone.*` above (used by the compiler and `media.qa`, not by specs). A token not in this list fails validation. Adding one is a new brand-kit version (R-02), which marks affected draft scenes invalid; approved and published versions are unchanged.

## Change log

| Date | Change |
|---|---|
| 2026-11-13 | First version: Studio UI tokens (light and dark) and video house style brand kit v1 (A-31). In client review with S-07. |
