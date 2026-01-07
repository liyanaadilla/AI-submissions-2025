export interface SensorData {
  timestamp: number;
  temperature: number;
  rpm: number;
  oil_pressure_psi: number;
  vibration_mms: number;
  voltage_v: number;
  state: EngineState;
  severity: AlertSeverity;
  state_changed: boolean;
  alert_message: string | null;
  simulation_time: number;
  tick_count: number;
  scheduled_tasks: ScheduledTask[];
  ml_insights: MLInsights | null;
  // Enhanced 6-state FSM fields
  dtcs: DTC[];
  active_dtcs: ActiveDTC[];
  drift_rate_per_min: number;
  estimated_rul_seconds: number | null;
  estimated_rul_display: string;
  scheduler_stats: SchedulerStats;
  // Decision tracking
  recent_decisions?: Decision[];
  decision_stats?: DecisionStats;
}

// 6-state FSM (per YSMAI_Project_Planning.txt)
export type EngineState = 'IDLE' | 'WARMUP' | 'NORMAL' | 'WARNING' | 'CRITICAL' | 'SHUTDOWN';

export type AlertSeverity = 'INFO' | 'WARNING' | 'CRITICAL';

export interface DTC {
  code: string;
  description: string;
}

export interface ActiveDTC {
  code: string;
  description: string;
  timestamp: number;
}

export interface SchedulerStats {
  total_tasks: number;
  overdue_count: number;
  soon_count: number;
  simulation_hours: number;
}

export interface ScheduledTask {
  task_id: string;
  name: string;
  description: string;
  task_type: string;
  severity: string;
  asset_criticality: string;
  remaining_hours: number;
  due_in_display: string;
  priority_score: number;
  status: string;
  estimated_duration_min: number;
  dtc_codes: string[];
}

// Decision tracking types
export type DecisionType = 
  | 'STATE_CHANGE' 
  | 'DTC_TRIGGER' 
  | 'DTC_CLEARED' 
  | 'MAINTENANCE' 
  | 'ML_PREDICTION' 
  | 'RUL_ESTIMATE' 
  | 'DRIFT_ALERT'
  | 'FAULT_DETECTED';

export type DecisionCategory = 'OPERATIONAL' | 'DIAGNOSTIC' | 'PREDICTIVE' | 'SAFETY';

export type DecisionSeverity = 'INFO' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface Decision {
  decision_id: string;
  timestamp: number;
  timestamp_display: string;
  tick_count: number;
  decision_type: DecisionType;
  category: DecisionCategory;
  severity: DecisionSeverity;
  title: string;
  description: string;
  trigger_value?: number;
  trigger_threshold?: number;
  previous_state?: string;
  new_state?: string;
  dtc_codes: string[];
  action_recommended?: string;
  confidence?: number;
  metadata: Record<string, unknown>;
}

export interface DecisionStats {
  total_decisions: number;
  by_type: Record<string, number>;
  by_category: Record<string, number>;
  by_severity: Record<string, number>;
  state_transitions: number;
  dtcs_triggered: number;
  faults_detected: number;
  ml_predictions: number;
  session_duration_sec: number;
  decisions_in_memory: number;
}

export interface Report {
  report_metadata: {
    generated_at: string;
    generated_timestamp: number;
    session_start: string;
    session_duration_seconds: number;
    session_duration_display: string;
    report_version: string;
  };
  summary: {
    total_decisions: number;
    state_transitions: number;
    dtcs_triggered: number;
    faults_detected: number;
    ml_predictions: number;
  };
  statistics: {
    by_type: Record<string, number>;
    by_category: Record<string, number>;
    by_severity: Record<string, number>;
  };
  critical_events: Decision[];
  high_priority_events: Decision[];
  state_transitions: Decision[];
  diagnostic_codes: Decision[];
  maintenance_decisions: Decision[];
  ml_predictions: Decision[];
  rul_estimates: Decision[];
  all_decisions: Decision[];
  current_state?: {
    tick_count: number;
    simulation_time: number;
    simulation_hours: number;
    agent_state: string;
    fault_injection_enabled: boolean;
    fault_magnitude: number;
  };
  scheduler_state?: SchedulerStats;
}

export interface MLInsights {
  fault_detection: {
    detected: boolean;
    confidence: number;
    inference_time: number;
  };
  vibration_anomaly: {
    detected: boolean;
    score: number;
    inference_time: number;
  };
  pressure_prediction: {
    predicted_pressure: number;
    actual_pressure: number;
    confidence: number;
    inference_time: number;
  };
}

export interface Alert {
  id: string;
  timestamp: number;
  message: string;
  source: string;
  severity: AlertSeverity;
  dtc_codes?: string[];  // DTC codes associated with alert
}

export interface MaintenanceTask {
  id: string;
  name: string;
  dueIn: string;
  status: 'Soon' | 'OK' | 'Overdue';
  icon: string;
  priority_score?: number;
  dtc_codes?: string[];
}
