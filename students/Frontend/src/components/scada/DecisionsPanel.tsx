import { useState, useEffect } from 'react';
import { 
  Brain, 
  AlertTriangle, 
  Activity, 
  Settings2, 
  Shield,
  ChevronDown,
  ChevronUp,
  Clock,
  Zap,
  Gauge
} from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Decision, DecisionStats } from '@/types/scada';

interface DecisionsPanelProps {
  decisions: Decision[];
  stats?: DecisionStats;
}

export const DecisionsPanel = ({ decisions, stats }: DecisionsPanelProps) => {
  const [expanded, setExpanded] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>('all');

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'STATE_CHANGE':
        return <Activity className="w-4 h-4" />;
      case 'DTC_TRIGGER':
      case 'DTC_CLEARED':
        return <AlertTriangle className="w-4 h-4" />;
      case 'ML_PREDICTION':
        return <Brain className="w-4 h-4" />;
      case 'MAINTENANCE':
        return <Settings2 className="w-4 h-4" />;
      case 'RUL_ESTIMATE':
        return <Clock className="w-4 h-4" />;
      case 'DRIFT_ALERT':
        return <Zap className="w-4 h-4" />;
      case 'FAULT_DETECTED':
        return <Shield className="w-4 h-4" />;
      default:
        return <Gauge className="w-4 h-4" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity?.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-red-500/20 text-red-400 border-red-500/50';
      case 'HIGH':
        return 'bg-orange-500/20 text-orange-400 border-orange-500/50';
      case 'MEDIUM':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50';
      case 'LOW':
        return 'bg-green-500/20 text-green-400 border-green-500/50';
      default:
        return 'bg-blue-500/20 text-blue-400 border-blue-500/50';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'SAFETY':
        return 'text-red-400';
      case 'DIAGNOSTIC':
        return 'text-orange-400';
      case 'PREDICTIVE':
        return 'text-purple-400';
      case 'OPERATIONAL':
        return 'text-blue-400';
      default:
        return 'text-gray-400';
    }
  };

  const filteredDecisions = decisions?.filter(d => {
    if (filter === 'all') return true;
    if (filter === 'critical') return d.severity === 'CRITICAL' || d.severity === 'HIGH';
    if (filter === 'state') return d.decision_type === 'STATE_CHANGE';
    if (filter === 'dtc') return d.decision_type === 'DTC_TRIGGER' || d.decision_type === 'DTC_CLEARED';
    if (filter === 'ml') return d.decision_type === 'ML_PREDICTION' || d.decision_type === 'RUL_ESTIMATE';
    return true;
  }) || [];

  return (
    <Card className="bg-card border-border p-4">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-sm font-display font-semibold flex items-center gap-2">
          <Brain className="w-4 h-4 text-purple-400" />
          AGENT DECISIONS
        </h4>
        {stats && (
          <div className="flex items-center gap-2 text-xs">
            <span className="bg-purple-500/20 text-purple-400 px-2 py-0.5 rounded-full">
              {stats.total_decisions} total
            </span>
          </div>
        )}
      </div>

      {/* Quick Stats */}
      {stats && (
        <div className="grid grid-cols-4 gap-2 mb-4">
          <div className="bg-muted/30 rounded-lg p-2 text-center">
            <div className="text-lg font-bold text-blue-400">{stats.state_transitions}</div>
            <div className="text-[10px] text-muted-foreground">States</div>
          </div>
          <div className="bg-muted/30 rounded-lg p-2 text-center">
            <div className="text-lg font-bold text-orange-400">{stats.dtcs_triggered}</div>
            <div className="text-[10px] text-muted-foreground">DTCs</div>
          </div>
          <div className="bg-muted/30 rounded-lg p-2 text-center">
            <div className="text-lg font-bold text-purple-400">{stats.ml_predictions}</div>
            <div className="text-[10px] text-muted-foreground">ML</div>
          </div>
          <div className="bg-muted/30 rounded-lg p-2 text-center">
            <div className="text-lg font-bold text-red-400">{stats.faults_detected}</div>
            <div className="text-[10px] text-muted-foreground">Faults</div>
          </div>
        </div>
      )}

      {/* Filter Tabs */}
      <div className="flex gap-1 mb-3 overflow-x-auto">
        {['all', 'critical', 'state', 'dtc', 'ml'].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-2 py-1 text-xs rounded-md transition-colors whitespace-nowrap ${
              filter === f
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted/30 text-muted-foreground hover:bg-muted/50'
            }`}
          >
            {f === 'all' ? 'All' : f === 'critical' ? 'Critical' : f === 'state' ? 'State' : f === 'dtc' ? 'DTC' : 'ML'}
          </button>
        ))}
      </div>

      {/* Decisions List */}
      <div className="space-y-2 max-h-[400px] overflow-y-auto">
        {filteredDecisions.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground text-sm">
            No decisions yet. Run the simulation to see agent decisions.
          </div>
        ) : (
          filteredDecisions.slice(0, 20).map((decision) => (
            <div
              key={decision.decision_id}
              className="border border-border rounded-lg bg-muted/20 overflow-hidden"
            >
              <div
                className="p-3 cursor-pointer hover:bg-muted/40 transition-colors"
                onClick={() => setExpanded(expanded === decision.decision_id ? null : decision.decision_id)}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-start gap-2 flex-1 min-w-0">
                    <div className={getCategoryColor(decision.category)}>
                      {getTypeIcon(decision.decision_type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-sm font-medium text-foreground truncate">
                          {decision.title}
                        </span>
                        <span className={`text-[10px] px-1.5 py-0.5 rounded border ${getSeverityColor(decision.severity)}`}>
                          {decision.severity}
                        </span>
                      </div>
                      <div className="text-xs text-muted-foreground mt-0.5">
                        Tick {decision.tick_count} • {decision.category}
                      </div>
                    </div>
                  </div>
                  {expanded === decision.decision_id ? (
                    <ChevronUp className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                  )}
                </div>
              </div>

              {expanded === decision.decision_id && (
                <div className="px-3 pb-3 pt-0 border-t border-border/50 bg-muted/10">
                  <p className="text-xs text-muted-foreground mt-2">
                    {decision.description}
                  </p>
                  
                  {decision.action_recommended && (
                    <div className="mt-2 p-2 bg-primary/10 rounded text-xs">
                      <span className="font-medium text-primary">Recommended:</span>{' '}
                      <span className="text-foreground">{decision.action_recommended}</span>
                    </div>
                  )}

                  {decision.dtc_codes?.length > 0 && (
                    <div className="flex gap-1 mt-2 flex-wrap">
                      {decision.dtc_codes.map((code) => (
                        <span
                          key={code}
                          className="text-[10px] bg-red-500/20 text-red-400 px-1.5 py-0.5 rounded font-mono"
                        >
                          {code}
                        </span>
                      ))}
                    </div>
                  )}

                  {decision.confidence !== undefined && decision.confidence !== null && (
                    <div className="mt-2 text-xs text-muted-foreground">
                      Confidence: <span className="text-foreground font-medium">{(decision.confidence * 100).toFixed(1)}%</span>
                    </div>
                  )}

                  <div className="mt-2 text-[10px] text-muted-foreground">
                    {decision.timestamp_display}
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {filteredDecisions.length > 20 && (
        <div className="text-center text-xs text-muted-foreground pt-2 border-t border-border mt-2">
          Showing 20 of {filteredDecisions.length} decisions
        </div>
      )}
    </Card>
  );
};
