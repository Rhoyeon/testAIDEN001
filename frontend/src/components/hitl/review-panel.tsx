"use client";

import { useState } from "react";
import {
  CheckCircle2,
  XCircle,
  RotateCcw,
  AlertTriangle,
  FileText,
  MessageSquare,
} from "lucide-react";
import { Card, CardHeader, Badge, Button } from "@/components/ui";
import { cn } from "@/lib/utils";
import type { HITLReviewResponse } from "@/lib/api";

interface ReviewPanelProps {
  review: HITLReviewResponse;
  onApprove: (id: string, feedback?: string) => Promise<void>;
  onReject: (id: string, feedback: string) => Promise<void>;
  onRequestRevision: (id: string, feedback: string) => Promise<void>;
  className?: string;
}

export function ReviewPanel({
  review,
  onApprove,
  onReject,
  onRequestRevision,
  className,
}: ReviewPanelProps) {
  const [feedback, setFeedback] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeAction, setActiveAction] = useState<string | null>(null);

  const handleAction = async (action: "approve" | "reject" | "revision") => {
    if ((action === "reject" || action === "revision") && !feedback.trim()) {
      return;
    }
    setLoading(true);
    setActiveAction(action);
    try {
      if (action === "approve") {
        await onApprove(review.id, feedback || undefined);
      } else if (action === "reject") {
        await onReject(review.id, feedback);
      } else {
        await onRequestRevision(review.id, feedback);
      }
    } finally {
      setLoading(false);
      setActiveAction(null);
    }
  };

  const snapshot = review.content_snapshot || {};

  return (
    <Card className={cn("", className)}>
      <CardHeader
        title="Human Review Required"
        description={`Review Type: ${review.review_type}`}
        action={
          <Badge variant="purple" size="md">
            <AlertTriangle className="mr-1 h-3 w-3" />
            Pending Review
          </Badge>
        }
      />

      {/* Review Content */}
      <div className="mt-4 space-y-4">
        {/* Content Snapshot Preview */}
        <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
          <div className="mb-2 flex items-center gap-2 text-sm font-medium text-gray-700">
            <FileText className="h-4 w-4" />
            Content to Review
          </div>
          <div className="max-h-96 overflow-y-auto">
            {Array.isArray(snapshot.requirements) && (
              <div className="space-y-2">
                <h5 className="text-sm font-medium text-gray-600">
                  Requirements ({(snapshot.requirements as unknown[]).length})
                </h5>
                <ul className="space-y-1">
                  {(snapshot.requirements as Array<{ id: string; title: string; priority?: string }>).map(
                    (req, i) => (
                      <li key={i} className="rounded bg-white px-3 py-2 text-sm">
                        <span className="font-mono text-xs text-gray-400">{req.id}</span>
                        <span className="ml-2">{req.title}</span>
                        {req.priority && (
                          <Badge
                            variant={req.priority === "high" ? "error" : "default"}
                            className="ml-2"
                          >
                            {req.priority}
                          </Badge>
                        )}
                      </li>
                    ),
                  )}
                </ul>
              </div>
            )}

            {Array.isArray(snapshot.ambiguities) && (
              <div className="mt-4 space-y-2">
                <h5 className="text-sm font-medium text-gray-600">
                  Ambiguities ({(snapshot.ambiguities as unknown[]).length})
                </h5>
                <ul className="space-y-1">
                  {(snapshot.ambiguities as Array<{ description: string; suggestion: string }>).map(
                    (amb, i) => (
                      <li key={i} className="rounded bg-yellow-50 px-3 py-2 text-sm">
                        <p className="text-yellow-800">{amb.description}</p>
                        <p className="mt-1 text-xs text-yellow-600">
                          Suggestion: {amb.suggestion}
                        </p>
                      </li>
                    ),
                  )}
                </ul>
              </div>
            )}

            {!Array.isArray(snapshot.requirements) && !Array.isArray(snapshot.ambiguities) && (
              <pre className="text-xs text-gray-600 whitespace-pre-wrap">
                {JSON.stringify(snapshot, null, 2)}
              </pre>
            )}
          </div>
        </div>

        {/* Feedback Input */}
        <div>
          <label className="mb-1 flex items-center gap-2 text-sm font-medium text-gray-700">
            <MessageSquare className="h-4 w-4" />
            Feedback
          </label>
          <textarea
            className="input-field min-h-[100px] resize-y"
            placeholder="Enter your feedback here... (required for reject/revision)"
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
          />
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3">
          <Button
            variant="primary"
            icon={<CheckCircle2 className="h-4 w-4" />}
            loading={loading && activeAction === "approve"}
            onClick={() => handleAction("approve")}
            disabled={loading}
          >
            Approve
          </Button>
          <Button
            variant="secondary"
            icon={<RotateCcw className="h-4 w-4" />}
            loading={loading && activeAction === "revision"}
            onClick={() => handleAction("revision")}
            disabled={loading || !feedback.trim()}
          >
            Request Revision
          </Button>
          <Button
            variant="danger"
            icon={<XCircle className="h-4 w-4" />}
            loading={loading && activeAction === "reject"}
            onClick={() => handleAction("reject")}
            disabled={loading || !feedback.trim()}
          >
            Reject
          </Button>
        </div>
      </div>
    </Card>
  );
}
