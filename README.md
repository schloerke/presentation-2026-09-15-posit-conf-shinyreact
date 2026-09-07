# Beyond Bootstrap: Building Custom Shiny UI with React

Slides: https://schloerke.com/presentation-2026-09-15-posit-conf-shinyreact/

## Links

* `{shinyreact}`: http://github.com/posit-dev/shinyreact
* `{shiny}`: https://shiny.posit.co/r/
* `React`: https://react.dev/

### Samuel Bharti's summer of Shiny

Posit engineering intern, summer 2026. The apps on the "In the wild" slide.

* Samuel Bharti: https://www.samuelbharti.com/ · https://github.com/samuelbharti
* The gallery: https://github.com/posit-dev/shiny-showcase-bioinformatics

| app | live | source | DOI |
|---|---|---|---|
| tahoe-explorer | [live](https://posit-tahoe-explorer.share.connect.posit.cloud/) | [source](https://github.com/samuelbharti/tahoe-explorer) | [10.5281/zenodo.21950641](https://doi.org/10.5281/zenodo.21950641) |
| genescout | [live](https://posit-genescout.share.connect.posit.cloud/) | [source](https://github.com/samuelbharti/genescout) | [10.5281/zenodo.21950644](https://doi.org/10.5281/zenodo.21950644) |
| variant-reviewer | [live](https://posit-variant-reviewer.share.connect.posit.cloud/) | [source](https://github.com/samuelbharti/variant-reviewer) | [10.5281/zenodo.21950635](https://doi.org/10.5281/zenodo.21950635) |
| gene-list-builder | [live](https://posit-gene-list-builder.share.connect.posit.cloud/) | [source](https://github.com/samuelbharti/gene-list-builder) | [10.5281/zenodo.21950640](https://doi.org/10.5281/zenodo.21950640) |
| Plotomics Live | [live](https://posit-plotomics-live.share.connect.posit.cloud/) | [source](https://github.com/samuelbharti/plotomics-live) | [10.5281/zenodo.21950647](https://doi.org/10.5281/zenodo.21950647) |



---

## Abstract

Shiny makes it easy to build interactive applications in R and Python. But when an app needs a truly custom user interface, authors often end up building markup, styling, and interaction details in the same language as their reactive logic. This talk introduces `{shinyreact}` which keeps Shiny's reactive engine and uses React's proven component ecosystem for the UI.

In this talk, we'll learn the basics by converting the familiar Old Faithful app into a `{shinyreact}` app by moving the UI from R into React JavaScript. We will see why that boundary is especially useful with coding agents: describe the interface in plain text, let an agent handle the busy-work UI details, and keep important logic in your familiar language.

You will leave with a practical model for adding fully custom React UI to Shiny without giving up Shiny's reactive core.
