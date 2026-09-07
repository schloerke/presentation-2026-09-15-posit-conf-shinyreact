library(shiny)
library(shinyreact)

# Base R ships the Old Faithful dataset; the Python servers read the same data
# from the faithful.csv exported next to this file.
x <- faithful$waiting

ui <- page_react_html("www/index.html")

server <- function(input, output, session) {
  # input$bin_count is NULL until the client's first
  # useShinyInput("bin_count", 30)
  # message arrives. Returning NULL leaves the React side on its "Loading…"
  # placeholder; req() would work too, but its silent error still reaches the
  # client. (Python's input.bin_count() raises a silent exception instead.)
  bin_count <- reactive(input$bin_count)

  output$dist_data <- reactive_output({
    n <- bin_count()
    if (is.null(n)) {
      return(NULL)
    }
    breaks <- seq(min(x), max(x), length.out = n + 1)
    bins <- hist(x, breaks = breaks, plot = FALSE)
    # I() keeps length-1 vectors as JSON arrays (n = 1) instead of scalars.
    list(breaks = I(bins$breaks), counts = I(bins$counts))
  })
}

shinyApp(ui, server)
