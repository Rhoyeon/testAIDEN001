import { cn } from "@/lib/utils";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "default" | "success" | "warning" | "error" | "info" | "purple";
  size?: "sm" | "md";
  className?: string;
}

const variantStyles: Record<string, string> = {
  default: "bg-gray-100 text-gray-700",
  success: "bg-green-100 text-green-700",
  warning: "bg-yellow-100 text-yellow-800",
  error: "bg-red-100 text-red-700",
  info: "bg-blue-100 text-blue-700",
  purple: "bg-purple-100 text-purple-700",
};

export function Badge({ children, variant = "default", size = "sm", className }: BadgeProps) {
  return (
    <span
      className={cn(
        "badge",
        variantStyles[variant],
        size === "md" && "px-3 py-1 text-sm",
        className,
      )}
    >
      {children}
    </span>
  );
}
