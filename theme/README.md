# shinyreact dark Keynote theme

Built from [`DESIGN.md`](DESIGN.md). Dark mode only.

```
build_theme.py        generator (the source of truth - edit this, not the .pptx)
shinyreact-dark.pptx  generated deck, 5 slides
preview/              Keynote's own PNG render of those slides, for review
shiny-react.png       logo, vendored from posit-dev/shinyreact
DESIGN.md             the spec: tokens, type scale, masters, measured contrast
```

## Rebuild

```bash
uv run --with python-pptx python build_theme.py
```

No project dependency is added — `--with` installs python-pptx into a throwaway
environment.

## Turning it into a `.kth` theme

Takes about a minute:

1. Open `shinyreact-dark.pptx` in Keynote. It shows a pptx-import warnings
   window — dismiss it.
2. **File → Save Theme…** → *Add to Theme Chooser*.
3. Name it `shinyreact dark`.

Keynote's AppleScript dictionary has no theme export (`export … as` offers PDF,
images, PowerPoint and Keynote '09, not `.kth`), but the menu item is reachable
through System Events if you ever want this automated:

```applescript
tell application "System Events" to tell process "Keynote"
  click menu item "Save Theme…" of menu "File" of menu bar 1
end tell
```

That needs Accessibility permission for whatever runs it — more setup than three
clicks are worth for a theme that changes rarely.

New presentations then start from it. The five slides become the ones you
duplicate — Keynote's master-slide system is not used, deliberately: the layouts
here are position-specific, and duplicating a designed slide is both simpler and
less fragile than maintaining parallel masters.

## Fonts

| Role | Used | Fallback if missing |
|---|---|---|
| Display / body | Inter (Regular/Medium/SemiBold/Bold/ExtraBold/Black) | Helvetica Neue → Arial |
| Code | Source Code Pro | Menlo → Courier New |

Inter was installed to `~/Library/Fonts/` during the build (OFL licensed, from
`github.com/rsms/inter` v4.1). To remove it:

```bash
rm ~/Library/Fonts/Inter-{Regular,Medium,SemiBold,Bold,ExtraBold,Black}.ttf
```

**Keynote does not embed fonts.** Presenting from a machine without Inter will
substitute Helvetica Neue. That sets narrower than Inter, so lines shrink rather
than overflow — degraded but not broken. This has not been tested on a clean
machine (acceptance criterion 4 in the spec).

## Placeholders to replace before presenting

- **QR code** on slide 1 — currently a white square labelled "QR". Replace the
  shape with a picture of your talk's QR code.
- Slide text is example copy from the spec's mockups.

## What is where

| Slide | Master |
|---|---|
| 1 | Title — logo on hex plate, orbit watermark, swoosh, footer lockup |
| 2 | Section divider — ghost number, centred orbit, no footer |
| 3 | Content — kicker, head, swoosh, cyan-rule bullets |
| 4 | Code two-up — equal-height elevated panels |
| 5 | Data — stat row + direct-labelled bar chart |

## Editing rules worth keeping

- `--cyan #00D8FF` is for **graphics only** (swoosh, orbit, bullet rules, logo).
  Text uses `#6FD4E8`. Both measure ~9.8:1; the split is about chromatic fringing
  at large sizes, not contrast.
- One motif per slide. The hexagon appears only in the title lockup.
- Chart series colors are assigned in fixed order and never cycled. A sixth
  series folds into "Other".
- Nothing below 28px on the 1920×1080 canvas.
