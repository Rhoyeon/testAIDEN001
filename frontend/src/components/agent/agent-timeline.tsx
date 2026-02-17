"use client";

import { CheckCircle2, Circle, Loader2, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

export interface TimelineNode {
  name: string;
  label: string;
  status: "pending" | "running" | "completed" | "error";
  duration?: number;
}

interface AgentTimelineProps {
  nodes: TimelineNode[];
  className?: string;
}

const statusIcon: Record<string, React.ReactNode> = {
  pending: <Circle className="h-5 w-5 text-gray-300" />,
  running: <Loader2 className="h-5 w-5 animate-spin text-aiden-500" />,
  completed: <CheckCircle2 className="h-5 w-5 text-green-500" />,
  error: <AlertCircle className="h-5 w-5 text-red-500" />,
};

export function AgentTimeline({ nodes, className }: AgentTimelineProps) {
  return (
    <div className={cn("space-y-0", className)}>
      {nodes.map((node, index) => (
        <div key={node.name} className="flex gap-3">
          {/* Timeline connector */}
          <div className="flex flex-col items-center">
            <div className="flex-shrink-0">{statusIcon[node.status]}</div>
            {index < nodes.length - 1 && (
              <div
                className={cn(
                  "w-0.5 flex-1 min-h-[24px]",
                  node.status === "completed" ? "bg-green-300" : "bg-gray-200",
                )}
              />
            )}
          </div>

          {/* Node content */}
          <div className="pb-4">
            <p
              className={cn(
                "text-sm font-medium",
                node.status === "running" && "text-aiden-700",
                node.status === "completed" && "text-gray-700",
                node.status === "pending" && "text-gray-400",
                node.status === "error" && "text-red-600",
              )}
            >
              {node.label}
            </p>
            {node.duration !== undefined && node.status === "completed" && (
              <p className="text-xs text-gray-400">{(node.duration / 1000).toFixed(1)}s</p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
