import { CheckCircle2, Clock, AlertTriangle, Wrench } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { ScheduledTask } from '@/types/scada';

interface ScheduledTasksPanelProps {
  tasks: ScheduledTask[];
}

export const ScheduledTasksPanel = ({ tasks }: ScheduledTasksPanelProps) => {
  const getSeverityColor = (severity: string) => {
    switch (severity?.toUpperCase()) {
      case 'CRITICAL':
        return 'text-red-500 bg-red-500/10 border-red-500/30';
      case 'HIGH':
        return 'text-orange-500 bg-orange-500/10 border-orange-500/30';
      case 'MEDIUM':
        return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/30';
      case 'LOW':
        return 'text-green-500 bg-green-500/10 border-green-500/30';
      default:
        return 'text-muted-foreground bg-muted/10 border-muted/30';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'OVERDUE':
        return 'text-red-500';
      case 'DUE_SOON':
        return 'text-yellow-500';
      case 'OK':
        return 'text-green-500';
      default:
        return 'text-muted-foreground';
    }
  };

  // Filter out undefined tasks
  const validTasks = tasks?.filter(task => task && task.task_id) || [];

  return (
    <Card className="bg-card border-border p-4">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-sm font-display font-semibold flex items-center gap-2">
          <Wrench className="w-4 h-4 text-primary" />
          MAINTENANCE SCHEDULE
        </h4>
        <div className="bg-secondary text-secondary-foreground border border-secondary rounded-full px-2.5 py-0.5 text-xs font-semibold">
          {validTasks.length} {validTasks.length === 1 ? 'task' : 'tasks'}
        </div>
      </div>

      {validTasks.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
          <CheckCircle2 className="w-8 h-8 mb-2 opacity-50" />
          <p className="text-xs">No scheduled tasks</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-[300px] overflow-y-auto">
          {validTasks.slice(0, 10).map((task, index) => (
            <div
              key={task.task_id || index}
              className="border border-border rounded-lg p-3 bg-muted/30 hover:bg-muted/50 transition-colors"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <Wrench className="w-3 h-3 text-primary" />
                    <span className={`text-xs font-medium ${getSeverityColor(task.severity || 'LOW')}`}>
                      {task.severity || 'NORMAL'}
                    </span>
                  </div>
                  <p className="text-sm font-semibold text-foreground mt-1">
                    {task.name || task.task_type || 'Maintenance Task'}
                  </p>
                </div>
                {task.priority_score !== undefined && (
                  <div className="bg-primary/10 text-primary border border-primary/30 rounded-full px-2 py-0.5 text-xs font-mono">
                    P: {task.priority_score.toFixed(2)}
                  </div>
                )}
              </div>

              <div className="space-y-2 text-xs">
                {task.description && (
                  <p className="text-muted-foreground text-xs">{task.description}</p>
                )}
                <div className="flex justify-between text-muted-foreground">
                  <span>Due:</span>
                  <span className={`font-medium ${getStatusColor(task.status || 'OK')}`}>
                    {task.due_in_display || `${task.remaining_hours?.toFixed(0)}h remaining`}
                  </span>
                </div>
                {task.estimated_duration_min && (
                  <div className="flex justify-between text-muted-foreground">
                    <span>Duration:</span>
                    <span className="text-foreground">{task.estimated_duration_min} min</span>
                  </div>
                )}
                {task.dtc_codes && task.dtc_codes.length > 0 && (
                  <div className="flex justify-between text-muted-foreground">
                    <span>DTCs:</span>
                    <div className="flex gap-1">
                      {task.dtc_codes.map((dtc: string) => (
                        <span key={dtc} className="bg-red-500/10 text-red-500 border border-red-500/30 rounded px-1.5 py-0.5 text-xs font-mono">
                          {dtc}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                <div className="flex justify-between text-muted-foreground">
                  <span>Criticality:</span>
                  <span className={`font-medium ${getSeverityColor(task.asset_criticality || 'NORMAL')}`}>
                    {task.asset_criticality || 'NORMAL'}
                  </span>
                </div>
              </div>
            </div>
          ))}

          {validTasks.length > 10 && (
            <div className="text-center text-xs text-muted-foreground py-2">
              +{validTasks.length - 10} more {validTasks.length - 10 === 1 ? 'task' : 'tasks'}
            </div>
          )}
        </div>
      )}

      <div className="border-t border-border mt-4 pt-3">
        <p className="text-xs text-muted-foreground">
          Priority score: P = (Severity × Criticality) / RUL. Tasks sorted by priority.
        </p>
      </div>
    </Card>
  );
};
