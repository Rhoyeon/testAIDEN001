"use client";

import { useState, useCallback } from "react";
import { Upload, FileText, X, CheckCircle2, AlertCircle } from "lucide-react";
import { Card, Button, Badge } from "@/components/ui";
import { documentsApi } from "@/lib/api";
import { cn } from "@/lib/utils";

interface DocumentUploadProps {
  projectId: string;
  onUploadComplete?: () => void;
  className?: string;
}

interface UploadFile {
  file: File;
  status: "pending" | "uploading" | "success" | "error";
  error?: string;
}

const ACCEPTED_TYPES = [
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "application/msword",
  "text/plain",
  "text/csv",
  "text/markdown",
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "application/vnd.ms-excel",
  "application/json",
  "application/x-hwp",
  "application/haansofthwp",
];

const ACCEPTED_EXTENSIONS = [
  ".pdf", ".docx", ".doc", ".txt", ".csv", ".md",
  ".xlsx", ".xls", ".json", ".hwp", ".hwpx",
];

function isAcceptedFile(f: File): boolean {
  if (ACCEPTED_TYPES.includes(f.type)) return true;
  const name = f.name.toLowerCase();
  return ACCEPTED_EXTENSIONS.some((ext) => name.endsWith(ext));
}

export function DocumentUpload({ projectId, onUploadComplete, className }: DocumentUploadProps) {
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [dragOver, setDragOver] = useState(false);

  const addFiles = useCallback((newFiles: FileList | null) => {
    if (!newFiles) return;
    const filtered = Array.from(newFiles)
      .filter(isAcceptedFile)
      .map((file) => ({ file, status: "pending" as const }));
    setFiles((prev) => [...prev, ...filtered]);
  }, []);

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    const pendingFiles = files.filter((f) => f.status === "pending");
    for (let i = 0; i < files.length; i++) {
      if (files[i].status !== "pending") continue;

      setFiles((prev) =>
        prev.map((f, idx) => (idx === i ? { ...f, status: "uploading" } : f)),
      );

      try {
        await documentsApi.upload(projectId, files[i].file);
        setFiles((prev) =>
          prev.map((f, idx) => (idx === i ? { ...f, status: "success" } : f)),
        );
      } catch (err) {
        setFiles((prev) =>
          prev.map((f, idx) =>
            idx === i ? { ...f, status: "error", error: (err as Error).message } : f,
          ),
        );
      }
    }
    onUploadComplete?.();
  };

  const hasPending = files.some((f) => f.status === "pending");

  return (
    <Card className={cn("", className)}>
      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => { e.preventDefault(); setDragOver(false); addFiles(e.dataTransfer.files); }}
        className={cn(
          "flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 transition-colors",
          dragOver ? "border-aiden-400 bg-aiden-50" : "border-gray-300 bg-gray-50",
        )}
      >
        <Upload className={cn("h-10 w-10", dragOver ? "text-aiden-500" : "text-gray-400")} />
        <p className="mt-3 text-sm font-medium text-gray-700">
          Drag & drop files here
        </p>
        <p className="mt-1 text-xs text-gray-500">PDF, DOCX, TXT, HWP, XLSX, CSV, MD, JSON</p>
        <label className="mt-4">
          <input
            type="file"
            multiple
            accept={ACCEPTED_EXTENSIONS.join(",")}
            className="hidden"
            onChange={(e) => addFiles(e.target.files)}
          />
          <span className="btn-secondary cursor-pointer text-sm">Browse Files</span>
        </label>
      </div>

      {/* File list */}
      {files.length > 0 && (
        <div className="mt-4 space-y-2">
          {files.map((f, i) => (
            <div
              key={i}
              className="flex items-center justify-between rounded-lg border border-gray-200 px-3 py-2"
            >
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4 text-gray-400" />
                <span className="text-sm text-gray-700">{f.file.name}</span>
                <span className="text-xs text-gray-400">
                  ({(f.file.size / 1024).toFixed(0)} KB)
                </span>
              </div>
              <div className="flex items-center gap-2">
                {f.status === "success" && (
                  <CheckCircle2 className="h-4 w-4 text-green-500" />
                )}
                {f.status === "error" && (
                  <span className="flex items-center gap-1 text-xs text-red-500">
                    <AlertCircle className="h-4 w-4" />
                    {f.error ?? "Upload failed"}
                  </span>
                )}
                {f.status === "uploading" && (
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-gray-200 border-t-aiden-500" />
                )}
                {f.status === "pending" && (
                  <button onClick={() => removeFile(i)} className="text-gray-400 hover:text-red-500">
                    <X className="h-4 w-4" />
                  </button>
                )}
              </div>
            </div>
          ))}

          {hasPending && (
            <Button onClick={handleUpload} className="mt-2 w-full">
              Upload {files.filter((f) => f.status === "pending").length} file(s)
            </Button>
          )}
        </div>
      )}
    </Card>
  );
}
