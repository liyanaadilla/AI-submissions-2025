import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Droplet, Filter, Cog, AlertTriangle, Wrench, Thermometer } from 'lucide-react';
import { ScheduledTask } from '@/types/scada';

interface MaintenanceScheduleProps {
  tasks?: ScheduledTask[];
}

const iconMap: Record<string, React.ElementType> = {
  oil_change: Droplet,
  filter: Filter,
  inspection: Cog,
  emergency: AlertTriangle,
  repair: Wrench,
  default: Thermometer,
};

const statusStyles = {
  Soon: 'text-warning',
  OK: 'text-success',
  Overdue: 'text-destructive',
};

export const MaintenanceSchedule = ({ tasks = [] }: MaintenanceScheduleProps) => {
  // If no tasks from API, show placeholder
  const displayTasks = tasks.length > 0 ? tasks : [];

  return (
    <Card className="bg-card border-border p-4">
      <h4 className="text-lg font-display font-semibold mb-4">Maintenance Schedule</h4>

      <div className="space-y-4">
        {displayTasks.map((task) => {
          const Icon = iconMap[task.task_type] || iconMap.default;
          const status = task.status || 'OK';
          return (
            <div
              key={task.task_id}
              className="flex items-center gap-3 p-3 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors"
            >
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                status === 'Overdue' ? 'bg-destructive/20' : 
                status === 'Soon' ? 'bg-warning/20' : 'bg-muted'
              }`}>
                <Icon className={`w-5 h-5 ${
                  status === 'Overdue' ? 'text-destructive' :
                  status === 'Soon' ? 'text-warning' : 'text-muted-foreground'
                }`} />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <p className="font-medium text-sm">{task.name}</p>
                  {task.dtc_codes && task.dtc_codes.length > 0 && (
                    <span className="text-xs font-mono text-amber-400">
                      [{task.dtc_codes.join(', ')}]
                    </span>
                  )}
                </div>
                <p className="text-xs text-muted-foreground">{task.due_in_display}</p>
                {task.priority_score > 0 && (
                  <p className="text-xs text-muted-foreground">
                    Priority: {task.priority_score.toFixed(2)}
                  </p>
                )}
              </div>
              <span className={`text-sm font-medium ${statusStyles[status]}`}>
                {status}
              </span>
            </div>
          );
        })}
        
        {displayTasks.length === 0 && (
          <div className="text-center py-4 text-muted-foreground text-sm">
            No scheduled tasks
          </div>
        )}
      </div>

      <Button className="w-full mt-4 bg-muted hover:bg-muted/80 text-foreground border border-border">
        Schedule Service
      </Button>
    </Card>
  );
};
