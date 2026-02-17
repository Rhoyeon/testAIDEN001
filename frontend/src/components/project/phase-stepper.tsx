"use client";

import { Check, Circle, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface PhaseItem {
  id: string;
  phase_type: string;
  phase_order: number;
  status: string;
}

interface PhaseStepperProps {
  phases: PhaseItem[];
  className?: string;
}

const phaseLabels: Record<string, string> = {
  analysis: "Analysis",
  design: "Design",
  development: "Development",
  testing: "Testing",
};

const phaseColors: Record<string, string> = {
  analysis: "bg-phase-analysis",
  design: "bg-phase-design",
  development: "bg-phase-development",
  testing: "bg-phase-testing",
};

export function PhaseStepper({ phases, className }: PhaseStepperProps) {
  const sortedPhases = [...phases].sort((a, b) => a.phase_order - b.phase_order);

  return (
    <div className={cn("flex items-center", className)}>
      {sortedPhases.map((phase, index) => {
        const isCompleted = phase.status === "completed";
        const isActive = phase.status === "in_progress";
        const isPending = phase.status === "pending";

        return (
          <div key={phase.id} className="flex items-center">
            {/* Step circle */}
            <div className="flex flex-col items-center">
              <div
                className={cn(
                  "flex h-10 w-10 items-center justify-center rounded-full border-2 transition-colors",
                  isCompleted && `${phaseColors[phase.phase_type]} border-transparent text-white`,
                  isActive && "border-aiden-500 bg-aiden-50 text-aiden-600",
                  isPending && "border-gray-300 bg-white text-gray-400",
                )}
              >
                {isCompleted ? (
                  <Check className="h-5 w-5" />
                ) : isActive ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <Circle className="h-5 w-5" />
                )}
              </div>
              <span
                className={cn(
                  "mt-2 text-xs font-medium",
                  isActive ? "text-aiden-700" : isCompleted ? "text-gray-700" : "text-gray-400",
                )}
              >
                {phaseLabels[phase.phase_type] || phase.phase_type}
              </span>
            </div>

            {/* Connector line */}
            {index < sortedPhases.length - 1 && (
              <div
                className={cn(
                  "mx-2 h-0.5 w-16",
                  isCompleted ? "bg-green-400" : "bg-gray-200",
                )}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
