import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface VibrationIndicatorProps {
  value: number;
}

export const VibrationIndicator = ({ value }: VibrationIndicatorProps) => {
  const isStable = value < 2.5;
  const maxHeight = 80;
  const barHeight = Math.min((value / 5) * maxHeight, maxHeight);

  return (
    <Card className="bg-card border-border p-4">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs text-muted-foreground uppercase tracking-wider font-medium">
          VIBRATION
        </span>
        <Badge 
          variant="outline" 
          className={`text-[10px] px-2 py-0.5 ${
            isStable 
              ? 'bg-success/20 text-success border-success/30' 
              : 'bg-warning/20 text-warning border-warning/30'
          }`}
        >
          {isStable ? 'Stable' : 'Elevated'}
        </Badge>
      </div>
      
      <div className="flex items-end justify-center gap-4">
        <div className="text-center">
          <div className="text-3xl font-display font-bold">{value.toFixed(1)}</div>
          <div className="text-xs text-muted-foreground">mm/s</div>
        </div>
        
        <div className="flex items-end gap-1 h-20">
          <div className="w-4 bg-muted rounded-t relative overflow-hidden" style={{ height: maxHeight }}>
            <div 
              className={`absolute bottom-0 left-0 right-0 rounded-t transition-all duration-300 ${
                value < 1.5 ? 'bg-success' : value < 2.5 ? 'bg-warning' : 'bg-destructive'
              }`}
              style={{ 
                height: barHeight,
                boxShadow: `0 0 10px ${value < 1.5 ? 'hsl(var(--success))' : value < 2.5 ? 'hsl(var(--warning))' : 'hsl(var(--destructive))'}` 
              }}
            />
            {/* Threshold markers */}
            <div 
              className="absolute left-0 right-0 h-0.5 bg-warning/50"
              style={{ bottom: (1.5 / 5) * maxHeight }}
            />
            <div 
              className="absolute left-0 right-0 h-0.5 bg-destructive/50"
              style={{ bottom: (2.5 / 5) * maxHeight }}
            />
          </div>
          
          {/* Zone indicator */}
          <div className="flex flex-col justify-between h-20 text-[8px] text-muted-foreground">
            <span>5.0</span>
            <span>2.5</span>
            <span>0</span>
          </div>
        </div>
      </div>
    </Card>
  );
};
