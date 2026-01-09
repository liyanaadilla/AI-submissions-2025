import React, { useState } from 'react';
import { AlertCircle, Play, RotateCcw, Loader } from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';

interface MetricsSnapshot {
  temperature: number;
  rpm: number;
  oil_pressure_psi: number;
  vibration_mms: number;
  voltage_v: number;
  fault_detected: boolean;
  active_dtcs: string[];
  ml_predictions?: Record<string, any>;
  maintenance_tasks?: any[];
  scheduled_tasks?: any[];
}

interface ScenarioResult {
  scenario: {
    fault_type: string;
    magnitude: number;
    duration_ticks: number;
  };
  baseline: MetricsSnapshot;
  faulty: {
    peak_values: MetricsSnapshot;
    all_ticks: any[];
    new_decisions: number;
    duration_actual: number;
  };
  recovery: {
    ticks: any[];
    duration: number;
  };
  comparison: {
    temperature_change: number;
    pressure_change: number;
    vibration_change: number;
    voltage_change: number;
    dtcs_generated: string[];
    fault_detected_at_tick: number;
  };
  success: boolean;
}

export const ScenarioTester: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ScenarioResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedFault, setSelectedFault] = useState('temperature');
  const [magnitude, setMagnitude] = useState(30);
  const [duration, setDuration] = useState(100);

  const faultTypes = [
    { id: 'temperature', label: 'Temperature Spike', unit: '°C', min: 10, max: 80 },
    { id: 'pressure', label: 'Pressure Drop', unit: 'PSI', min: 5, max: 50 },
    { id: 'vibration', label: 'High Vibration', unit: 'mm/s', min: 5, max: 100 },
    { id: 'voltage', label: 'Voltage Surge', unit: 'V', min: 5, max: 50 },
  ];

  const currentFault = faultTypes.find((f) => f.id === selectedFault)!;

  const runScenario = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/test/scenario', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          fault_type: selectedFault,
          magnitude,
          duration_ticks: duration,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = (await response.json()) as ScenarioResult;
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to run scenario');
    } finally {
      setIsLoading(false);
    }
  };

  const faultDetectionSpeed = result
    ? `Detected at tick ${result.comparison.fault_detected_at_tick + 1}`
    : '-';

  return (
    <div className="w-full max-w-7xl mx-auto p-6">
      <h2 className="text-3xl font-bold mb-6 flex items-center gap-2">
        <AlertCircle className="w-8 h-8 text-orange-500" />
        Scenario Tester - System Response Demonstration
      </h2>

      {/* Control Panel */}
      <Card className="mb-6 p-6 bg-gradient-to-r from-slate-900 to-slate-800 border-slate-700">
        <h3 className="text-xl font-semibold mb-6 text-white">Fault Injection Controls</h3>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {/* Fault Type Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-3">Fault Type</label>
            <select
              value={selectedFault}
              onChange={(e) => setSelectedFault(e.target.value)}
              disabled={isLoading}
              className="w-full px-4 py-2 rounded bg-slate-700 text-white border border-slate-600 focus:border-blue-500 focus:outline-none disabled:opacity-50"
            >
              {faultTypes.map((f) => (
                <option key={f.id} value={f.id}>
                  {f.label}
                </option>
              ))}
            </select>
          </div>

          {/* Magnitude Slider */}
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-300 mb-3">
              Magnitude: {magnitude} {currentFault.unit}
            </label>
            <input
              type="range"
              min={currentFault.min}
              max={currentFault.max}
              value={magnitude}
              onChange={(e) => setMagnitude(parseInt(e.target.value))}
              disabled={isLoading}
              className="w-full h-2 bg-slate-600 rounded-lg appearance-none cursor-pointer disabled:opacity-50"
            />
            <div className="flex justify-between text-xs text-gray-400 mt-1">
              <span>{currentFault.min}</span>
              <span>{currentFault.max}</span>
            </div>
          </div>

          {/* Duration */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-3">Duration (ticks)</label>
            <input
              type="number"
              value={duration}
              onChange={(e) => setDuration(Math.max(10, parseInt(e.target.value) || 100))}
              disabled={isLoading}
              min={10}
              max={500}
              className="w-full px-4 py-2 rounded bg-slate-700 text-white border border-slate-600 focus:border-blue-500 focus:outline-none disabled:opacity-50"
            />
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-900 border border-red-700 rounded text-red-200 flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            {error}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-4">
          <Button
            onClick={runScenario}
            disabled={isLoading}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700"
          >
            {isLoading ? (
              <>
                <Loader className="w-4 h-4 animate-spin" />
                Running Scenario...
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Inject & Run
              </>
            )}
          </Button>

          {result && (
            <Button
              onClick={() => setResult(null)}
              variant="outline"
              className="flex items-center gap-2"
            >
              <RotateCcw className="w-4 h-4" />
              Clear Results
            </Button>
          )}
        </div>
      </Card>

      {/* Results Section */}
      {result && (
        <div className="space-y-6">
          {/* Comparison Summary */}
          <Card className="p-6 bg-gradient-to-r from-green-900 to-emerald-900 border-green-700">
            <h3 className="text-xl font-semibold mb-4 text-white flex items-center gap-2">
              ✓ Scenario Complete
            </h3>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <div className="text-xs text-gray-300 uppercase tracking-wide">Temperature Change</div>
                <div
                  className={`text-2xl font-bold ${
                    result.comparison.temperature_change > 0
                      ? 'text-red-400'
                      : 'text-green-400'
                  }`}
                >
                  {result.comparison.temperature_change > 0 ? '+' : ''}
                  {result.comparison.temperature_change.toFixed(1)}°C
                </div>
              </div>

              <div>
                <div className="text-xs text-gray-300 uppercase tracking-wide">Pressure Change</div>
                <div
                  className={`text-2xl font-bold ${
                    Math.abs(result.comparison.pressure_change) > 2
                      ? 'text-red-400'
                      : 'text-green-400'
                  }`}
                >
                  {result.comparison.pressure_change > 0 ? '+' : ''}
                  {result.comparison.pressure_change.toFixed(1)} PSI
                </div>
              </div>

              <div>
                <div className="text-xs text-gray-300 uppercase tracking-wide">Vibration Change</div>
                <div
                  className={`text-2xl font-bold ${
                    result.comparison.vibration_change > 5
                      ? 'text-red-400'
                      : 'text-green-400'
                  }`}
                >
                  {result.comparison.vibration_change > 0 ? '+' : ''}
                  {result.comparison.vibration_change.toFixed(2)} mm/s
                </div>
              </div>

              <div>
                <div className="text-xs text-gray-300 uppercase tracking-wide">Detection Speed</div>
                <div className="text-2xl font-bold text-yellow-400">
                  {result.comparison.fault_detected_at_tick >= 0
                    ? `Tick ${result.comparison.fault_detected_at_tick + 1}`
                    : 'Not detected'}
                </div>
              </div>
            </div>
          </Card>

          {/* Side-by-Side Comparison */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Normal State */}
            <Card className="p-6 bg-slate-900 border-green-700">
              <h4 className="text-lg font-semibold mb-4 text-green-400">✓ Normal Engine State</h4>
              <div className="space-y-3">
                <div className="flex justify-between py-2 border-b border-slate-700">
                  <span className="text-gray-400">Temperature</span>
                  <span className="font-mono font-bold text-green-300">
                    {result.baseline.temperature.toFixed(1)}°C
                  </span>
                </div>
                <div className="flex justify-between py-2 border-b border-slate-700">
                  <span className="text-gray-400">RPM</span>
                  <span className="font-mono font-bold text-green-300">
                    {result.baseline.rpm.toFixed(0)}
                  </span>
                </div>
                <div className="flex justify-between py-2 border-b border-slate-700">
                  <span className="text-gray-400">Oil Pressure</span>
                  <span className="font-mono font-bold text-green-300">
                    {result.baseline.oil_pressure_psi.toFixed(1)} PSI
                  </span>
                </div>
                <div className="flex justify-between py-2 border-b border-slate-700">
                  <span className="text-gray-400">Vibration</span>
                  <span className="font-mono font-bold text-green-300">
                    {result.baseline.vibration_mms.toFixed(2)} mm/s
                  </span>
                </div>
                <div className="flex justify-between py-2 border-b border-slate-700">
                  <span className="text-gray-400">Voltage</span>
                  <span className="font-mono font-bold text-green-300">
                    {result.baseline.voltage_v.toFixed(1)}V
                  </span>
                </div>
                <div className="mt-4 p-3 bg-slate-800 rounded">
                  <div className="text-xs text-gray-400 uppercase mb-2">Fault Status</div>
                  <div className="text-green-400 font-semibold">✓ Normal Operation</div>
                </div>
                <div className="mt-3 p-3 bg-slate-800 rounded">
                  <div className="text-xs text-gray-400 uppercase mb-2">Active DTCs</div>
                  <div className="text-gray-300">
                    {result.baseline.active_dtcs?.length === 0
                      ? 'None'
                      : result.baseline.active_dtcs?.join(', ')}
                  </div>
                </div>
              </div>
            </Card>

            {/* Faulty State */}
            <Card className="p-6 bg-slate-900 border-red-700">
              <h4 className="text-lg font-semibold mb-4 text-red-400">⚠ Faulty Engine State</h4>
              <div className="space-y-3">
                <div className="flex justify-between py-2 border-b border-slate-700">
                  <span className="text-gray-400">Temperature</span>
                  <span className="font-mono font-bold text-red-300">
                    {result.faulty.peak_values.temperature.toFixed(1)}°C
                  </span>
                </div>
                <div className="flex justify-between py-2 border-b border-slate-700">
                  <span className="text-gray-400">RPM</span>
                  <span className="font-mono font-bold text-red-300">
                    {result.faulty.peak_values.rpm.toFixed(0)}
                  </span>
                </div>
                <div className="flex justify-between py-2 border-b border-slate-700">
                  <span className="text-gray-400">Oil Pressure</span>
                  <span className="font-mono font-bold text-red-300">
                    {result.faulty.peak_values.oil_pressure_psi.toFixed(1)} PSI
                  </span>
                </div>
                <div className="flex justify-between py-2 border-b border-slate-700">
                  <span className="text-gray-400">Vibration</span>
                  <span className="font-mono font-bold text-red-300">
                    {result.faulty.peak_values.vibration_mms.toFixed(2)} mm/s
                  </span>
                </div>
                <div className="flex justify-between py-2 border-b border-slate-700">
                  <span className="text-gray-400">Voltage</span>
                  <span className="font-mono font-bold text-red-300">
                    {result.faulty.peak_values.voltage_v.toFixed(1)}V
                  </span>
                </div>
                <div className="mt-4 p-3 bg-red-900 rounded">
                  <div className="text-xs text-gray-400 uppercase mb-2">Fault Status</div>
                  <div className="text-red-400 font-semibold">
                    {result.faulty.peak_values.fault_detected
                      ? '🚨 FAULT DETECTED!'
                      : '⚠ Anomaly in progress'}
                  </div>
                </div>
                <div className="mt-3 p-3 bg-red-900 rounded">
                  <div className="text-xs text-gray-400 uppercase mb-2">Generated DTCs</div>
                  <div className="text-red-300 font-semibold">
                    {result.comparison.dtcs_generated?.length > 0
                      ? result.comparison.dtcs_generated?.join(', ')
                      : 'None'}
                  </div>
                </div>
              </div>
            </Card>
          </div>

          {/* System Response */}
          <Card className="p-6 bg-slate-900 border-slate-700">
            <h4 className="text-lg font-semibold mb-4 text-white">System Response</h4>

            <div className="grid grid-cols-3 gap-4">
              <div className="p-4 bg-slate-800 rounded border border-slate-700">
                <div className="text-xs text-gray-400 uppercase tracking-wide mb-2">Fault Duration</div>
                <div className="text-2xl font-bold text-orange-400">
                  {result.faulty.duration_actual} ticks
                </div>
              </div>

              <div className="p-4 bg-slate-800 rounded border border-slate-700">
                <div className="text-xs text-gray-400 uppercase tracking-wide mb-2">New Decisions</div>
                <div className="text-2xl font-bold text-yellow-400">
                  {result.faulty.new_decisions}
                </div>
                <div className="text-xs text-gray-400 mt-1">Made during fault</div>
              </div>

              <div className="p-4 bg-slate-800 rounded border border-slate-700">
                <div className="text-xs text-gray-400 uppercase tracking-wide mb-2">Recovery Time</div>
                <div className="text-2xl font-bold text-green-400">
                  {result.recovery.duration} ticks
                </div>
              </div>
            </div>

            <div className="mt-6 p-4 bg-slate-800 rounded border border-slate-700">
              <div className="text-sm text-gray-400 mb-3">Detection Timeline:</div>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-green-500"></div>
                  <span>
                    <strong>T+0</strong>: Baseline captured
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-orange-500"></div>
                  <span>
                    <strong>T+1-{result.comparison.fault_detected_at_tick + 1}</strong>: Fault
                    injection active
                  </span>
                </div>
                {result.comparison.fault_detected_at_tick >= 0 && (
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full bg-red-500"></div>
                    <span>
                      <strong>T+{result.comparison.fault_detected_at_tick + 1}</strong>: Anomaly
                      detected by ML model
                    </span>
                  </div>
                )}
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                  <span>
                    <strong>T+{result.faulty.duration_actual + 1}</strong>: Fault removed
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-green-500"></div>
                  <span>
                    <strong>T+{result.faulty.duration_actual + result.recovery.duration}</strong>:
                    System recovered
                  </span>
                </div>
              </div>
            </div>
          </Card>

          {/* Data Export */}
          <div className="flex gap-4">
            <Button
              onClick={() => {
                const dataStr = JSON.stringify(result, null, 2);
                const dataBlob = new Blob([dataStr], { type: 'application/json' });
                const url = URL.createObjectURL(dataBlob);
                const link = document.createElement('a');
                link.href = url;
                link.download = `scenario-${selectedFault}-${Date.now()}.json`;
                link.click();
              }}
              className="bg-green-600 hover:bg-green-700"
            >
              Export Results as JSON
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ScenarioTester;
