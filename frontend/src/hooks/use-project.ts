"use client";

import { useEffect, useCallback } from "react";
import { useProjectStore } from "@/stores/project-store";

/**
 * Custom hook for project data and operations.
 * Uses the Zustand project-store for state management.
 */
export function useProject(projectId?: string) {
  const {
    selectedProject: project,
    loading,
    error,
    fetchProject,
    startProject: storeStartProject,
    updateProject: storeUpdateProject,
  } = useProjectStore();

  useEffect(() => {
    if (projectId) {
      fetchProject(projectId);
    }
  }, [projectId, fetchProject]);

  const refetch = useCallback(() => {
    if (projectId) {
      return fetchProject(projectId);
    }
    return Promise.resolve();
  }, [projectId, fetchProject]);

  const startProject = useCallback(async () => {
    if (!projectId) return;
    await storeStartProject(projectId);
  }, [projectId, storeStartProject]);

  const updateProject = useCallback(
    async (data: Record<string, unknown>) => {
      if (!projectId) return;
      await storeUpdateProject(projectId, data);
    },
    [projectId, storeUpdateProject],
  );

  return {
    project,
    phases: project?.phases ?? [],
    loading,
    error,
    refetch,
    startProject,
    updateProject,
  } as const;
}
