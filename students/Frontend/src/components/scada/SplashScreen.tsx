import { useEffect, useState } from 'react';

interface DataCollectionStep {
  name: string;
  icon: string;
  progress: number;
}

interface SplashScreenProps {
  onComplete: () => void;
}

export const SplashScreen = ({ onComplete }: SplashScreenProps) => {
  const [steps, setSteps] = useState<DataCollectionStep[]>([
    { name: 'Initializing Engine Controller', icon: '⚙️', progress: 0 },
    { name: 'Reading Temperature Sensor', icon: '🌡️', progress: 0 },
    { name: 'Scanning RPM Detector', icon: '📊', progress: 0 },
    { name: 'Checking Oil Pressure', icon: '💧', progress: 0 },
    { name: 'Analyzing Vibration Data', icon: '📈', progress: 0 },
    { name: 'Loading ML Models', icon: '🤖', progress: 0 },
  ]);

  const [currentStep, setCurrentStep] = useState(0);
  const [fadeOut, setFadeOut] = useState(false);
  const [completed, setCompleted] = useState(false);

  useEffect(() => {
    if (completed) return;

    const interval = setInterval(() => {
      setSteps((prev) => {
        const updated = prev.map((step, idx) => {
          if (idx < currentStep) {
            return { ...step, progress: 100 };
          } else if (idx === currentStep) {
            const newProgress = Math.min(step.progress + 8, 100);
            return { ...step, progress: newProgress };
          }
          return step;
        });

        // Check if current step completed, move to next
        if (updated[currentStep]?.progress >= 100 && currentStep < prev.length - 1) {
          setCurrentStep((c) => c + 1);
        }

        // Check if last step completed
        if (currentStep === prev.length - 1 && updated[currentStep]?.progress >= 100 && !completed) {
          setCompleted(true);
          setTimeout(() => {
            setFadeOut(true);
            setTimeout(onComplete, 500);
          }, 300);
        }

        return updated;
      });
    }, 60);

    return () => clearInterval(interval);
  }, [currentStep, completed, onComplete]);

  return (
    <div
      className={`fixed inset-0 bg-gradient-to-b from-slate-950 via-slate-900 to-blue-950 flex items-center justify-center transition-opacity duration-600 z-50 ${
        fadeOut ? 'opacity-0 pointer-events-none' : 'opacity-100'
      }`}
    >
      {/* Grid background effect */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0" style={{
          backgroundImage: 'linear-gradient(0deg, transparent 24%, rgba(33, 150, 243, .1) 25%, rgba(33, 150, 243, .1) 26%, transparent 27%, transparent 74%, rgba(33, 150, 243, .1) 75%, rgba(33, 150, 243, .1) 76%, transparent 77%, transparent), linear-gradient(90deg, transparent 24%, rgba(33, 150, 243, .1) 25%, rgba(33, 150, 243, .1) 26%, transparent 27%, transparent 74%, rgba(33, 150, 243, .1) 75%, rgba(33, 150, 243, .1) 76%, transparent 77%, transparent)',
          backgroundSize: '50px 50px'
        }} />
      </div>

      <div className="relative w-full max-w-2xl px-6 py-12">
        {/* Logo/Title */}
        <div className="text-center mb-16">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="text-4xl">🔧</div>
            <h1 className="text-5xl font-display font-bold bg-gradient-to-r from-primary to-blue-400 bg-clip-text text-transparent">
              YSMAI SCADA
            </h1>
          </div>
          <p className="text-slate-400 text-lg tracking-wide">Initializing Engine Monitoring System</p>
        </div>

        {/* Data Collection Steps */}
        <div className="space-y-5 mb-16">
          {steps.map((step, idx) => (
            <div key={idx} className="space-y-2">
              <div className="flex items-center gap-4">
                <span className="text-3xl flex-shrink-0">{step.icon}</span>
                <span
                  className={`text-sm font-medium transition-colors duration-300 flex-grow ${
                    idx < currentStep
                      ? 'text-green-400'
                      : idx === currentStep
                      ? 'text-blue-400 font-semibold'
                      : 'text-slate-500'
                  }`}
                >
                  {step.name}
                </span>
                {idx < currentStep && (
                  <span className="text-green-400 text-lg flex-shrink-0">✓</span>
                )}
              </div>

              {/* Progress Bar - Industrial Style */}
              <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden border border-slate-700">
                <div
                  className={`h-full rounded-full transition-all duration-100 shadow-lg ${
                    idx < currentStep
                      ? 'bg-gradient-to-r from-green-500 to-emerald-400 w-full'
                      : idx === currentStep
                      ? 'bg-gradient-to-r from-blue-500 to-cyan-400'
                      : 'bg-slate-700'
                  }`}
                  style={{
                    width: `${idx <= currentStep ? step.progress : 0}%`,
                    boxShadow: idx === currentStep ? '0 0 20px rgba(59, 130, 246, 0.5)' : 'none',
                  }}
                />
              </div>
            </div>
          ))}
        </div>

        {/* Bottom Status */}
        <div className="border-t border-slate-700 pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm">
                Status: <span className="text-blue-400 font-semibold">{currentStep + 1} of {steps.length} components</span>
              </p>
              <p className="text-slate-500 text-xs mt-1">Backend connection established</p>
            </div>
            <div className="flex items-center gap-2">
              <div className={`w-2.5 h-2.5 rounded-full ${
                currentStep === steps.length - 1 && steps[steps.length - 1].progress >= 100
                  ? 'bg-green-500 animate-pulse'
                  : 'bg-blue-500 animate-pulse'
              }`} />
              <span className="text-xs text-slate-500">System Ready</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
