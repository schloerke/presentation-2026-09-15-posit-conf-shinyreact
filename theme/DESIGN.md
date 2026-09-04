# shinyreact Keynote theme — design spec

**Date:** 2026-08-18
**Status:** Implemented — this directory
**Direction:** A — "Hex & Orbit", with the bullet motif toned down and the text
palette re-stepped to AAA
**Scope change (2026-08-18):** dark mode only. The light variant is dropped; §4.2
is retained as measured reference in case it is ever revived.

## 1. Purpose and scope

A reusable, shinyreact-branded Keynote theme for posit::conf(2026) talks. **Dark
mode only.** 16:9, 1920×1080 design canvas.

The theme must stay legible from the back row of a conference ballroom. That
constraint outranks density: a master that cannot hold its content at the
minimum type sizes in §5 is the wrong master, not a reason to shrink the type.

**In scope:** color tokens, type scale, five masters (plus light variants), chart
and stat specs, motif rules, font-substitution strategy.

**Out of scope:** the `.kth` production mechanics (tracked separately — see §10),
talk content, and any Posit-wide template obligations, which as of this writing
the conference has not published.

## 2. Source material

| Source | What it contributes |
|---|---|
| `logo/shiny-react.svg` | Ground `#1C1D22`, accent `#00D8FF`, hexagon silhouette, React orbit, the swoosh under the "Shiny" wordmark |
| react.dev | Type discipline: large sizes, generous whitespace, elevated rounded code surfaces. Source Code Pro for code |
| posit::conf(2026) site | Confirms the conference reads "digital": navy `#030A5F`, acid lime `#BBF81B`, pixel display face, dot-grid textures |
| 2025 OTel deck | Footer conventions retained: conf logo + QR bottom-left, speaker lockup bottom-right |
| Posit brand.yml | Source Code Pro as the sanctioned mono; Arial as the sanctioned web-safe fallback |

Two deliberate departures from source. Posit's brand blue `#447099` is not used —
it is a mid-value blue that turns to mud at projection distance. The conf(2026)
lime and pixel face are not used either; they were explored in a rejected
direction and read as conference furniture rather than talk identity. The
conference connection is carried by the footer lockup instead.

## 3. Design principles

1. **One motif per slide.** The hexagon, the orbit, and the swoosh are all
   logo-derived and all cyan. Two of them on one slide reads as decoration.
2. **The hexagon is the logo's, not the theme's.** It appears in the title
   lockup and nowhere else. Repeating it as list furniture was tried and cut —
   it read as clip art.
3. **Color carries one meaning at a time.** Cyan means "this is the accent."
   Chart series colors mean "this is a different entity." They never mix on one
   slide.
4. **Text tokens are never series colors,** and series colors are never used for
   body text.
5. **Scale each master to its floor.** See §5.

## 4. Color tokens

All ratios below are measured WCAG 2.1 contrast, not estimated. Every **text**
pair clears AAA (7:1) — beyond the 3:1 that slide-sized type technically needs,
because projector gamma and ambient light erode measured contrast in the room.

### 4.1 Dark mode (primary)

| Token | Hex | On | Ratio | |
|---|---|---|---|---|
| `--ink` (ground) | `#1C1D22` | — | — | slide background |
| `--ink-deep` (panel/divider) | `#141519` | — | — | code panels, divider slides |
| `--text` | `#F2F4F8` | `--ink` | **15.28:1** | AAA |
| `--text` on panel | `#F2F4F8` | `--ink-deep` | **16.57:1** | AAA |
| `--muted` | `#A3ACBB` | `--ink` | **7.35:1** | AAA |
| `--muted` on panel | `#A3ACBB` | `--ink-deep` | **7.97:1** | AAA |
| `--cyan` (graphic only) | `#00D8FF` | `--ink` | 9.83:1 | swoosh, orbit, bullet rules, logo |
| `--cyan-text` | `#6FD4E8` | `--ink` | **9.82:1** | AAA |
| `--cyan-text` on panel | `#6FD4E8` | `--ink-deep` | **10.65:1** | AAA |

**Why cyan is split into two tokens.** Contrast is not the reason — the two are
within 0.01 of each other. Fully saturated `#00D8FF` at 52px bold on a near-black
ground produces visible chromatic fringing on high-brightness LED walls and for
astigmatic viewers, which WCAG does not measure. `--cyan-text` is the same hue at
roughly 20% less saturation, so the fix is free. Graphic elements keep the pure
cyan: a swoosh has no letterforms to fringe.

Code tokens, all on `--ink-deep`:

| Token | Hex | Ratio | |
|---|---|---|---|
| default | `#F2F4F8` | 16.57:1 | AAA |
| keyword | `#C7A0FF` | 8.60:1 | AAA |
| function / filename | `#6FD4E8` | 10.65:1 | AAA |
| string | `#9FE88D` | 12.51:1 | AAA |
| number | `#FFB86C` | 10.71:1 | AAA |
| comment | `#9AA3B2` | **7.17:1** | AAA |
| JSX prop | `#F0A6C8` | 9.55:1 | AAA |

The comment color is the one value that had to change from a conventional
syntax theme. The inherited `#6B7280` measured **3.77:1** — legal for large text,
invisible from row 30. Editor themes assume 14px on a monitor at arm's length.
Worst pair in the dark deck is now 7.17:1.

### 4.2 Light mode — DROPPED, retained for reference

Not implemented. Kept because the values are measured and re-deriving them is the
expensive part; if a light variant is ever wanted, start here rather than from
scratch.

Light mode is **selected, not flipped.** Inverting the dark values produces
either invisible cyan or muddy grays; each token was re-stepped against the light
ground and re-measured.

| Token | Hex | On | Ratio | |
|---|---|---|---|---|
| ground | `#F4F6FA` | — | — | |
| panel | `#E9EDF4` | — | — | |
| `--text` | `#12131A` | ground | **17.12:1** | AAA |
| headline (alt) | `#030A5F` | ground | **16.01:1** | AAA — conf navy, optional |
| `--muted` | `#4C5462` | ground | **7.05:1** | AAA |
| `--cyan-text` | `#045067` | ground | **8.26:1** | AAA |
| `--cyan` (graphic) | `#0B8CA8` | ground | 3.64:1 | passes the 3:1 non-text floor |

Code tokens on the light panel `#E9EDF4`:

| Token | Hex | Ratio | |
|---|---|---|---|
| default | `#12131A` | 15.77:1 | AAA |
| keyword | `#523086` | 8.41:1 | AAA |
| function | `#045067` | 7.62:1 | AAA |
| string | `#17532C` | 7.74:1 | AAA |
| number | `#6E3B00` | 7.81:1 | AAA |
| comment | `#464D5A` | 7.24:1 | AAA |

Note that `#00D8FF` cannot be used for anything in light mode, including graphics
— it measures under 1.5:1 on a light ground. Light mode's graphic cyan is
`#0B8CA8`.

### 4.3 Chart series palette

Validated with `scripts/validate_palette.js` from the dataviz skill — all six
checks (lightness band, chroma floor, CVD separation, normal-vision floor,
contrast vs surface), not eyeballed.

| Slot | Hue | Dark (in use) | Light (dropped) |
|---|---|---|---|
| 1 | cyan | `#0E9DBA` | `#0C8CA6` |
| 2 | orange | `#E2622B` | `#D2551F` |
| 3 | blue | `#3D8AE0` | `#2A78D6` |
| 4 | green | `#74A012` | `#5F8A0C` |
| 5 | magenta | `#C74BD1` | `#B23BBC` |

Assign in this fixed order, never cycled. A sixth series folds into "Other" or
becomes small multiples.

These are stepped down from the brand colors and are deliberately *not*
`#00D8FF`/`#BBF81B`. At full strength those fail the lightness band, and more
practically, conf blue against conf magenta collided at ΔE 4.2 under
deuteranopia — indistinguishable for roughly 1 in 12 men in the audience.

One caveat: series colors sit at 4.3–5.4:1 on the dark ground. That clears the
3:1 non-text floor but not AAA — which is correct, as they are marks, not text.
Their labels wear text tokens.

(The dropped light set's worst adjacent pair sat at tritan ΔE 7.5, inside the 6–8
warn band, which would have made direct labels mandatory rather than merely
preferred. Dark has no such constraint — a small bonus of going dark-only.)

## 5. Typography

### 5.1 Faces and the substitution problem

**Keynote does not embed fonts.** A theme opened on a Mac without the intended
face silently substitutes and reflows. For a theme meant to be handed to other
people this is the primary technical risk, so the stack is specified in tiers:

| Role | Preferred | Fallback 1 | Fallback 2 |
|---|---|---|---|
| Display / body | Inter | Helvetica Neue | Arial |
| Code | Source Code Pro | Menlo | Courier New |

Fallback 1 in both rows ships with every Mac, so the worst realistic case is
still a designed outcome rather than a random one. Source Code Pro is the
sanctioned mono in both Posit's brand.yml and react.dev, which is a rare and
convenient agreement.

Inter is preferred over Posit's Open Sans for its larger x-height and more open
apertures, both of which survive distance better. Open Sans remains acceptable if
brand consistency is judged to outrank legibility for a given deck.

**Masters must be built with ~8% horizontal slack** on every text box. Helvetica
Neue sets narrower than Inter; without slack, substitution reflows headlines onto
an extra line.

### 5.2 Type scale and legibility floors

Sizes are on the 1920×1080 canvas. The percentage is of slide height, which is
the projection-invariant figure.

| Role | Size | % of height | Weight |
|---|---|---|---|
| Title (H1) | 128px | 11.9% | 800 |
| Section / slide head (H2) | 96px | 8.9% | 800 |
| Content head | 84px | 7.8% | 800 |
| Bullet / body | 52px | 4.8% | 500 |
| Lede | 46px | 4.3% | 400 |
| Code | 34px | 3.1% | 400 |
| Stat number | 132px | 12.2% | 800 |
| Kicker / label | 30–34px | 2.8–3.1% | 600–700 |
| Footer | 30px | 2.8% | 400 |

**Hard floors: body ≥ 36px, code ≥ 32px, nothing below 28px ever.** A slide that
needs smaller type needs less content or two slides.

Practical check before shipping a deck: view the slide at 12.5% scale from about
two feet. Anything you cannot read is what the back row cannot read.

## 6. Layout

- **Margins:** 96px left/right, 60px bottom to the footer baseline. Nothing
  bleeds except background motifs.
- **Footer** (all masters except the section divider): conf logo + QR
  bottom-left, speaker lockup bottom-right, both in `--muted`. Carried over from
  the 2025 deck, where it worked.
- **Social marks:** the speaker lockup's handle line is preceded by the octocat
  and the bluesky butterfly, 38px tall, in `--muted` at 85% fill opacity, one
  mark-width gap apart (they were overlapped first, which read as one blob) and
  6px from the handle. The handle is the same on both services, so one mark
  pair stands for both — the marks have to sit closer to the handle than to
  each other, or they read as a separate thought. The closing divider
  carries the handle line (and these marks) on its own, since master 2 has no
  footer. Ported to the SCSS only — the Keynote theme does not carry them.
- **Title underline:** the logo's swoosh, 8px stroke, round caps, as a static
  block below the headline — never absolutely positioned. Absolute positioning is
  what collided it with the lede during mockup.

### The five masters

1. **Title** — headline left over ~1100px, swoosh, lede. Logo right on a
   `--cyan` hex ring sized 40px larger than the logo's own hex and concentric
   with it. The ring was `#23252C` at first, which read as a grey smudge the
   logo's atom happened to cross; in the logo's own cyan the atom overlapping it
   reads as intentional. Orbit watermark bleeding off the top-right at
   7% opacity. Full footer.
2. **Section divider** — ground drops to `--ink-deep`. Ghost section number at
   240px/900 in `rgba(0,216,255,.22)` (decorative; the section name carries the
   meaning, so this is exempt from the text contrast floor). Centered orbit
   watermark at 10%. No footer.
3. **Content** — kicker, head, swoosh, then bullets. **Bullets are a 5px cyan
   rule with 42px of padding**, running the height of the item. Not hexagons —
   those were tried and cut per §3.2. Emphasis inside a bullet uses
   `--cyan-text` at weight 700.
4. **Code, two-up** — two panels, `--ink-deep` on a 2px `rgba(0,216,255,.18)`
   hairline, 20px radius, 40/44px padding. Filename as a letter-spaced
   `--cyan-text` label above the block, in whatever casing the slide wrote —
   `app.R` is a filename, not a heading, so nothing upper-cases it. Panels are equal-width;
   pad the shorter listing with blank lines rather than letting the panels differ
   in height.
5. **Data** — optional stat row (number in `--cyan-text`, label in `--muted`
   beneath), then one chart. One chart per slide.

Dark only — no light counterparts.

## 7. Charts and stat tiles

- Horizontal bars for magnitude comparison across named entities; 4px rounded
  ends anchored to the baseline; 2px surface gap between adjacent fills.
- Recessive grid: 1px at 16% opacity. Baseline axis 2px at 45–50% opacity.
- **Direct-label every bar.**
- No legend for a single series; the slide head names it. Two or more series
  always get a legend *and* direct labels on up to four.
- Never two y-scales. Two measures of different scale become two charts.
- Series color follows the entity, never its rank — filtering must not repaint
  the survivors.
- Axis labels and values wear `--muted` and `--text`, never a series color.

## 8. Motif rules

| Motif | Where | Never |
|---|---|---|
| Hexagon | Title lockup only | As bullets, image frames, or repeated shapes |
| Orbit | Title (7%), divider (10%) | On content, code, or data slides |
| Swoosh | Under a headline, once | As a divider between body elements, or twice on a slide |
| Cyan rule | Bullet items | As a decorative line elsewhere |

## 9. Acceptance criteria

1. ✅ Every text pair measures ≥ 7:1. Verified by script, not by eye. Worst pair
   is the code comment at 7.17:1.
2. ✅ Every chart mark measures ≥ 3:1 against the ground (4.3–5.4:1), and the
   categorical palette passes all six dataviz checks in dark mode.
3. ✅ No text below 28px on the 1920×1080 canvas; body ≥ 36px; code ≥ 32px
   (smallest in use: code at 34px, footer/labels at 30px).
4. ⚠️ **Not verified.** Substitution behaviour with Inter uninstalled has not
   been tested. Partial mitigation: Helvetica Neue sets *narrower* than Inter, so
   substitution shrinks rather than overflows lines — the failure mode is ugly,
   not broken. A real test needs a second Mac or a font-cache flush.
5. ✅ Dark only, per the scope change. Not applicable.
6. ✅ No slide carries more than one motif from §8.

## 10. Deferred / open

- **`.kth` production — resolved.** The `.pptx` route won: PowerPoint slide
  layouts import as Keynote master slides, and `<p:ph>` placeholders import as
  editable Keynote placeholders. `build_theme.py` generates the deck; the final
  step is Save Theme in Keynote (see the README).
- **Masters are the product, not slides.** Save Theme captures master slides and
  discards content slides. The first build drew the design on slides, so the
  resulting theme carried only the background colour. Every design element must
  live on a layout, and every editable region must be a real placeholder whose
  **list style** (`a:lvl1pPr`) carries the styling — run-level styling alone is
  lost as soon as the user retypes the text.
- **Light variant.** Dropped 2026-08-18. §4.2 holds the measured values if revived.
- **Licensed faces.** If the conf(2026) pixel display face is ever wanted, CoFo
  Sans Pixel is commercial and would need a license. Currently unused.
- **Conference template obligations.** None published as of 2026-08-18. If the
  conference issues a mandated title slide or sponsor lockup, §6 master 1 is the
  only thing that should need to change.
- **R/Python parity is not a concern here** — this is a presentation artifact,
  not package surface.

## Appendix: reference mockups

Three HTML mockups were built to choose the direction: "Hex & Orbit" (this spec),
"Docs Projected" (react.dev discipline, no ornament), and a hybrid that leaned on
conf(2026)'s lime/pixel motifs. They live in the shinyreact repo working tree and
were not carried over — `preview/` holds Keynote's render of the built result,
which supersedes them.
