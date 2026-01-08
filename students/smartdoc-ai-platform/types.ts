export enum AppState {
  IDLE = 'IDLE',
  SCANNING = 'SCANNING',
  PROCESSING = 'PROCESSING',
  REVIEW = 'REVIEW',
  COMPLETED = 'COMPLETED'
}

export enum ProcessingStep {
  SCAN = 'Scan Document',
  PREPROCESS = 'Image Pre-processing',
  DETECT = 'Detect Text Regions',
  OCR = 'OCR Extraction',
  VALIDATE = 'Validation & Rules',
  OUTPUT = 'Final Output'
}

export enum AppView {
  UPLOAD = 'UPLOAD',
  DASHBOARD = 'DASHBOARD',
  DOCUMENTS = 'DOCUMENTS',
  QUEUE = 'QUEUE',
  TEAM = 'TEAM'
}

export interface ExtractedField {
  key: string;
  value: string;
  confidence: number;
  validationError?: string; // Logic rule failure message
}

export interface ProcessingResult {
  documentType: string;
  language: string;
  summary: string;
  fields: ExtractedField[];
  riskDegree: 'Low' | 'Medium' | 'High'; // Based on PDF logic (I, II, III)
  rawText: string;
  overallConfidence: number;
}

export interface SavedDocument extends ProcessingResult {
  id: string;
  timestamp: string;
  fileName: string;
}

export interface LogEntry {
  timestamp: string;
  step: ProcessingStep;
  message: string;
  status: 'info' | 'success' | 'warning' | 'error';
}