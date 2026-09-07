library(shiny)
library(bslib)

ui <- page_sidebar(
  title = "Hello Shiny!",
  sidebar = sidebar(
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
  })
}

shinyApp(ui = ui, server = server)
