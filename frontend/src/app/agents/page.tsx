"use client";

import { Bot, Cpu, Clock, Zap } from "lucide-react";
import { AppLayout } from "@/components/layout";
import { Card, CardHeader, Badge } from "@/components/ui";

const agentDefinitions = [
  {
    name: "Ryan",
    phase: "Analysis",
    description:
      "Analyzes development request documents, extracts requirements, detects ambiguities, and generates requirements specification with traceability matrix.",
    status: "ready",
    capabilities: [
      "Document Analysis (PDF/DOCX)",
      "RAG-based Context Retrieval",
      "Requirements Extraction & Classification",
      "Ambiguity Detection",
      "Traceability Matrix Generation",
      "Requirements Specification Generation",
    ],
    model: "GPT-4.1 / Claude Sonnet 4",
  },
  {
    name: "TBD",
    phase: "Design",
    description: "Will handle system design phase including architecture, data model, and API design.",
    status: "planned",
    capabilities: ["Architecture Design", "Data Model Design", "API Specification"],
    model: "TBD",
  },
  {
    name: "TBD",
    phase: "Development",
    description: "Will handle code generation and implementation based on design specifications.",
    status: "planned",
    capabilities: ["Code Generation", "Unit Test Generation", "Code Review"],
    model: "TBD",
  },
  {
    name: "TBD",
    phase: "Testing",
    description: "Will handle test planning, test case generation, and quality assurance.",
    status: "planned",
    capabilities: ["Test Plan Generation", "Test Case Design", "QA Validation"],
    model: "TBD",
  },
];

export default function AgentsPage() {
  return (
    <AppLayout title="Agents">
      <p className="text-sm text-gray-500">
        AI agents powering each phase of the development lifecycle
      </p>

      <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-2">
        {agentDefinitions.map((agent) => (
          <Card key={agent.phase}>
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-aiden-50">
                  <Bot className="h-6 w-6 text-aiden-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{agent.name}</h3>
                  <p className="text-xs text-gray-500">{agent.phase} Phase</p>
                </div>
              </div>
              <Badge variant={agent.status === "ready" ? "success" : "default"}>
                {agent.status === "ready" ? "Ready" : "Planned"}
              </Badge>
            </div>

            <p className="mt-3 text-sm text-gray-600">{agent.description}</p>

            <div className="mt-4">
              <h4 className="flex items-center gap-1 text-xs font-medium text-gray-500">
                <Zap className="h-3 w-3" /> Capabilities
              </h4>
              <div className="mt-2 flex flex-wrap gap-1.5">
                {agent.capabilities.map((cap) => (
                  <span
                    key={cap}
                    className="rounded-md bg-gray-100 px-2 py-0.5 text-xs text-gray-600"
                  >
                    {cap}
                  </span>
                ))}
              </div>
            </div>

            <div className="mt-4 flex items-center gap-1 text-xs text-gray-400">
              <Cpu className="h-3 w-3" />
              Model: {agent.model}
            </div>
          </Card>
        ))}
      </div>
    </AppLayout>
  );
}
