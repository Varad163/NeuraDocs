import { useState } from "react";

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [chunks, setChunks] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [asking, setAsking] = useState(false);

  const uploadPDF = async () => {
    if (!file) return alert("Please select a PDF");

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    setChunks([]);
    setAnswer("");

    try {
      const res = await fetch("http://127.0.0.1:8000/extract", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`Server error: ${res.status} ${text}`);
      }

      const data = await res.json();
      setChunks(data.chunks || []);
      if (data.message) console.log("Backend:", data.message);
    } catch (error) {
      console.error(error);
      alert("Error extracting PDF — check backend terminal and CORS/network");
    }

    setLoading(false);
  };

  const askAI = async () => {
    if (!question.trim()) return alert("Please type a question");

    setAsking(true);
    setAnswer("");

    try {
      const res = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: question }),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`Server error: ${res.status} ${text}`);
      }

      const data = await res.json();
      setAnswer(data.answer || "No answer returned.");
    } catch (error) {
      console.error(error);
      setAnswer("Error contacting AI — check backend terminal.");
    }

    setAsking(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 via-slate-200 to-slate-300 flex flex-col items-center">
 
      <header className="w-full bg-white/80 backdrop-blur-md shadow-sm border-b border-gray-300 py-4 px-10 flex items-center">
        <h1 className="text-4xl font-bold text-gray-900 tracking-tight">
          📄 NeuraDocs
        </h1>
      </header>

      <div className="w-full max-w-[1800px] flex flex-row gap-10 p-10">

        <div className="w-[400px] bg-white rounded-3xl shadow-2xl p-8 border border-gray-200">
          <h2 className="text-2xl font-semibold mb-6">Upload Your PDF</h2>

          <div className="flex flex-col gap-4">
            <label>
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
              <p className="text-gray-700 font-medium">
                📌 <span className="font-semibold">{file.name}</span>
              </p>
            )}

            <button
              onClick={uploadPDF}
              className="w-full bg-blue-600 text-white py-3 rounded-xl font-semibold text-lg 
              hover:bg-blue-700 active:scale-95 transition shadow-md"
            >
              {loading ? "Extracting..." : "Extract PDF"}
            </button>
          </div>

          <div className="mt-10 pt-8 border-t border-gray-300">
            <h2 className="text-2xl font-semibold mb-4">Ask AI</h2>

            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask something about your PDF..."
              className="w-full p-4 rounded-xl border border-gray-300 shadow-sm 
              focus:ring-2 focus:ring-purple-500 outline-none text-gray-900"
              rows={4}
            />

            <button
              onClick={askAI}
              className="w-full mt-4 bg-purple-600 text-white py-3 rounded-xl font-semibold text-lg 
              hover:bg-purple-700 active:scale-95 transition shadow-md"
            >
              {asking ? "Thinking..." : "Ask AI"}
            </button>

            {answer && (
              <div className="mt-5 p-4 bg-gray-100 rounded-xl border border-gray-300 shadow-inner">
                <h3 className="text-lg font-semibold mb-2 text-gray-900">AI Response:</h3>
                <p className="text-gray-800 whitespace-pre-wrap">{answer}</p>
              </div>
            )}
          </div>
        </div>

        <div className="flex-1 bg-white rounded-3xl shadow-xl p-8 border border-gray-200 overflow-y-auto h-[85vh]">
          <h2 className="text-3xl font-semibold mb-6 text-gray-900">
            Extracted Chunks {chunks.length > 0 && `(${chunks.length})`}
          </h2>

          {chunks.length === 0 ? (
            <p className="text-gray-600 text-lg">
              Upload a PDF to view extracted text chunks.
            </p>
          ) : (
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
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
