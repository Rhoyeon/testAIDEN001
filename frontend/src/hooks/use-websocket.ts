"use client";

import { useEffect, useCallback } from "react";
import { getWebSocketManager, type WSMessage } from "@/lib/websocket";
import { useWebSocketStore } from "@/stores/websocket-store";
import type { WebSocketEvent } from "@/types";

/**
 * Custom hook for WebSocket connection to a project's event stream.
 * Uses the singleton WebSocketManager from lib/websocket.
 */
export function useWebSocket(projectId: string | undefined) {
  const status = useWebSocketStore((s) => s.connectionStatus);
  const lastEvent = useWebSocketStore((s) => s.lastEvent);
  const events = useWebSocketStore((s) => s.events);
  const setStatus = useWebSocketStore((s) => s.setStatus);
  const addEvent = useWebSocketStore((s) => s.addEvent);
  const clearEvents = useWebSocketStore((s) => s.clearEvents);

  useEffect(() => {
    if (!projectId) return;

    const manager = getWebSocketManager();

    const unsubState = manager.onStateChange((state) => {
      setStatus(state as "connecting" | "connected" | "disconnected" | "error");
    });

    const unsubMessage = manager.onMessage((msg: WSMessage) => {
      const wsEvent: WebSocketEvent = {
        event_type: msg.event || msg.type || "unknown",
        project_id: msg.project_id || "",
        data: (msg.data as Record<string, unknown>) ?? {},
        timestamp: msg.timestamp || new Date().toISOString(),
      };
      addEvent(wsEvent);
    });

    setStatus("connecting");
    manager.connect(projectId);

    return () => {
      unsubState();
      unsubMessage();
      manager.disconnect();
      clearEvents();
      setStatus("disconnected");
    };
  }, [projectId, setStatus, addEvent, clearEvents]);

  const send = useCallback(
    (data: Record<string, unknown>) => {
      const manager = getWebSocketManager();
      manager.send(data as never);
    },
    [],
  );

  return { status, lastEvent, events, send } as const;
}
