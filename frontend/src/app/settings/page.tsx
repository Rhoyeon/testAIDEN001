"use client";

import { Settings, Key, Database, Bot, Globe } from "lucide-react";
import { AppLayout } from "@/components/layout";
import { Card, CardHeader, Button } from "@/components/ui";

export default function SettingsPage() {
  return (
    <AppLayout title="Settings">
      <p className="text-sm text-gray-500">
        Configure AIDEN platform settings
      </p>

      <div className="mt-6 space-y-6">
        {/* LLM Configuration */}
        <Card>
          <CardHeader
            title="LLM Providers"
            description="Configure API keys for AI models"
            action={<Button size="sm" variant="secondary">Save</Button>}
          />
          <div className="mt-4 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">OpenAI API Key</label>
              <div className="mt-1 flex gap-2">
                <input
                  type="password"
                  className="input-field flex-1"
                  placeholder="sk-..."
                />
                <Button variant="ghost" size="sm" icon={<Key className="h-4 w-4" />}>
                  Test
                </Button>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Anthropic API Key</label>
              <div className="mt-1 flex gap-2">
                <input
                  type="password"
                  className="input-field flex-1"
                  placeholder="sk-ant-..."
                />
                <Button variant="ghost" size="sm" icon={<Key className="h-4 w-4" />}>
                  Test
                </Button>
              </div>
            </div>
          </div>
        </Card>

        {/* Database */}
        <Card>
          <CardHeader
            title="Database"
            description="PostgreSQL and Redis connection settings"
          />
          <div className="mt-4 space-y-3">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2 text-gray-500">
                <Database className="h-4 w-4" /> PostgreSQL
              </div>
              <span className="text-gray-400">Configured via environment variables</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2 text-gray-500">
                <Database className="h-4 w-4" /> Redis
              </div>
              <span className="text-gray-400">Configured via environment variables</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2 text-gray-500">
                <Globe className="h-4 w-4" /> ChromaDB
              </div>
              <span className="text-gray-400">Configured via environment variables</span>
            </div>
          </div>
        </Card>

        {/* Agent Configuration */}
        <Card>
          <CardHeader
            title="Agent Configuration"
            description="Default settings for AI agents"
          />
          <div className="mt-4 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Default Model for Analysis
              </label>
              <select className="input-field mt-1">
                <option>gpt-4.1</option>
                <option>claude-sonnet-4</option>
                <option>gpt-4o</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Max Tokens per Request
              </label>
              <input
                type="number"
                className="input-field mt-1"
                defaultValue={4096}
              />
            </div>
          </div>
        </Card>
      </div>
    </AppLayout>
  );
}
