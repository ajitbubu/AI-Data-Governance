"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { api, type AuditEventListItem, type AuditStats, type PaginatedResponse } from "@/lib/api";
import { PageHeader, EmptyState, AuditEventBadge } from "@/components/shared";
import { DataTable, type Column, Button, Input, Select, ErrorBoundary, useToast, StatCard } from "@/components/ui";

const EVENT_TYPES = [
  { value: "SYSTEM_REGISTERED", label: "System Registered" },
  { value: "SYSTEM_UPDATED", label: "System Updated" },
  { value: "SYSTEM_ARCHIVED", label: "System Archived" },
  { value: "CLASSIFICATION_COMPLETED", label: "Classification Completed" },
  { value: "APPROVAL_CREATED", label: "Approval Created" },
  { value: "APPROVAL_APPROVED", label: "Approval Approved" },
  { value: "APPROVAL_REJECTED", label: "Approval Rejected" },
  { value: "POLICY_ENFORCED", label: "Policy Enforced" },
  { value: "RISK_ALERT_TRIGGERED", label: "Risk Alert Triggered" },
];

const ENTITY_TYPES = [
  { value: "ai_system", label: "AI System" },
  { value: "approval", label: "Approval" },
];

export default function AuditPage() {
  const [data, setData] = useState<PaginatedResponse<AuditEventListItem> | null>(null);
  const [stats, setStats] = useState<AuditStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [fetching, setFetching] = useState(false);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [search, setSearch] = useState("");
  const [eventTypeFilter, setEventTypeFilter] = useState("");
  const [entityTypeFilter, setEntityTypeFilter] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const searchTimeoutRef = useRef<NodeJS.Timeout>();
  const toast = useToast();

  const hasLoadedRef = useRef(false);

  const fetchAuditEvents = useCallback(async (
    searchVal: string,
    eventTypeVal: string,
    entityTypeVal: string,
    dateFromVal: string,
    dateToVal: string,
    pageVal: number
  ) => {
    if (!hasLoadedRef.current) setLoading(true);
    else setFetching(true);
    try {
      const params: Record<string, string> = {
        page: String(pageVal),
        page_size: String(pageSize),
      };
      if (searchVal) params.search = searchVal;
      if (eventTypeVal) params.event_type = eventTypeVal;
      if (entityTypeVal) params.entity_type = entityTypeVal;
      if (dateFromVal) params.date_from = dateFromVal;
      if (dateToVal) params.date_to = dateToVal;

      const result = await api.listAuditEvents(params);
      setData(result);
      hasLoadedRef.current = true;
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load audit events";
      toast.error(message);
    } finally {
      setLoading(false);
      setFetching(false);
    }
  }, [pageSize, toast]);

  const fetchStats = useCallback(async () => {
    try {
      const result = await api.getAuditStats();
      setStats(result);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load stats";
      toast.error(message);
    }
  }, [toast]);

  // Single effect: debounced fetch on any filter/search/page change
  useEffect(() => {
    if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current);
    searchTimeoutRef.current = setTimeout(() => {
      fetchAuditEvents(search, eventTypeFilter, entityTypeFilter, dateFrom, dateTo, page);
    }, 300);

    return () => {
      if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search, eventTypeFilter, entityTypeFilter, dateFrom, dateTo, page]);

  // Fetch stats on mount
  useEffect(() => {
    fetchStats();
  }, []);

  const handleRowClick = (event: AuditEventListItem) => {
    window.location.href = `/audit/${event.id}`;
  };

  const columns: Column<AuditEventListItem>[] = [
    {
      key: "created_at",
      label: "Timestamp",
      sortable: true,
      render: (value) => new Date(value).toLocaleString(),
    },
    {
      key: "event_type",
      label: "Event Type",
      render: (value) => <AuditEventBadge eventType={value} size="sm" />,
    },
    {
      key: "entity_type",
      label: "Entity",
      render: (value) => <span className="capitalize text-sm">{value.replace(/_/g, " ")}</span>,
    },
    {
      key: "action",
      label: "Action",
      render: (value) => <span className="capitalize text-sm">{value.replace(/_/g, " ")}</span>,
    },
    {
      key: "actor_email",
      label: "Actor",
      render: (value) => <span className="text-sm text-gray-700">{value || "System"}</span>,
    },
  ];

  const todayCount = (stats?.events_per_day?.length ?? 0) > 0
    ? stats!.events_per_day[stats!.events_per_day.length - 1]?.count || 0
    : 0;

  const mostCommonEventType = stats?.by_event_type
    ? Object.entries(stats.by_event_type).sort((a, b) => b[1] - a[1])[0]?.[0]
    : "N/A";

  return (
    <div className="p-8">
      <PageHeader
        title="Compliance Audit Trail"
        description="Monitor all system activities and changes"
        breadcrumbs={[{ label: "Audit Trail" }]}
        actions={
          <Button
            variant="outline"
            onClick={() => {
              window.location.href = "/api/v1/audit/events/export";
            }}
          >
            ⬇ Export Events
          </Button>
        }
      />

      {/* Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          label="Total Events"
          value={stats?.total_events || 0}
          color="blue"
          loading={!stats}
        />
        <StatCard
          label="Today's Events"
          value={todayCount}
          color="green"
          loading={!stats}
        />
        <StatCard
          label="Unique Actors"
          value={stats?.by_event_type ? Object.keys(stats.by_event_type).length : 0}
          color="orange"
          loading={!stats}
        />
        <StatCard
          label="Most Common Event"
          value={mostCommonEventType}
          color="blue"
          loading={!stats}
        />
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
        <Input
          placeholder="Search by entity or email..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
        />
        <Select
          value={eventTypeFilter}
          onChange={(e) => {
            setEventTypeFilter(e.target.value);
            setPage(1);
          }}
          options={[
            { value: "", label: "All Event Types" },
            ...EVENT_TYPES,
          ]}
        />
        <Select
          value={entityTypeFilter}
          onChange={(e) => {
            setEntityTypeFilter(e.target.value);
            setPage(1);
          }}
          options={[
            { value: "", label: "All Entity Types" },
            ...ENTITY_TYPES,
          ]}
        />
        <Input
          type="date"
          value={dateFrom}
          onChange={(e) => {
            setDateFrom(e.target.value);
            setPage(1);
          }}
          placeholder="From"
        />
        <Input
          type="date"
          value={dateTo}
          onChange={(e) => {
            setDateTo(e.target.value);
            setPage(1);
          }}
          placeholder="To"
        />
      </div>

      {/* Table */}
      <ErrorBoundary>
        {data?.items.length === 0 && !loading ? (
          <EmptyState
            icon="📋"
            title="No Audit Events Found"
            description="No events match your search criteria"
            action={{
              label: "Clear Filters",
              onClick: () => {
                setSearch("");
                setEventTypeFilter("");
                setEntityTypeFilter("");
                setDateFrom("");
                setDateTo("");
              },
            }}
          />
        ) : (
          <>
            <div className={`relative transition-opacity duration-200 ${fetching ? "opacity-60 pointer-events-none" : ""}`}>
              {fetching && (
                <div className="absolute inset-0 flex items-center justify-center z-10">
                  <div className="w-5 h-5 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
                </div>
              )}
              <DataTable<AuditEventListItem>
                columns={columns}
                data={data?.items ?? []}
                loading={loading}
                onRowClick={handleRowClick}
                emptyMessage="No audit events found"
              />
            </div>

            {/* Pagination */}
            {data && data.total_pages > 1 && (
              <div className="mt-6 flex items-center justify-between">
                <div className="text-sm text-gray-600">
                  Page {data.page} of {data.total_pages} ({data.total} events)
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                  >
                    Previous
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage((p) => Math.min(data.total_pages, p + 1))}
                    disabled={page >= data.total_pages}
                  >
                    Next
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </ErrorBoundary>
    </div>
  );
}
