"use client";

import { useEffect } from "react";
import { useHITLStore } from "@/stores/hitl-store";
import { useWebSocket } from "@/hooks/use-websocket";

/**
 * Custom hook for HITL review management.
 * Fetches pending reviews and listens for real-time HITL events.
 */
export function useHITL(projectId?: string, reviewId?: string) {
  const {
    pendingReviews,
    currentReview,
    loading,
    fetchPendingReviews,
    fetchReview,
    approveReview,
    rejectReview,
    requestRevision,
  } = useHITLStore();

  const { events } = useWebSocket(projectId);

  // Initial fetch
  useEffect(() => {
    fetchPendingReviews();
  }, [fetchPendingReviews]);

  useEffect(() => {
    if (reviewId) {
      fetchReview(reviewId);
    }
  }, [reviewId, fetchReview]);

  // React to HITL WebSocket events
  useEffect(() => {
    if (events.length === 0) return;
    const latest = events[0]; // newest-first
    if (!latest) return;

    if (latest.event_type === "agent.hitl.requested") {
      fetchPendingReviews();
    }
  }, [events, fetchPendingReviews]);

  return {
    pendingReviews,
    currentReview,
    loading,
    approve: approveReview,
    reject: rejectReview,
    requestRevision,
  } as const;
}
