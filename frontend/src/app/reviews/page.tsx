"use client";

import { useEffect, useState } from "react";
import { AppLayout } from "@/components/layout";
import { Spinner } from "@/components/ui";
import { ReviewPanel, ReviewList } from "@/components/hitl";
import { useHITLStore } from "@/stores/hitl-store";
import type { HITLReviewResponse } from "@/lib/api";

export default function ReviewsPage() {
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

  const [selectedReview, setSelectedReview] = useState<HITLReviewResponse | null>(null);

  useEffect(() => {
    fetchPendingReviews();
  }, [fetchPendingReviews]);

  const handleSelect = (review: HITLReviewResponse) => {
    setSelectedReview(review);
    fetchReview(review.id);
  };

  return (
    <AppLayout title="Reviews">
      <p className="text-sm text-gray-500">
        Review and approve agent outputs before finalization
      </p>

      {loading && !pendingReviews.length ? (
        <div className="mt-12 flex justify-center">
          <Spinner size="lg" />
        </div>
      ) : (
        <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Review List */}
          <div className="lg:col-span-1">
            <ReviewList
              reviews={pendingReviews}
              onSelect={handleSelect}
              selectedId={selectedReview?.id}
            />
          </div>

          {/* Review Detail */}
          <div className="lg:col-span-2">
            {currentReview ? (
              <ReviewPanel
                review={currentReview}
                onApprove={approveReview}
                onReject={rejectReview}
                onRequestRevision={requestRevision}
              />
            ) : (
              <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-gray-300 py-20">
                <p className="text-sm text-gray-400">
                  Select a review from the list to get started
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </AppLayout>
  );
}
