import React from 'react';
import { ProcessingStep } from '../types';
import { CheckCircle2, Circle, Loader2 } from 'lucide-react';

interface ProgressBarProps {
  currentStep: ProcessingStep;
  completedSteps: ProcessingStep[];
}

const steps = Object.values(ProcessingStep);

export const ProgressBar: React.FC<ProgressBarProps> = ({ currentStep, completedSteps }) => {
  return (
    <div className="w-full py-6">
      <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">State Space Search Workflow</h3>
      <div className="flex items-center justify-between relative">
        {/* Connector Line */}
        <div className="absolute left-0 top-1/2 transform -translate-y-1/2 w-full h-1 bg-gray-200 -z-10" />
        
        {steps.map((step, index) => {
          const isCompleted = completedSteps.includes(step);
          const isCurrent = step === currentStep;
          
          return (
            <div key={step} className="flex flex-col items-center group">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center border-4 transition-all duration-300 bg-white
                ${isCompleted ? 'border-green-500 text-green-500' : isCurrent ? 'border-blue-600 text-blue-600 scale-110' : 'border-gray-300 text-gray-300'}
              `}>
                {isCompleted ? (
                  <CheckCircle2 size={20} />
                ) : isCurrent ? (
                  <Loader2 size={20} className="animate-spin" />
                ) : (
                  <Circle size={20} />
                )}
              </div>
              <span className={`absolute mt-12 text-xs font-medium w-24 text-center transition-colors duration-300
                ${isCurrent ? 'text-blue-700 font-bold' : isCompleted ? 'text-green-600' : 'text-gray-400'}
              `}>
                {step}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
