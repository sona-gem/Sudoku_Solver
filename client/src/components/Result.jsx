export default function Result({ result }) {
  const {
    original_image,
    solved_board,
    original_board,
    solve_time_ms,
  } = result;

  return (
    <div className="mt-8 flex flex-col gap-5">
      <div className="grid gap-4 md:grid-cols-3">
        <StatCard label="Solve time" value={`${solve_time_ms}ms`} icon="⏱" />
        <StatCard
          label="Clues found"
          value={original_board.flat().filter((v) => v !== 0).length}
          icon="💡"
        />
        <StatCard
          label="Cells filled"
          value={
            solved_board.flat().filter((v) => v !== 0).length -
            original_board.flat().filter((v) => v !== 0).length
          }
          icon="✓"
        />
      </div>

      <div className="grid gap-5 lg:grid-cols-[1.05fr_0.95fr]">
        <Panel title="Original Image" badge="OCR Scan">
          <img
            src={`data:image/png;base64,${original_image}`}
            alt="original"
            className="w-full rounded-lg border border-dashed border-white/10 bg-zinc-950 shadow-inner"
          />
        </Panel>

        <Panel title="Solved Solution" badge="Verified">
          <div className="overflow-hidden rounded-lg border border-white/10 bg-zinc-950 shadow-sm">
            <div className="grid grid-cols-9">
              {solved_board.map((row, r) =>
                row.map((val, c) => {
                  const isClue = original_board[r][c] !== 0;
                  const borderR = (r + 1) % 3 === 0 && r !== 8;
                  const borderC = (c + 1) % 3 === 0 && c !== 8;

                  return (
                    <div
                      key={`${r}-${c}`}
                      className={`flex h-10 items-center justify-center select-none border-b border-r text-base font-mono font-semibold ${
                        isClue ? "text-zinc-100" : "text-emerald-400"
                      } ${borderR ? "border-b-2 border-b-black" : "border-b border-b-white/10"} ${borderC ? "border-r-2 border-r-black" : "border-r border-r-white/10"}`}
                    >
                      {val !== 0 ? val : ""}
                    </div>
                  );
                }),
              )}
            </div>
          </div>
        </Panel>
      </div>
    </div>
  );
}

function StatCard({ label, value, icon }) {
  return (
    <div className="rounded-xl border border-white/10 bg-[#141414] px-4 py-3 shadow-[0_4px_14px_rgba(0,0,0,0.35)]">
      <div className="flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white/10 text-sky-300 ring-1 ring-white/10">
          <span className="text-sm font-bold">{icon}</span>
        </div>
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-zinc-500">
            {label}
          </p>
          <p className="text-lg font-bold leading-none text-white">{value}</p>
        </div>
      </div>
    </div>
  );
}

function Panel({ title, badge, children }) {
  return (
    <section className="rounded-2xl border border-white/10 bg-white/5 p-4 shadow-[0_10px_30px_rgba(0,0,0,0.35)] backdrop-blur">
      <div className="mb-3 flex items-center justify-between gap-3">
        <h2 className="text-base font-semibold text-white">{title}</h2>
        <span className="rounded-md bg-white/10 px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.18em] text-zinc-300">
          {badge}
        </span>
      </div>
      {children}
    </section>
  );
}
