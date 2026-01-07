import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert } from '@/types/scada';
import { Button } from '@/components/ui/button';

interface AlertLogProps {
  alerts: Alert[];
}

export const AlertLog = ({ alerts }: AlertLogProps) => {
  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    });
  };

  const severityStyles = {
    INFO: 'bg-primary/20 text-primary border-primary/30',
    WARNING: 'bg-warning/20 text-warning border-warning/30',
    CRITICAL: 'bg-destructive/20 text-destructive border-destructive/30',
  };

  return (
    <Card className="bg-card border-border p-4">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-lg font-display font-semibold">System Alert Log</h4>
        <Button variant="link" className="text-primary p-0 h-auto text-sm">
          View All
        </Button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left py-2 px-3 text-xs text-muted-foreground font-medium uppercase tracking-wider">
                Timestamp
              </th>
              <th className="text-left py-2 px-3 text-xs text-muted-foreground font-medium uppercase tracking-wider">
                DTC
              </th>
              <th className="text-left py-2 px-3 text-xs text-muted-foreground font-medium uppercase tracking-wider">
                Message
              </th>
              <th className="text-left py-2 px-3 text-xs text-muted-foreground font-medium uppercase tracking-wider">
                Source
              </th>
              <th className="text-left py-2 px-3 text-xs text-muted-foreground font-medium uppercase tracking-wider">
                Severity
              </th>
            </tr>
          </thead>
          <tbody>
            {alerts.slice(0, 5).map((alert) => (
              <tr key={alert.id} className="border-b border-border/50 hover:bg-muted/30 transition-colors">
                <td className="py-3 px-3 font-mono text-muted-foreground">
                  {formatTime(alert.timestamp)}
                </td>
                <td className="py-3 px-3 font-mono text-amber-400">
                  {alert.dtc_codes && alert.dtc_codes.length > 0 
                    ? alert.dtc_codes.join(', ') 
                    : '—'}
                </td>
                <td className="py-3 px-3">{alert.message}</td>
                <td className="py-3 px-3 text-muted-foreground">{alert.source}</td>
                <td className="py-3 px-3">
                  <Badge
                    variant="outline"
                    className={`text-xs ${severityStyles[alert.severity]}`}
                  >
                    {alert.severity}
                  </Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {alerts.length === 0 && (
        <div className="text-center py-8 text-muted-foreground">
          No alerts recorded
        </div>
      )}
    </Card>
  );
};
