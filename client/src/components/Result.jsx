export default function Result({ result }) {
  const {
    original_image,
    solved_image,
    solved_board,
    original_board,
    solve_time_ms,
  } = result;

  return (
    <div className="mt-10 flex flex-col gap-8">
      {/* Stats bar */}
      <div className="flex gap-6 justify-center">
        <div className="text-center">
          <p className="text-2xl font-bold text-green-600">✅</p>
          <p className="text-xs text-gray-500 mt-1">Solved</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-gray-800">{solve_time_ms}ms</p>
          <p className="text-xs text-gray-500 mt-1">Solve time</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-gray-800">
            {original_board.flat().filter((v) => v !== 0).length}
          </p>
          <p className="text-xs text-gray-500 mt-1">Clues given</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-blue-600">
            {solved_board.flat().filter((v) => v !== 0).length -
              original_board.flat().filter((v) => v !== 0).length}
          </p>
          <p className="text-xs text-gray-500 mt-1">Cells filled</p>
        </div>
      </div>

      {/* Images */}
      <div className="grid grid-cols-2 gap-6">
        <div className="flex flex-col items-center gap-2">
          <p className="text-sm font-semibold text-gray-600">Original</p>
          <img
            src={`data:image/png;base64,${original_image}`}
            alt="original"
            className="w-full rounded-xl border border-gray-200 shadow-sm"
          />
        </div>
        <div className="flex flex-col items-center gap-2">
          <p className="text-sm font-semibold text-green-600">Solved</p>
          <img
            src={`data:image/png;base64,${solved_image}`}
            alt="solved"
            className="w-full rounded-xl border border-green-200 shadow-sm"
          />
        </div>
      </div>

      {/* Board grid */}
      <div className="flex flex-col items-center gap-2">
        <p className="text-sm font-semibold text-gray-600">Solution</p>
        <div
          className="grid grid-cols-9 border-2 border-gray-800 
                        rounded-lg overflow-hidden"
        >
          {solved_board.map((row, r) =>
            row.map((val, c) => {
              const isClue = original_board[r][c] !== 0;
              const borderR = (r + 1) % 3 === 0 && r !== 8;
              const borderC = (c + 1) % 3 === 0 && c !== 8;

              return (
                <div
                  key={`${r}-${c}`}
                  className={`
                    w-9 h-9 flex items-center justify-center text-sm
                    font-mono select-none
                    ${
                      isClue
                        ? "bg-gray-100 text-gray-900 font-bold"
                        : "bg-white text-green-600 font-semibold"
                    }
                    ${borderR ? "border-b-2 border-b-gray-800" : "border-b border-b-gray-200"}
                    ${borderC ? "border-r-2 border-r-gray-800" : "border-r border-r-gray-200"}
                  `}
                >
                  {val !== 0 ? val : ""}
                </div>
              );
            }),
          )}
        </div>
      </div>
    </div>
  );
}
