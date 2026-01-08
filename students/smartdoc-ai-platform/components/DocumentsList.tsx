import React from 'react';
import { SavedDocument } from '../types';
import { FileText, MoreVertical, Search, Filter, ArrowRight } from 'lucide-react';

interface DocumentsListProps {
  documents: SavedDocument[];
  title?: string;
  filterHighRisk?: boolean;
  onSelect: (doc: SavedDocument) => void;
}

export const DocumentsList: React.FC<DocumentsListProps> = ({ documents, title = "Documents History", filterHighRisk = false, onSelect }) => {
  const filteredDocs = filterHighRisk 
    ? documents.filter(d => d.riskDegree === 'High' || d.riskDegree === 'Medium') 
    : documents;

  return (
    <div className="w-full max-w-7xl mx-auto animate-in fade-in duration-500">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
        <div className="flex gap-2">
           <div className="relative">
             <Search size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
             <input type="text" placeholder="Search docs..." className="pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
           </div>
           <button className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-gray-600">
             <Filter size={18} />
           </button>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-600">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-4 font-semibold text-gray-900">Document</th>
                <th className="px-6 py-4 font-semibold text-gray-900">Type</th>
                <th className="px-6 py-4 font-semibold text-gray-900">Date Processed</th>
                <th className="px-6 py-4 font-semibold text-gray-900">Confidence</th>
                <th className="px-6 py-4 font-semibold text-gray-900">Risk Status</th>
                <th className="px-6 py-4 font-semibold text-gray-900 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filteredDocs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-gray-400 italic">
                    {filterHighRisk ? "No high risk documents in queue." : "No documents found in history."}
                  </td>
                </tr>
              ) : (
                filteredDocs.map((doc) => (
                  <tr 
                    key={doc.id} 
                    onClick={() => onSelect(doc)}
                    className="hover:bg-blue-50 transition-colors cursor-pointer group"
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-blue-100 text-blue-600 rounded-lg group-hover:bg-blue-200 transition-colors">
                          <FileText size={18} />
                        </div>
                        <span className="font-medium text-gray-900 truncate max-w-[150px]">{doc.fileName}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">{doc.documentType}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{doc.timestamp}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                          <div 
                            className={`h-full rounded-full ${doc.overallConfidence > 0.8 ? 'bg-green-500' : doc.overallConfidence > 0.5 ? 'bg-yellow-500' : 'bg-red-500'}`} 
                            style={{ width: `${doc.overallConfidence * 100}%` }}
                          />
                        </div>
                        <span className="text-xs">{(doc.overallConfidence * 100).toFixed(0)}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                       <span className={`px-2.5 py-1 rounded-full text-xs font-bold inline-flex items-center gap-1
                         ${doc.riskDegree === 'High' ? 'bg-red-100 text-red-700' : 
                           doc.riskDegree === 'Medium' ? 'bg-yellow-100 text-yellow-700' : 'bg-green-100 text-green-700'}
                       `}>
                         {doc.riskDegree}
                       </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2 text-gray-400">
                        <ArrowRight size={16} className="opacity-0 group-hover:opacity-100 transition-opacity text-blue-500" />
                        <MoreVertical size={18} className="hover:text-gray-600" />
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};