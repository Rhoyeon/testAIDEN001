"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Play, FileText, Bot, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { AppLayout } from "@/components/layout";
import { Button, Card, CardHeader, Badge, Spinner } from "@/components/ui";
import { PhaseStepper, DocumentUpload } from "@/components/project";
import { AgentMonitor } from "@/components/agent";
import { ReviewPanel } from "@/components/hitl";
import { useProjectStore } from "@/stores/project-store";
import { phasesApi, type PhaseResponse } from "@/lib/api";
import { getStatusLabel } from "@/lib/utils";

export default function ProjectDetailPage() {
  const params = useParams();
  const projectId = params?.id as string;
  const { selectedProject, loading, fetchProject, startProject } = useProjectStore();
  const [phases, setPhases] = useState<PhaseResponse[]>([]);
  const [starting, setStarting] = useState(false);

  useEffect(() => {
    if (projectId) {
      fetchProject(projectId);
      phasesApi.list(projectId).then(setPhases).catch(console.error);
    }
  }, [projectId, fetchProject]);

  if (loading || !selectedProject) {
    return (
      <AppLayout title="Project">
        <div className="flex justify-center py-20">
          <Spinner size="lg" />
        </div>
      </AppLayout>
    );
  }

  const handleStart = async () => {
    setStarting(true);
    try {
      await startProject(projectId);
      const updatedPhases = await phasesApi.list(projectId);
      setPhases(updatedPhases);
    } finally {
      setStarting(false);
    }
  };

  const statusVariant = selectedProject.status === "completed"
    ? "success"
    : selectedProject.status === "in_progress"
    ? "info"
    : selectedProject.status === "failed"
    ? "error"
    : "default";

  return (
    <AppLayout title={selectedProject.name}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link href="/projects" className="rounded-lg p-1 text-gray-400 hover:bg-gray-100">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <h2 className="text-xl font-bold text-gray-900">{selectedProject.name}</h2>
            {selectedProject.description && (
              <p className="mt-0.5 text-sm text-gray-500">{selectedProject.description}</p>
            )}
          </div>
          <Badge variant={statusVariant} size="md">
            {getStatusLabel(selectedProject.status)}
          </Badge>
        </div>
        {selectedProject.status === "created" && (
          <Button
            icon={<Play className="h-4 w-4" />}
            loading={starting}
            onClick={handleStart}
          >
            Start Project
          </Button>
        )}
      </div>

      {/* Phase Stepper */}
      {phases.length > 0 && (
        <Card className="mt-6">
          <PhaseStepper phases={phases} />
        </Card>
      )}

      {/* Main Content Grid */}
      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Left: Documents & Deliverables */}
        <div className="lg:col-span-2 space-y-6">
          {/* Document Upload */}
          <div>
            <CardHeader title="Documents" description="Upload development request documents" />
            <div className="mt-3">
              <DocumentUpload projectId={projectId} />
            </div>
          </div>

          {/* Agent Monitor (shown when project is running) */}
          {selectedProject.status === "in_progress" && (
            <AgentMonitor
              agentName="Ryan"
              status="running"
              currentNode="extract_requirements"
              completedNodes={["load_document", "retrieve_context"]}
            />
          )}
        </div>

        {/* Right: Status & Actions */}
        <div className="space-y-6">
          <Card>
            <CardHeader title="Project Info" />
            <dl className="mt-4 space-y-3">
              <div className="flex justify-between text-sm">
                <dt className="text-gray-500">Status</dt>
                <dd className="font-medium">{getStatusLabel(selectedProject.status)}</dd>
              </div>
              <div className="flex justify-between text-sm">
                <dt className="text-gray-500">Current Phase</dt>
                <dd className="font-medium">
                  {selectedProject.current_phase
                    ? selectedProject.current_phase.charAt(0).toUpperCase() +
                      selectedProject.current_phase.slice(1)
                    : "-"}
                </dd>
              </div>
              <div className="flex justify-between text-sm">
                <dt className="text-gray-500">Created</dt>
                <dd className="font-medium">
                  {new Date(selectedProject.created_at).toLocaleDateString("ko-KR")}
                </dd>
              </div>
            </dl>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader title="Quick Actions" />
            <div className="mt-4 space-y-2">
              <Button variant="secondary" className="w-full justify-start" icon={<FileText className="h-4 w-4" />}>
                View Deliverables
              </Button>
              <Button variant="secondary" className="w-full justify-start" icon={<Bot className="h-4 w-4" />}>
                Agent History
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </AppLayout>
  );
}
