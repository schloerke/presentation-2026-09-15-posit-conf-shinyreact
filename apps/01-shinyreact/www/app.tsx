// SCRATCH / NOT COMMITTED — a TSX sketch of what www/app.js would look like
// behind a Vite build. Same ids, same hooks, same servers; nothing in app.py,
// app-core.py, or app.R changes. Delete this directory when you're done.
//
// Under the repo's Vite convention (see examples/04-shadcn), React comes from
// the "react" import (externalized to window.shinyreact.React by the Vite
// config) and the hooks are destructured off the window global. TypeScript
// needs that global declared — in a real setup this block would live in a
// shared shinyreact.d.ts rather than at the top of the entry file.

declare global {
  interface Window {
    shinyreact: {
      React: typeof import("react");
      ReactDOM: typeof import("react-dom/client");
      useShinyInput: <T>(
        id: string,
        defaultValue: T,
        options?: { debounceMs?: number; priority?: "event" | "immediate" },
      ) => [T, (value: T) => void];
      useShinyOutputValue: <T>(id: string, defaultValue: T) => T;
      useShinyOutputStatus: (
        id: string,
      ) => "pending" | "ready" | "recalculating" | "error";
      useShinyInitialized: () => boolean;
    };
  }
}

const {
  useShinyInput,
  useShinyOutputValue,
  useShinyOutputStatus,
  useShinyInitialized,
} = window.shinyreact;

// --- the server contract, written down ------------------------------------
//
// This is the part the .js version cannot express: `dist_data` is a
// reactive_output on three different servers (Express, Core, R), and this
// interface is the only place the shape they agree on is stated. `breaks` is
// always `counts.length + 1` long. R needs I() to keep these as arrays when
// bins = 1 — a violation of *this* type was the bug that caused.

interface HistData {
  breaks: number[];
  counts: number[];
}

// --- histogram chart -------------------------------------------------------

const W = 620;
const H = 380;
const M = { top: 16, right: 16, bottom: 48, left: 56 };
const PLOT_W = W - M.left - M.right;
const PLOT_H = H - M.top - M.bottom;

// Round `max` up to a friendly axis top, using a 1/2/5 × 10^n tick step.
function yTicks(max: number): { top: number; ticks: number[] } {
  const raw = Math.max(max, 1) / 4;
  const mag = Math.pow(10, Math.floor(Math.log10(raw)));
  const step = [1, 2, 5, 10].map((m) => m * mag).find((s) => s >= raw)!;
  const top = Math.ceil(max / step) * step;
  const ticks: number[] = [];
  for (let v = 0; v <= top; v += step) ticks.push(v);
  return { top, ticks };
}

function xTicks(lo: number, hi: number): number[] {
  const step = 10;
  const ticks: number[] = [];
  for (let v = Math.ceil(lo / step) * step; v <= hi; v += step) ticks.push(v);
  return ticks;
}

function Histogram({ data }: { data: HistData }) {
  const { breaks, counts } = data;
  const lo = breaks[0];
  const hi = breaks[breaks.length - 1];
  const { top, ticks } = yTicks(Math.max(...counts));

  const x = (v: number) => M.left + ((v - lo) / (hi - lo)) * PLOT_W;
  const y = (v: number) => M.top + PLOT_H - (v / top) * PLOT_H;

  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      width="100%"
      role="img"
      aria-label={`Histogram of Old Faithful waiting times in ${counts.length} bins`}
    >
      {ticks.map((t) => (
        <g key={`y${t}`}>
          <line
            x1={M.left}
            x2={M.left + PLOT_W}
            y1={y(t)}
            y2={y(t)}
            stroke="#e5e5e5"
          />
          <text
            x={M.left - 10}
            y={y(t)}
            textAnchor="end"
            dominantBaseline="middle"
            fontSize={12}
            fill="#666"
          >
            {t}
          </text>
        </g>
      ))}

      {counts.map((count, i) => {
        const x0 = x(breaks[i]);
        const x1 = x(breaks[i + 1]);
        return (
          <rect
            key={i}
            x={x0}
            width={Math.max(x1 - x0 - 1, 1)}
            y={y(count)}
            height={M.top + PLOT_H - y(count)}
            fill="#447099"
          />
        );
      })}

      <line
        x1={M.left}
        x2={M.left + PLOT_W}
        y1={M.top + PLOT_H}
        y2={M.top + PLOT_H}
        stroke="#888"
      />
      {xTicks(lo, hi).map((t) => (
        <text
          key={`x${t}`}
          x={x(t)}
          y={M.top + PLOT_H + 20}
          textAnchor="middle"
          fontSize={12}
          fill="#666"
        >
          {t}
        </text>
      ))}

      <text
        x={M.left + PLOT_W / 2}
        y={H - 8}
        textAnchor="middle"
        fontSize={13}
        fill="#333"
      >
        Waiting time to next eruption (minutes)
      </text>
      <text
        transform={`translate(16 ${M.top + PLOT_H / 2}) rotate(-90)`}
        textAnchor="middle"
        fontSize={13}
        fill="#333"
      >
        Frequency
      </text>
    </svg>
  );
}

// --- app -------------------------------------------------------------------

export default function App() {
  const initialized = useShinyInitialized();
  const [bins, setBins] = useShinyInput<number>("bins", 30);
  const data = useShinyOutputValue<HistData | null>("dist_data", null);
  const status = useShinyOutputStatus("dist_data");

  if (!initialized) return null;

  return (
    <main className="layout">
      <aside className="sidebar">
        <label htmlFor="bins">Number of bins:</label>
        <input
          id="bins"
          type="range"
          min={1}
          max={50}
          value={bins}
          onChange={(e) => setBins(Number(e.target.value))}
        />
        <output htmlFor="bins" className="bins-value">
          {bins}
        </output>
      </aside>

      <section className="panel">
        <h1>Hello Shiny!</h1>
        {/* Keep the chart mounted while the server recomputes — only show the
            placeholder before the first value has ever arrived. */}
        {data ? (
          <div className={status === "recalculating" ? "recalculating" : ""}>
            <Histogram data={data} />
          </div>
        ) : (
          <div className="placeholder">Loading…</div>
        )}
      </section>
    </main>
  );
}
