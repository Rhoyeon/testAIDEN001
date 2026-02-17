"use client";

import { FileText, Upload } from "lucide-react";
import { AppLayout } from "@/components/layout";
import { Card } from "@/components/ui";

export default function DocumentsPage() {
  return (
    <AppLayout title="Documents">
      <p className="text-sm text-gray-500">
        Manage project documents and uploaded files
      </p>

      <Card className="mt-6 flex flex-col items-center justify-center py-16">
        <FileText className="h-16 w-16 text-gray-200" />
        <p className="mt-4 text-sm text-gray-500">
          Select a project to manage documents
        </p>
        <p className="mt-1 text-xs text-gray-400">
          Documents are organized per project. Go to a project to upload and manage files.
        </p>
      </Card>
    </AppLayout>
  );
}
