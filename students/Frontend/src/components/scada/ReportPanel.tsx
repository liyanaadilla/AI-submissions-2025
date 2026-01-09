import { useState } from 'react';
import { 
  FileText, 
  Download, 
  RefreshCw, 
  Clock,
  Activity,
  AlertTriangle,
  Brain,
  Settings2,
  ChevronRight
} from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Report } from '@/types/scada';

interface ReportPanelProps {
  onGenerateReport: () => void;
  onDownloadReport: () => void;
  report: Report | null;
  isLoading?: boolean;
}

export const ReportPanel = ({ 
  onGenerateReport, 
  onDownloadReport, 
  report, 
  isLoading = false 
}: ReportPanelProps) => {
  const [activeTab, setActiveTab] = useState<'summary' | 'critical' | 'all'>('summary');

  return (
    <Card className="bg-card border-border p-4">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-sm font-display font-semibold flex items-center gap-2">
          <FileText className="w-4 h-4 text-primary" />
          SYSTEM REPORT
        </h4>
        <div className="flex gap-2">
          <button
            onClick={onGenerateReport}
            disabled={isLoading}
            className="flex items-center gap-1 px-2 py-1 text-xs bg-primary/20 text-primary rounded-md hover:bg-primary/30 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3 h-3 ${isLoading ? 'animate-spin' : ''}`} />
            Generate
          </button>
          <button
            onClick={onDownloadReport}
            disabled={!report || isLoading}
            className="flex items-center gap-1 px-2 py-1 text-xs bg-green-500/20 text-green-400 rounded-md hover:bg-green-500/30 transition-colors disabled:opacity-50"
          >
            <Download className="w-3 h-3" />
            Download
          </button>
        </div>
      </div>

      {!report ? (
        <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
          <FileText className="w-12 h-12 mb-3 opacity-30" />
          <p className="text-sm mb-2">No report generated yet</p>
          <p className="text-xs text-center max-w-[200px]">
            Click "Generate" to create a comprehensive report of all agent decisions
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Report Metadata */}
          <div className="bg-muted/30 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="w-4 h-4 text-muted-foreground" />
              <span className="text-xs text-muted-foreground">
                Generated: {report.report_metadata.generated_at}
              </span>
            </div>
            <div className="text-xs text-muted-foreground">
              Session Duration: <span className="text-foreground font-medium">{report.report_metadata.session_duration_display}</span>
            </div>
          </div>

          {/* Summary Stats */}
          <div className="grid grid-cols-2 gap-2">
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
              <div className="flex items-center gap-2 mb-1">
                <Activity className="w-4 h-4 text-blue-400" />
                <span className="text-xs text-muted-foreground">Total Decisions</span>
              </div>
              <div className="text-2xl font-bold text-blue-400">
                {report.summary.total_decisions}
              </div>
            </div>
            <div className="bg-orange-500/10 border border-orange-500/30 rounded-lg p-3">
              <div className="flex items-center gap-2 mb-1">
                <AlertTriangle className="w-4 h-4 text-orange-400" />
                <span className="text-xs text-muted-foreground">DTCs Triggered</span>
              </div>
              <div className="text-2xl font-bold text-orange-400">
                {report.summary.dtcs_triggered}
              </div>
            </div>
            <div className="bg-purple-500/10 border border-purple-500/30 rounded-lg p-3">
              <div className="flex items-center gap-2 mb-1">
                <Brain className="w-4 h-4 text-purple-400" />
                <span className="text-xs text-muted-foreground">ML Predictions</span>
              </div>
              <div className="text-2xl font-bold text-purple-400">
                {report.summary.ml_predictions}
              </div>
            </div>
            <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3">
              <div className="flex items-center gap-2 mb-1">
                <Settings2 className="w-4 h-4 text-green-400" />
                <span className="text-xs text-muted-foreground">State Changes</span>
              </div>
              <div className="text-2xl font-bold text-green-400">
                {report.summary.state_transitions}
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-1 border-b border-border">
            {[
              { id: 'summary', label: 'Summary' },
              { id: 'critical', label: 'Critical' },
              { id: 'all', label: 'All Decisions' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as typeof activeTab)}
                className={`px-3 py-2 text-xs font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'text-primary border-b-2 border-primary -mb-px'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="max-h-[300px] overflow-y-auto">
            {activeTab === 'summary' && (
              <div className="space-y-3">
                {/* By Type */}
                <div>
                  <h5 className="text-xs font-medium text-muted-foreground mb-2">By Type</h5>
                  <div className="space-y-1">
                    {Object.entries(report.statistics.by_type).map(([type, count]) => (
                      <div key={type} className="flex items-center justify-between text-xs">
                        <span className="text-foreground">{type.replace(/_/g, ' ')}</span>
                        <span className="font-mono text-muted-foreground">{count}</span>
                      </div>
                    ))}
                  </div>
                </div>
                
                {/* By Severity */}
                <div>
                  <h5 className="text-xs font-medium text-muted-foreground mb-2">By Severity</h5>
                  <div className="space-y-1">
                    {Object.entries(report.statistics.by_severity).map(([severity, count]) => (
                      <div key={severity} className="flex items-center justify-between text-xs">
                        <span className={
                          severity === 'CRITICAL' ? 'text-red-400' :
                          severity === 'HIGH' ? 'text-orange-400' :
                          severity === 'MEDIUM' ? 'text-yellow-400' :
                          'text-green-400'
                        }>
                          {severity}
                        </span>
                        <span className="font-mono text-muted-foreground">{count}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Current State */}
                {report.current_state && (
                  <div>
                    <h5 className="text-xs font-medium text-muted-foreground mb-2">Current State</h5>
                    <div className="bg-muted/30 rounded-lg p-2 text-xs space-y-1">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Agent State:</span>
                        <span className="text-foreground font-medium">{report.current_state.agent_state}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Tick Count:</span>
                        <span className="text-foreground font-mono">{report.current_state.tick_count}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Sim Hours:</span>
                        <span className="text-foreground font-mono">{report.current_state.simulation_hours.toFixed(2)}</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'critical' && (
              <div className="space-y-2">
                {report.critical_events.length === 0 && report.high_priority_events.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground text-xs">
                    No critical or high priority events
                  </div>
                ) : (
                  [...report.critical_events, ...report.high_priority_events].slice(0, 15).map((event) => (
                    <div key={event.decision_id} className="border border-border rounded-lg p-2 bg-muted/20">
                      <div className="flex items-center gap-2">
                        <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                          event.severity === 'CRITICAL' ? 'bg-red-500/20 text-red-400' : 'bg-orange-500/20 text-orange-400'
                        }`}>
                          {event.severity}
                        </span>
                        <span className="text-xs font-medium text-foreground">{event.title}</span>
                      </div>
                      <p className="text-[10px] text-muted-foreground mt-1 line-clamp-2">
                        {event.description}
                      </p>
                      <div className="text-[10px] text-muted-foreground mt-1">
                        Tick {event.tick_count}
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {activeTab === 'all' && (
              <div className="space-y-1">
                {report.all_decisions.slice(0, 25).map((decision) => (
                  <div 
                    key={decision.decision_id}
                    className="flex items-center gap-2 text-xs p-2 rounded hover:bg-muted/30 transition-colors"
                  >
                    <ChevronRight className="w-3 h-3 text-muted-foreground flex-shrink-0" />
                    <span className={`text-[10px] px-1 rounded ${
                      decision.severity === 'CRITICAL' ? 'bg-red-500/20 text-red-400' :
                      decision.severity === 'HIGH' ? 'bg-orange-500/20 text-orange-400' :
                      decision.severity === 'MEDIUM' ? 'bg-yellow-500/20 text-yellow-400' :
                      'bg-blue-500/20 text-blue-400'
                    }`}>
                      {decision.severity.charAt(0)}
                    </span>
                    <span className="text-foreground flex-1 truncate">{decision.title}</span>
                    <span className="text-muted-foreground font-mono text-[10px]">
                      #{decision.tick_count}
                    </span>
                  </div>
                ))}
                {report.all_decisions.length > 25 && (
                  <div className="text-center text-[10px] text-muted-foreground py-2">
                    +{report.all_decisions.length - 25} more decisions in full report
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </Card>
  );
};
