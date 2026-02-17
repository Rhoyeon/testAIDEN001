"use client";

import { useEffect } from "react";
import {
  FolderKanban,
  Bot,
  AlertTriangle,
  CheckCircle2,
  TrendingUp,
  Clock,
} from "lucide-react";
import { AppLayout } from "@/components/layout";
import { Card, CardHeader, Badge, Spinner } from "@/components/ui";
import { ProjectCard } from "@/components/project";
import { useProjectStore } from "@/stores/project-store";

function StatCard({
  title,
  value,
  icon,
  trend,
}: {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: string;
}) {
  return (
    <Card>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <p className="mt-1 text-2xl font-bold text-gray-900">{value}</p>
          {trend && (
            <p className="mt-1 flex items-center gap-1 text-xs text-green-600">
              <TrendingUp className="h-3 w-3" />
              {trend}
            </p>
          )}
        </div>
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-aiden-50">
          {icon}
        </div>
      </div>
    </Card>
  );
}

export default function DashboardPage() {
  const { projects, loading, fetchProjects } = useProjectStore();

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const activeProjects = projects.filter((p) => p.status === "in_progress");
  const completedProjects = projects.filter((p) => p.status === "completed");

  return (
    <AppLayout title="Dashboard">
      {/* Stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Projects"
          value={projects.length}
          icon={<FolderKanban className="h-6 w-6 text-aiden-600" />}
        />
        <StatCard
          title="Active"
          value={activeProjects.length}
          icon={<Bot className="h-6 w-6 text-green-600" />}
        />
        <StatCard
          title="Pending Reviews"
          value={0}
          icon={<AlertTriangle className="h-6 w-6 text-yellow-600" />}
        />
        <StatCard
          title="Completed"
          value={completedProjects.length}
          icon={<CheckCircle2 className="h-6 w-6 text-purple-600" />}
        />
      </div>

      {/* Recent Projects */}
      <div className="mt-8">
        <CardHeader title="Recent Projects" description="Your latest development projects" />
        {loading ? (
          <div className="mt-6 flex justify-center">
            <Spinner size="lg" />
          </div>
        ) : projects.length === 0 ? (
          <Card className="mt-4 flex flex-col items-center justify-center py-12">
            <FolderKanban className="h-16 w-16 text-gray-200" />
            <p className="mt-4 text-sm text-gray-500">No projects yet</p>
            <p className="mt-1 text-xs text-gray-400">
              Create your first project to get started
            </p>
          </Card>
        ) : (
          <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {projects.slice(0, 6).map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </div>
        )}
      </div>

      {/* Activity Feed */}
      <div className="mt-8">
        <CardHeader title="Recent Activity" description="Latest system events" />
        <Card className="mt-4">
          <div className="flex flex-col items-center justify-center py-8">
            <Clock className="h-10 w-10 text-gray-200" />
            <p className="mt-3 text-sm text-gray-500">No recent activity</p>
          </div>
        </Card>
      </div>
    </AppLayout>
  );
}
