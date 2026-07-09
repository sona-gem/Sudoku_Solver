import { useState } from "react";
import Upload from "./components/Upload";
import Result from "./components/Result";

export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-2xl font-bold text-gray-900">
            Sudoku OCR Solver
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Upload a printed Sudoku puzzle image to solve it instantly
          </p>
        </div>
      </header>

      {/* Main */}
      <main className="max-w-4xl mx-auto px-6 py-10">
        <Upload
          setResult={setResult}
          setLoading={setLoading}
          setError={setError}
          loading={loading}
        />

        {error && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700 text-sm font-medium">❌ {error}</p>
          </div>
        )}

        {loading && (
          <div className="mt-10 flex flex-col items-center gap-3">
            <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-gray-500 text-sm">
              Detecting grid, recognizing digits, solving...
            </p>
          </div>
        )}

        {result && !loading && <Result result={result} />}
      </main>

      {/* Footer */}
      <footer className="text-center py-6 text-xs text-gray-400">
        Built with OpenCV · TensorFlow · Flask · React
      </footer>
    </div>
  );
}
