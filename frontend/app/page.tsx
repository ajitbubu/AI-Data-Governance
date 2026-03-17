"use client";

import { useEffect, useState } from "react";
import { api, type Stats } from "@/lib/api";
import {
  PageHeader,
  EmptyState,
} from "@/components/shared";
import {
  StatCard,
  ErrorBoundary,
  SkeletonCard,
  useToast,
} from "@/components/ui";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from "recharts";
import { EU_TIER_COLORS, STATUS_COLORS } from "@/lib/utils";

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const toast = useToast();

  useEffect(() => {
    const fetchStats = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await api.getStats();
        setStats(data);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to load dashboard";
        setError(message);
        toast.error(message);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (error && !stats) {
    return (
      <div className="p-8">
        <PageHeader title="AI Governance Dashboard" description="Error loading dashboard data" />
        <EmptyState
          icon="❌"
          title="Failed to Load Dashboard"
          description={error}
          action={{ label: "Retry", onClick: () => window.location.reload() }}
        />
      </div>
    );
  }

  const systemsCount = stats?.total_systems ?? 0;

  return (
    <div className="p-8">
      <PageHeader
        title="AI Governance Dashboard"
        description="Real-time overview of AI system compliance and risk"
      />

      {/* Empty State */}
      {!loading && systemsCount === 0 && (
        <EmptyState
          icon="🤖"
          title="No AI Systems Registered"
          description="Start by registering your first AI system to begin compliance tracking."
          action={{
            label: "Register AI System",
            href: "/inventory/register",
          }}
        />
      )}

      {/* Statistics Cards */}
      {systemsCount > 0 && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <ErrorBoundary>
              <StatCard
                label="Total AI Systems"
                value={systemsCount}
                color="blue"
                loading={loading}
              />
            </ErrorBoundary>
            <ErrorBoundary>
              <StatCard
                label="High-Risk (EU)"
                value={stats?.by_eu_tier?.high ?? 0}
                color="orange"
                trend={{
                  value: 5,
                  direction: "up",
                }}
                loading={loading}
              />
            </ErrorBoundary>
            <ErrorBoundary>
              <StatCard
                label="High-Impact (US)"
                value={stats?.by_us_designation?.high_impact ?? 0}
                color="red"
                trend={{
                  value: 3,
                  direction: "down",
                }}
                loading={loading}
              />
            </ErrorBoundary>
            <ErrorBoundary>
              <StatCard
                label="Pending Approvals"
                value={stats?.pending_approvals ?? 0}
                color="yellow"
                loading={loading}
              />
            </ErrorBoundary>
          </div>

          {/* Charts Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* EU Risk Distribution */}
            <ErrorBoundary>
              {loading ? (
                <SkeletonCard />
              ) : (
                <Card>
                  <CardHeader>
                    <CardTitle>EU AI Act Risk Distribution</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {stats?.by_eu_tier && Object.keys(stats.by_eu_tier).length > 0 ? (
                      <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                          <Pie
                            data={Object.entries(stats.by_eu_tier).map(([tier, count]) => ({
                              name: EU_TIER_COLORS[tier]?.label || tier,
                              value: count,
                            }))}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, value }) => `${name}: ${value}`}
                            outerRadius={100}
                            fill="#8884d8"
                            dataKey="value"
                          >
                            {Object.keys(stats.by_eu_tier).map((tier) => (
                              <Cell
                                key={tier}
                                fill={
                                  EU_TIER_COLORS[tier]?.bg === "bg-red-100"
                                    ? "#ef4444"
                                    : EU_TIER_COLORS[tier]?.bg === "bg-orange-100"
                                      ? "#f97316"
                                      : EU_TIER_COLORS[tier]?.bg === "bg-yellow-100"
                                        ? "#eab308"
                                        : "#22c55e"
                                }
                              />
                            ))}
                          </Pie>
                          <Tooltip />
                        </PieChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="h-80 flex items-center justify-center text-gray-500">
                        No data available
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}
            </ErrorBoundary>

            {/* Status Distribution */}
            <ErrorBoundary>
              {loading ? (
                <SkeletonCard />
              ) : (
                <Card>
                  <CardHeader>
                    <CardTitle>Systems by Status</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {stats?.by_status && Object.keys(stats.by_status).length > 0 ? (
                      <div className="space-y-3">
                        {Object.entries(stats.by_status).map(([status, count]) => {
                          const colors = STATUS_COLORS[status] || STATUS_COLORS.draft;
                          const total = stats.total_systems || 1;
                          const pct = Math.round((count / total) * 100);
                          return (
                            <div key={status}>
                              <div className="flex justify-between text-sm mb-2">
                                <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors.bg} ${colors.text}`}>
                                  {status}
                                </span>
                                <span className="text-gray-600">{count} ({pct}%)</span>
                              </div>
                              <div className="w-full bg-gray-200 rounded-full h-2">
                                <div
                                  className={`h-2 rounded-full bg-blue-500`}
                                  style={{ width: `${pct}%` }}
                                />
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <div className="h-80 flex items-center justify-center text-gray-500">
                        No data available
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}
            </ErrorBoundary>
          </div>
        </>
      )}
    </div>
  );
}
