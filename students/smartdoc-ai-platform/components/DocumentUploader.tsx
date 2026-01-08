import React, { useCallback, useState } from 'react';
import { UploadCloud, FileText, Camera } from 'lucide-react';

interface DocumentUploaderProps {
  onUpload: (file: File) => void;
}

export const DocumentUploader: React.FC<DocumentUploaderProps> = ({ onUpload }) => {
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onUpload(e.dataTransfer.files[0]);
    }
  }, [onUpload]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onUpload(e.target.files[0]);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto mt-10">
      <div 
        className={`relative flex flex-col items-center justify-center w-full h-80 border-3 border-dashed rounded-2xl transition-all duration-200 ease-in-out cursor-pointer overflow-hidden
          ${dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-white hover:bg-gray-50 hover:border-gray-400'}
        `}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => document.getElementById('file-upload')?.click()}
      >
        <div className="flex flex-col items-center justify-center pt-5 pb-6 text-center px-4">
          <div className="p-4 bg-blue-100 rounded-full mb-4 text-blue-600">
            <UploadCloud size={40} />
          </div>
          <p className="mb-2 text-xl font-semibold text-gray-700">
            Drop your document here
          </p>
          <p className="mb-4 text-sm text-gray-500">
            Support for scanned PDFs, Images (JPG, PNG)
          </p>
          <div className="flex gap-3">
             <button className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors shadow-md">
              Select File
            </button>
            
          </div>
        </div>
        <input 
          id="file-upload" 
          type="file" 
          className="hidden" 
          accept="image/*"
          onChange={handleChange} 
        />
        <input 
          id="camera-upload" 
          type="file" 
          className="hidden" 
          accept="image/*"
          capture="environment"
          onChange={handleChange} 
        />
      </div>
      
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
        <div className="p-4 bg-white rounded-xl shadow-sm border border-gray-100">
          <div className="font-semibold text-gray-800">1. Upload</div>
          <div className="text-xs text-gray-500 mt-1">Images or Scans</div>
        </div>
        <div className="p-4 bg-white rounded-xl shadow-sm border border-gray-100">
          <div className="font-semibold text-gray-800">2. AI Analysis</div>
          <div className="text-xs text-gray-500 mt-1">OCR & Validation</div>
        </div>
        <div className="p-4 bg-white rounded-xl shadow-sm border border-gray-100">
          <div className="font-semibold text-gray-800">3. Verification</div>
          <div className="text-xs text-gray-500 mt-1">Human-in-the-loop</div>
        </div>
      </div>
    </div>
  );
};
