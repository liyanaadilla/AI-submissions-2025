import React from 'react';
import { SavedDocument } from '../types';
import { BarChart, FileCheck, AlertTriangle, Activity } from 'lucide-react';

interface DashboardProps {
  documents: SavedDocument[];
}

export const Dashboard: React.FC<DashboardProps> = ({ documents }) => {
  const totalDocs = documents.length;
  const highRiskDocs = documents.filter(d => d.riskDegree === 'High').length;
  const avgConfidence = totalDocs > 0 
    ? (documents.reduce((acc, doc) => acc + doc.overallConfidence, 0) / totalDocs * 100).toFixed(1) 
    : '0';

  return (
    <div className="max-w-7xl mx-auto w-full animate-in fade-in duration-500">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Dashboard Overview</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-blue-100 text-blue-600 rounded-lg">
            <FileCheck size={24} />
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900">{totalDocs}</div>
            <div className="text-sm text-gray-500">Processed Documents</div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-red-100 text-red-600 rounded-lg">
            <AlertTriangle size={24} />
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900">{highRiskDocs}</div>
            <div className="text-sm text-gray-500">High Risk Flags</div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-green-100 text-green-600 rounded-lg">
            <Activity size={24} />
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900">{avgConfidence}%</div>
            <div className="text-sm text-gray-500">Average AI Confidence</div>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
        <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <BarChart size={18} />
          Recent Activity
        </h3>
        {documents.length === 0 ? (
          <div className="h-40 flex items-center justify-center text-gray-400 italic">
            No data available yet. Upload documents to see activity.
          </div>
        ) : (
          <div className="space-y-4">
             {documents.slice(-5).reverse().map(doc => (
               <div key={doc.id} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg border border-transparent hover:border-gray-100 transition-colors">
                 <div>
                   <div className="font-medium text-gray-900">{doc.documentType}</div>
                   <div className="text-xs text-gray-500">{doc.timestamp}</div>
                 </div>
                 <div className={`text-xs px-2 py-1 rounded-full font-bold
                    ${doc.riskDegree === 'High' ? 'bg-red-100 text-red-700' : 
                      doc.riskDegree === 'Medium' ? 'bg-yellow-100 text-yellow-700' : 'bg-green-100 text-green-700'}
                 `}>
                   {doc.riskDegree} Risk
                 </div>
               </div>
             ))}
          </div>
        )}
      </div>
    </div>
  );
};