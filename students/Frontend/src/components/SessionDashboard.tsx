/**
 * Session Dashboard Component
 * Displays current session status, checkpoint timeline, and session controls
 */

import { useEffect, useState } from "react";
import { useSessionManager } from "@/hooks/useSessionManager";
import { SessionCheckpoint } from "@/types/sessions";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { AlertCircle, Clock, Zap, Thermometer } from "lucide-react";

export function SessionDashboard() {
  const {
    currentSession,
    sessionHistory,
    isLoading,
    error,
    createCheckpoint,
    endSession,
    getSessionHistory,
  } = useSessionManager();

  const [selectedSession, setSelectedSession] = useState<string | null>(null);

  // Refresh session history on mount
  useEffect(() => {
    getSessionHistory(10);
  }, [getSessionHistory]);

  if (error) {
    return (
      <Card className="border-red-500 bg-red-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-red-700">
            <AlertCircle className="h-5 w-5" />
            Session Error
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-600">{error}</p>
        </CardContent>
      </Card>
    );
  }

  if (!currentSession) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Session Dashboard</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-500">
            {isLoading ? "Loading session..." : "No active session"}
          </p>
        </CardContent>
      </Card>
    );
  }

  const formatTime = (isoString: string) => {
    try {
      const date = new Date(isoString);
      return date.toLocaleTimeString();
    } catch {
      return isoString;
    }
  };

  const formatDate = (isoString: string) => {
    try {
      const date = new Date(isoString);
      return date.toLocaleDateString();
    } catch {
      return isoString;
    }
  };

  const getTemperatureColor = (temp: number) => {
    if (temp < 70) return "text-blue-600";
    if (temp < 80) return "text-yellow-600";
    if (temp < 90) return "text-orange-600";
    return "text-red-600";
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "CRITICAL":
        return "bg-red-100 text-red-800 border-red-300";
      case "WARNING":
        return "bg-yellow-100 text-yellow-800 border-yellow-300";
      case "INFO":
      default:
        return "bg-blue-100 text-blue-800 border-blue-300";
    }
  };

  return (
    <div className="space-y-4">
      {/* Current Session Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Current Session</span>
            <span className="inline-block h-3 w-3 rounded-full bg-green-500 animate-pulse"></span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Session ID and Time */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-gray-500 uppercase">Session ID</p>
              <p className="font-mono text-sm break-all">
                {currentSession.session_id}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 uppercase">Started</p>
              <p className="text-sm">
                {formatDate(currentSession.start_time)}{" "}
                {formatTime(currentSession.start_time)}
              </p>
            </div>
          </div>

          {/* Checkpoint Count */}
          <div className="grid grid-cols-2 gap-4 pt-2 border-t">
            <div>
              <p className="text-xs text-gray-500 uppercase">Checkpoints</p>
              <p className="text-2xl font-bold">
                {currentSession.checkpoint_count}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 uppercase">
                Auto-Checkpoint Interval
              </p>
              <p className="text-sm">600 ticks (~5 min)</p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2 pt-2">
            <Button
              onClick={() => createCheckpoint()}
              disabled={isLoading}
              variant="outline"
              size="sm"
              className="flex-1"
            >
              <Zap className="mr-2 h-4 w-4" />
              Manual Checkpoint
            </Button>
            <Button
              onClick={() => endSession()}
              disabled={isLoading}
              variant="destructive"
              size="sm"
              className="flex-1"
            >
              <Clock className="mr-2 h-4 w-4" />
              End Session
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Checkpoint Timeline */}
      {currentSession.checkpoint_count > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Checkpoint Timeline</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {currentSession.checkpoints.map(
                (checkpoint: SessionCheckpoint, index: number) => (
                  <div
                    key={checkpoint.checkpoint_id}
                    className="flex items-start gap-3 p-2 rounded border border-gray-200 hover:bg-gray-50"
                  >
                    {/* Index Badge */}
                    <div className="flex-shrink-0 h-6 w-6 flex items-center justify-center rounded-full bg-gray-200 text-xs font-bold">
                      {index + 1}
                    </div>

                    {/* Checkpoint Details */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-2 mb-1">
                        <span className="text-xs text-gray-500">
                          Tick {checkpoint.tick_count}
                        </span>
                        <span
                          className={`inline-block px-2 py-1 text-xs rounded border ${getSeverityColor(
                            checkpoint.severity
                          )}`}
                        >
                          {checkpoint.severity}
                        </span>
                      </div>
                      <div className="flex items-center gap-4 text-sm">
                        <span className="flex items-center gap-1">
                          <Thermometer className={`h-4 w-4 ${getTemperatureColor(
                            checkpoint.temperature
                          )}`} />
                          <span className={`font-semibold ${getTemperatureColor(
                            checkpoint.temperature
                          )}`}>
                            {checkpoint.temperature.toFixed(1)}°C
                          </span>
                        </span>
                        <span className="text-gray-500">
                          {checkpoint.decision_count} decisions
                        </span>
                        {checkpoint.critical_event_trigger && (
                          <span className="inline-block px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded font-semibold">
                            🚨 Critical Event
                          </span>
                        )}
                      </div>
                      {checkpoint.active_dtcs.length > 0 && (
                        <div className="text-xs text-gray-600 mt-1">
                          DTCs: {checkpoint.active_dtcs.join(", ")}
                        </div>
                      )}
                    </div>
                  </div>
                )
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recent Sessions */}
      {sessionHistory.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Recent Sessions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {sessionHistory.slice(0, 5).map((session) => (
                <div
                  key={session.session_id}
                  onClick={() => setSelectedSession(session.session_id)}
                  className="p-2 rounded border border-gray-200 hover:bg-blue-50 cursor-pointer"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-mono text-gray-500">
                      {session.session_id.substring(0, 12)}...
                    </span>
                    <span className="text-xs text-gray-500">
                      {session.duration_seconds.toFixed(1)}s
                    </span>
                  </div>
                  <div className="flex items-center gap-4 text-xs">
                    <span>
                      {session.checkpoints_created} checkpoints
                    </span>
                    <span>
                      {session.total_decisions} decisions
                    </span>
                    <span className="text-gray-500">
                      {session.temp_min.toFixed(0)}°C -{" "}
                      {session.temp_max.toFixed(0)}°C
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Info Box */}
      <div className="p-3 rounded border border-blue-200 bg-blue-50">
        <p className="text-xs text-blue-700">
          <strong>Auto-Checkpoints:</strong> The system automatically creates
          checkpoints every 600 ticks or when critical events occur. You can
          also manually create checkpoints or end the session to start fresh.
        </p>
      </div>
    </div>
  );
}
