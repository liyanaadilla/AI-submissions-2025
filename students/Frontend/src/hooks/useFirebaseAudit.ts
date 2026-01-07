/**
 * Firebase Firestore Hook for YSMAI
 * Provides real-time audit log data from Firebase
 */

import { useEffect, useState } from 'react';
import { initializeApp } from 'firebase/app';
import { getFirestore, collection, query, orderBy, limit, onSnapshot } from 'firebase/firestore';
import { firebaseConfig, isFirebaseConfigured } from '@/config/firebase';

interface AuditLog {
  id: string;
  timestamp: any;
  tick_count: number;
  temperature: number;
  rpm: number;
  oil_pressure_psi: number;
  vibration_mms: number;
  voltage: number;
  state: string;
  state_changed: boolean;
  alert_message: string | null;
  [key: string]: any;
}

interface Alert {
  id: string;
  timestamp: any;
  type: string;
  severity: string;
  message: string;
  trigger_value: number;
  threshold: number;
  tick_count: number;
}

export const useFirebaseAudit = (maxRecords = 50) => {
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [enabled, setEnabled] = useState(false);

  useEffect(() => {
    if (!isFirebaseConfigured()) {
      setEnabled(false);
      setError('Firebase not configured');
      setLoading(false);
      return;
    }

    try {
      // Initialize Firebase
      const app = initializeApp(firebaseConfig);
      const db = getFirestore(app);

      setEnabled(true);

      // Subscribe to sensor data collection
      const sensorQuery = query(
        collection(db, 'sensor_data'),
        orderBy('timestamp', 'desc'),
        limit(maxRecords)
      );

      const unsubscribeSensor = onSnapshot(
        sensorQuery,
        (snapshot) => {
          const logs: AuditLog[] = [];
          snapshot.forEach((doc) => {
            logs.push({
              id: doc.id,
              ...doc.data(),
            } as AuditLog);
          });
          setAuditLogs(logs);
          setError(null);
        },
        (err) => {
          console.error('Error fetching sensor data:', err);
          setError(err.message);
          setLoading(false);
        }
      );

      // Subscribe to alerts collection
      const alertsQuery = query(
        collection(db, 'alerts'),
        orderBy('timestamp', 'desc'),
        limit(20)
      );

      const unsubscribeAlerts = onSnapshot(
        alertsQuery,
        (snapshot) => {
          const alertList: Alert[] = [];
          snapshot.forEach((doc) => {
            alertList.push({
              id: doc.id,
              ...doc.data(),
            } as Alert);
          });
          setAlerts(alertList);
          setLoading(false);
        },
        (err) => {
          console.error('Error fetching alerts:', err);
          setError(err.message);
          setLoading(false);
        }
      );

      return () => {
        unsubscribeSensor();
        unsubscribeAlerts();
      };
    } catch (err) {
      console.error('Firebase initialization error:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
      setEnabled(false);
      setLoading(false);
    }
  }, [maxRecords]);

  return {
    auditLogs,
    alerts,
    loading,
    error,
    enabled,
  };
};
