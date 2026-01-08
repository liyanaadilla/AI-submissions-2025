import React, { useState, useEffect } from 'react';
import { ProcessingResult, ExtractedField } from '../types';
import { AlertTriangle, CheckCircle, ShieldAlert, FileText, Globe, ChevronDown, ChevronUp, AlignLeft, Copy, Save, Edit2 } from 'lucide-react';

interface ResultViewProps {
  result: ProcessingResult;
  imageUrl: string;
  onReset: () => void;
  onSave: (updatedResult: ProcessingResult) => void;
}

export const ResultView: React.FC<ResultViewProps> = ({ result, imageUrl, onReset, onSave }) => {
  const [showFullText, setShowFullText] = useState(false);
  
  // Local state to manage edits before saving
  const [editableResult, setEditableResult] = useState<ProcessingResult>(result);

  // Sync state when prop changes (e.g. selecting a different doc from history)
  useEffect(() => {
    setEditableResult(result);
  }, [result]);

  // Auto-expand raw text if confidence is low (Risk is High or Medium)
  useEffect(() => {
    if (result.riskDegree === 'High' || result.riskDegree === 'Medium' || result.overallConfidence < 0.7) {
      setShowFullText(true);
    }
  }, [result]);

  const handleFieldChange = (index: number, newValue: string) => {
    const newFields = [...editableResult.fields];
    newFields[index] = { ...newFields[index], value: newValue, validationError: undefined }; // Clear error on manual edit? Optional choice.
    setEditableResult({ ...editableResult, fields: newFields });
  };

  const handleRawTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setEditableResult({ ...editableResult, rawText: e.target.value });
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'High': return 'bg-red-100 text-red-800 border-red-200';
      case 'Medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'Low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const copyToClipboard = () => {
    if (editableResult.rawText) {
      navigator.clipboard.writeText(editableResult.rawText);
    }
  };

  return (
    <div className="w-full h-full flex flex-col lg:flex-row gap-6 p-4">
      {/* Left Column: Image Preview */}
      <div className="w-full lg:w-1/2 flex flex-col gap-4">
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200 h-[600px] flex flex-col">
          <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <FileText size={16} /> Original Document
          </h3>
          <div className="flex-1 bg-gray-100 rounded-lg overflow-hidden border border-gray-200 relative">
             <img 
               src={imageUrl} 
               alt="Scanned Document" 
               className="w-full h-full object-contain"
             />
          </div>
        </div>
      </div>

      {/* Right Column: Data Extraction */}
      <div className="w-full lg:w-1/2 flex flex-col gap-4">
        {/* Summary Card */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h2 className="text-xl font-bold text-gray-900">{editableResult.documentType}</h2>
              <div className="flex items-center gap-2 mt-1 text-sm text-gray-500">
                <Globe size={14} />
                <span>Detected Language: <span className="font-medium text-gray-700">{editableResult.language}</span></span>
              </div>
            </div>
            <div className={`px-3 py-1 rounded-full text-sm font-bold border flex items-center gap-2 ${getRiskColor(editableResult.riskDegree)}`}>
              <ShieldAlert size={16} />
              Risk Degree: {editableResult.riskDegree}
            </div>
          </div>
          <p className="text-gray-600 text-sm leading-relaxed bg-gray-50 p-3 rounded-lg border border-gray-100">
            {editableResult.summary}
          </p>
        </div>

        {/* Fields List & Raw Text Container */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden flex-1 flex flex-col">
          <div className="px-6 py-4 border-b border-gray-100 bg-gray-50 flex justify-between items-center shrink-0">
            <h3 className="font-semibold text-gray-800">Extracted Knowledge</h3>
            <span className="text-xs text-gray-500">Confidence Score: {(editableResult.overallConfidence * 100).toFixed(0)}%</span>
          </div>
          
          {/* Scrollable Fields */}
          <div className={`divide-y divide-gray-100 overflow-y-auto ${editableResult.fields.length === 0 ? 'h-32 flex items-center justify-center' : 'flex-1 min-h-[150px]'}`}>
            {editableResult.fields.length === 0 ? (
              <div className="text-center text-gray-400 text-sm italic p-4">
                No specific fields were extracted. 
                <br/>Check the raw text below.
              </div>
            ) : (
              editableResult.fields.map((field, idx) => (
                <div key={idx} className="p-4 hover:bg-gray-50 transition-colors group">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <label className="text-xs font-bold text-gray-400 uppercase tracking-wider block mb-1">
                        {field.key.replace(/_/g, ' ')}
                      </label>
                      <div className="flex items-center gap-2 relative">
                        <input 
                          type="text" 
                          value={field.value}
                          onChange={(e) => handleFieldChange(idx, e.target.value)}
                          className={`text-sm font-medium text-gray-900 bg-transparent border-b border-dashed border-gray-300 focus:border-blue-500 focus:bg-blue-50 focus:outline-none w-full py-1 pr-6
                            ${field.validationError ? 'text-red-600 border-red-300' : ''}
                          `}
                        />
                        <Edit2 size={10} className="absolute right-0 text-gray-400 opacity-0 group-hover:opacity-100 pointer-events-none" />
                      </div>
                    </div>
                    
                    {/* Validation Status Indicator */}
                    <div className="ml-4 flex flex-col items-end gap-1">
                      {field.validationError ? (
                        <div className="flex items-center gap-1 text-red-600 text-xs font-medium bg-red-50 px-2 py-1 rounded">
                          <AlertTriangle size={12} />
                          {field.validationError}
                        </div>
                      ) : (
                          <div className="flex items-center gap-1 text-green-600 text-xs font-medium bg-green-50 px-2 py-1 rounded">
                            <CheckCircle size={12} />
                            Valid
                          </div>
                      )}
                      <span className={`text-[10px] ${field.confidence < 0.7 ? 'text-orange-500' : 'text-gray-400'}`}>
                        {(field.confidence * 100).toFixed(0)}% conf.
                      </span>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Raw Text Section - Collapsible & Editable */}
          <div className="border-t border-gray-200">
            <button 
              onClick={() => setShowFullText(!showFullText)}
              className="w-full px-6 py-3 flex items-center justify-between bg-gray-50 hover:bg-gray-100 transition-colors"
            >
              <div className="flex items-center gap-2 text-xs font-bold text-gray-600 uppercase tracking-wider">
                <AlignLeft size={14} />
                Computerized Text (OCR)
                {editableResult.overallConfidence < 0.7 && <span className="ml-2 text-[10px] bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded-full">Review Needed</span>}
              </div>
              <div className="flex items-center gap-1">
                 {showFullText ? <ChevronUp size={14} className="text-gray-500" /> : <ChevronDown size={14} className="text-gray-500" />}
              </div>
            </button>
            
            {showFullText && (
               <div className="p-4 bg-gray-50 border-t border-gray-100 relative group animate-in slide-in-from-top-2 duration-200">
                 <button 
                   onClick={copyToClipboard}
                   className="absolute top-2 right-2 p-1.5 bg-white border border-gray-200 rounded text-gray-500 hover:text-blue-600 shadow-sm opacity-0 group-hover:opacity-100 transition-opacity z-10"
                   title="Copy Text"
                 >
                   <Copy size={12} />
                 </button>
                 <textarea
                   value={editableResult.rawText}
                   onChange={handleRawTextChange}
                   className="w-full text-xs font-mono text-gray-700 leading-relaxed min-h-[150px] max-h-[300px] p-3 bg-white rounded border border-gray-200 focus:border-blue-500 focus:outline-none resize-y"
                 />
               </div>
            )}
          </div>

          {/* Footer Actions */}
          <div className="p-4 bg-white border-t border-gray-200 flex justify-end gap-3 shrink-0 z-10">
             <button 
               onClick={onReset}
               className="px-4 py-2 text-gray-600 text-sm font-medium hover:bg-gray-100 rounded-lg transition-colors"
             >
               Back / Discard
             </button>
             <button 
               onClick={() => onSave(editableResult)}
               className="px-6 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 shadow-sm transition-all hover:scale-105 flex items-center gap-2"
             >
               <Save size={16} />
               Save Changes
             </button>
          </div>
        </div>
      </div>
    </div>
  );
};