"use client";

import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";

export type ToastType = "success" | "error" | "warning" | "info";

export interface Toast {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
}

const typeStyles: Record<ToastType, string> = {
  success: "bg-green-50 border-green-200 text-green-800",
  error: "bg-red-50 border-red-200 text-red-800",
  warning: "bg-yellow-50 border-yellow-200 text-yellow-800",
  info: "bg-blue-50 border-blue-200 text-blue-800",
};

const typeIcons: Record<ToastType, string> = {
  success: "✓",
  error: "✕",
  warning: "⚠",
  info: "ℹ",
};

interface ToastItemProps {
  toast: Toast;
  onDismiss: (id: string) => void;
}

function ToastItem({ toast, onDismiss }: ToastItemProps) {
  useEffect(() => {
    if (!toast.duration || toast.duration <= 0) return;
    const timer = setTimeout(() => onDismiss(toast.id), toast.duration);
    return () => clearTimeout(timer);
  }, [toast, onDismiss]);

  return (
    <div
      className={cn(
        "flex items-center gap-3 rounded-lg border px-4 py-3 mb-2 shadow-md",
        "animate-in slide-in-from-top-2 duration-300",
        typeStyles[toast.type]
      )}
    >
      <span className="text-lg font-bold">{typeIcons[toast.type]}</span>
      <span className="text-sm font-medium flex-1">{toast.message}</span>
      <button
        onClick={() => onDismiss(toast.id)}
        className="text-lg leading-none hover:opacity-70 transition-opacity"
      >
        ×
      </button>
    </div>
  );
}

let toastId = 0;
let toastCallback: ((toast: Toast) => void) | null = null;

// Stable singleton — never changes between renders, breaks infinite re-render loops
const toastActions = {
  success: (message: string, duration = 4000) => {
    const toast: Toast = { id: String(toastId++), type: "success", message, duration };
    toastCallback?.(toast);
  },
  error: (message: string, duration = 5000) => {
    const toast: Toast = { id: String(toastId++), type: "error", message, duration };
    toastCallback?.(toast);
  },
  warning: (message: string, duration = 4000) => {
    const toast: Toast = { id: String(toastId++), type: "warning", message, duration };
    toastCallback?.(toast);
  },
  info: (message: string, duration = 4000) => {
    const toast: Toast = { id: String(toastId++), type: "info", message, duration };
    toastCallback?.(toast);
  },
};

export function useToast() {
  return toastActions;
}

export function ToastContainer() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  useEffect(() => {
    toastCallback = (toast) => {
      setToasts((prev) => {
        const updated = [...prev, toast];
        return updated.slice(-5); // Max 5 toasts
      });
    };
  }, []);

  const handleDismiss = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <div className="fixed top-4 right-4 z-50 w-80 max-w-[calc(100%-2rem)]">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onDismiss={handleDismiss} />
      ))}
    </div>
  );
}
