import { CheckCircle2, AlertTriangle, XCircle, Power, Thermometer, OctagonX } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { EngineState } from '@/types/scada';

interface EngineStateCardProps {
  state: EngineState;
  driftRate?: number;
  rulDisplay?: string;
  activeDtcCount?: number;
}

export const EngineStateCard = ({ state, driftRate, rulDisplay, activeDtcCount }: EngineStateCardProps) => {
  // 6-state FSM configuration
  const stateConfig: Record<EngineState, { label: string; icon: React.ElementType; color: string; glow: string; bg: string }> = {
    IDLE: {
      label: 'IDLE',
      icon: Power,
      color: 'text-muted-foreground',
      glow: '',
      bg: 'bg-muted/20',
    },
    WARMUP: {
      label: 'WARMING UP',
      icon: Thermometer,
      color: 'text-primary',
      glow: 'glow-primary',
      bg: 'bg-primary/10',
    },
    NORMAL: {
      label: 'OPERATIONAL',
      icon: CheckCircle2,
      color: 'text-success',
      glow: 'glow-success',
      bg: 'bg-success/10',
    },
    WARNING: {
      label: 'WARNING',
      icon: AlertTriangle,
      color: 'text-warning',
      glow: 'glow-warning',
      bg: 'bg-warning/10',
    },
    CRITICAL: {
      label: 'CRITICAL',
      icon: XCircle,
      color: 'text-destructive',
      glow: 'glow-danger',
      bg: 'bg-destructive/10',
    },
    SHUTDOWN: {
      label: 'SHUTDOWN',
      icon: OctagonX,
      color: 'text-destructive',
      glow: 'glow-danger',
      bg: 'bg-destructive/20',
    },
  };

  const config = stateConfig[state] || stateConfig.NORMAL;
  const Icon = config.icon;

  return (
    <Card className={`bg-card border-border p-4 ${config.glow}`}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs text-muted-foreground uppercase tracking-wider font-medium">
          ENGINE STATE
        </span>
        {activeDtcCount !== undefined && activeDtcCount > 0 && (
          <span className="text-xs font-mono text-amber-400 bg-amber-400/10 px-2 py-0.5 rounded">
            {activeDtcCount} DTC{activeDtcCount > 1 ? 's' : ''}
          </span>
        )}
      </div>
      <div className={`flex items-center justify-center gap-2 py-2 px-4 rounded-lg ${config.bg}`}>
        <span className={`text-base font-display font-bold tracking-wide ${config.color}`}>
          {config.label}
        </span>
        <Icon className={`w-6 h-6 ${config.color}`} />
      </div>
      
      {/* Drift rate and RUL display */}
      {(driftRate !== undefined || rulDisplay) && (
        <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
          {driftRate !== undefined && (
            <div className="bg-muted/30 rounded px-2 py-1">
              <span className="text-muted-foreground">Drift: </span>
              <span className={driftRate > 1 ? 'text-warning' : 'text-foreground'}>
                {driftRate > 0 ? '+' : ''}{driftRate.toFixed(2)}°F/min
              </span>
            </div>
          )}
          {rulDisplay && rulDisplay !== 'N/A' && (
            <div className="bg-muted/30 rounded px-2 py-1">
              <span className="text-muted-foreground">RUL: </span>
              <span className={rulDisplay === 'IMMINENT' ? 'text-destructive font-bold' : 'text-foreground'}>
                {rulDisplay}
              </span>
            </div>
          )}
        </div>
      )}
    </Card>
  );
};
