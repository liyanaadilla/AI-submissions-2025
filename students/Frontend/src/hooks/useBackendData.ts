import { useState, useEffect, useCallback, useRef } from 'react';
import { SensorData } from '@/types/scada';
import { fetchTick, healthCheck, ApiError } from '@/lib/api';
import { useSimulatedData } from './useSimulatedData';

interface UseBackendDataOptions {
  autoFetch?: boolean;
  intervalMs?: number;
  fallbackToSimulation?: boolean;
  manualMode?: boolean;
}

interface UseBackendDataResult {
  data: SensorData | null;
  isLoading: boolean;
  error: ApiError | null;
  isOnline: boolean;
  isSimulated: boolean;
  refetch: () => Promise<void>;
  reset: () => void;
}

/**
 * Hook to fetch data from backend with automatic health checks and fallback to simulation
 */
export function useBackendData({
  autoFetch = true,
  intervalMs = 1500,
  fallbackToSimulation = true,
  manualMode = false,
}: UseBackendDataOptions = {}): UseBackendDataResult {
  const [data, setData] = useState<SensorData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [isOnline, setIsOnline] = useState(false);
  const [isSimulated, setIsSimulated] = useState(false);
  const healthCheckIntervalRef = useRef<number | null>(null);
  const fetchIntervalRef = useRef<number | null>(null);

  // Fallback simulation hook
  const simulatedController = useSimulatedData();

  /**
   * Perform health check to see if backend is available
   */
  const checkHealth = useCallback(async () => {
    const isHealthy = await healthCheck();
    setIsOnline(isHealthy);
    return isHealthy;
  }, []);

  /**
   * Fetch a single tick
   */
  const fetchData = useCallback(async () => {
    if (!isOnline) {
      // Backend offline; use simulation if fallback enabled
      if (fallbackToSimulation) {
        setData(simulatedController.currentData);
        setIsSimulated(true);
        setError(null);
      }
      return;
    }

    setIsLoading(true);
    try {
      const tickData = await fetchTick();
      setData(tickData);
      setIsSimulated(false);
      setError(null);
      setIsLoading(false);
    } catch (err) {
      const apiErr = err instanceof ApiError ? err : new ApiError(
        String(err),
        'UNKNOWN_ERROR'
      );
      setError(apiErr);
      setIsLoading(false);

      // Fallback to simulation on error
      if (fallbackToSimulation) {
        const simData = simulatedController.currentData;
        setData(simData);
        setIsSimulated(true);
      }

      // Mark backend as offline after error
      setIsOnline(false);
    }
  }, [isOnline, fallbackToSimulation, simulatedController]);

  /**
   * Initial health check on mount
   */
  useEffect(() => {
    checkHealth();

    // Health check every 10s to detect recovery
    const hcInterval = window.setInterval(checkHealth, 10000);
    healthCheckIntervalRef.current = hcInterval;

    return () => {
      if (healthCheckIntervalRef.current) {
        window.clearInterval(healthCheckIntervalRef.current);
      }
    };
  }, [checkHealth]);

  /**
   * Auto-fetch loop
   */
  useEffect(() => {
    if (!autoFetch) return;

    // Fetch immediately on mount or when backend comes online
    fetchData();

    const interval = window.setInterval(fetchData, intervalMs);
    fetchIntervalRef.current = interval;

    return () => {
      if (fetchIntervalRef.current) {
        window.clearInterval(fetchIntervalRef.current);
      }
    };
  }, [autoFetch, intervalMs, fetchData]);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setIsSimulated(false);
  }, []);

  return {
    data,
    isLoading,
    error,
    isOnline,
    isSimulated,
    refetch: fetchData,
    reset,
  };
}
