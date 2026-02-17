import { create } from "zustand";
import type { WebSocketEvent } from "@/types";

type ConnectionStatus = "connecting" | "connected" | "disconnected" | "error";

interface WebSocketState {
  connectionStatus: ConnectionStatus;
  lastEvent: WebSocketEvent | null;
  events: WebSocketEvent[];

  setStatus: (status: ConnectionStatus) => void;
  addEvent: (event: WebSocketEvent) => void;
  clearEvents: () => void;
}

const MAX_EVENTS = 100;

export const useWebSocketStore = create<WebSocketState>((set) => ({
  connectionStatus: "disconnected",
  lastEvent: null,
  events: [],

  setStatus: (status) => set({ connectionStatus: status }),

  addEvent: (event) =>
    set((state) => {
      const newEvents = [event, ...state.events].slice(0, MAX_EVENTS);
      return { lastEvent: event, events: newEvents };
    }),

  clearEvents: () => set({ events: [], lastEvent: null }),
}));
