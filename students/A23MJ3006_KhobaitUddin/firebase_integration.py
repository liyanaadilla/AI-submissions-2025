"""
Firebase Integration Module for YSMAI Backend
Handles real-time data persistence and audit logging
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List

# Try to import Firebase Admin SDK
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("⚠️  Firebase Admin SDK not installed. Install with: pip3 install firebase-admin")


class FirebaseManager:
    """
    Manages Firebase Firestore connections and data logging
    Gracefully degrades if Firebase is not available or not configured
    """

    def __init__(self):
        self.db = None
        self.enabled = False
        self.error_logged = False
        self._initialize()

    def _initialize(self):
        """Initialize Firebase connection"""
        if not FIREBASE_AVAILABLE:
            return

        try:
            # Resolve Firebase service account key path
            # Priority: FIREBASE_KEY_PATH -> GOOGLE_APPLICATION_CREDENTIALS -> repo root known files
            key_path = os.environ.get("FIREBASE_KEY_PATH") or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

            if not key_path:
                repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
                # Try common filenames in repo root
                candidates = [
                    os.path.join(repo_root, "firebase-key.json"),
                    os.path.join(repo_root, "ysmai-50617-firebase-adminsdk-fbsvc-efd3a85599.json"),
                ]
                # Also scan for any *firebase-adminsdk*.json in repo root
                try:
                    for name in os.listdir(repo_root):
                        if name.endswith(".json") and "firebase-adminsdk" in name:
                            candidates.append(os.path.join(repo_root, name))
                except Exception:
                    pass

                key_path = next((p for p in candidates if os.path.exists(p)), None)

            if not key_path or not os.path.exists(key_path):
                if not self.error_logged:
                    print("ℹ️  Firebase service account key not found.")
                    print("   Set env FIREBASE_KEY_PATH or GOOGLE_APPLICATION_CREDENTIALS")
                    print("   Or place your key at repo root as firebase-key.json")
                    print("   See students/Frontend/INTEGRATION_GUIDE.md for setup.")
                    self.error_logged = True
                return

            # Initialize Firebase Admin SDK (idempotent)
            cred = credentials.Certificate(key_path)
            try:
                firebase_admin.get_app()
            except ValueError:
                firebase_admin.initialize_app(cred)

            # Firestore client
            self.db = firestore.client()
            self.enabled = True

            # Best-effort: report project ID for clarity
            try:
                with open(key_path, "r") as f:
                    svc = json.load(f)
                project_id = svc.get("project_id") or "(unknown)"
            except Exception:
                project_id = "(unknown)"

            print(f"✅ Firebase Firestore connected successfully (project: {project_id})")
            print(f"   Using service account key at: {key_path}")

        except Exception as e:
            if not self.error_logged:
                msg = str(e)
                print(f"ℹ️  Firebase connection failed: {msg}")
                # Common hint if Firestore not yet enabled for the project
                if "not found" in msg.lower() or "failed to connect" in msg.lower():
                    print("   Hint: Ensure Firestore is enabled (Native mode) in Firebase Console")
                print("   System will continue without persistence")
                self.error_logged = True

    def log_sensor_data(self, tick_data: Dict[str, Any]) -> bool:
        """
        Log sensor reading to Firestore
        
        Args:
            tick_data: Complete tick data from simulation
            
        Returns:
            bool: True if logged, False if Firebase unavailable
        """
        if not self.enabled or not self.db:
            return False

        try:
            doc_id = f"tick_{tick_data.get('tick_count', 0)}"

            self.db.collection("sensor_data").document(doc_id).set({
                "timestamp": datetime.utcnow(),
                "tick_count": tick_data.get("tick_count"),
                "temperature": tick_data.get("temperature"),
                "rpm": tick_data.get("rpm"),
                "oil_pressure_psi": tick_data.get("oil_pressure_psi"),
                "vibration_mms": tick_data.get("vibration_mms"),
                "voltage_v": tick_data.get("voltage_v"),
                "state": tick_data.get("state"),
                "severity": tick_data.get("severity"),
                "state_changed": tick_data.get("state_changed"),
                "alert_message": tick_data.get("alert_message"),
                # Enhanced fields for 6-state FSM
                "active_dtcs": tick_data.get("active_dtcs", []),
                "drift_rate_per_min": tick_data.get("drift_rate_per_min", 0.0),
                "estimated_rul_display": tick_data.get("estimated_rul_display"),
                "scheduled_tasks": tick_data.get("scheduled_tasks", []),
                "ml_insights": tick_data.get("ml_insights"),
            })
            return True

        except Exception as e:
            print(f"⚠️  Error logging to Firebase: {str(e)}")
            return False

    def log_alert(self, alert_data: Dict[str, Any]) -> bool:
        """
        Log alert event to Firestore
        
        Args:
            alert_data: Alert event data
            
        Returns:
            bool: True if logged, False if Firebase unavailable
        """
        if not self.enabled or not self.db:
            return False

        try:
            self.db.collection("alerts").add({
                "timestamp": datetime.utcnow(),
                "type": alert_data.get("type"),
                "severity": alert_data.get("severity"),
                "message": alert_data.get("message"),
                "trigger_value": alert_data.get("trigger_value"),
                "threshold": alert_data.get("threshold"),
                "tick_count": alert_data.get("tick_count"),
                # Enhanced: DTC codes
                "dtc_codes": alert_data.get("dtc_codes", []),
                "state": alert_data.get("state"),
            })
            return True

        except Exception as e:
            print(f"⚠️  Error logging alert to Firebase: {str(e)}")
            return False

    def log_audit_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Log audit event to Firestore
        
        Args:
            event_data: Audit event data
            
        Returns:
            bool: True if logged, False if Firebase unavailable
        """
        if not self.enabled or not self.db:
            return False

        try:
            self.db.collection("audit_log").add({
                "timestamp": datetime.utcnow(),
                "event_type": event_data.get("event_type"),
                "description": event_data.get("description"),
                "data": event_data.get("data"),
                "tick_count": event_data.get("tick_count"),
            })
            return True

        except Exception as e:
            print(f"⚠️  Error logging audit event to Firebase: {str(e)}")
            return False

    def get_latest_readings(self, limit: int = 10) -> list:
        """
        Get latest sensor readings from Firestore
        
        Args:
            limit: Number of readings to retrieve
            
        Returns:
            list: Array of sensor data documents
        """
        if not self.enabled or not self.db:
            return []

        try:
            docs = (
                self.db.collection("sensor_data")
                .order_by("timestamp", direction=firestore.Query.DESCENDING)
                .limit(limit)
                .stream()
            )

            readings = []
            for doc in docs:
                reading = doc.to_dict()
                reading["id"] = doc.id
                readings.append(reading)

            return readings

        except Exception as e:
            print(f"⚠️  Error retrieving readings from Firebase: {str(e)}")
            return []

    def get_recent_alerts(self, limit: int = 20) -> list:
        """
        Get recent alerts from Firestore
        
        Args:
            limit: Number of alerts to retrieve
            
        Returns:
            list: Array of alert documents
        """
        if not self.enabled or not self.db:
            return []

        try:
            docs = (
                self.db.collection("alerts")
                .order_by("timestamp", direction=firestore.Query.DESCENDING)
                .limit(limit)
                .stream()
            )

            alerts = []
            for doc in docs:
                alert = doc.to_dict()
                alert["id"] = doc.id
                alerts.append(alert)

            return alerts

        except Exception as e:
            print(f"⚠️  Error retrieving alerts from Firebase: {str(e)}")
            return []

    def is_enabled(self) -> bool:
        """Check if Firebase is enabled and connected"""
        return self.enabled

    def save_session(self, session_data: Dict[str, Any]) -> bool:
        """
        Save a completed session to Firestore
        
        Args:
            session_data: Session summary data (dict from SessionSummary asdict)
            
        Returns:
            bool: True if saved, False if Firebase unavailable
        """
        if not self.enabled or not self.db:
            return False

        try:
            session_id = session_data.get("session_id")
            self.db.collection("sessions").document(session_id).set({
                "timestamp": datetime.utcnow(),
                "session_id": session_id,
                "start_time": session_data.get("start_time"),
                "end_time": session_data.get("end_time"),
                "duration_seconds": session_data.get("duration_seconds"),
                "duration_ticks": session_data.get("duration_ticks"),
                "temp_min": session_data.get("temp_min"),
                "temp_max": session_data.get("temp_max"),
                "temp_avg": session_data.get("temp_avg"),
                "total_decisions": session_data.get("total_decisions"),
                "total_dtc_events": session_data.get("total_dtc_events"),
                "state_transitions": session_data.get("state_transitions"),
                "max_severity_reached": session_data.get("max_severity_reached"),
                "checkpoints_created": session_data.get("checkpoints_created"),
                "critical_events_triggered": session_data.get("critical_events_triggered"),
            })
            return True

        except Exception as e:
            print(f"⚠️  Error saving session to Firebase: {str(e)}")
            return False

    def log_checkpoint(self, checkpoint_data: Dict[str, Any]) -> bool:
        """
        Log a checkpoint snapshot to Firestore
        
        Args:
            checkpoint_data: Checkpoint data (dict from SessionCheckpoint asdict)
            
        Returns:
            bool: True if logged, False if Firebase unavailable
        """
        if not self.enabled or not self.db:
            return False

        try:
            checkpoint_id = checkpoint_data.get("checkpoint_id")
            session_id = checkpoint_data.get("session_id")
            
            self.db.collection("checkpoints").document(checkpoint_id).set({
                "timestamp": datetime.utcnow(),
                "checkpoint_id": checkpoint_id,
                "session_id": session_id,
                "tick_count": checkpoint_data.get("tick_count"),
                "temperature": checkpoint_data.get("temperature"),
                "state": checkpoint_data.get("state"),
                "severity": checkpoint_data.get("severity"),
                "decision_count": checkpoint_data.get("decision_count"),
                "active_dtcs": checkpoint_data.get("active_dtcs", []),
                "critical_event_trigger": checkpoint_data.get("critical_event_trigger", False),
                "trigger_reason": checkpoint_data.get("trigger_reason", ""),
            })
            return True

        except Exception as e:
            print(f"⚠️  Error logging checkpoint to Firebase: {str(e)}")
            return False

    def get_session_by_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a session from Firestore
        
        Args:
            session_id: The session ID to retrieve
            
        Returns:
            dict: Session data if found, None otherwise
        """
        if not self.enabled or not self.db:
            return None

        try:
            doc = self.db.collection("sessions").document(session_id).get()
            if doc.exists:
                data = doc.to_dict()
                data["id"] = doc.id
                return data
            return None

        except Exception as e:
            print(f"⚠️  Error retrieving session from Firebase: {str(e)}")
            return None

    def get_session_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent sessions from Firestore
        
        Args:
            limit: Number of sessions to retrieve
            
        Returns:
            list: Array of session documents
        """
        if not self.enabled or not self.db:
            return []

        try:
            docs = (
                self.db.collection("sessions")
                .order_by("timestamp", direction=firestore.Query.DESCENDING)
                .limit(limit)
                .stream()
            )

            sessions = []
            for doc in docs:
                session = doc.to_dict()
                session["id"] = doc.id
                sessions.append(session)

            return sessions

        except Exception as e:
            print(f"⚠️  Error retrieving session history from Firebase: {str(e)}")
            return []


# Global Firebase manager instance
_firebase_manager = None


def get_firebase_manager() -> FirebaseManager:
    """Get or create the global Firebase manager"""
    global _firebase_manager
    if _firebase_manager is None:
        _firebase_manager = FirebaseManager()
    return _firebase_manager


if __name__ == "__main__":
    print("Running Firebase connectivity diagnostics…")
    mgr = get_firebase_manager()
    if not mgr.is_enabled():
        print("Result: Firebase disabled or not configured. See logs above.")
        raise SystemExit(1)

    # Best-effort read/write diagnostic
    try:
        print("- Attempting a test write to 'diagnostics' collection…")
        payload = {
            "timestamp": datetime.utcnow(),
            "component": "firebase_integration_diagnostic",
            "status": "ok",
        }
        doc_ref = mgr.db.collection("diagnostics").add(payload)[1]
        print(f"  Wrote doc id: {doc_ref.id}")

        print("- Fetching latest diagnostics doc…")
        docs = (
            mgr.db.collection("diagnostics")
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(1)
            .stream()
        )
        latest = next(iter(docs), None)
        if latest:
            print(f"  Read back doc id: {latest.id}")
            print("  Connectivity test PASS ✅")
        else:
            print("  Unable to read back diagnostic doc (but write may have succeeded)")

    except Exception as e:
        print(f"Connectivity test FAIL ⚠️  {e}")
        print("Hint: Ensure Firestore is enabled in your Firebase project and service account has access.")
