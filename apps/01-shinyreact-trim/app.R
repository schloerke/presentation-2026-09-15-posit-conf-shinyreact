library(shiny)
library(shinyreact)

x <- faithful$waiting

ui <- page_react_html("www/index.html")

server <- function(input, output, session) {
  output$dist_data <- reactive_output({
    req(input$bins)
    breaks <- seq(min(x), max(x), length.out = input$bins + 1)
    info <- hist(x, breaks = breaks, plot = FALSE)
    list(breaks = I(info$breaks), counts = I(info$counts))
  })
}

shinyApp(ui, server)
