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
    <div className="min-h-screen bg-gray-100 p-6 flex flex-col items-center">
      <h1 className="text-4xl font-bold mb-8">📄 NeuraDocs</h1>

      <div className="bg-white p-6 rounded-lg shadow max-w-lg w-full">
        <label className="block mb-4 font-semibold">Upload a PDF</label>

        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="mb-4 border p-2 w-full rounded"
        />

        <button
          onClick={uploadPDF}
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition"
        >
          {loading ? "Extracting..." : "Extract PDF"}
        </button>
      </div>

      {/* Display Chunks */}
      <div className="max-w-3xl w-full mt-10">
        {chunks.length > 0 && (
          <h2 className="text-2xl font-bold mb-4">Extracted Chunks</h2>
        )}

        <div className="space-y-4">
          {chunks.map((chunk, index) => (
            <div key={index} className="bg-white p-4 rounded shadow text-gray-800">
              <p>{chunk}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
