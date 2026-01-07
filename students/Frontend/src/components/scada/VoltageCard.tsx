import { AlertTriangle, CheckCircle2 } from 'lucide-react';
import { Card } from '@/components/ui/card';

interface VoltageCardProps {
  value: number;
}

export const VoltageCard = ({ value }: VoltageCardProps) => {
  const isLow = value < 11;
  const isHigh = value > 14.5;
  const isNormal = !isLow && !isHigh;

  const color = isNormal ? 'text-success' : isHigh ? 'text-warning' : 'text-destructive';
  const bgColor = isNormal ? 'bg-success/10' : isHigh ? 'bg-warning/10' : 'bg-destructive/10';
  const Icon = isNormal ? CheckCircle2 : AlertTriangle;

  return (
    <Card className={`bg-card border-border p-4 ${bgColor}`}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs text-muted-foreground uppercase tracking-wider font-medium">
          VOLTAGE
        </span>
        <Icon className={`w-4 h-4 ${color}`} />
      </div>

      <div className="mb-3">
        <div className="text-2xl font-display font-bold tracking-tight">
          {value.toFixed(1)}
        </div>
        <div className="text-xs text-muted-foreground uppercase tracking-wider">Volts</div>
      </div>

      <div className="flex items-center gap-2">
        <div className="flex-1 h-1 bg-muted rounded-full overflow-hidden">
          <div
            className={`h-full transition-all ${
              isNormal ? 'bg-success' : isHigh ? 'bg-warning' : 'bg-destructive'
            }`}
            style={{ width: `${Math.min(100, (value / 15) * 100)}%` }}
          />
        </div>
        <span className={`text-xs font-medium ${color}`}>
          {isNormal ? 'OK' : isHigh ? 'HIGH' : 'LOW'}
        </span>
      </div>
    </Card>
  );
};
