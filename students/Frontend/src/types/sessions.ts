/**
 * Session Management Types
 * Interfaces for session tracking, checkpoints, and session comparison
 */

/**
 * Session lifecycle states
 */
export enum SessionStatus {
  ACTIVE = "active",
  CHECKPOINT = "checkpoint",
  ENDED = "ended",
}

/**
 * A snapshot of system state at a checkpoint
 */
export interface SessionCheckpoint {
  checkpoint_id: string;
  session_id: string;
  tick_count: number;
  timestamp: string; // ISO format datetime
  temperature: number;
  rpm: number;
  oil_pressure_psi: number;
  vibration_mms: number;
  voltage_v: number;
  state: string; // e.g., "NORMAL", "CAUTION", "WARNING", "CRITICAL"
  severity: string; // e.g., "INFO", "WARNING", "CRITICAL"
  active_dtcs: string[];
  decision_count: number;
  critical_event_trigger: boolean;
  trigger_reason: string; // e.g., "tick_interval", "critical_temperature"
}

/**
 * Summary statistics for a completed session
 */
export interface SessionSummary {
  session_id: string;
  start_tick: number;
  start_time: string; // ISO format datetime
  end_tick: number;
  end_time: string; // ISO format datetime
  duration_ticks: number;
  duration_seconds: number;

  // Temperature statistics
  temp_min: number;
  temp_max: number;
  temp_avg: number;
  temp_readings_count: number;

  // Decision tracking
  total_decisions: number;
  decision_by_type: Record<string, number>;
  decision_by_severity: Record<string, number>;

  // DTC tracking
  total_dtc_events: number;
  unique_dtc_codes: string[];

  // State transitions
  state_transitions: number;
  max_severity_reached: string;

  // Checkpoint data
  checkpoints_created: number;
  critical_events_triggered: number;
}

/**
 * Complete session data with checkpoints and summary
 */
export interface SessionData {
  summary: SessionSummary;
  checkpoints: SessionCheckpoint[];
  notes?: string;
}

/**
 * Current session information with active checkpoints
 */
export interface CurrentSession {
  session_id: string;
  start_time: string;
  checkpoints: SessionCheckpoint[];
  checkpoint_count: number;
}

/**
 * Response from session history endpoint
 */
export interface SessionHistoryResponse {
  sessions: SessionSummary[];
}

/**
 * Response from end session endpoint
 */
export interface EndSessionResponse {
  status: string;
  session_id: string;
  duration_seconds: number;
  duration_ticks: number;
  decisions: number;
  checkpoints: number;
  temp_min: number;
  temp_max: number;
  temp_avg: number;
  new_session_id: string;
}

/**
 * Checkpoint creation response
 */
export interface CheckpointCreatedResponse {
  status: string;
  checkpoint_id: string;
  session_id: string;
  tick_count: number;
}

/**
 * Session comparison data
 */
export interface SessionComparison {
  session_ids: string[];
  timestamp: string;
  comparison: Record<
    string,
    {
      duration_seconds: number;
      total_decisions: number;
      total_dtc_events: number;
      checkpoints: number;
      temp_range: string;
      max_severity: string;
    }
  >;
  summary: {
    sessions_compared: number;
    total_decisions_all: number;
    total_dtc_events_all: number;
    total_checkpoints_all: number;
    avg_temp_across_sessions: number;
  };
  insights: string[];
}

/**
 * Session decision information
 */
export interface SessionDecisionInfo {
  session_id: string;
  decisions: any[];
  decision_count: number;
  stats_snapshot: {
    total_decisions: number;
    decisions_by_type: Record<string, number>;
    decisions_by_severity: Record<string, number>;
  };
}

/**
 * Session checkpoint batch response
 */
export interface SessionCheckpointBatch {
  session_id: string;
  checkpoints: SessionCheckpoint[];
  checkpoint_count: number;
}
