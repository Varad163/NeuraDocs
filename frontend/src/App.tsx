import { useState } from "react";

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [chunks, setChunks] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const uploadPDF = async () => {
    if (!file) return alert("Please select a PDF");

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/extract", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      setChunks(data.chunks || []);
    } catch (error) {
      console.error(error);
      alert("Error extracting PDF");
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 via-slate-200 to-slate-300 flex flex-col items-center">

      {/* HEADER */}
      <header className="w-full bg-white/80 backdrop-blur-md shadow-sm border-b border-gray-300 py-4 px-10 flex items-center">
        <h1 className="text-4xl font-bold text-gray-900 tracking-tight">📄 NeuraDocs</h1>
      </header>

      {/* MAIN FULL-WIDTH AREA */}
      <div className="w-full max-w-[1800px] flex flex-row gap-10 p-10">

        {/* LEFT PANEL (BIG AND BEAUTIFUL) */}
        <div className="w-[400px] bg-white rounded-3xl shadow-2xl p-8 border border-gray-200">
          <h2 className="text-2xl font-semibold mb-6">Upload Your PDF</h2>

          <div className="flex flex-col gap-4">
            <label className="w-full">
              <input
                type="file"
                accept="application/pdf"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="block w-full text-sm text-gray-800 file:mr-4 file:py-2 file:px-4 
                file:rounded-lg file:border-0 file:text-sm file:font-semibold
                file:bg-blue-600 file:text-white hover:file:bg-blue-700 cursor-pointer"
              />
            </label>

            {file && (
              <p className="text-gray-700 font-medium mt-2">
                📌 <span className="font-semibold">{file.name}</span>
              </p>
            )}

            <button
              onClick={uploadPDF}
              className="w-full mt-4 bg-blue-600 text-white py-3 rounded-xl font-semibold text-lg 
              hover:bg-blue-700 active:scale-95 transition transform shadow-md"
            >
              {loading ? "Extracting..." : "Extract PDF"}
            </button>
          </div>
        </div>

        {/* RIGHT PANEL — FULL WIDTH */}
        <div className="flex-1 bg-white rounded-3xl shadow-xl p-8 border border-gray-200 overflow-y-auto h-[80vh]">
          <h2 className="text-3xl font-semibold mb-6 text-gray-900">
            Extracted Chunks {chunks.length > 0 && `(${chunks.length})`}
          </h2>

          {chunks.length === 0 && (
            <p className="text-gray-600 text-lg">Upload a PDF to view extracted text chunks.</p>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {chunks.map((chunk, index) => (
              <div
                key={index}
                className="bg-gray-50 p-6 rounded-2xl shadow-md border border-gray-200 hover:shadow-xl transition"
              >
                <p className="text-gray-800 leading-relaxed whitespace-pre-wrap text-lg">
                  {chunk}
                </p>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}

export default App;
