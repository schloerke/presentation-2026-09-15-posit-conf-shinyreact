
> Today I want to talk about using reactjs within your shiny applications. But before I do that, I want to talk about my favorite Shiny application. _Everyone remembers their first... app_, and mine was Old Faithful.

* Demo
  * ** show's app on screen
  * > I have been building Shiny apps since 2016 and the Shiny Team since 2018. The Old Faithful app is the kind of app that made me love Shiny: one input, one plot, a complete interactive application in just a few lines of R.
  * > And this app is still Old Faithful in another sense: dependable, familiar, and exactly the UI we have all seen before.
  * ** Run app


* Old faithful
  > Let's dig into the code

  * UI
    * > Traditionally, shiny requires you to own both the UI and server definitions
    *
      ```r
        ui <- bslib::page_sidebar(
          sidebar = bslib::sidebar(
            sliderInput(inputId = "bin_count", ...)
          ),
          plotOutput(outputId = "distPlot")
        )
      ```

    * R owns both the UI definition and reactive computation
      * > For an app like this, the R UI is wonderful. bslib gets us from nothing to something to be proud of in just a small set of functions.
      * > But when a request comes in for a distinctive interface, richer interaction, or a component from a modern design system...
        > You're suddenly authoring an up-hill battle of markup, styling, and interactions details.

      * > But you want to keep Shiny's reactive data model... Its your domain expertise!
      * >
      * > So... I do not want to replace Shiny. I want to keep Shiny for reactive computation while using a modern UI ecosystem (such as react.js) for the interface.


* "Wait... what?" - full-bleed meme, straight after the React.js divider.
  The big question in the room is asked the moment React is proposed, not
  twelve slides later, so the rest of section 02 is the answer to it.
  * "You want me to write JavaScript?!?"
  * Joe: "Shiny authors shouldn't need to write JavaScript"
    * Barret: I believe this still holds true!
  * > Agents today have far more examples of mainstream React patterns than custom Shiny UI apps. I trust any frontier model to write react.js code better than I can
    * > That narrow IDs and JSON contract makes the client boundary practical to review and maintain
  * > You need to be able to describe your UI and review the result.

* React.js
  * "The library for web and native user interfaces"
  * "... build user interfaces out of individual pieces called components"
  * A component is a function that returns markup

  * UI is assembled given data's state
    * > React is _REALLY_ good at just taking JSON at mapping data to UI
    * > Don't worry about managing the transitions from one data state to another!

  * DEMO SLIDE + its code

  (The mechanics run uninterrupted - what it is, how you write it, how it
   thinks, watch it work, here is the whole file - and *then* the two "why"
   slides land together as the on-ramp to the mark.)

  * Why React?
    * > MASSIVE ecosystem of proven components ready for production environments
    * > ... dwarfs what R/python readily has available
    * > show off existing libraries

  * Why Shiny + React?
    * Hand-rolled HTML and JavaScript in Shiny
    * Use the proper tool for the job
      * > happy to do car maintenance with a multitool - but the proper tool
        saves time, effort, and the skin on your knuckles
    * AI excels at building well-known frameworks

* Animation: shiny + react. Hex logo creation slide


* `shinyreact`
  * "Shiny UI infrastructure for React-based component rendering"
    * > With `shinyreact`, the Shiny server contains only reactive data computation, and the UI is a React client you own. `shinyreact` provides the bridge between the two and ships zero UI components itself.
  * Reactive Model
    * > Pure functional programming makes logic easy to reason about as apps scale up in complexity.
    * > This make both of these frameworks a joy to work in
  * Build the whole UI from the ground up using react / typescript
    * > Experimental package for the brave few

* Old Faithful w/ `shinyreact`
  * > Let's re-imagine our Old Faithful app using `shinyreact`
    * Original
      ```r
      x <- faithful$waiting
      server <- function(input, output) {
        output$distPlot <-
          renderPlot({
            breaks <- seq(min(x), max(x), length.out = input$bin_count + 1)
            hist(x, breaks = breaks)
          })
      }
      ```
      * `input$bin_count` -> `breaks` -> `hist()` -> `renderPlot()`
        * > We can see the single input value `bin_count` being used to calculate `breaks`
        * > This value is then fed into `hist()` with the specified breaks to produce a histogram of the data

    * shinyreact
      * > The reactive computation is unchanged. What has changed is the value sent by the server.
      * `input$bin_count` -> `breaks` -> `bins` -> `reactive_output()`
        ```r
        x <- faithful$waiting
        server <- function(input, output) {
          output$distPlot <-
            shinyreact::reactive_output({ # <<
              breaks <- seq(min(x), max(x), length.out = input$bin_count + 1)
              bins <- hist(x, breaks = breaks, plot = FALSE) # <<
              bins[c("breaks", "counts")] # <<
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
          sliderInput(inputId = "bin_count", ...)
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
          const [binCount, setBinCount] = useShinyInput<number>("bin_count", 30);
          const bins = useShinyOutputValue<HistData | null>("distPlot", null);

          return (
            <main className="layout">
              <aside className="sidebar">
                <label htmlFor="bin_count">Number of bins:</label>
                <input  // # <<
                  id="bin_count"
                  type="range"
                  value={binCount}
                  onChange={(e) => setBinCount(Number(e.target.value))}
                />
              </aside>

              <section className="panel">
                <div className="chart">
                  <Histogram bins={bins} /> // # <<
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

* Test coverage!
  * > Agents today have far more examples of mainstream React patterns than custom Shiny UI apps. I trust any frontier model to write react.js code better than I can
    * > That narrow IDs and JSON contract makes the client boundary practical to review and maintain
  * > You need to be able to describe your UI and review the result.
  * within server - testServer() (R) / test_server() + local_server fixture (py-shiny 1.8.0)
    * set inputs, confirm output values - no browser
  * from server to client - wire_tap
    * assert shinyreact messages within the websocket
  * within client - js unit tests
    * _Agent's choice_
  * confirm client - _features.md_
    * nested list of features that you can read and other agents can confirm

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
  * Q: Can I use existing outputs?
    * A: Yup. Use regular render methods, just like normal. But pair them with `<ShinyOutput id="distPlot" />` in your React.js code. Do not reinvent the wheel
    * A: Then your UI app is more about layout than it is Outputs
