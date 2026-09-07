library(shiny)
library(shinyreact)

x <- faithful$waiting

ui <- page_react_html("www/index.html")

server <- function(input, output, session) {
  output$dist_data <- reactive_output({
    req(input$bin_count)
    breaks <- seq(min(x), max(x), length.out = input$bin_count + 1)
    bins <- hist(x, breaks = breaks, plot = FALSE)
    list(breaks = I(bins$breaks), counts = I(bins$counts))
  })
}

shinyApp(ui, server)
