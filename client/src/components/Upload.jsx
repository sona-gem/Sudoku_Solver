import { useState, useRef } from "react";
import axios from "axios";

export default function Upload({ setResult, setLoading, setError, loading }) {
  const [preview, setPreview] = useState(null);
  const [file, setFile] = useState(null);
  const inputRef = useRef();

  const handleFile = (f) => {
    if (!f) return;
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setResult(null);
    setError(null);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    handleFile(e.dataTransfer.files[0]);
  };

  const handleSolve = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);

    const form = new FormData();
    form.append("image", file);

    try {
      const res = await axios.post("/api/solve", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(res.data);
    } catch (err) {
      const msg = err.response?.data?.error || "Something went wrong";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-5">
      <div className="w-full max-w-6xl">
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-zinc-400">
              Input
            </p>
            <p className="mt-1 text-lg font-semibold text-white">
              Upload Sudoku Image
            </p>
          </div>
          <span className="rounded-full border border-white/10 bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-zinc-200">
            Ready to scan
          </span>
        </div>
      </div>

      {/* Drop zone */}
      <div
        className="w-full max-w-2xl cursor-pointer rounded-2xl border border-white/10 bg-white/5 p-8 text-center shadow-[0_14px_40px_rgba(0,0,0,0.45)] transition duration-200 hover:border-white/20 hover:bg-white/8"
        onClick={() => inputRef.current.click()}
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
      >
        {preview ? (
          <img
            src={preview}
            alt="preview"
            className="mx-auto max-h-64 rounded-xl object-contain ring-1 ring-white/10"
          />
        ) : (
          <div className="flex flex-col items-center gap-2 text-zinc-400">
            <svg
              className="h-12 w-12 text-zinc-300"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 
                       2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 
                       4.5M12 3v13.5"
              />
            </svg>
            <p className="text-sm font-medium text-white">
              Drop image here or click to upload
            </p>
            <p className="text-xs text-zinc-500">JPG, PNG supported</p>
          </div>
        )}
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => handleFile(e.target.files[0])}
        />
      </div>

      {/* Solve button */}
      <button
        onClick={handleSolve}
        disabled={!file || loading}
        className="rounded-xl bg-white px-8 py-3 font-semibold text-black shadow-[0_12px_30px_rgba(255,255,255,0.08)] transition hover:bg-zinc-200 disabled:cursor-not-allowed disabled:opacity-40"
      >
        {loading ? "Solving..." : "Solve Puzzle"}
      </button>
    </div>
  );
}
