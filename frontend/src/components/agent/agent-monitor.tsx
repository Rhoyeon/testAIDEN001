"use client";

import { Bot, Clock, Zap, DollarSign } from "lucide-react";
import { Card, CardHeader, Badge, ProgressBar } from "@/components/ui";
import { AgentTimeline, type TimelineNode } from "./agent-timeline";
import { cn } from "@/lib/utils";

// Ryan agent node definitions
const RYAN_NODES: { name: string; label: string }[] = [
  { name: "load_document", label: "Load Document" },
  { name: "retrieve_context", label: "RAG Retrieval" },
  { name: "extract_requirements", label: "Extract Requirements" },
  { name: "classify_requirements", label: "Classify Requirements" },
  { name: "detect_ambiguities", label: "Detect Ambiguities" },
  { name: "hitl_ambiguity_review", label: "HITL: Ambiguity Review" },
  { name: "refine_requirements", label: "Refine Requirements" },
  { name: "build_traceability", label: "Build Traceability Matrix" },
  { name: "generate_spec_document", label: "Generate Spec Document" },
  { name: "hitl_final_review", label: "HITL: Final Review" },
  { name: "finalize_deliverables", label: "Finalize Deliverables" },
];

interface AgentMonitorProps {
  agentName: string;
  status: string;
  currentNode?: string;
  totalTokens?: number;
  totalCost?: number;
  startedAt?: string;
  completedNodes?: string[];
  errorNode?: string;
  className?: string;
}

export function AgentMonitor({
  agentName,
  status,
  currentNode,
  totalTokens = 0,
  totalCost = 0,
  startedAt,
  completedNodes = [],
  errorNode,
  className,
}: AgentMonitorProps) {
  const nodes: TimelineNode[] = RYAN_NODES.map((n) => {
    let nodeStatus: TimelineNode["status"] = "pending";
    if (n.name === errorNode) nodeStatus = "error";
    else if (n.name === currentNode) nodeStatus = "running";
    else if (completedNodes.includes(n.name)) nodeStatus = "completed";
    return { ...n, status: nodeStatus };
  });

  const progress = RYAN_NODES.length > 0
    ? (completedNodes.length / RYAN_NODES.length) * 100
    : 0;

  const statusVariant = status === "running"
    ? "info"
    : status === "completed"
    ? "success"
    : status === "failed"
    ? "error"
    : "default";

  return (
    <Card className={cn("", className)}>
      <CardHeader
        title={`Agent: ${agentName}`}
        description="Real-time execution monitor"
        action={<Badge variant={statusVariant}>{status}</Badge>}
      />

      <div className="mt-4">
        <ProgressBar value={progress} showLabel />
      </div>

      {/* Stats */}
      <div className="mt-4 grid grid-cols-3 gap-4">
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <Zap className="h-4 w-4" />
          <span>{totalTokens.toLocaleString()} tokens</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <DollarSign className="h-4 w-4" />
          <span>${totalCost.toFixed(4)}</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <Clock className="h-4 w-4" />
          <span>{startedAt ? "Running" : "Waiting"}</span>
        </div>
      </div>

      {/* Timeline */}
      <div className="mt-6">
        <h4 className="mb-3 text-sm font-medium text-gray-700">Execution Flow</h4>
        <AgentTimeline nodes={nodes} />
      </div>
    </Card>
  );
}
