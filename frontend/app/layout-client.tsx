"use client";

import { useState, ReactNode } from "react";
import { usePathname } from "next/navigation";
import { ErrorBoundary, ToastContainer } from "@/components/ui";
import { cn } from "@/lib/utils";

const navSections = [
  {
    label: "Core",
    items: [
      { href: "/", label: "Dashboard" },
      { href: "/inventory", label: "AI System Inventory" },
    ],
  },
  {
    label: "Compliance",
    items: [
      { href: "/compliance", label: "Compliance Engine" },
      { href: "/audit", label: "Audit Trail" },
      { href: "/gpai", label: "GPAI Dashboard" },
    ],
  },
  {
    label: "Operations",
    items: [
      { href: "/security", label: "Security Pipeline" },
      { href: "/bias", label: "Bias Detection" },
      { href: "/data-governance", label: "Data Governance" },
      { href: "/monitoring", label: "Monitoring" },
      { href: "/vendors", label: "Vendor Governance" },
      { href: "/hitl", label: "Human-in-the-Loop" },
      { href: "/documentation", label: "Documentation" },
    ],
  },
];

interface RootLayoutClientProps {
  children: ReactNode;
}

export function RootLayoutClient({ children }: RootLayoutClientProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const pathname = usePathname();

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname.startsWith(href);
  };

  return (
    <ErrorBoundary>
      <div className="min-h-screen flex bg-gray-50">
        {/* Sidebar */}
        <aside
          className={cn(
            "fixed inset-y-0 left-0 z-50 flex flex-col w-64 bg-blue-900 text-white transition-transform duration-300 lg:static lg:translate-x-0",
            sidebarOpen ? "translate-x-0" : "-translate-x-full"
          )}
        >
          {/* Logo */}
          <div className="px-6 py-6 border-b border-blue-800">
            <h1 className="text-xl font-bold tracking-tight">DataSafeguard</h1>
            <p className="text-xs text-blue-200 mt-1">AI Governance</p>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto px-3 py-6 space-y-8">
            {navSections.map((section) => (
              <div key={section.label}>
                <h3 className="px-3 text-xs font-semibold text-blue-300 uppercase tracking-wider mb-3">
                  {section.label}
                </h3>
                <div className="space-y-1">
                  {section.items.map((item) => (
                    <a
                      key={item.href}
                      href={item.href}
                      className={cn(
                        "block px-3 py-2.5 rounded-md text-sm transition-colors",
                        isActive(item.href)
                          ? "bg-blue-800 text-white font-medium"
                          : "text-blue-100 hover:bg-blue-800 hover:text-white"
                      )}
                    >
                      {item.label}
                    </a>
                  ))}
                </div>
              </div>
            ))}
          </nav>

          {/* Footer */}
          <div className="px-3 py-4 border-t border-blue-800">
            <div className="px-3 text-xs text-blue-300">
              <p className="font-medium mb-1">DataSafeguard</p>
              <p>v0.1.0 — UC-1 MVP</p>
            </div>
            <div className="mt-4 flex items-center gap-3 px-3 py-2 rounded-md bg-blue-800">
              <div className="w-8 h-8 rounded-full bg-blue-300" />
              <div className="text-sm truncate">
                <p className="font-medium">Admin</p>
                <p className="text-xs text-blue-200">admin@datasafeguard</p>
              </div>
            </div>
          </div>
        </aside>

        {/* Overlay for mobile */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 z-40 bg-black/50 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Main Content */}
        <main className="flex-1 flex flex-col w-full">
          {/* Top Bar */}
          <div className="lg:hidden px-4 py-3 bg-white border-b border-gray-200 flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 hover:bg-gray-100 rounded-md transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            </button>
            <span className="text-sm font-medium text-gray-700">DataSafeguard</span>
          </div>

          {/* Page Content */}
          <div className="flex-1 overflow-auto">
            {children}
          </div>
        </main>

        {/* Toast Container */}
        <ToastContainer />
      </div>
    </ErrorBoundary>
  );
}
