import { useState } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:5000";

export default function FileUpload() {
  const [file, setFile] = useState(null);
  const [tableData, setTableData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file first.");
      return;
    }
    
    setLoading(true);
    setError(null);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(`${BACKEND_URL}/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      setTableData(response.data.table_data);
    } catch (err) {
      setError("Error uploading file. Please try again.");
    }
    
    setLoading(false);
  };

  return (
    <div className="p-6 max-w-lg mx-auto">
      <h2 className="text-xl font-bold mb-4">Upload Image or PDF</h2>
      <input type="file" onChange={handleFileChange} className="mb-4" />
      <button 
        onClick={handleUpload} 
        className="bg-blue-500 text-white px-4 py-2 rounded"
        disabled={loading}
      >
        {loading ? "Processing..." : "Upload"}
      </button>
      {error && <p className="text-red-500 mt-2">{error}</p>}
      {tableData.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold">Extracted Table Data:</h3>
          <table className="border-collapse border border-gray-500 mt-2 w-full">
            <tbody>
              {tableData.map((row, index) => (
                <tr key={index} className="border border-gray-400">
                  <td className="p-2 border border-gray-400">{row}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
