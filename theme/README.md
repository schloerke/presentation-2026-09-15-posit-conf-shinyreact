# shinyreact dark Keynote theme

Built from [`DESIGN.md`](DESIGN.md). Dark mode only.

```
build_theme.py        generator (the source of truth - edit this, not the .pptx)
shinyreact-dark.pptx  5 masters + 5 example slides
preview/slide-N.png       the example slides
preview/master-N-blank.png a fresh slide from each master - what you actually get
shiny-react.png       logo, vendored from posit-dev/shinyreact
DESIGN.md             the spec: tokens, type scale, masters, measured contrast
```

## The thing that was wrong the first time

**Keynote's "Save Theme" captures master slides, not content slides.** Version one
drew the whole design on slides and deliberately skipped masters, so the saved
`.kth` carried the master's background colour and nothing else. Every new
presentation from it came out blank on a dark background.

So: all design furniture lives on **slide layouts** (PowerPoint's name for what
Keynote calls masters), and every editable text region is a real `<p:ph>`
placeholder. Content slides in the deck are only examples.

`preview/master-N-blank.png` is the regression check — a *fresh* slide from each
master, which is what a theme user gets. If those go blank again, the theme is
broken no matter how good `slide-N.png` looks.

## Rebuild

```bash
uv run --with python-pptx python build_theme.py
```

## Turning it into a `.kth` theme

1. Open `shinyreact-dark.pptx` in Keynote. Dismiss the pptx-import warnings window.
2. Confirm you are on the right window, then **File → Save Theme…** →
   *Add to Theme Chooser*.
3. Name it `shinyreact dark`.

**Save the theme from the correct window.** Keynote keeps documents open across
sessions, and saving from a stale window silently produces a theme with Apple's
nine stock masters instead of these five. That failure looks identical to
success until you start a presentation from it.

Verify in one line — a good theme reports five masters with these names:

```bash
osascript -e 'tell application "Keynote" to return name of slide layouts of front document'
# Title, Section divider, Content, Code two-up, Data
```

Automating the menu item is possible (`click menu item "Save Theme…" of menu
"File" of menu bar 1` via System Events, needs Accessibility permission), but the
file-save panel resists scripting; *Add to Theme Chooser* is one click and works.

## The masters

| Master | Static furniture | Editable |
|---|---|---|
| Title | orbit, hex ring + logo, kicker, swoosh, conf/QR/speaker lockup | title, subtitle |
| Section divider | orbit, swoosh | section name, number |
| Content | swoosh, footer | title, bullets (cyan bar) |
| Code two-up | two elevated panels, footer | title, 2x filename, 2x code |
| Data | footer | title, caption |

Bullets are a cyan `▍` bullet character, not a drawn rectangle, so they stay
aligned when a bullet wraps to two lines.

## Fonts

| Role | Used | Fallback if missing |
|---|---|---|
| Display / body | Inter (Regular/Medium/SemiBold/Bold/ExtraBold/Black) | Helvetica Neue → Arial |
| Code | Source Code Pro | Menlo → Courier New |

Inter was installed to `~/Library/Fonts/` (OFL, from `github.com/rsms/inter` v4.1):

```bash
rm ~/Library/Fonts/Inter-{Regular,Medium,SemiBold,Bold,ExtraBold,Black}.ttf
```

Keynote does not embed fonts. Presenting without Inter substitutes Helvetica Neue,
which sets narrower — degraded, not broken. Untested on a clean machine.

## Placeholders to replace

- **QR code** on the Title master is a white square labelled "QR".
- Example slide text is copy from the spec mockups.
