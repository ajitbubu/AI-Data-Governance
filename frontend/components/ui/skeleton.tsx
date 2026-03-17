import { cn } from "@/lib/utils";

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "rect" | "circle" | "text";
  width?: string | number;
  height?: string | number;
}

export function Skeleton({
  variant = "rect",
  width,
  height,
  className,
  ...props
}: SkeletonProps) {
  const widthStyle = typeof width === "number" ? `${width}px` : width;
  const heightStyle = typeof height === "number" ? `${height}px` : height;

  return (
    <div
      className={cn(
        "bg-gray-200 animate-pulse",
        variant === "circle" && "rounded-full",
        variant === "rect" && "rounded-md",
        variant === "text" && "rounded-sm",
        className
      )}
      style={{
        width: widthStyle,
        height: heightStyle,
      }}
      {...props}
    />
  );
}

export function SkeletonLine({ className }: { className?: string }) {
  return <Skeleton variant="text" height={20} className={cn("w-full", className)} />;
}

export function SkeletonCard({ className }: { className?: string }) {
  return (
    <div className={cn("rounded-lg border border-gray-200 p-6 space-y-4", className)}>
      <Skeleton variant="rect" height={24} width="60%" />
      <Skeleton variant="text" height={16} width="100%" />
      <Skeleton variant="text" height={16} width="90%" />
    </div>
  );
}

export function SkeletonTableRows({
  rows = 5,
  columns = 8,
}: {
  rows?: number;
  columns?: number;
}) {
  return (
    <>
      {Array.from({ length: rows }).map((_, i) => (
        <tr key={i}>
          {Array.from({ length: columns }).map((_, j) => (
            <td key={j} className="px-4 py-3">
              <Skeleton variant="text" height={16} width="100%" />
            </td>
          ))}
        </tr>
      ))}
    </>
  );
}
