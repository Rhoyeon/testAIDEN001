"use client";

import Link from "next/link";
import { FolderKanban, Clock, Play, ArrowRight } from "lucide-react";
import { Card, Badge, ProgressBar } from "@/components/ui";
import { cn, getStatusColor, getStatusLabel, formatRelativeTime } from "@/lib/utils";

interface ProjectLike {
  id: string;
  name: string;
  description: string | null;
  status: string;
  current_phase: string | null;
  created_at: string;
}

interface ProjectCardProps {
  project: ProjectLike;
  className?: string;
}

const phaseProgress: Record<string, number> = {
  analysis: 25,
  design: 50,
  development: 75,
  testing: 100,
};

export function ProjectCard({ project, className }: ProjectCardProps) {
  const progress = project.current_phase
    ? phaseProgress[project.current_phase] || 0
    : project.status === "completed" ? 100 : 0;

  const statusVariant = project.status === "completed"
    ? "success"
    : project.status === "in_progress"
    ? "info"
    : project.status === "failed"
    ? "error"
    : "default";

  return (
    <Link href={`/projects/${project.id}`}>
      <Card
        className={cn(
          "group cursor-pointer transition-all hover:border-aiden-200 hover:shadow-md",
          className,
        )}
      >
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-aiden-50">
              <FolderKanban className="h-5 w-5 text-aiden-600" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-gray-900 group-hover:text-aiden-700">
                {project.name}
              </h3>
              {project.description && (
                <p className="mt-0.5 text-xs text-gray-500 line-clamp-1">
                  {project.description}
                </p>
              )}
            </div>
          </div>
          <Badge variant={statusVariant}>{getStatusLabel(project.status)}</Badge>
        </div>

        <div className="mt-4">
          <ProgressBar value={progress} size="sm" />
        </div>

        <div className="mt-3 flex items-center justify-between">
          <div className="flex items-center gap-1 text-xs text-gray-400">
            <Clock className="h-3.5 w-3.5" />
            {formatRelativeTime(project.created_at)}
          </div>
          {project.current_phase && (
            <span className="text-xs font-medium text-aiden-600">
              {project.current_phase.charAt(0).toUpperCase() + project.current_phase.slice(1)}
            </span>
          )}
          <ArrowRight className="h-4 w-4 text-gray-300 transition-transform group-hover:translate-x-0.5 group-hover:text-aiden-500" />
        </div>
      </Card>
    </Link>
  );
}
