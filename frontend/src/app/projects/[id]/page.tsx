"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import {
  Play,
  FileText,
  Bot,
  ArrowLeft,
  Database,
  CheckCircle2,
  Clock,
  RefreshCw,
} from "lucide-react";
import Link from "next/link";
import { AppLayout } from "@/components/layout";
import { Button, Card, CardHeader, Badge, Spinner } from "@/components/ui";
import { PhaseStepper, DocumentUpload } from "@/components/project";
import { AgentMonitor } from "@/components/agent";
import { ReviewPanel } from "@/components/hitl";
import { useProjectStore } from "@/stores/project-store";
import {
  phasesApi,
  documentsApi,
  deliverablesApi,
  agentsApi,
  type PhaseResponse,
  type DocumentResponse,
  type DeliverableResponse,
  type AgentExecutionResponse,
} from "@/lib/api";
import { getStatusLabel } from "@/lib/utils";

export default function ProjectDetailPage() {
  const params = useParams();
  const projectId = params?.id as string;
  const { selectedProject, loading, fetchProject, startProject } =
    useProjectStore();
  const [phases, setPhases] = useState<PhaseResponse[]>([]);
  const [documents, setDocuments] = useState<DocumentResponse[]>([]);
  const [deliverables, setDeliverables] = useState<DeliverableResponse[]>([]);
  const [starting, setStarting] = useState(false);

  const fetchDocuments = useCallback(async () => {
    if (!projectId) return;
    try {
      const docs = await documentsApi.list(projectId);
      setDocuments(docs);
    } catch (err) {
      console.error("Failed to fetch documents:", err);
    }
  }, [projectId]);

  const fetchDeliverables = useCallback(
    async (phaseList: PhaseResponse[]) => {
      const allDeliverables: DeliverableResponse[] = [];
      for (const phase of phaseList) {
        if (phase.status === "completed") {
          try {
            const dels = await deliverablesApi.list(phase.id);
            allDeliverables.push(...dels);
          } catch {
            // Phase may not have deliverables yet
          }
        }
      }
      setDeliverables(allDeliverables);
    },
    [],
  );

  useEffect(() => {
    if (projectId) {
      fetchProject(projectId);
      phasesApi.list(projectId).then((p) => {
        setPhases(p);
        fetchDeliverables(p);
      }).catch(console.error);
      fetchDocuments();
    }
  }, [projectId, fetchProject, fetchDocuments, fetchDeliverables]);

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
      // Refetch project to get updated status
      await fetchProject(projectId);
    } finally {
      setStarting(false);
    }
  };

  const handleUploadComplete = () => {
    fetchDocuments();
  };

  const handleRefresh = async () => {
    await fetchProject(projectId);
    const updatedPhases = await phasesApi.list(projectId);
    setPhases(updatedPhases);
    await fetchDocuments();
    await fetchDeliverables(updatedPhases);
  };

  const statusVariant =
    selectedProject.status === "completed"
      ? "success"
      : selectedProject.status === "analysis" ||
          selectedProject.status === "in_progress"
        ? "info"
        : selectedProject.status === "failed"
          ? "error"
          : "default";

  const isRunning =
    selectedProject.status === "analysis" ||
    selectedProject.status === "design" ||
    selectedProject.status === "development" ||
    selectedProject.status === "testing" ||
    selectedProject.status === "in_progress";

  // Find the active phase for agent monitoring
  const activePhase = phases.find((p) => p.status === "in_progress");

  return (
    <AppLayout title={selectedProject.name}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link
            href="/projects"
            className="rounded-lg p-1 text-gray-400 hover:bg-gray-100"
          >
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <h2 className="text-xl font-bold text-gray-900">
              {selectedProject.name}
            </h2>
            {selectedProject.description && (
              <p className="mt-0.5 text-sm text-gray-500">
                {selectedProject.description}
              </p>
            )}
          </div>
          <Badge variant={statusVariant} size="md">
            {getStatusLabel(selectedProject.status)}
          </Badge>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            icon={<RefreshCw className="h-4 w-4" />}
            onClick={handleRefresh}
          >
            Refresh
          </Button>
          {selectedProject.status === "created" && (
            <Button
              icon={<Play className="h-4 w-4" />}
              loading={starting}
              onClick={handleStart}
              disabled={documents.length === 0}
            >
              Start Project
            </Button>
          )}
        </div>
      </div>

      {/* Phase Stepper */}
      {phases.length > 0 && (
        <Card className="mt-6">
          <PhaseStepper phases={phases} />
        </Card>
      )}

      {/* Main Content Grid */}
      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Left: Documents, Agent, Deliverables */}
        <div className="space-y-6 lg:col-span-2">
          {/* Document Upload & List */}
          <div>
            <CardHeader
              title="Documents"
              description={`${documents.length} document(s) uploaded`}
            />
            <div className="mt-3">
              <DocumentUpload
                projectId={projectId}
                onUploadComplete={handleUploadComplete}
              />
            </div>

            {/* Uploaded Document List */}
            {documents.length > 0 && (
              <div className="mt-4 space-y-2">
                {documents.map((doc) => (
                  <div
                    key={doc.id}
                    className="flex items-center justify-between rounded-lg border border-gray-200 bg-white px-4 py-3"
                  >
                    <div className="flex items-center gap-3">
                      <FileText className="h-5 w-5 text-gray-400" />
                      <div>
                        <p className="text-sm font-medium text-gray-800">
                          {doc.title}
                        </p>
                        <p className="text-xs text-gray-500">
                          {doc.file_name} &middot;{" "}
                          {doc.file_size
                            ? `${(doc.file_size / 1024).toFixed(0)} KB`
                            : ""}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge
                        variant={doc.doc_type === "dev_request" ? "info" : "default"}
                        size="sm"
                      >
                        {doc.doc_type}
                      </Badge>
                      {doc.is_indexed ? (
                        <Badge variant="success" size="sm">
                          <CheckCircle2 className="mr-1 h-3 w-3" />
                          Indexed
                        </Badge>
                      ) : (
                        <Badge variant="default" size="sm">
                          <Clock className="mr-1 h-3 w-3" />
                          Pending
                        </Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Agent Monitor (shown when project is running) */}
          {isRunning && activePhase && (
            <AgentMonitor
              agentName={activePhase.agent_name || "Ryan"}
              status="running"
              currentNode={undefined}
              completedNodes={[]}
            />
          )}

          {/* Deliverables (shown after completion) */}
          {deliverables.length > 0 && (
            <div>
              <CardHeader
                title="Deliverables"
                description="Generated artifacts from agent execution"
              />
              <div className="mt-3 space-y-3">
                {deliverables.map((del) => (
                  <Card key={del.id}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Database className="h-5 w-5 text-aiden-500" />
                        <div>
                          <p className="text-sm font-semibold text-gray-800">
                            {del.title}
                          </p>
                          <p className="text-xs text-gray-500">
                            Type: {del.deliverable_type} &middot; Format:{" "}
                            {del.format || "text"} &middot; Version v
                            {del.current_version}
                          </p>
                        </div>
                      </div>
                      <Badge
                        variant={
                          del.status === "approved"
                            ? "success"
                            : del.status === "draft"
                              ? "default"
                              : "info"
                        }
                        size="sm"
                      >
                        {del.status}
                      </Badge>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right: Status & Actions */}
        <div className="space-y-6">
          <Card>
            <CardHeader title="Project Info" />
            <dl className="mt-4 space-y-3">
              <div className="flex justify-between text-sm">
                <dt className="text-gray-500">Status</dt>
                <dd className="font-medium">
                  {getStatusLabel(selectedProject.status)}
                </dd>
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
                <dt className="text-gray-500">Documents</dt>
                <dd className="font-medium">{documents.length}</dd>
              </div>
              <div className="flex justify-between text-sm">
                <dt className="text-gray-500">Indexed</dt>
                <dd className="font-medium">
                  {documents.filter((d) => d.is_indexed).length} /{" "}
                  {documents.length}
                </dd>
              </div>
              <div className="flex justify-between text-sm">
                <dt className="text-gray-500">Deliverables</dt>
                <dd className="font-medium">{deliverables.length}</dd>
              </div>
              <div className="flex justify-between text-sm">
                <dt className="text-gray-500">Created</dt>
                <dd className="font-medium">
                  {new Date(selectedProject.created_at).toLocaleDateString(
                    "ko-KR",
                  )}
                </dd>
              </div>
            </dl>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader title="Quick Actions" />
            <div className="mt-4 space-y-2">
              <Button
                variant="secondary"
                className="w-full justify-start"
                icon={<FileText className="h-4 w-4" />}
                disabled={deliverables.length === 0}
              >
                View Deliverables ({deliverables.length})
              </Button>
              <Button
                variant="secondary"
                className="w-full justify-start"
                icon={<Bot className="h-4 w-4" />}
              >
                Agent History
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </AppLayout>
  );
}
