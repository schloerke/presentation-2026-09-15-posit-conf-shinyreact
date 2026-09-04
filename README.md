# Beyond Bootstrap: Building Custom Shiny UI with React

Slides: https://schloerke.com/presentation-2026-09-15-posit-conf-shinyreact/

## Links

* `{shinyreact}`: http://github.com/posit-dev/shinyreact
* `{shiny}`: https://shiny.posit.co/r/
* `React`: https://react.dev/



---

## Abstract

Shiny makes it easy to build interactive applications in R and Python. But when an app needs a truly custom user interface, authors often end up building markup, styling, and interaction details in the same language as their reactive logic. This talk introduces `{shinyreact}` which keeps Shiny's reactive engine and uses React's proven component ecosystem for the UI.

In this talk, we'll learn the basics by converting the familiar Old Faithful app into a `{shinyreact}` app by moving the UI from R into React JavaScript. We will see why that boundary is especially useful with coding agents: describe the interface in plain text, let an agent handle the busy-work UI details, and keep important logic in your familiar language.

You will leave with a practical model for adding fully custom React UI to Shiny without giving up Shiny's reactive core.
