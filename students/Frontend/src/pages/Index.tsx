import { Header } from '@/components/scada/Header';
import { KPICard } from '@/components/scada/KPICard';
import { GaugeChart } from '@/components/scada/GaugeChart';
import { EngineStateCard } from '@/components/scada/EngineStateCard';
import { VibrationIndicator } from '@/components/scada/VibrationIndicator';
import { VoltageCard } from '@/components/scada/VoltageCard';
import { TemperatureChart } from '@/components/scada/TemperatureChart';
import { SecondaryCharts } from '@/components/scada/SecondaryCharts';
import { AlertLog } from '@/components/scada/AlertLog';
import { MaintenanceSchedule } from '@/components/scada/MaintenanceSchedule';
import { MLInsightsPanel } from '@/components/scada/MLInsightsPanel';
import { ScheduledTasksPanel } from '@/components/scada/ScheduledTasksPanel';
import { DecisionsPanel } from '@/components/scada/DecisionsPanel';
import { ReportPanel } from '@/components/scada/ReportPanel';
import { ErrorNotification } from '@/components/scada/ErrorNotification';
import { SplashScreen } from '@/components/scada/SplashScreen';
import { MLModelsPanel } from '@/components/MLModelsPanel';
import { useBackendData } from '@/hooks/useBackendData';
import { useSimulatedData } from '@/hooks/useSimulatedData';
import { useState, useCallback, useEffect, useRef } from 'react';
import { Alert, SensorData, Report } from '@/types/scada';
import { Button } from '@/components/ui/button';
import { RotateCcw, Play, Pause, Zap } from 'lucide-react';

const Index = () => {
  const [showSplash, setShowSplash] = useState(true);
  const [sensorHistory, setSensorHistory] = useState<SensorData[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playSpeed, setPlaySpeed] = useState(1.0);
  const [faultMagnitude, setFaultMagnitude] = useState(0);
  const [report, setReport] = useState<Report | null>(null);
  const [isReportLoading, setIsReportLoading] = useState(false);
  const playIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // MANUAL MODE: autoFetch disabled, only fetch on button click
  const { data: backendData, isOnline, isSimulated, error: backendError, refetch } = useBackendData({
    autoFetch: false,
    fallbackToSimulation: true,
  });

  // Splash completion - fetch first tick
  const handleSplashComplete = useCallback(async () => {
    setShowSplash(false);
    setIsLoading(true);
    await refetch();
    setIsLoading(false);
  }, [refetch]);

  // Next Tick button
  const handleNextTick = useCallback(async () => {
    setIsLoading(true);
    await refetch();
    
    if (backendData) {
      setSensorHistory((prev) => [...prev, backendData]);

      // Capture state change as alert with DTC codes
      if (backendData.state_changed && backendData.alert_message) {
        const dtcCodes = backendData.dtcs?.map((d: { code: string }) => d.code) || [];
        const newAlert: Alert = {
          id: `${Date.now()}-${Math.random()}`,
          timestamp: backendData.simulation_time,
          message: backendData.alert_message,
          source: 'FSM',
          severity: backendData.severity || 'INFO',
          dtc_codes: dtcCodes,
        };
        setAlerts((prev) => [newAlert, ...prev.slice(0, 99)]);
      }
    }
    
    setIsLoading(false);
  }, [backendData, refetch]);

  // Reset everything
  const handleReset = useCallback(() => {
    setSensorHistory([]);
    setAlerts([]);
    setIsPlaying(false);
    setFaultMagnitude(0);
    if (playIntervalRef.current) {
      clearInterval(playIntervalRef.current);
      playIntervalRef.current = null;
    }
  }, []);

  // Fault Injection Slider
  const handleFaultChange = useCallback(async (magnitude: number) => {
    setFaultMagnitude(magnitude);
    
    // Call backend to set fault injection
    if (isOnline) {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/fault`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ magnitude }),
        });
        
        if (!response.ok) {
          console.warn('Fault injection request failed:', response.status);
        }
      } catch (err) {
        console.error('Failed to set fault injection:', err);
      }
    }
  }, [isOnline]);

  // Generate Report
  const handleGenerateReport = useCallback(async () => {
    if (!isOnline) return;
    
    setIsReportLoading(true);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/report`);
      if (response.ok) {
        const data = await response.json();
        setReport(data);
      }
    } catch (err) {
      console.error('Failed to generate report:', err);
    } finally {
      setIsReportLoading(false);
    }
  }, [isOnline]);

  // Download Report
  const handleDownloadReport = useCallback(async () => {
    if (!isOnline) return;
    
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/report/download`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ysmai_report_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (err) {
      console.error('Failed to download report:', err);
    }
  }, [isOnline]);

  // Auto-play with speed control
  useEffect(() => {
    if (isPlaying && !isLoading) {
      const tickDuration = 500 / playSpeed; // Base 500ms per tick, scaled by speed
      
      playIntervalRef.current = setInterval(() => {
        handleNextTick();
      }, tickDuration);
    } else {
      if (playIntervalRef.current) {
        clearInterval(playIntervalRef.current);
        playIntervalRef.current = null;
      }
    }

    return () => {
      if (playIntervalRef.current) {
        clearInterval(playIntervalRef.current);
      }
    };
  }, [isPlaying, playSpeed, isLoading, handleNextTick]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (showSplash) return;

      switch (e.code) {
        case 'Space':
          e.preventDefault();
          if (isPlaying) {
            setIsPlaying(false);
          } else {
            handleNextTick();
          }
          break;
        case 'KeyP':
          e.preventDefault();
          setIsPlaying((prev) => !prev);
          break;
        case 'KeyR':
          e.preventDefault();
          handleReset();
          break;
        default:
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [showSplash, isPlaying, handleNextTick, handleReset]);

  if (showSplash) {
    return <SplashScreen onComplete={handleSplashComplete} />;
  }

  const currentData = backendData || sensorHistory[sensorHistory.length - 1];

  if (!currentData) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Initializing dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header 
        isOnline={isOnline} 
        tickCount={sensorHistory.length} 
        uptime={`${Math.floor((sensorHistory.length * 0.5) / 60)}m`}
        isSimulated={isSimulated}
      />

      {/* Demo Mode Banner */}
      <div className="bg-gradient-to-r from-blue-950/60 to-cyan-950/40 border-b border-blue-800/50 px-6 py-3 backdrop-blur-sm space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex gap-1">
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" style={{ animationDelay: '150ms' }} />
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" style={{ animationDelay: '300ms' }} />
            </div>
            <p className="text-sm text-blue-200 font-medium">
              Demo Mode | <span className="text-cyan-300 font-bold">Spacebar</span>: Advance | 
              <span className="text-cyan-300 font-bold ml-2">P</span>: Play | 
              <span className="text-cyan-300 font-bold ml-2">R</span>: Reset
            </p>
          </div>
          <div className="flex gap-2">
            <Button
              onClick={() => setIsPlaying(!isPlaying)}
              className={`gap-2 font-semibold px-6 ${
                isPlaying 
                  ? 'bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-700 hover:to-orange-700' 
                  : 'bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700'
              } text-white`}
              size="sm"
            >
              {isPlaying ? (
                <>
                  <Pause className="w-4 h-4" />
                  Pause
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  Play
                </>
              )}
            </Button>
            <Button
              onClick={handleNextTick}
              disabled={isLoading || isPlaying}
              className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-semibold px-6 gap-2 disabled:opacity-50"
              size="sm"
            >
              <Play className="w-4 h-4" />
              Next Tick
            </Button>
            <Button
              onClick={handleReset}
              disabled={isLoading}
              variant="outline"
              size="sm"
              className="border-slate-600 text-slate-300 hover:bg-slate-800/50 gap-2"
            >
              <RotateCcw className="w-4 h-4" />
              Reset
            </Button>
          </div>
        </div>

        {/* Speed Control - Only show when playing */}
        {isPlaying && (
          <div className="flex items-center gap-4 pl-8">
            <span className="text-xs text-slate-300">Speed:</span>
            <div className="flex items-center gap-2 flex-1 max-w-xs">
              <input
                type="range"
                min="0.5"
                max="5"
                step="0.5"
                value={playSpeed}
                onChange={(e) => setPlaySpeed(parseFloat(e.target.value))}
                className="flex-1 h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-cyan-500"
              />
              <span className="text-xs text-cyan-400 font-mono w-8 text-right">
                {playSpeed.toFixed(1)}x
              </span>
            </div>
          </div>
        )}

        {/* Fault Injection Slider */}
        <div className="flex items-center gap-4 pl-8">
          <span className="text-xs text-slate-300 flex items-center gap-2">
            <Zap className="w-3 h-3 text-amber-400" />
            Fault Injection:
          </span>
          <div className="flex items-center gap-2 flex-1 max-w-xs">
            <input
              type="range"
              min="0"
              max="40"
              step="1"
              value={faultMagnitude}
              onChange={(e) => handleFaultChange(parseFloat(e.target.value))}
              className="flex-1 h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-amber-500"
            />
            <span className={`text-xs font-mono w-12 text-right ${
              faultMagnitude > 0 ? 'text-amber-400 font-bold' : 'text-slate-400'
            }`}>
              {faultMagnitude > 0 ? `+${faultMagnitude}°F` : 'Normal'}
            </span>
          </div>
        </div>

        <p className="text-xs text-slate-400 pl-8">Ticks: <span className="text-cyan-400 font-mono">{sensorHistory.length}</span> | Simulation Time: <span className="text-cyan-400 font-mono">{currentData?.simulation_time?.toFixed(1)}s</span></p>
      </div>

      {/* Status Banners */}
      {isSimulated && (
        <div className="bg-amber-900/30 border-b border-amber-700 px-6 py-2">
          <p className="text-xs text-amber-200">
            ⚠ Running in simulation mode (backend offline)
          </p>
        </div>
      )}

      {backendError && (
        <div className="bg-red-900/30 border-b border-red-700 px-6 py-2">
          <p className="text-xs text-red-200">
            ⚠ Backend Error: {backendError.message}
          </p>
        </div>
      )}

      <main className="flex-1 p-4 md:p-6 space-y-4 md:space-y-6">
        {/* KPI Cards Row */}
        <div className="grid grid-cols-2 md:grid-cols-6 gap-3 md:gap-4">
          <EngineStateCard 
            state={currentData.state} 
            driftRate={currentData.drift_rate_per_min}
            rulDisplay={currentData.estimated_rul_display}
            activeDtcCount={currentData.active_dtcs?.length || 0}
          />

          <KPICard title="RPM">
            <GaugeChart
              value={currentData.rpm}
              min={0}
              max={3000}
              label="RPM"
              unit="×1000"
              thresholds={{ warning: 2500, danger: 2800 }}
              size="md"
            />
          </KPICard>

          <KPICard
            title="COOLANT"
            badge={{ text: 'OK', variant: currentData.temperature > 85 ? 'danger' : 'success' }}
          >
            <GaugeChart
              value={currentData.temperature}
              min={0}
              max={120}
              label="Temperature"
              unit="°F"
              thresholds={{ warning: 75, danger: 85 }}
              size="md"
            />
          </KPICard>

          <KPICard
            title="OIL PRESSURE"
            badge={{
              text: currentData.oil_pressure_psi > 40 ? '+2%' : '-1.5%',
              variant: currentData.oil_pressure_psi > 40 ? 'success' : 'warning',
            }}
          >
            <GaugeChart
              value={currentData.oil_pressure_psi / 10}
              min={0}
              max={8}
              label="Pressure"
              unit="Bar"
              thresholds={{ warning: 5, danger: 7 }}
              size="md"
            />
          </KPICard>

          <VibrationIndicator value={currentData.vibration_mms} />

          <VoltageCard value={currentData.voltage_v} />
        </div>

        {/* Main Temperature Chart */}
        <TemperatureChart data={sensorHistory} currentTemp={currentData.temperature} />

        {/* Secondary Charts */}
        <SecondaryCharts data={sensorHistory} />

        {/* ML Real-Time Monitor Panel */}
        <MLModelsPanel 
          mlInsights={currentData.ml_insights} 
          sensorData={currentData}
          tickCount={sensorHistory.length}
        />

        {/* ML Insights Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2">
            <MLInsightsPanel insights={currentData.ml_insights} />
          </div>
          <ScheduledTasksPanel tasks={currentData.scheduled_tasks} />
        </div>

        {/* Decisions & Reports Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <DecisionsPanel 
            decisions={currentData.recent_decisions || []} 
            stats={currentData.decision_stats}
          />
          <ReportPanel 
            onGenerateReport={handleGenerateReport}
            onDownloadReport={handleDownloadReport}
            report={report}
            isLoading={isReportLoading}
          />
        </div>

        {/* Bottom Section: Alerts & Maintenance */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2">
            <AlertLog alerts={alerts} />
          </div>
          <MaintenanceSchedule tasks={currentData.scheduled_tasks} />
        </div>
      </main>

      <ErrorNotification message={backendError?.message || null} onDismiss={() => {}} />
    </div>
  );
};

export default Index;
