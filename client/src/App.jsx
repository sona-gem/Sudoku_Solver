import { useState } from "react";
import Upload from "./components/Upload";
import Result from "./components/Result";

export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  return (
    <div className="min-h-screen bg-black text-zinc-100">
      <div className="fixed inset-0 -z-10 bg-[radial-gradient(circle_at_top,rgba(255,255,255,0.08),transparent_34%),linear-gradient(180deg,#121212_0%,#050505_100%)]" />

      {/* Header */}
      <header className="border-b border-white/10 bg-black/75 px-6 py-5 backdrop-blur-xl">
        <div className="mx-auto max-w-6xl">
          <h1 className="text-2xl font-semibold tracking-tight text-white">
            Sudoku OCR Solver
          </h1>
          <p className="mt-1 text-sm text-zinc-400">
            Upload a printed Sudoku puzzle image to solve it instantly
          </p>
        </div>
      </header>

      {/* Main */}
      <main className="mx-auto max-w-6xl px-6 py-8">
        <section className="rounded-2xl border border-white/10 bg-white/5 p-5 shadow-[0_20px_60px_rgba(0,0,0,0.45)] backdrop-blur">
          <Upload
            setResult={setResult}
            setLoading={setLoading}
            setError={setError}
            loading={loading}
          />
        </section>

        {error && (
          <div className="mt-5 rounded-xl border border-rose-500/20 bg-rose-500/10 p-4">
            <p className="text-sm font-medium text-rose-200">❌ {error}</p>
          </div>
        )}

        {loading && (
          <div className="mt-8 flex flex-col items-center gap-3 py-6">
            <div className="h-10 w-10 animate-spin rounded-full border-4 border-zinc-700 border-t-white" />
            <p className="text-sm text-zinc-400">
              Detecting grid, recognizing digits, solving...
            </p>
          </div>
        )}

        {result && !loading && <Result result={result} />}
      </main>

      {/* Footer */}
      <footer className="py-6 text-center text-xs text-zinc-500">
        Built with OpenCV · TensorFlow · Flask · React
      </footer>
    </div>
  );
}
