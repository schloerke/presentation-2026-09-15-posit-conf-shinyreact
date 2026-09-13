library(shiny)
library(bslib)

ui <- page_sidebar(
  # Sized for a projector, not a laptop: this runs at 1:1 with the 1920x1080
  # canvas, same as the other two demos' `html { font-size: 26px }`.
  theme = bs_theme(font_scale = 1.6),
  # ionRangeSlider's parts are fixed px whatever the font size is: 11px bubble,
  # 10px min/max, 9px grid, a 3px bar and a 19px handle. Scaling the whole
  # widget with a transform fixes the size but shrinks the track to match, so
  # the parts are resized instead - each `top` re-centred on the same 40px axis.
  # `.irs-bar` needs `!important`: bslib's own rule lands after this style tag.
  tags$style(HTML("
    .irs--shiny { height: 80px; }
    .irs--shiny .irs-line { height: 8px; top: 36px; border-radius: 4px; }
    .irs--shiny .irs-bar { height: 8px !important; top: 36px !important; }
    .irs--shiny .irs-handle { width: 32px; height: 32px; top: 24px; }
    .irs--shiny .irs-single { font-size: 20px; top: 0; padding: 2px 10px; }
    .irs--shiny .irs-min, .irs--shiny .irs-max { font-size: 18px; top: 0; padding: 2px 8px; }
    .irs--shiny .irs-grid { top: 52px; height: 24px; }
    .irs--shiny .irs-grid-text { font-size: 16px; top: 12px; }
  ")),
  title = "Hello Shiny!",
  sidebar = sidebar(
    width = 420,
    sliderInput(
      inputId = "bin_count",
      label = "Number of bins:",
      min = 1,
      max = 50,
      value = 30
    )
  ),

  plotOutput(outputId = "distPlot")
)

server <- function(input, output) {
  # The plot's text is in device pixels, so `font_scale` does not reach it;
  # `res` is the lever for the chart, as the svg's width is for the React one.
  output$distPlot <- renderPlot({
    x <- faithful$waiting
    breaks <- seq(min(x), max(x), length.out = input$bin_count + 1)

    hist(
      x,
      breaks = breaks,
      col = "#75AADB",
      border = "white",
      xlab = "Waiting time to next eruption (in mins)",
      main = "Histogram of waiting times"
    )
  }, res = 130)
}

shinyApp(ui = ui, server = server)
