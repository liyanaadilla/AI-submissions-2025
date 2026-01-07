/**
 * Data Audit Panel Component
 * Shows real-time Firebase Firestore data flow
 * Demonstrates complete data persistence and auditability
 */

import React, { useState } from 'react';
import { useFirebaseAudit } from '@/hooks/useFirebaseAudit';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AlertCircle, CheckCircle, Database, Clock, TrendingUp } from 'lucide-react';

export const DataAuditPanel: React.FC = () => {
  const { auditLogs, alerts, loading, error, enabled } = useFirebaseAudit(50);
  const [selectedTab, setSelectedTab] = useState('overview');

  if (!enabled) {
    return (
      <Card className="w-full bg-slate-900 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Database className="w-5 h-5 text-slate-400" />
            Firebase Data Audit
          </CardTitle>
          <CardDescription>Real-time data persistence</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-4 text-slate-300">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-yellow-500 mt-0.5 flex-shrink-0" />
              <div>
                <p className="font-medium">Firebase Not Configured</p>
                <p className="text-sm text-slate-400 mt-1">
                  To enable real-time data auditing:
                </p>
                <ol className="text-sm text-slate-400 mt-2 space-y-1 list-decimal list-inside">
                  <li>Follow the setup in FIREBASE_SETUP.md</li>
                  <li>Add your Firebase config to .env file</li>
                  <li>Restart the frontend dev server</li>
                </ol>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (loading) {
    return (
      <Card className="w-full bg-slate-900 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">Firebase Data Audit</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-slate-400">
            Connecting to Firebase...
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="w-full bg-slate-900 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">Firebase Data Audit</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="bg-red-900/20 border border-red-700 rounded-lg p-4 text-red-400">
            <p className="font-medium">Connection Error</p>
            <p className="text-sm mt-1">{error}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const latestReading = auditLogs.length > 0 ? auditLogs[0] : null;
  const recentAlerts = alerts.slice(0, 5);

  return (
    <Card className="w-full bg-slate-900 border-slate-700">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <Database className="w-5 h-5 text-blue-400" />
          Firebase Data Audit
        </CardTitle>
        <CardDescription>
          Real-time data persistence and auditability
        </CardDescription>
      </CardHeader>

      <CardContent>
        <Tabs value={selectedTab} onValueChange={setSelectedTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3 bg-slate-800">
            <TabsTrigger value="overview" className="text-slate-300">Overview</TabsTrigger>
            <TabsTrigger value="readings" className="text-slate-300">Readings</TabsTrigger>
            <TabsTrigger value="alerts" className="text-slate-300">Alerts</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4 mt-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  <span className="text-xs text-slate-400">Status</span>
                </div>
                <p className="text-lg font-semibold text-green-400">🟢 Connected</p>
              </div>

              <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="w-4 h-4 text-blue-500" />
                  <span className="text-xs text-slate-400">Total Readings</span>
                </div>
                <p className="text-lg font-semibold text-blue-400">{auditLogs.length}</p>
              </div>

              <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
                <div className="flex items-center gap-2 mb-2">
                  <AlertCircle className="w-4 h-4 text-orange-500" />
                  <span className="text-xs text-slate-400">Total Alerts</span>
                </div>
                <p className="text-lg font-semibold text-orange-400">{alerts.length}</p>
              </div>

              <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
                <div className="flex items-center gap-2 mb-2">
                  <Clock className="w-4 h-4 text-purple-500" />
                  <span className="text-xs text-slate-400">Latest Tick</span>
                </div>
                <p className="text-lg font-semibold text-purple-400">
                  {latestReading?.tick_count || '-'}
                </p>
              </div>
            </div>

            {latestReading && (
              <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
                <h4 className="text-sm font-semibold text-white mb-3">Latest Reading</h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <span className="text-slate-400">Temp:</span>
                    <span className="ml-2 text-blue-400 font-medium">
                      {latestReading.temperature?.toFixed(1)}°F
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400">RPM:</span>
                    <span className="ml-2 text-green-400 font-medium">
                      {latestReading.rpm}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400">Pressure:</span>
                    <span className="ml-2 text-yellow-400 font-medium">
                      {latestReading.oil_pressure_psi?.toFixed(1)} PSI
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400">State:</span>
                    <span className={`ml-2 font-medium ${
                      latestReading.state === 'ALERT_HIGH' ? 'text-red-400' : 'text-green-400'
                    }`}>
                      {latestReading.state}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </TabsContent>

          <TabsContent value="readings" className="space-y-3 mt-4 max-h-96 overflow-y-auto">
            {auditLogs.length === 0 ? (
              <p className="text-slate-400 text-sm">No readings yet</p>
            ) : (
              auditLogs.slice(0, 20).map((log) => (
                <div
                  key={log.id}
                  className="bg-slate-800 rounded p-3 border border-slate-700 text-xs"
                >
                  <div className="flex justify-between items-start mb-2">
                    <span className="text-slate-400">Tick #{log.tick_count}</span>
                    <span className={`px-2 py-1 rounded text-white text-xs ${
                      log.state === 'ALERT_HIGH' ? 'bg-red-600/30' : 'bg-green-600/30'
                    }`}>
                      {log.state}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-slate-300">
                    <div>T: {log.temperature?.toFixed(1)}°F</div>
                    <div>RPM: {log.rpm}</div>
                    <div>P: {log.oil_pressure_psi?.toFixed(1)} PSI</div>
                    <div>V: {log.vibration_mms?.toFixed(1)} mm/s</div>
                  </div>
                </div>
              ))
            )}
          </TabsContent>

          <TabsContent value="alerts" className="space-y-3 mt-4 max-h-96 overflow-y-auto">
            {recentAlerts.length === 0 ? (
              <p className="text-slate-400 text-sm">No alerts recorded</p>
            ) : (
              recentAlerts.map((alert) => (
                <div
                  key={alert.id}
                  className={`rounded p-3 border text-xs ${
                    alert.severity === 'warning'
                      ? 'bg-red-900/20 border-red-700'
                      : 'bg-blue-900/20 border-blue-700'
                  }`}
                >
                  <div className="flex justify-between items-start mb-1">
                    <span className="font-semibold text-white">{alert.type}</span>
                    <span className={`text-xs px-2 py-1 rounded ${
                      alert.severity === 'warning' ? 'text-red-300' : 'text-blue-300'
                    }`}>
                      {alert.severity.toUpperCase()}
                    </span>
                  </div>
                  <p className={`text-sm ${
                    alert.severity === 'warning' ? 'text-red-300' : 'text-blue-300'
                  }`}>
                    {alert.message}
                  </p>
                  <p className="text-slate-400 text-xs mt-1">
                    Tick: {alert.tick_count} | Value: {alert.trigger_value?.toFixed(1)}
                  </p>
                </div>
              ))
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};
