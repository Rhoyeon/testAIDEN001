"use client";

import { useEffect, useMemo, useState } from "react";
import { useWebSocket } from "@/hooks/use-websocket";

/** Known Ryan agent nodes and approximate cumulative progress. */
const NODE_PROGRESS_MAP: Record<string, number> = {
  load_document: 9,
  retrieve_context: 18,
  extract_requirements: 27,
  classify_requirements: 36,
  detect_ambiguities: 45,
  hitl_ambiguity_review: 54,
  refine_requirements: 63,
  build_traceability: 72,
  generate_spec_document: 81,
  hitl_final_review: 90,
  finalize_deliverables: 100,
};

interface AgentLogEntry {
  timestamp: string;
  eventType: string;
  node: string | null;
  message: string;
}

/**
 * Custom hook for tracking agent execution progress via WebSocket events.
 */
export function useAgentStream(projectId: string | undefined) {
  const { events } = useWebSocket(projectId);
  const [currentNode, setCurrentNode] = useState<string | null>(null);
  const [status, setStatus] = useState<string>("idle");
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState<AgentLogEntry[]>([]);

  // Filter for agent events only
  const agentEvents = useMemo(
    () => events.filter((e) => e.event_type.startsWith("agent.")),
    [events],
  );

  useEffect(() => {
    if (agentEvents.length === 0) return;

    const latest = agentEvents[0]; // events are newest-first from the store
    if (!latest) return;

    const { event_type, data } = latest;

    // Log every agent event
    setLogs((prev) => [
      {
        timestamp: latest.timestamp,
        eventType: event_type,
        node: (data?.node_name as string) ?? null,
        message: (data?.message as string) ?? event_type,
      },
      ...prev,
    ].slice(0, 200));

    switch (event_type) {
      case "agent.started":
        setStatus("running");
        setProgress(0);
        break;
      case "agent.node.enter": {
        const nodeName = data?.node_name as string | undefined;
        if (nodeName) {
          setCurrentNode(nodeName);
          const pct = NODE_PROGRESS_MAP[nodeName];
          if (pct !== undefined) setProgress(pct);
        }
        break;
      }
      case "agent.completed":
        setStatus("completed");
        setProgress(100);
        break;
      case "agent.error":
        setStatus("error");
        break;
      case "agent.hitl.requested":
        setStatus("waiting_for_review");
        break;
      case "agent.hitl.resolved":
        setStatus("running");
        break;
      default:
        break;
    }
  }, [agentEvents]);

  // Reset when projectId changes
  useEffect(() => {
    return () => {
      setCurrentNode(null);
      setStatus("idle");
      setProgress(0);
      setLogs([]);
    };
  }, [projectId]);

  return { currentNode, status, progress, logs } as const;
}
