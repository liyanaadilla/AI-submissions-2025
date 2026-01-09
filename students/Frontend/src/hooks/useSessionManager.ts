/**
 * Session Manager Hook
 * React hook for managing sessions, checkpoints, and session history
 */

import { useState, useCallback, useEffect } from "react";
import {
  SessionStatus,
  CurrentSession,
  SessionSummary,
  SessionCheckpoint,
  SessionComparison,
  SessionDecisionInfo,
} from "@/types/sessions";

const API_URL = "http://localhost:8000";

/**
 * Hook for managing session operations
 */
export function useSessionManager() {
  const [currentSession, setCurrentSession] = useState<CurrentSession | null>(
    null
  );
  const [sessionHistory, setSessionHistory] = useState<SessionSummary[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Get the current active session
   */
  const getCurrentSession = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/sessions/current`);
      if (!response.ok) {
        throw new Error(`Failed to fetch current session: ${response.statusText}`);
      }

      const data = await response.json();
      setCurrentSession(data);
      return data;
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Unknown error";
      setError(errorMessage);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Get session history
   */
  const getSessionHistory = useCallback(async (limit: number = 10) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/sessions/history?limit=${limit}`);
      if (!response.ok) {
        throw new Error(
          `Failed to fetch session history: ${response.statusText}`
        );
      }

      const data = await response.json();
      setSessionHistory(data.sessions || []);
      return data.sessions;
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Unknown error";
      setError(errorMessage);
      return [];
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Create a manual checkpoint for the current session
   */
  const createCheckpoint = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/sessions/checkpoint`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      if (!response.ok) {
        throw new Error(`Failed to create checkpoint: ${response.statusText}`);
      }

      const data = await response.json();

      // Refresh current session to show new checkpoint
      await getCurrentSession();

      return data;
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Unknown error";
      setError(errorMessage);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [getCurrentSession]);

  /**
   * End the current session and start a new one
   */
  const endSession = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/sessions/end`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      if (!response.ok) {
        throw new Error(`Failed to end session: ${response.statusText}`);
      }

      const data = await response.json();

      // Refresh both current session and history
      await getCurrentSession();
      await getSessionHistory();

      return data;
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Unknown error";
      setError(errorMessage);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [getCurrentSession, getSessionHistory]);

  /**
   * Get checkpoints for a specific session
   */
  const getSessionCheckpoints = useCallback(
    async (sessionId: string) => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await fetch(`${API_URL}/sessions/${sessionId}/checkpoints`);
        if (!response.ok) {
          throw new Error(
            `Failed to fetch checkpoints: ${response.statusText}`
          );
        }

        const data = await response.json();
        return data.checkpoints;
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Unknown error";
        setError(errorMessage);
        return [];
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  /**
   * Get summary for a specific session
   */
  const getSessionSummary = useCallback(async (sessionId: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/sessions/${sessionId}/summary`);
      if (!response.ok) {
        throw new Error(`Failed to fetch session summary: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Unknown error";
      setError(errorMessage);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Get decisions made during a specific session
   */
  const getSessionDecisions = useCallback(
    async (sessionId: string): Promise<SessionDecisionInfo | null> => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await fetch(`${API_URL}/sessions/${sessionId}/decisions`);
        if (!response.ok) {
          throw new Error(`Failed to fetch decisions: ${response.statusText}`);
        }

        const data = await response.json();
        return data;
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Unknown error";
        setError(errorMessage);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  /**
   * Compare multiple sessions
   */
  const compareSessions = useCallback(
    async (sessionIds: string[]): Promise<SessionComparison | null> => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await fetch(`${API_URL}/sessions/compare`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ session_ids: sessionIds }),
        });

        if (!response.ok) {
          throw new Error(`Failed to compare sessions: ${response.statusText}`);
        }

        const data = await response.json();
        return data;
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Unknown error";
        setError(errorMessage);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  /**
   * Initialize by fetching current session
   */
  useEffect(() => {
    getCurrentSession();
  }, [getCurrentSession]);

  return {
    // State
    currentSession,
    sessionHistory,
    isLoading,
    error,

    // Operations
    getCurrentSession,
    getSessionHistory,
    createCheckpoint,
    endSession,
    getSessionCheckpoints,
    getSessionSummary,
    getSessionDecisions,
    compareSessions,
  };
}

export type UseSessionManagerReturn = ReturnType<typeof useSessionManager>;
