import { create } from "zustand";
import { hitlApi, type HITLReviewResponse } from "@/lib/api";

type HITLReview = HITLReviewResponse;

interface HITLState {
  pendingReviews: HITLReview[];
  currentReview: HITLReview | null;
  loading: boolean;
  error: string | null;

  fetchPendingReviews: () => Promise<void>;
  fetchReview: (id: string) => Promise<void>;
  approveReview: (id: string, feedback?: string) => Promise<void>;
  rejectReview: (id: string, feedback: string) => Promise<void>;
  requestRevision: (id: string, feedback: string, edits?: Record<string, unknown>) => Promise<void>;
  addPendingReview: (review: HITLReview) => void;
}

export const useHITLStore = create<HITLState>((set) => ({
  pendingReviews: [],
  currentReview: null,
  loading: false,
  error: null,

  fetchPendingReviews: async () => {
    set({ loading: true, error: null });
    try {
      const reviews = await hitlApi.listPending();
      set({ pendingReviews: reviews, loading: false });
    } catch (err) {
      set({ error: (err as Error).message, loading: false });
    }
  },

  fetchReview: async (id) => {
    set({ loading: true, error: null });
    try {
      const review = await hitlApi.get(id);
      set({ currentReview: review, loading: false });
    } catch (err) {
      set({ error: (err as Error).message, loading: false });
    }
  },

  approveReview: async (id, feedback) => {
    await hitlApi.approve(id, feedback);
    set((state) => ({
      pendingReviews: state.pendingReviews.filter((r) => r.id !== id),
      currentReview: state.currentReview?.id === id ? null : state.currentReview,
    }));
  },

  rejectReview: async (id, feedback) => {
    await hitlApi.reject(id, feedback);
    set((state) => ({
      pendingReviews: state.pendingReviews.filter((r) => r.id !== id),
      currentReview: state.currentReview?.id === id ? null : state.currentReview,
    }));
  },

  requestRevision: async (id, feedback, edits) => {
    await hitlApi.requestRevision(id, feedback, edits);
    set((state) => ({
      pendingReviews: state.pendingReviews.filter((r) => r.id !== id),
      currentReview: state.currentReview?.id === id ? null : state.currentReview,
    }));
  },

  addPendingReview: (review) =>
    set((state) => ({
      pendingReviews: [...state.pendingReviews, review],
    })),
}));
