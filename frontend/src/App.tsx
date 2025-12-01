import { useState } from "react";

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [chunks, setChunks] = useState([]);
  const [loading, setLoading] = useState(false);

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [chatLoading, setChatLoading] = useState(false);

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
      if (data.error) throw new Error(data.error);

      setChunks(data.chunks || []);
      alert("PDF uploaded & saved to Pinecone!");
    } catch (err) {
      alert("Error extracting PDF");
    }

    setLoading(false);
  };

  const askQuestion = async () => {
    if (!question.trim()) return;

    setChatLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: question }),
      });

      const data = await res.json();
      setAnswer(data.answer || "No answer returned.");
    } catch (err) {
      alert("Error asking question");
    }

    setChatLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="w-full bg-white shadow px-10 py-5">
        <h1 className="text-3xl font-bold">📘 NeuraDocs</h1>
      </header>

      <div className="grid grid-cols-3 gap-6 p-8">
        {/* UPLOAD PANEL */}
        <div className="bg-white p-6 rounded-xl shadow-md col-span-1">
          <h2 className="text-xl font-semibold mb-4">Upload PDF</h2>

          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />

          {file && <p className="mt-2">📌 {file.name}</p>}

          <button
            onClick={uploadPDF}
            disabled={loading}
            className="w-full mt-4 bg-blue-600 text-white py-2 rounded-lg"
          >
            {loading ? "Extracting..." : "Extract PDF"}
          </button>

          <hr className="my-6" />

          <h2 className="text-xl font-semibold mb-3">Ask PDF</h2>

          <textarea
            rows={3}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask anything..."
            className="w-full p-3 border rounded-lg"
          />

          <button
            onClick={askQuestion}
            disabled={chatLoading}
            className="w-full mt-4 bg-green-600 text-white py-2 rounded-lg"
          >
            {chatLoading ? "Thinking..." : "Ask AI"}
          </button>
        </div>

        {/* RIGHT SIDE */}
        <div className="col-span-2 space-y-6">
          {/* CHUNKS */}
          <div className="bg-white p-6 rounded-xl shadow-md max-h-[350px] overflow-y-auto">
            <h2 className="text-2xl font-bold">Extracted Chunks ({chunks.length})</h2>

            {chunks.map((chunk, i) => (
              <div key={i} className="p-3 mt-3 border rounded bg-gray-50">
                {chunk}
              </div>
            ))}

            {!chunks.length && <p>No chunks yet.</p>}
          </div>

          {/* ANSWER */}
          <div className="bg-white p-6 rounded-xl shadow-md">
            <h2 className="text-2xl font-bold">AI Answer</h2>
            {answer ? (
              <p className="mt-3">{answer}</p>
            ) : (
              <p className="text-gray-500">Ask a question to get an answer.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
