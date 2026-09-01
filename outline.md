

* Demo
  * ** show's app on screen
  * > I have been building Shiny apps since 2016 and the Shiny Team since 2018. The Old Faithful app is the kind of app that made me love Shiny: one input, one plot, a complete interactive application in just a few lines of R.
  * > And this app is still Old Faithful in another sense: dependable, familiar, and exactly the UI we have all seen before.
  * ** Run app


* Old faithful
  > Let's dig into the code for Old Faithful

  * UI
    * > Historically, shiny requires you to own both the UI and server definitions
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

      *
      * > For an app like this, the R UI is wonderful.
      * > But when working with larger teams, you may want to hand off some of the responsibility to a colleague or LMM.
      * TODO: > But when a request comes in for a distinctive interface, richer interaction, or a component from a modern design system... You are suddenly authoring markup, styling, and interaction details too.

      * > Still want to keep Shiny's reactive model. This is your domain expertise!
      * > I do not want to replace Shiny. I want to keep Shiny for reactive computation while using a modern UI ecosystem for the interface.

      * TODO: What are people expecting?
        * bslib covers 80% with a small set of functions... but customizations are MUCH harder


* React.js
  * >> The library for web and native user interfaces
  * >> ... build user interfaces out of individual pieces called components
  * Why React?
    * > MASSIVE ecosystem of proven components ready for production environments
    * > ... dwarfs what R/python readily has available
  * TODO: DEMO SLIDE
    * UI is assembled given data's state
      * > React is _REALLY_ good at just taking JSON at mapping data to UI
      * > Don't worry about managing the transitions from one data state to another!

  TODO: better placement
  * Why Shiny + React?
    * > If you've found yourself writing custom HTML and JavaScript, React.js is a perfect framework to help scale your larger projects
  * TODO: Move You expect me to write JavaScript?!?
    * With baby pink logo for react.js
    * "We picked it up off the shelf to not write JS.. Happy with the tradeoffs"
    * AI does better when building on top of existing frameworks is safer.


* Animation: shiny + react. Hex logo creation slide


* `shinyreact`
  * "Shiny UI infrastructure for React-based component rendering"
    * > With `shinyreact`, the Shiny server contains only reactive data computation, and the UI is a React client you own. `shinyreact` provides the bridge between the two and ships zero UI components itself.
  * Reactive Model
    * > Pure functional programming makes logic easy to reason about as apps scale up in complexity.
    * > This make both of these frameworks a joy to work in
  * Build the whole UI from the ground up using react / typescript
    * > Experimental package for the brave few

    <!-- * > "Similar to working on cars... " you know that using the right tool will save you time and energy. -->


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
            shinyreact::reactive_output({ # <<
              breaks <- seq(min(x), max(x), length.out = input$bins + 1)
              info <- hist(x, breaks = breaks, plot = FALSE) # <<
              info[c("breaks", "counts")] # <<
            })
        }
        ```

      * shinyreact::reactive_output()
        * > `hist(x, plot = FALSE)` creates list containing `breaks` and `counts`
        * > Now, we just send the required data
        * > That is the contracted shape the browser receives
        * > Let React display your data's state within the UI
        * Name: Convert data to send to the client as JSON
          * > No direct corresponding UI component
          * > This is a new concept!!!
            * TODO: Amazon returns
        * > With this model, we are strongly encouraging the server to pass data directly to the front end. Then, let React handle the data from there


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
        * > Note that you're signing up for all UI inputs and outputs living in TypeScript!
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
                <input  // # <<
                  id="bins"
                  type="range"
                  value={bins}
                  onChange={(e) => setBins(Number(e.target.value))}
                />
              </aside>

              <section className="panel">
                <div className="chart">
                  <Histogram data={data} /> // # <<
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
    * TODO: > Inputs still travel to the Shiny server. Outputs now travel back as data.
    * > IDs and JSON are the contract

> At this point you might be thinking... "You want me to write JavaScript?!?"
* "You want me to write JavaScript?!?"
  * Joe: "Shiny authors shouldn't need to write JavaScript"
    * Barret: I believe this still holds true!
  * > Agents today have far more examples of mainstream React patterns than custom Shiny UI apps. I trust any frontier model to write react.js code better than I can
    * > That narrow IDs and JSON contract makes the client boundary practical to review and maintain
  * > You need to be able to describe your UI and review the result.

  * Q: Can I use existing outputs?
    * A: Yup. Use regular render methods, just like normal. But pair them with `<ShinyOutput id="distPlot" />` in your React.js code. Do not reinvent the wheel
    * A: Then your UI app is more about layout than it is Outputs


* Future work
  * Incremental adoption: Embed react components into existing apps
    * > Makes it so you don't have to port your whole application into React.js
    * > Opens the door for helper packages down the road.
    * > Today, everything will feel ad-hoc when writing shinyreact apps


* Recap
  * Keep R/Python for reactive data processing
  * Let an agent build the React.js client.
  * IDs and JSON structures are the communication contract


* Q & A
  * Q: Is node.js needed?
    * A: No, but highly recommended. TSX code is much more readible than vanilla JavaScript. And you'll be able to use a build system which can lint / strong type your code.
  * Q: How do I review/confirm generated code?
    * A: If this is an absolute requirement,
    * A: Unit tests will help with drift, but the unit tests will confirm existing behavior
    * A: The logic that you care about is in the server-side code. You can review it, defend it, and write independent tests. But I'm comfortable delegating busy-work UI details off to the LLM
  * Q: What can I do for existing apps?
    * A: Agent Skills are available to convert your Shiny apps to use shinyreact
