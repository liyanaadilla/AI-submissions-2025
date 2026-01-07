import { useState, useEffect, useCallback } from 'react';
import { SensorData, Alert, EngineState } from '@/types/scada';

const generateRandomValue = (base: number, variance: number) => {
  return base + (Math.random() - 0.5) * variance * 2;
};

const generateSensorData = (tickCount: number, prevTemp: number): SensorData => {
  const baseTemp = 75 + Math.sin(tickCount * 0.02) * 15;
  const temperature = generateRandomValue(baseTemp, 3);
  const rpm = Math.round(generateRandomValue(2400, 100));
  const oil_pressure_psi = generateRandomValue(42, 3);
  const vibration_mms = generateRandomValue(1.2, 0.3);
  const voltage_v = generateRandomValue(13.2, 0.2);

  let state: EngineState = 'NORMAL';
  let alert_message: string | null = null;
  const state_changed = false;

  if (temperature > 85) {
    state = 'ALERT_HIGH';
    alert_message = `High temperature alert: ${temperature.toFixed(1)}°F threshold exceeded`;
  } else if (temperature < 50) {
    state = 'ALERT_LOW';
    alert_message = `Low temperature alert: ${temperature.toFixed(1)}°F below threshold`;
  }

  return {
    timestamp: Date.now(),
    temperature,
    rpm,
    oil_pressure_psi,
    vibration_mms,
    voltage_v,
    state,
    state_changed,
    alert_message,
    simulation_time: tickCount * 0.5,
    tick_count: tickCount,
    scheduled_tasks: [],
    ml_insights: {
      fault_detection: {
        detected: false,
        confidence: 0.92 + Math.random() * 0.08,
      },
      vibration_anomaly: {
        detected: vibration_mms > 2.5,
        score: Math.random() * 0.3,
      },
      pressure_prediction: {
        predicted_pressure: oil_pressure_psi + (Math.random() - 0.5) * 2,
        actual_pressure: oil_pressure_psi,
      },
    },
  };
};

const initialAlerts: Alert[] = [
  {
    id: '1',
    timestamp: Date.now() - 300000,
    message: 'Oil pressure fluctuation detected',
    source: 'Sensor OP-1',
    severity: 'WARNING',
  },
  {
    id: '2',
    timestamp: Date.now() - 600000,
    message: 'Routine self-diagnostic completed',
    source: 'System Core',
    severity: 'INFO',
  },
  {
    id: '3',
    timestamp: Date.now() - 900000,
    message: 'Connection latency high',
    source: 'Network GW',
    severity: 'WARNING',
  },
];

export const useSimulatedData = () => {
  const [tickCount, setTickCount] = useState(0);
  const [currentData, setCurrentData] = useState<SensorData | null>(null);
  const [sensorHistory, setSensorHistory] = useState<SensorData[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>(initialAlerts);
  const [isRunning, setIsRunning] = useState(true);
  const [startTime] = useState(Date.now());
  const [previousState, setPreviousState] = useState<EngineState>('NORMAL');
  const [hasError, setHasError] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const tick = useCallback(() => {
    try {
      setHasError(false);
      setErrorMessage(null);

      setTickCount((prev) => {
        const newTick = prev + 1;
        const prevTemp = currentData?.temperature ?? 75;
        const newData = generateSensorData(newTick, prevTemp);
        
        setCurrentData(newData);
        setSensorHistory((prevHistory) => {
          const updated = [...prevHistory, newData];
          return updated.slice(-300);
        });

        // Handle alert lifecycle based on state transitions
        if (newData.state !== previousState) {
          if (newData.state === 'NORMAL') {
            // System recovered - add recovery alert
            const recoveryAlert: Alert = {
              id: Date.now().toString(),
              timestamp: Date.now(),
              message: 'System returned to normal operation',
              source: 'Engine Monitor',
              severity: 'INFO',
            };
            setAlerts((prev) => [recoveryAlert, ...prev].slice(0, 100));
          } else if (newData.alert_message) {
            // New alert triggered
            const newAlert: Alert = {
              id: Date.now().toString(),
              timestamp: Date.now(),
              message: newData.alert_message,
              source: 'Engine Monitor',
              severity: newData.state === 'CRITICAL' ? 'CRITICAL' : 'WARNING',
            };
            setAlerts((prev) => [newAlert, ...prev].slice(0, 100));
          }
          setPreviousState(newData.state);
        }

        return newTick;
      });
    } catch (error) {
      setHasError(true);
      setErrorMessage(
        error instanceof Error ? error.message : 'An unexpected error occurred'
      );
      console.error('Error in tick:', error);
    }
  }, [currentData?.temperature, previousState]);

  useEffect(() => {
    if (!isRunning) return;

    const interval = setInterval(tick, 1500);
    return () => clearInterval(interval);
  }, [isRunning, tick]);

  useEffect(() => {
    tick();
  }, []);

  const uptime = Math.floor((Date.now() - startTime) / 1000);
  const hours = Math.floor(uptime / 3600);
  const minutes = Math.floor((uptime % 3600) / 60);
  const seconds = uptime % 60;
  const uptimeString = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

  return {
    currentData,
    sensorHistory,
    alerts,
    tickCount,
    isRunning,
    setIsRunning,
    uptimeString,
    hasError,
    errorMessage,
  };
};
