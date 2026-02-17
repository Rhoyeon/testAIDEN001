import { cn } from "@/lib/utils";

interface SpinnerProps {
  size?: "sm" | "md" | "lg";
  className?: string;
}

const sizeStyles: Record<string, string> = {
  sm: "h-4 w-4",
  md: "h-6 w-6",
  lg: "h-10 w-10",
};

export function Spinner({ size = "md", className }: SpinnerProps) {
  return (
    <div
      className={cn(
        "animate-spin rounded-full border-2 border-gray-200 border-t-aiden-600",
        sizeStyles[size],
        className,
      )}
      role="status"
    >
      <span className="sr-only">Loading...</span>
    </div>
  );
}
