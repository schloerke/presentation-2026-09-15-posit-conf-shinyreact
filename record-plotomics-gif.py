"""Record the Plotomics Live Visium panel as a frame sequence.

NOTE: the deck no longer uses this. Its slide now shows a hand-recorded clip of
the *Xenium* page (see CLAUDE.md) - that page's million WebGL points come out
sparse and wrong under automation, so it cannot be captured this way. This
script is kept because it still works for the Visium page, which is 3,798 spots
over a photograph rather than mass WebGL.

Four beats, in the order the talk needs them: the React render, fading the
spots to reveal the H&E underneath, recolouring by gene (a server round trip),
and the same computation as a classic ggplot2 image. Frames land in
.context/frames/ for `magick` to assemble.

Not part of the deck's build - run by hand when the GIF needs redoing.
"""

import pathlib
import shutil

from playwright.sync_api import sync_playwright

URL = "https://posit-plotomics-live.share.connect.posit.cloud/#/visium"
OUT = pathlib.Path(".context/frames")


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    n = 0

    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1400, "height": 1000})
        pg.goto(URL, wait_until="networkidle")
        pg.wait_for_selector("canvas")
        pg.wait_for_timeout(3000)
        panel = pg.locator(".panel")

        def shot(k=1):
            nonlocal n
            for _ in range(k):
                panel.screenshot(path=str(OUT / f"f{n:03d}.png"))
                n += 1

        # beat 1: as it lands - clusters over the histology
        shot(6)

        # beat 2: fade the spots out and back. Keyboard rather than a set on
        # .value: the slider is React-controlled, so it needs real input events.
        slider = pg.locator("input[type=range]")
        slider.focus()
        for _ in range(12):
            slider.press("ArrowLeft")
            pg.wait_for_timeout(60)
            shot()
        shot(3)
        for _ in range(12):
            slider.press("ArrowRight")
            pg.wait_for_timeout(60)
            shot()

        # beat 3: colour by gene - the server recomputes and the spots restyle
        pg.locator(".panel select").first.select_option("gene")
        pg.wait_for_timeout(1200)
        shot(8)

        # beat 4: the same numbers, drawn by ggplot2 on the server
        pg.get_by_role("button", name="ggplot2 (classic)").click()
        pg.wait_for_timeout(2500)
        shot(10)

        # back to React, so the loop closes where it started
        pg.get_by_role("button", name="Shiny React").click()
        pg.wait_for_timeout(1500)
        shot(4)
        pg.locator(".panel select").first.select_option("cluster")
        pg.wait_for_timeout(1200)
        shot(4)

        b.close()

    print(f"{n} frames in {OUT}")


if __name__ == "__main__":
    main()
