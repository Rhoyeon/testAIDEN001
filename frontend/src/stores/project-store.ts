import { create } from "zustand";
import {
  projectsApi,
  type ProjectResponse,
  type ProjectDetailResponse,
} from "@/lib/api";

interface ProjectState {
  projects: ProjectResponse[];
  selectedProject: ProjectDetailResponse | null;
  loading: boolean;
  error: string | null;

  fetchProjects: () => Promise<void>;
  fetchProject: (id: string) => Promise<void>;
  createProject: (data: { name: string; description?: string }) => Promise<ProjectDetailResponse>;
  updateProject: (id: string, data: Record<string, unknown>) => Promise<void>;
  deleteProject: (id: string) => Promise<void>;
  startProject: (id: string) => Promise<void>;
  setSelectedProject: (project: ProjectDetailResponse | null) => void;
}

export const useProjectStore = create<ProjectState>((set) => ({
  projects: [],
  selectedProject: null,
  loading: false,
  error: null,

  fetchProjects: async () => {
    set({ loading: true, error: null });
    try {
      const projects = await projectsApi.list();
      set({ projects, loading: false });
    } catch (err) {
      set({ error: (err as Error).message, loading: false });
    }
  },

  fetchProject: async (id: string) => {
    set({ loading: true, error: null });
    try {
      const project = await projectsApi.get(id);
      set({ selectedProject: project, loading: false });
    } catch (err) {
      set({ error: (err as Error).message, loading: false });
    }
  },

  createProject: async (data) => {
    const project = await projectsApi.create(data);
    set((state) => ({ projects: [...state.projects, project] }));
    return project;
  },

  updateProject: async (id, data) => {
    const updated = await projectsApi.update(id, data);
    set((state) => ({
      projects: state.projects.map((p) => (p.id === id ? updated : p)),
      selectedProject: state.selectedProject?.id === id ? updated : state.selectedProject,
    }));
  },

  deleteProject: async (id) => {
    await projectsApi.delete(id);
    set((state) => ({
      projects: state.projects.filter((p) => p.id !== id),
      selectedProject: state.selectedProject?.id === id ? null : state.selectedProject,
    }));
  },

  startProject: async (id) => {
    const updated = await projectsApi.start(id);
    set((state) => ({
      projects: state.projects.map((p) => (p.id === id ? updated : p)),
      selectedProject: state.selectedProject?.id === id ? updated : state.selectedProject,
    }));
  },

  setSelectedProject: (project) => set({ selectedProject: project }),
}));
