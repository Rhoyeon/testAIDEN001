"use client";

import { cn } from "@/lib/utils";

interface LogEntry {
  id: string;
  timestamp: string;
  level: "info" | "warning" | "error" | "debug";
  node_name?: string;
  event_type?: string;
  message: string;
}

interface AgentLogViewerProps {
  logs: LogEntry[];
  maxHeight?: string;
  className?: string;
}

const levelColors: Record<string, string> = {
  info: "text-blue-600",
  warning: "text-yellow-600",
  error: "text-red-600",
  debug: "text-gray-400",
};

const levelBg: Record<string, string> = {
  info: "bg-blue-50",
  warning: "bg-yellow-50",
  error: "bg-red-50",
  debug: "bg-gray-50",
};

export function AgentLogViewer({ logs, maxHeight = "400px", className }: AgentLogViewerProps) {
  return (
    <div
      className={cn("overflow-y-auto rounded-lg border border-gray-200 bg-gray-950", className)}
      style={{ maxHeight }}
    >
      <div className="p-3 space-y-1">
        {logs.length === 0 ? (
          <p className="text-center text-sm text-gray-500 py-8">No logs yet...</p>
        ) : (
          logs.map((log) => (
            <div
              key={log.id}
              className="flex gap-2 rounded px-2 py-1 font-mono text-xs"
            >
              <span className="flex-shrink-0 text-gray-500">
                {new Date(log.timestamp).toLocaleTimeString()}
              </span>
              <span className={cn("flex-shrink-0 uppercase font-bold w-12", levelColors[log.level])}>
                {log.level}
              </span>
              {log.node_name && (
                <span className="flex-shrink-0 text-purple-400">[{log.node_name}]</span>
              )}
              <span className="text-gray-300">{log.message}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
