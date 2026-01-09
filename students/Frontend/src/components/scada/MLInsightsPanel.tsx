import { AlertTriangle, TrendingUp, CheckCircle2 } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { MLInsights } from '@/types/scada';

interface MLInsightsPanelProps {
  insights: MLInsights | null;
}

export const MLInsightsPanel = ({ insights }: MLInsightsPanelProps) => {
  if (!insights) {
    return (
      <Card className="bg-card border-border p-4">
        <h4 className="text-sm font-display font-semibold mb-4">ML INSIGHTS</h4>
        <div className="text-center py-6 text-muted-foreground">
          ML predictions unavailable
        </div>
      </Card>
    );
  }

  const faultConfidence = Math.round(insights.fault_detection.confidence * 100);
  const vibrationScore = Math.round(insights.vibration_anomaly.score * 100);
  const pressureDiff = Math.abs(
    insights.pressure_prediction.predicted_pressure - insights.pressure_prediction.actual_pressure
  ).toFixed(1);

  return (
    <Card className="bg-card border-border p-4">
      <h4 className="text-sm font-display font-semibold mb-4">ML INSIGHTS</h4>
      
      <div className="space-y-4">
        {/* Fault Detection */}
        <div className="border border-border rounded-lg p-3 bg-muted/30">
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center gap-2">
              {insights.fault_detection.detected ? (
                <AlertTriangle className="w-4 h-4 text-warning" />
              ) : (
                <CheckCircle2 className="w-4 h-4 text-success" />
              )}
              <span className="text-xs font-medium text-muted-foreground uppercase">
                Fault Detection
              </span>
            </div>
            <div
              className={
                insights.fault_detection.detected
                  ? 'bg-warning/20 text-warning border border-warning/30 rounded-full px-2 py-1 text-xs font-semibold'
                  : 'bg-success/20 text-success border border-success/30 rounded-full px-2 py-1 text-xs font-semibold'
              }
            >
              {faultConfidence}%
            </div>
          </div>
          <div className="text-sm">
            <p className="text-foreground font-semibold">
              {insights.fault_detection.detected ? 'Potential Fault Detected' : 'No Faults Detected'}
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Confidence: {faultConfidence}%
            </p>
          </div>
        </div>

        {/* Vibration Anomaly */}
        <div className="border border-border rounded-lg p-3 bg-muted/30">
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center gap-2">
              {insights.vibration_anomaly.detected ? (
                <AlertTriangle className="w-4 h-4 text-destructive" />
              ) : (
                <CheckCircle2 className="w-4 h-4 text-success" />
              )}
              <span className="text-xs font-medium text-muted-foreground uppercase">
                Vibration Anomaly
              </span>
            </div>
            <div
              className={
                insights.vibration_anomaly.detected
                  ? 'bg-destructive/20 text-destructive border border-destructive/30 rounded-full px-2 py-1 text-xs font-semibold'
                  : 'bg-success/20 text-success border border-success/30 rounded-full px-2 py-1 text-xs font-semibold'
              }
            >
              {vibrationScore}%
            </div>
          </div>
          <div className="text-sm">
            <p className="text-foreground font-semibold">
              {insights.vibration_anomaly.detected ? 'Anomaly Detected' : 'Normal'}
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Anomaly Score: {vibrationScore}%
            </p>
          </div>
        </div>

        {/* Pressure Prediction */}
        <div className="border border-border rounded-lg p-3 bg-muted/30">
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-primary" />
              <span className="text-xs font-medium text-muted-foreground uppercase">
                Pressure Forecast
              </span>
            </div>
            <div className="bg-primary/20 text-primary border border-primary/30 rounded-full px-2 py-1 text-xs font-semibold">
              ±{pressureDiff} PSI
            </div>
          </div>
          <div className="text-sm">
            <div className="flex justify-between mb-1">
              <span className="text-muted-foreground">Predicted:</span>
              <span className="font-semibold text-foreground">
                {insights.pressure_prediction.predicted_pressure.toFixed(1)} PSI
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Actual:</span>
              <span className="font-semibold text-foreground">
                {insights.pressure_prediction.actual_pressure.toFixed(1)} PSI
              </span>
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Accuracy: {(100 - parseFloat(pressureDiff)).toFixed(1)}%
            </p>
          </div>
        </div>
      </div>
    </Card>
  );
};
