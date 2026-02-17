import { cn } from "@/lib/utils";

interface ProgressBarProps {
  value: number; // 0-100
  size?: "sm" | "md" | "lg";
  variant?: "default" | "success" | "warning" | "error";
  showLabel?: boolean;
  className?: string;
}

const variantColors: Record<string, string> = {
  default: "bg-aiden-500",
  success: "bg-green-500",
  warning: "bg-yellow-500",
  error: "bg-red-500",
};

const sizeStyles: Record<string, string> = {
  sm: "h-1",
  md: "h-2",
  lg: "h-3",
};

export function ProgressBar({
  value,
  size = "md",
  variant = "default",
  showLabel = false,
  className,
}: ProgressBarProps) {
  const clampedValue = Math.min(100, Math.max(0, value));

  return (
    <div className={cn("w-full", className)}>
      {showLabel && (
        <div className="mb-1 flex justify-between text-xs text-gray-500">
          <span>Progress</span>
          <span>{Math.round(clampedValue)}%</span>
        </div>
      )}
      <div className={cn("w-full overflow-hidden rounded-full bg-gray-200", sizeStyles[size])}>
        <div
          className={cn(
            "h-full rounded-full transition-all duration-500 ease-out",
            variantColors[variant],
          )}
          style={{ width: `${clampedValue}%` }}
        />
      </div>
    </div>
  );
}
