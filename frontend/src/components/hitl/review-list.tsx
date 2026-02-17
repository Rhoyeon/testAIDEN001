"use client";

import { AlertTriangle, Clock, CheckCircle2, XCircle } from "lucide-react";
import { Card, Badge } from "@/components/ui";
import { cn, formatRelativeTime } from "@/lib/utils";
import type { HITLReviewResponse } from "@/lib/api";

interface ReviewListProps {
  reviews: HITLReviewResponse[];
  onSelect: (review: HITLReviewResponse) => void;
  selectedId?: string;
  className?: string;
}

const statusConfig: Record<string, { icon: React.ReactNode; variant: "default" | "success" | "warning" | "error" | "purple"; label: string }> = {
  pending: { icon: <Clock className="h-3.5 w-3.5" />, variant: "warning", label: "Pending" },
  approved: { icon: <CheckCircle2 className="h-3.5 w-3.5" />, variant: "success", label: "Approved" },
  rejected: { icon: <XCircle className="h-3.5 w-3.5" />, variant: "error", label: "Rejected" },
  revision_requested: { icon: <AlertTriangle className="h-3.5 w-3.5" />, variant: "purple", label: "Revision" },
};

export function ReviewList({ reviews, onSelect, selectedId, className }: ReviewListProps) {
  if (reviews.length === 0) {
    return (
      <Card className={cn("flex flex-col items-center justify-center py-12", className)}>
        <CheckCircle2 className="h-12 w-12 text-gray-300" />
        <p className="mt-3 text-sm text-gray-500">No pending reviews</p>
      </Card>
    );
  }

  return (
    <div className={cn("space-y-2", className)}>
      {reviews.map((review) => {
        const config = statusConfig[review.status] || statusConfig.pending;
        const isSelected = review.id === selectedId;

        return (
          <button
            key={review.id}
            onClick={() => onSelect(review)}
            className={cn(
              "w-full rounded-lg border p-4 text-left transition-all hover:shadow-sm",
              isSelected
                ? "border-aiden-300 bg-aiden-50 shadow-sm"
                : "border-gray-200 bg-white hover:border-gray-300",
            )}
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900">
                  {review.review_type === "ambiguity_review"
                    ? "Ambiguity Review"
                    : "Final Review"}
                </p>
                <p className="mt-0.5 text-xs text-gray-500">
                  ID: {review.id.slice(0, 8)}...
                </p>
              </div>
              <Badge variant={config.variant}>
                {config.icon}
                <span className="ml-1">{config.label}</span>
              </Badge>
            </div>
            <p className="mt-2 text-xs text-gray-400">
              {formatRelativeTime(review.created_at)}
            </p>
          </button>
        );
      })}
    </div>
  );
}
