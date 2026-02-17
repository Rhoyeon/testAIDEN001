"use client";

import { useEffect, useState } from "react";
import { Plus } from "lucide-react";
import { AppLayout } from "@/components/layout";
import { Button, Spinner } from "@/components/ui";
import { ProjectCard, CreateProjectModal } from "@/components/project";
import { useProjectStore } from "@/stores/project-store";

export default function ProjectsPage() {
  const { projects, loading, fetchProjects, createProject } = useProjectStore();
  const [showCreate, setShowCreate] = useState(false);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  return (
    <AppLayout title="Projects">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">
            Manage your AIDEN development projects
          </p>
        </div>
        <Button icon={<Plus className="h-4 w-4" />} onClick={() => setShowCreate(true)}>
          New Project
        </Button>
      </div>

      {loading ? (
        <div className="mt-12 flex justify-center">
          <Spinner size="lg" />
        </div>
      ) : (
        <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {projects.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      )}

      <CreateProjectModal
        open={showCreate}
        onClose={() => setShowCreate(false)}
        onCreate={async (data) => {
          await createProject(data);
        }}
      />
    </AppLayout>
  );
}
