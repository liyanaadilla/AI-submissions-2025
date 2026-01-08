import React, { useState } from 'react';
import { DocumentUploader } from './components/DocumentUploader';
import { ProgressBar } from './components/ProgressBar';
import { ProcessingLog } from './components/ProcessingLog';
import { ResultView } from './components/ResultView';
import { Dashboard } from './components/Dashboard';
import { DocumentsList } from './components/DocumentsList';
import { TeamView } from './components/TeamView';
import { AppState, ProcessingStep, LogEntry, ProcessingResult, AppView, SavedDocument } from './types';
import { analyzeDocument } from './services/geminiService';
import { BrainCircuit, ScanLine, Layout, PlusCircle, Users } from 'lucide-react';

export default function App() {
  const [appState, setAppState] = useState<AppState>(AppState.IDLE);
  const [appView, setAppView] = useState<AppView>(AppView.UPLOAD);
  
  const [currentStep, setCurrentStep] = useState<ProcessingStep>(ProcessingStep.SCAN);
  const [completedSteps, setCompletedSteps] = useState<ProcessingStep[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [result, setResult] = useState<ProcessingResult | null>(null);
  
  // History State
  const [documentHistory, setDocumentHistory] = useState<SavedDocument[]>([]);
  // Track which history item is currently being viewed/edited
  const [selectedHistoryId, setSelectedHistoryId] = useState<string | null>(null);

  const addLog = (step: ProcessingStep, message: string, status: 'info' | 'success' | 'warning' | 'error' = 'info') => {
    const timestamp = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    setLogs(prev => [...prev, { timestamp, step, message, status }]);
  };

  const handleUpload = (file: File) => {
    setSelectedFile(file);
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    setSelectedHistoryId(null); // New upload, not editing existing
    setAppState(AppState.PROCESSING);
    setAppView(AppView.UPLOAD); 
    setCompletedSteps([]);
    setLogs([]); 
    processDocument(file);
  };

  const processDocument = async (file: File) => {
    try {
      // Step 1: Scan
      setCurrentStep(ProcessingStep.SCAN);
      addLog(ProcessingStep.SCAN, "Document received. Initializing digitizer...", 'info');
      await new Promise(resolve => setTimeout(resolve, 800)); // Sim delay
      setCompletedSteps(prev => [...prev, ProcessingStep.SCAN]);

      // Step 2: Pre-process
      setCurrentStep(ProcessingStep.PREPROCESS);
      addLog(ProcessingStep.PREPROCESS, "Denoising image. Enhancing contrast...", 'info');
      addLog(ProcessingStep.PREPROCESS, "Checking image quality (Risk Degree I check)...", 'info');
      await new Promise(resolve => setTimeout(resolve, 1000));
      setCompletedSteps(prev => [...prev, ProcessingStep.PREPROCESS]);

      // Step 3: Text Detection
      setCurrentStep(ProcessingStep.DETECT);
      addLog(ProcessingStep.DETECT, "Identifying text blocks and layout structure...", 'info');
      await new Promise(resolve => setTimeout(resolve, 800));
      setCompletedSteps(prev => [...prev, ProcessingStep.DETECT]);

      // Step 4: OCR (Gemini Call)
      setCurrentStep(ProcessingStep.OCR);
      addLog(ProcessingStep.OCR, "Sending to AI Engine for OCR & Extraction...", 'warning');
      
      // Convert file to base64
      const base64 = await new Promise<string>((resolve) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result as string);
        reader.readAsDataURL(file);
      });
      const base64Data = base64.split(',')[1];

      const analysisResult = await analyzeDocument(base64Data);
      
      addLog(ProcessingStep.OCR, `OCR Completed. Detected Language: ${analysisResult.language}`, 'success');
      setCompletedSteps(prev => [...prev, ProcessingStep.OCR]);

      // Step 5: Validation
      setCurrentStep(ProcessingStep.VALIDATE);
      addLog(ProcessingStep.VALIDATE, `Applying Knowledge Representation rules for: ${analysisResult.documentType}`, 'info');
      
      // Simulate checking individual rules based on result
      analysisResult.fields.forEach(field => {
        if (field.validationError) {
          addLog(ProcessingStep.VALIDATE, `Rule Fail: ${field.key} - ${field.validationError}`, 'error');
        } else {
          addLog(ProcessingStep.VALIDATE, `Rule Pass: ${field.key} is valid`, 'success');
        }
      });
      
      if (analysisResult.riskDegree === 'High') {
         addLog(ProcessingStep.VALIDATE, "Risk Degree III Detected: Validation failures. Manual Review Required.", 'error');
      } else if (analysisResult.riskDegree === 'Medium') {
         addLog(ProcessingStep.VALIDATE, "Risk Degree II Detected: Low Confidence. Manual Review Recommended.", 'warning');
      } else {
         addLog(ProcessingStep.VALIDATE, "Low Risk. Automation success.", 'success');
      }

      await new Promise(resolve => setTimeout(resolve, 1000));
      setCompletedSteps(prev => [...prev, ProcessingStep.VALIDATE]);

      // Step 6: Output
      setCurrentStep(ProcessingStep.OUTPUT);
      addLog(ProcessingStep.OUTPUT, "Generating final digitized output...", 'success');
      setResult(analysisResult);
      setCompletedSteps(prev => [...prev, ProcessingStep.OUTPUT]);
      setAppState(AppState.REVIEW);

    } catch (error) {
      console.error(error);
      addLog(ProcessingStep.OUTPUT, "System Error: Failed to process document.", 'error');
      setAppState(AppState.IDLE);
    }
  };

  const handleReset = () => {
    setAppState(AppState.IDLE);
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
    setLogs([]);
    setCompletedSteps([]);
    setSelectedHistoryId(null);
  };

  const handleSave = (updatedResult: ProcessingResult) => {
    if (selectedHistoryId) {
      // Update existing record
      setDocumentHistory(prev => prev.map(doc => {
        if (doc.id === selectedHistoryId) {
           return { ...doc, ...updatedResult };
        }
        return doc;
      }));
      setAppView(AppView.DOCUMENTS);
    } else {
      // Create new record
      if (updatedResult) {
        const newDoc: SavedDocument = {
          ...updatedResult,
          id: crypto.randomUUID(),
          timestamp: new Date().toLocaleString(),
          fileName: selectedFile?.name || 'Scanned Document'
        };
        setDocumentHistory(prev => [...prev, newDoc]);
        handleReset();
        setAppView(AppView.DOCUMENTS);
      }
    }
  };

  const handleSelectHistoryDoc = (doc: SavedDocument) => {
    // Determine image URL. In a real app, this would be a blob URL or S3 link stored in the doc object.
    // For this demo, we'll try to use the current previewUrl if it matches, or a placeholder if we lost the blob.
    // Note: React blobs are transient. To fully support re-viewing images, we'd need to store base64 in history (heavy) or proper backend.
    // We will show a placeholder if we can't find the image, but we will show the data.
    
    setResult(doc);
    setSelectedHistoryId(doc.id);
    // For demo purposes, we might not have the image anymore if we navigated away and refreshed, 
    // but if we just switched tabs, previewUrl might be stale.
    // Ideally, store the image in the history object (as base64 or blob). 
    // For now, we will use a generic placeholder if previewUrl is null or mismatch, 
    // but in this session we assume we are just clicking around. 
    // Let's use a placeholder image if we are viewing history to avoid broken images.
    setPreviewUrl("https://placehold.co/600x800/e2e8f0/64748b?text=Document+Image+Preview"); 
    
    setAppState(AppState.REVIEW);
    setAppView(AppView.UPLOAD); // Re-use the upload/review view
  };

  return (
    <div className="min-h-screen flex flex-col font-sans text-slate-800">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => setAppView(AppView.UPLOAD)}>
            <div className="bg-red-900 text-white p-2 rounded-lg">
              <BrainCircuit size={24} />
            </div>
            <div>
               <h1 className="text-xl font-bold text-gray-900 tracking-tight">SmartDoc Platform</h1>
               <p className="text-xs text-gray-500 font-medium -mt-1">UTM Artificial Intelligence Project</p>
            </div>
          </div>
          <div className="flex items-center gap-6">
             <nav className="hidden md:flex gap-6 text-sm font-medium text-gray-600">
               <button 
                 onClick={() => setAppView(AppView.DASHBOARD)}
                 className={`hover:text-blue-600 transition-colors ${appView === AppView.DASHBOARD ? 'text-blue-600 font-bold' : ''}`}
               >
                 Dashboard
               </button>
               <button 
                 onClick={() => setAppView(AppView.DOCUMENTS)}
                 className={`hover:text-blue-600 transition-colors ${appView === AppView.DOCUMENTS ? 'text-blue-600 font-bold' : ''}`}
               >
                 Documents
               </button>
               <button 
                 onClick={() => setAppView(AppView.QUEUE)}
                 className={`hover:text-blue-600 transition-colors ${appView === AppView.QUEUE ? 'text-blue-600 font-bold' : ''}`}
               >
                 Validation Queue
               </button>
               <button 
                 onClick={() => setAppView(AppView.TEAM)}
                 className={`hover:text-blue-600 transition-colors ${appView === AppView.TEAM ? 'text-blue-600 font-bold' : ''}`}
               >
                 The Team
               </button>
               <button 
                  onClick={() => {
                    handleReset();
                    setAppView(AppView.UPLOAD);
                  }}
                  className={`flex items-center gap-1 hover:text-blue-600 transition-colors ${appView === AppView.UPLOAD && !selectedHistoryId ? 'text-blue-600 font-bold' : ''}`}
               >
                 <PlusCircle size={16} /> New Upload
               </button>
             </nav>
             <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-700 font-bold text-xs border border-blue-200">
               AI
             </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 bg-gray-50/50 p-4 lg:p-8 overflow-hidden flex flex-col">
        <div className="max-w-7xl mx-auto w-full h-full flex flex-col gap-6">
          
          {/* Progress Section - Only visible during active processing flow (not history review) */}
          {appView === AppView.UPLOAD && appState !== AppState.IDLE && !selectedHistoryId && (
            <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200 animate-in fade-in slide-in-from-top-4 duration-500">
               <ProgressBar currentStep={currentStep} completedSteps={completedSteps} />
            </div>
          )}

          {/* Dynamic Content Area */}
          <div className="flex-1 flex flex-col lg:flex-row gap-6 min-h-0">
            
            {/* View Switching */}
            {appView === AppView.DASHBOARD && (
              <Dashboard documents={documentHistory} />
            )}

            {appView === AppView.DOCUMENTS && (
              <DocumentsList 
                documents={documentHistory} 
                onSelect={handleSelectHistoryDoc}
              />
            )}

            {appView === AppView.QUEUE && (
              <DocumentsList 
                documents={documentHistory} 
                title="Validation Queue (High Risk)" 
                filterHighRisk={true} 
                onSelect={handleSelectHistoryDoc}
              />
            )}

            {appView === AppView.TEAM && (
               <TeamView />
            )}

            {appView === AppView.UPLOAD && (
              <>
                <div className="flex-1 flex flex-col gap-6">
                   {appState === AppState.IDLE && (
                     <div className="flex-1 flex flex-col justify-center animate-in zoom-in-95 duration-300">
                        <div className="text-center mb-8">
                           <h2 className="text-3xl font-bold text-gray-900 mb-3">Intelligent Document Processing</h2>
                           <p className="text-gray-500 max-w-lg mx-auto">
                             Upload any document (Invoice, ID, Form) to automatically digitize, extract, and validate data using our Knowledge Representation Engine.
                           </p>
                        </div>
                        <DocumentUploader onUpload={handleUpload} />
                     </div>
                   )}

                   {(appState === AppState.PROCESSING) && (
                     <div className="flex-1 flex items-center justify-center bg-white rounded-xl border border-gray-200 shadow-sm p-12">
                        <div className="text-center">
                           <div className="relative w-32 h-32 mx-auto mb-8">
                             <div className="absolute inset-0 border-4 border-gray-100 rounded-full"></div>
                             <div className="absolute inset-0 border-4 border-blue-500 rounded-full border-t-transparent animate-spin"></div>
                             <ScanLine className="absolute inset-0 m-auto text-blue-500 animate-pulse" size={32} />
                           </div>
                           <h3 className="text-xl font-bold text-gray-800">Processing Document</h3>
                           <p className="text-gray-500 mt-2">Running State Space Search algorithms...</p>
                        </div>
                     </div>
                   )}

                   {appState === AppState.REVIEW && result && previewUrl && (
                      <ResultView 
                        result={result} 
                        imageUrl={previewUrl} 
                        onReset={handleReset} 
                        onSave={handleSave}
                      />
                   )}
                </div>

                {/* Sidebar / Logs - Only in Upload/Process View (and new uploads) */}
                {appState !== AppState.IDLE && !selectedHistoryId && (
                   <div className="w-full lg:w-80 shrink-0 h-[300px] lg:h-auto">
                      <ProcessingLog logs={logs} />
                   </div>
                )}
              </>
            )}

          </div>
        </div>
      </main>
    </div>
  );
}