

* Demo
  * ** show's app on screen
  * **Run app
  * > I have been building Shiny apps since 2016 and the Shiny Team since 2018. The Old Faithful app is the kind of app that made me love Shiny: one input, one plot, a complete interactive application in just a few lines of R.
  * > And this app is still Old Faithful in another sense: dependable, familiar, and exactly the UI we have all seen before.


* Old faithful
  > Let's dig into the code for Old Faithful

  * UI
    *
      ```r
        ui <- bslib::page_sidebar(
          sidebar = bslib::sidebar(
            sliderInput(inputId = "bins", ...)
          ),
          plotOutput(outputId = "distPlot")
        )
      ```
    * R owns both the UI definition and reactive computation

    * > For an app like this, the R UI is wonderful. But when a request comes in for a distinctive interface, richer interaction, or a component from a modern design system... I am suddenly authoring markup, styling, and interaction details too.
    * > I do not want to replace Shiny. I want to keep Shiny for reactive computation while using a modern UI ecosystem for the interface.


* React.js
  * >> The library for web and native user interfaces
  * >> ... build user interfaces out of individual pieces called components
  * UI is assembled given data's state. (Don't worry about transitions!)


* `shinyreact`
  * "Shiny UI infrastructure for React-based component rendering"
  * > With `shinyreact`, the Shiny server contains only reactive computation, and the UI is a React client you own. `shinyreact` provides the bridge between the two and ships zero UI components itself.


* Animation: Hex logo creation slide


* Old Faithful w/ `shinyreact`
  * > Let's re-imagine our Old Faithful app using `shinyreact`
    * Original
      ```r
      x <- faithful$waiting
      server <- function(input, output) {
        output$distPlot <-
          renderPlot({
            breaks <- seq(min(x), max(x), length.out = input$bins + 1)
            hist(x, breaks = breaks)
          })
      }
      ```
      * `input$bins` -> `breaks` -> `hist()`
        * > We can see the single input value `bins` being used to calculate `breaks`
        * > This value is then fed into `hist()` with the specified breaks to produce a histogram of the data

    * shinyreact
      * > The reactive computation is unchanged. What has changed is the value sent by the server.
        ```r
        x <- faithful$waiting
        server <- function(input, output) {
          output$distPlot <-
            shinyreact::reactive_output({
              breaks <- seq(min(x), max(x), length.out = input$bins + 1)
              info <- hist(x, breaks = breaks, plot = FALSE) # <<
              info[c("breaks", "counts")] # <<
            })
        }
        ```
      * shinyreact::reactive_output()
        * Send data to the browser w/ no direct corresponding UI component
        * > `hist(x, plot = FALSE)` creates list containing `breaks` and `counts`
        * > Now, we just send the required data
        * > That is the contracted shape the browser receives
        * > Let React display your data's state within the UI


  * UI
    * > Now let's look at the UI definitions
    * >
    * R Shiny
      ```r
      # app.R
      ui <- bslib::page_sidebar(
        sidebar = bslib::sidebar(
          sliderInput(inputId = "bins", ...)
        ),
        plotOutput(outputId = "distPlot")
      )
      ```
    * react
      * All UI is defined within JavaScript / TypeScript files
      * Within app.R: `ui <- shinyreact::page_react_html()`
      * ui.tsx
        * > `ui.tsx` is Shiny's index.html escape hatch, but upgraded for React
        ```tsx
        // www/ui.tsx
        export default function App() {
          const [bins, setBins] = useShinyInput<number>("bins", 30);
          const data = useShinyOutputValue<HistData | null>("distPlot", null);

          return (
            <main className="layout">
              <aside className="sidebar">
                <label htmlFor="bins">Number of bins:</label>
                <input
                  id="bins"
                  type="range"
                  value={bins}
                  onChange={(e) => setBins(Number(e.target.value))}
                />
              </aside>

              <section className="panel">
                <div className="chart">
                  <Histogram data={data} />
                </div>
              </section>
            </main>
          );
        }
        ```
      * > `useShinyInput("<id>", default)`
      * > `useShinyOutputValue("<id>", default)`


* Data Cycle - image
  * > Shiny R/Python
    * > Server: `input$value` -> `reactive()` -> `renderFn()`

  * shinyreact
    * Server: `input$value` -> `reactive()` -> `reactive_output()`
    * Browser:
      * Get and set Input values
        * `const [value, setValue] = useShinyInput("<id>", default)`
      * Get output values
        * `const value = useShinyOutputValue("<id>", default)`
    * > Keep R/Python for data work and reactivity.
    * > Inputs still travel to the Shiny server. Outputs now travel back as data.
    * > IDs and JSON are the contract

> At this point you might be thinking... "You want me to write JavaScript?!?"
* "You want me to write JavaScript?!?"
  * > That narrow IDs and JSON contract makes the client boundary practical to review and maintain
  * Joe: "Shiny authors shouldn't need to write JavaScript"
    * Barret: I believe this still holds true!
  * > Agents today have far more examples of mainstream React patterns than custom Shiny UI apps. I trust any frontier model to write react.js code better than I can
  * > You need to be able to describe your UI and review the result.


* Future work
  * Incremental adoption: Embed react components into existing apps
    * > Makes it so you don't have to port your whole application into React.js
    * > Opens the door for helper packages down the road.


* Recap
  * Keep R/Python for reactive data processing
  * Let an agent build the React.js client.
  * IDs and JSON structures are the communication contract


* Q&A
  * Q: Can I use existing outputs?
    * A: Yup. Use regular render methods, just like normal. But pair them with `<ShinyOutput id="distPlot" />` in your React.js code. Do not reinvent the wheel
  * Q: How do I review/confirm generated code?
  * Q: Is node.js needed?
    * A: No, but preferred
