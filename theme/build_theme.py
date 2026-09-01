#!/usr/bin/env python3
"""Build the shinyreact dark Keynote theme as a .pptx.

Keynote imports .pptx and can then re-save as a .kth theme, which is the only
practical programmatic route: Keynote's own AppleScript dictionary cannot create
master slides.

Design authority is DESIGN.md, alongside this file.
Dark mode only, per the 2026-08-18 decision to drop the light variant.

Coordinate system: the spec is written against a 1920x1080 px canvas. The deck is
960x540 pt (13.333in x 7.5in, 16:9), so **pt = px / 2** exactly. PX() does that
conversion so the code can quote spec numbers verbatim.

Run:  uv run --with python-pptx python build_theme.py
"""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Pt

HERE = Path(__file__).parent
LOGO = HERE / "shiny-react.png"  # vendored from posit-dev/shinyreact
OUT = HERE / "shinyreact-dark.pptx"

# ---------------------------------------------------------------- spec tokens

INK = RGBColor(0x1C, 0x1D, 0x22)  # slide ground
INK_DEEP = RGBColor(0x14, 0x15, 0x19)  # code panels, divider slides
HEX_PLATE = RGBColor(0x23, 0x25, 0x2C)  # ring behind the title logo
TEXT = RGBColor(0xF2, 0xF4, 0xF8)  # 15.28:1 on INK
MUTED = RGBColor(0xA3, 0xAC, 0xBB)  # 7.35:1 on INK
CYAN = RGBColor(0x00, 0xD8, 0xFF)  # GRAPHIC ONLY - swoosh, orbit, rules
CYAN_TEXT = RGBColor(0x6F, 0xD4, 0xE8)  # 9.82:1 on INK - all text runs

# code tokens, all >= 7:1 on INK_DEEP
C_KEYWORD = RGBColor(0xC7, 0xA0, 0xFF)
C_STRING = RGBColor(0x9F, 0xE8, 0x8D)
C_NUMBER = RGBColor(0xFF, 0xB8, 0x6C)
C_COMMENT = RGBColor(0x9A, 0xA3, 0xB2)  # was #6B7280 at 3.77:1 - the one failure

# validated categorical palette, dark steps, fixed order, never cycled
SERIES = [
    RGBColor(0x0E, 0x9D, 0xBA),
    RGBColor(0xE2, 0x62, 0x2B),
    RGBColor(0x3D, 0x8A, 0xE0),
    RGBColor(0x74, 0xA0, 0x12),
    RGBColor(0xC7, 0x4B, 0xD1),
]

DISPLAY = "Inter ExtraBold"
BODY_MED = "Inter Medium"
BODY = "Inter"
BOLD = "Inter Bold"
MONO = "Source Code Pro"

MARGIN = 96  # px, left/right
FOOTER_BOTTOM = 60  # px, to footer baseline


def PX(px):
    """Spec pixels (1920x1080 canvas) -> points (960x540 deck)."""
    return Pt(px / 2)


# ------------------------------------------------------------------- helpers


def set_alpha(color_format, pct):
    """python-pptx has no opacity API; splice <a:alpha> into the colour element.

    Takes a ColorFormat (shape.fill.fore_color, shape.line.color, run.font.color) -
    its _xFill IS the <a:solidFill>, so srgbClr is a direct child.
    """
    srgb = color_format._xFill.find(qn("a:srgbClr"))
    alpha = srgb.makeelement(qn("a:alpha"), {"val": str(int(pct * 1000))})
    srgb.append(alpha)


def set_letter_spacing(run, pt_value):
    """Tracking, in points. OOXML wants hundredths of a point on rPr/@spc."""
    run.font._rPr.set("spc", str(int(pt_value * 100)))


def no_autofit(tf):
    """Keep text boxes at their designed size; Keynote must not reflow them."""
    tf.word_wrap = True
    bodyPr = tf._txBody.find(qn("a:bodyPr"))
    for tag in ("a:normAutofit", "a:spAutoFit"):
        found = bodyPr.find(qn(tag))
        if found is not None:
            bodyPr.remove(found)


def shapes_of(container):
    """Accept either a Slide/SlideLayout or an already-unwrapped shape tree."""
    return container.shapes if hasattr(container, "shapes") else container


def textbox(container, x, y, w, h, *, anchor=MSO_ANCHOR.TOP):
    box = shapes_of(container).add_textbox(PX(x), PX(y), PX(w), PX(h))
    tf = box.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    no_autofit(tf)
    return box, tf


def style(
    para,
    text,
    *,
    size,
    color,
    font=BODY,
    spacing=None,
    align=PP_ALIGN.LEFT,
    line=None,
):
    """Add one run to a paragraph with spec-quoted px sizing."""
    para.alignment = align
    run = para.add_run()
    run.text = text
    run.font.size = PX(size)
    run.font.color.rgb = color
    run.font.name = font
    if spacing:
        set_letter_spacing(run, spacing / 2)  # px -> pt
    if line:
        para.line_spacing = line
    return run


def rect(container, x, y, w, h, color, *, shape=MSO_SHAPE.RECTANGLE, alpha=None):
    sh = shapes_of(container).add_shape(shape, PX(x), PX(y), PX(w), PX(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = color
    if alpha is not None:
        set_alpha(sh.fill.fore_color, alpha)
    sh.line.fill.background()
    sh.shadow.inherit = False
    return sh


def hexagon(container, x, y, w, h, color):
    """Pointy-top hexagon matching the sticker silhouette.

    Built as a freeform rather than MSO_SHAPE.HEXAGON: that preset is flat-top,
    and rotating it 90 degrees swaps the bounding box, so a 560x647 plate renders
    647 wide and lands off-register behind the logo.
    """
    pts = [
        (x + w / 2, y), (x + w, y + h * 0.25), (x + w, y + h * 0.75),
        (x + w / 2, y + h), (x, y + h * 0.75), (x, y + h * 0.25),
    ]
    builder = shapes_of(container).build_freeform(PX(pts[0][0]), PX(pts[0][1]))
    builder.add_line_segments([(PX(a), PX(b)) for a, b in pts[1:]], close=True)
    sh = builder.convert_to_shape()
    sh.fill.solid()
    sh.fill.fore_color.rgb = color
    sh.line.fill.background()
    sh.shadow.inherit = False
    return sh


def bezier_points(p0, p1, p2, p3, n=48):
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        x = u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0]
        y = u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1]
        pts.append((x, y))
    return pts


def swoosh(container, x, y, width):
    """The logo's swoosh, reused as the rule under a headline.

    Sampled from the mockup's cubic `M4 34 C 150 6, 340 6, 516 20` in a 520x46 box,
    then scaled. Freeform with no fill + a stroke gives a polyline.
    """
    s = width / 520.0
    pts = bezier_points((4, 34), (150, 6), (340, 6), (516, 20))
    scaled = [(x + px * s, y + py * s) for px, py in pts]
    builder = shapes_of(container).build_freeform(PX(scaled[0][0]), PX(scaled[0][1]))
    builder.add_line_segments(
        [(PX(px), PX(py)) for px, py in scaled[1:]], close=False
    )
    sh = builder.convert_to_shape()
    sh.fill.background()
    sh.line.color.rgb = CYAN
    sh.line.width = PX(8)
    sh.shadow.inherit = False
    lnPr = sh.line._get_or_add_ln()
    lnPr.set("cap", "rnd")
    return sh


def orbit(container, cx, cy, size, alpha):
    """React atom watermark - three rotated ellipses, no fill."""
    rx, ry = size * 0.92, size * 0.35
    for angle in (0, 60, 120):
        el = shapes_of(container).add_shape(
            MSO_SHAPE.OVAL, PX(cx - rx), PX(cy - ry), PX(rx * 2), PX(ry * 2)
        )
        el.fill.background()
        el.line.color.rgb = CYAN
        el.line.width = PX(3)
        el.rotation = angle
        el.shadow.inherit = False
        set_alpha(el.line.color, alpha)


def footer(container, *, speaker=True):
    """Bottom lockup, carried over from the 2025 OTel deck."""
    y = 1080 - FOOTER_BOTTOM - 34
    if speaker:
        _, tf = textbox(container, 1920 - MARGIN - 700, y, 700, 40)
        p = tf.paragraphs[0]
        style(p, "posit::conf(2026) · @schloerke", size=30, color=MUTED,
              align=PP_ALIGN.RIGHT)


# --------------------------------------------------------------- code panels


def code_panel(slide, x, y, w, h, filename, lines):
    """Elevated panel. `lines` is a list of [(text, color), ...] runs."""
    panel = rect(slide, x, y, w, h, INK_DEEP, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    panel.adjustments[0] = 0.06
    panel.line.color.rgb = CYAN
    panel.line.width = PX(2)
    set_alpha(panel.line.color, 18)

    _, tf = textbox(slide, x + 44, y + 40, w - 88, 40)
    style(tf.paragraphs[0], filename.upper(), size=28, color=CYAN_TEXT,
          font=BOLD, spacing=4)

    _, tf = textbox(slide, x + 44, y + 108, w - 88, h - 148)
    for i, runs in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        # 1.5 overflowed the panel once Keynote applied its own line pitch.
        p.line_spacing = 1.35
        if not runs:
            style(p, " ", size=34, color=TEXT, font=MONO)
            continue
        for text, color in runs:
            r = p.add_run()
            r.text = text
            r.font.size = PX(34)
            r.font.color.rgb = color
            r.font.name = MONO


UI_TSX = [
    [("const", C_KEYWORD), (" [n, setN] = ", TEXT), ("useShinyInput", CYAN_TEXT), ("(", TEXT)],
    [("  ", TEXT), ('"bins"', C_STRING), (", ", TEXT), ("30", C_NUMBER)],
    [(");", TEXT)],
    [("const", C_KEYWORD), (" plot = ", TEXT), ("useShinyOutputValue", CYAN_TEXT), ("(", TEXT)],
    [("  ", TEXT), ('"hist"', C_STRING)],
    [(");", TEXT)],
    [],
    [("return", C_KEYWORD), (" <", TEXT), ("Slider", CYAN_TEXT), (" value={n}", TEXT)],
    [("  onChange={setN} />;", TEXT)],
]

APP_PY = [
    [("# reactive computation only", C_COMMENT)],
    [("@shinyreact.reactive_output", CYAN_TEXT)],
    [("def", C_KEYWORD), (" ", TEXT), ("hist", CYAN_TEXT), ("():", TEXT)],
    [("    ", TEXT), ("return", C_KEYWORD), (" histogram(", TEXT)],
    [("        data, bins=input.bins()", TEXT)],
    [("    )", TEXT)],
]


# ------------------------------------------------------------------- masters


def build():
    prs = Presentation()
    prs.slide_width = PX(1920)
    prs.slide_height = PX(1080)

    master = prs.slide_masters[0]
    blank = master.slide_layouts[6]  # the stock "Blank" layout

    # Ground colour lives on the master so every Keynote master inherits it.
    master.background.fill.solid()
    master.background.fill.fore_color.rgb = INK

    def new_slide(bg=None):
        s = prs.slides.add_slide(blank)
        s.background.fill.solid()
        s.background.fill.fore_color.rgb = bg or INK
        return s

    # ---- 1. Title ---------------------------------------------------------
    s = new_slide()
    orbit(s, 1770, 370, 550, 7)

    _, tf = textbox(s, MARGIN, 250, 1100, 60)
    style(tf.paragraphs[0], "POSIT::CONF(2026)", size=34, color=CYAN_TEXT,
          font=BOLD, spacing=7.5)

    _, tf = textbox(s, MARGIN, 306, 1100, 280)
    for i, txt in enumerate(("React UI,", "Shiny brain.")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        style(p, txt, size=128, color=TEXT, font=DISPLAY, line=0.98)

    swoosh(s, MARGIN, 596, 520)

    _, tf = textbox(s, MARGIN, 686, 1100, 160)
    p = tf.paragraphs[0]
    p.line_spacing = 1.35
    style(p, "Building Shiny apps whose entire", size=46, color=MUTED)
    p2 = tf.add_paragraph()
    p2.line_spacing = 1.35
    style(p2, "interface lives in ", size=46, color=MUTED)
    r = p2.add_run()
    r.text = "ui.tsx"
    r.font.size = PX(46)
    r.font.color.rgb = CYAN_TEXT
    r.font.name = MONO

    # Plate is concentric with the logo's own hex and 40px larger -> reads as a ring
    hexagon(s, 1920 - 130 - 560, 247, 560, 647, HEX_PLATE)
    s.shapes.add_picture(str(LOGO), PX(1920 - 150 - 520), PX(270), width=PX(520))

    _, tf = textbox(s, MARGIN, 940, 400, 90)
    p = tf.paragraphs[0]
    style(p, "posit", size=40, color=TEXT, font=DISPLAY)
    p2 = tf.add_paragraph()
    style(p2, "conf (2026)", size=26, color=MUTED, font=BODY_MED)

    # QR placeholder - swap the fill for a picture of your talk's QR code.
    qr = rect(s, MARGIN + 220, 918, 132, 132, TEXT)
    _, tf = textbox(s, MARGIN + 220, 968, 132, 40)
    style(tf.paragraphs[0], "QR", size=28, color=INK, font=BOLD,
          align=PP_ALIGN.CENTER)

    _, tf = textbox(s, 1920 - MARGIN - 700, 918, 700, 140)
    for txt in ("Barret Schloerke", "posit / Shiny Team", "@schloerke"):
        p = tf.paragraphs[0] if txt.startswith("Barret") else tf.add_paragraph()
        p.line_spacing = 1.45
        style(p, txt, size=30, color=MUTED, align=PP_ALIGN.RIGHT)

    # ---- 2. Section divider ----------------------------------------------
    s = new_slide(INK_DEEP)
    orbit(s, 960, 540, 750, 10)

    _, tf = textbox(s, MARGIN, 400, 600, 220)
    r = style(tf.paragraphs[0], "02", size=240, color=CYAN, font="Inter Black")
    set_alpha(r.font.color, 22)

    _, tf = textbox(s, MARGIN, 636, 1400, 130)
    style(tf.paragraphs[0], "The hook family", size=96, color=TEXT, font=DISPLAY)

    swoosh(s, MARGIN, 790, 640)

    # ---- 3. Content -------------------------------------------------------
    s = new_slide()
    _, tf = textbox(s, MARGIN, 120, 1500, 50)
    style(tf.paragraphs[0], "ONE RESPONSIBILITY EACH", size=34, color=CYAN_TEXT,
          font=BOLD, spacing=7.5)

    _, tf = textbox(s, MARGIN, 176, 1500, 120)
    style(tf.paragraphs[0], "Pick the narrowest hook", size=84, color=TEXT,
          font=DISPLAY)

    swoosh(s, MARGIN, 320, 440)

    bullets = [
        ("A button that only pushes events uses ", "useSetShinyInput"),
        ("A card that only reads uses ", "useShinyOutputValue"),
        ("Narrow hooks make data-flow direction ", "visible at the call site"),
    ]
    y = 456
    for plain, emph in bullets:
        # Bullets are a cyan rule, not a hexagon - hexagons read as clip art.
        rect(s, MARGIN, y, 5, 78, CYAN)
        # 1400 was too narrow - bullet 1 wrapped and collided with bullet 2.
        _, tf = textbox(s, MARGIN + 47, y + 6, 1660, 90)
        p = tf.paragraphs[0]
        p.line_spacing = 1.3
        style(p, plain, size=52, color=TEXT, font=BODY_MED)
        r = p.add_run()
        r.text = emph
        r.font.size = PX(52)
        r.font.color.rgb = CYAN_TEXT
        r.font.name = BOLD
        y += 132
    footer(s)

    # ---- 4. Code, two-up --------------------------------------------------
    s = new_slide()
    _, tf = textbox(s, MARGIN, 96, 1500, 110)
    style(tf.paragraphs[0], "Two files, one app", size=76, color=TEXT, font=DISPLAY)

    gap, panel_w = 48, (1920 - 2 * MARGIN - 48) // 2
    # Equal heights: pad the shorter listing with blank lines, never shrink a panel.
    code_panel(s, MARGIN, 250, panel_w, 660, "ui.tsx", UI_TSX)
    code_panel(s, MARGIN + panel_w + gap, 250, panel_w, 660, "app.py", APP_PY)
    footer(s)

    # ---- 5. Data ----------------------------------------------------------
    s = new_slide()
    _, tf = textbox(s, MARGIN, 96, 1500, 110)
    style(tf.paragraphs[0], "Bundle size by dependency", size=76, color=TEXT,
          font=DISPLAY)

    stats = [("41 kB", "GZIPPED TOTAL"), ("0", "UI COMPONENTS SHIPPED"),
             ("2", "LANGUAGES SUPPORTED")]
    x = MARGIN
    for num, lbl in stats:
        _, tf = textbox(s, x, 232, 560, 150)
        style(tf.paragraphs[0], num, size=132, color=CYAN_TEXT, font=DISPLAY)
        _, tf = textbox(s, x, 386, 560, 46)
        style(tf.paragraphs[0], lbl, size=30, color=MUTED, font=BODY_MED, spacing=1.2)
        x += 620

    # Single series -> no legend; the slide head names it. Every bar direct-labelled.
    bars = [("react", 880, "22.4 kB"), ("react-dom", 540, "13.7 kB"),
            ("shiny-react", 196, "4.9 kB"), ("css", 64, "1.6 kB"),
            ("glue", 30, "0.8 kB")]
    axis_x, y = 566, 500
    rect(s, axis_x, y - 10, 2, 410, MUTED, alpha=50)  # baseline
    for i, (label, width, value) in enumerate(bars):
        _, tf = textbox(s, axis_x - 430, y + 6, 400, 50)
        style(tf.paragraphs[0], label, size=30, color=MUTED, font=BODY_MED,
              align=PP_ALIGN.RIGHT)
        bar = rect(s, axis_x + 12, y, width, 46, SERIES[i],
                   shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        bar.adjustments[0] = 0.09
        _, tf = textbox(s, axis_x + width + 42, y + 6, 300, 50)
        style(tf.paragraphs[0], value, size=30, color=TEXT, font=MONO)
        y += 80
    footer(s)

    prs.save(OUT)
    print(f"wrote {OUT}  ({OUT.stat().st_size // 1024} kB, {len(prs.slides.__iter__.__self__._sldIdLst)} slides)")


if __name__ == "__main__":
    build()
