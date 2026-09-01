# Original Title - Beyond Bootstrap: Building Custom Shiny UI Packages with AI
# Proposed Title - Beyond Bootstrap: Building Custom Shiny UI with React

Slides: https://schloerke.com/presentation-2026-09-15-posit-conf-shinyreact/

## Links

* `{shinyreact}`: http://github.com/posit-dev/shinyreact
* `{shiny}`: https://shiny.posit.co/r/
* `React`: https://react.dev/



-------------------------------

## Original Abstract

Shiny developers have long been limited to Bootstrap and a handful of pre-built UI frameworks. But what if you could use Material UI, Ant Design, or any modern react.js web framework you love? This talk demonstrates how AI can generate production-ready R packages that wrap your favorite UI frameworks for Shiny. We'll walk through using AI to translate JavaScript components into R bindings, handle dependencies, and create idiomatic interfaces—no JavaScript expertise required. You'll see live examples, learn effective prompting patterns, and discover how to maintain AI-generated packages. Whether you want Material Design or Web Components, AI makes it possible to bring any UI framework into your Shiny apps.


## Proposed Abstract

Shiny makes it easy to build interactive applications in R and Python. But when an app needs a truly custom user interface, authors often end up building markup, styling, and interaction details in the same language as their reactive logic. This talk introduces `{shinyreact}` which keeps Shiny's reactive engine and uses React's proven component ecosystem for the UI.

In this talk, we'll learn the basics by converting the familiar Old Faithful app into a `{shinyreact}` app by moving the UI from R into React JavaScript. We will see why that boundary is especially useful with coding agents: describe the interface in plain text, let an agent handle the busy-work UI details, and keep important logic in your familiar language.

You will leave with a practical model for adding fully custom React UI to Shiny without giving up Shiny's reactive core.
