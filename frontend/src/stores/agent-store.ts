import { create } from "zustand";
import type { AgentExecution, AgentLog } from "@/types";

interface AgentState {
  executions: Map<string, AgentExecution>;
  logs: Map<string, AgentLog[]>;
  activeExecutionId: string | null;

  setExecution: (execution: AgentExecution) => void;
  addLog: (executionId: string, log: AgentLog) => void;
  setActiveExecution: (id: string | null) => void;
  clearLogs: (executionId: string) => void;
}

export const useAgentStore = create<AgentState>((set) => ({
  executions: new Map(),
  logs: new Map(),
  activeExecutionId: null,

  setExecution: (execution) =>
    set((state) => {
      const newExecs = new Map(state.executions);
      newExecs.set(execution.id, execution);
      return { executions: newExecs };
    }),

  addLog: (executionId, log) =>
    set((state) => {
      const newLogs = new Map(state.logs);
      const existing = newLogs.get(executionId) || [];
      newLogs.set(executionId, [...existing, log]);
      return { logs: newLogs };
    }),

  setActiveExecution: (id) => set({ activeExecutionId: id }),

  clearLogs: (executionId) =>
    set((state) => {
      const newLogs = new Map(state.logs);
      newLogs.delete(executionId);
      return { logs: newLogs };
    }),
}));
