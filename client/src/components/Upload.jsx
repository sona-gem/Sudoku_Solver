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
    <div className="flex flex-col items-center gap-6">
      {/* Drop zone */}
      <div
        className="w-full max-w-lg border-2 border-dashed border-gray-300 
                   rounded-xl p-10 text-center cursor-pointer
                   hover:border-blue-400 hover:bg-blue-50 transition-colors"
        onClick={() => inputRef.current.click()}
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
      >
        {preview ? (
          <img
            src={preview}
            alt="preview"
            className="max-h-64 mx-auto rounded-lg object-contain"
          />
        ) : (
          <div className="flex flex-col items-center gap-2 text-gray-400">
            <svg
              className="w-12 h-12"
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
            <p className="text-sm font-medium">
              Drop image here or click to upload
            </p>
            <p className="text-xs">JPG, PNG supported</p>
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
        className="px-8 py-3 bg-blue-600 text-white font-semibold 
                   rounded-lg hover:bg-blue-700 disabled:opacity-40 
                   disabled:cursor-not-allowed transition-colors"
      >
        {loading ? "Solving..." : "Solve Puzzle"}
      </button>
    </div>
  );
}
