"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { api, type AISystemListItem, type PaginatedResponse } from "@/lib/api";
import { PageHeader, EmptyState } from "@/components/shared";
import { EURiskBadge, USDesignationBadge, RiskScoreBadge } from "@/components/shared/risk-badge";
import { DataTable, type Column, Button, Input, Select, ErrorBoundary, useToast } from "@/components/ui";

export default function InventoryPage() {
  const [data, setData] = useState<PaginatedResponse<AISystemListItem> | null>(null);
  const [loading, setLoading] = useState(true);
  const [fetching, setFetching] = useState(false);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [search, setSearch] = useState("");
  const [euFilter, setEuFilter] = useState("");
  const [usFilter, setUsFilter] = useState("");
  const [sectorFilter, setSectorFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const searchTimeoutRef = useRef<NodeJS.Timeout>();
  const toast = useToast();

  const hasLoadedRef = useRef(false);

  const fetchSystems = useCallback(async (
    searchVal: string,
    euVal: string,
    usVal: string,
    sectorVal: string,
    statusVal: string,
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
      if (euVal) params.eu_risk_tier = euVal;
      if (usVal) params.us_designation = usVal;
      if (sectorVal) params.sector = sectorVal;
      if (statusVal) params.status = statusVal;

      const result = await api.listSystems(params);
      setData(result);
      hasLoadedRef.current = true;
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load systems";
      toast.error(message);
    } finally {
      setLoading(false);
      setFetching(false);
    }
  }, [pageSize, toast]);

  // Single effect: debounced fetch on any filter/search/page change
  useEffect(() => {
    if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current);
    searchTimeoutRef.current = setTimeout(() => {
      fetchSystems(search, euFilter, usFilter, sectorFilter, statusFilter, page);
    }, 300);

    return () => {
      if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search, euFilter, usFilter, sectorFilter, statusFilter, page]);

  const handleRowClick = (system: AISystemListItem) => {
    window.location.href = `/inventory/${system.id}`;
  };

  const columns: Column<AISystemListItem>[] = [
    {
      key: "name",
      label: "Name",
      sortable: true,
      render: (value) => <span className="font-medium">{value}</span>,
    },
    {
      key: "model_type",
      label: "Type",
      sortable: true,
      render: (value) => <span className="capitalize">{value}</span>,
    },
    {
      key: "sector",
      label: "Sector",
      sortable: true,
      render: (value) => <span className="capitalize">{value.replace(/_/g, " ")}</span>,
    },
    {
      key: "eu_risk_tier",
      label: "EU Risk Tier",
      render: (value) => <EURiskBadge tier={value} size="sm" />,
    },
    {
      key: "us_designation",
      label: "US Designation",
      render: (value) => <USDesignationBadge designation={value} size="sm" />,
    },
    {
      key: "risk_score",
      label: "Risk Score",
      sortable: true,
      render: (value) => <RiskScoreBadge score={value ?? 0} size="sm" />,
    },
    {
      key: "status",
      label: "Status",
      sortable: true,
      render: (value) => <span className="capitalize">{value}</span>,
    },
    {
      key: "updated_at",
      label: "Updated",
      render: (value) => new Date(value).toLocaleDateString(),
    },
  ];

  return (
    <div className="p-8">
      <PageHeader
        title="AI System Inventory"
        description="Manage and monitor all registered AI systems"
        breadcrumbs={[{ label: "Inventory" }]}
        actions={
          <Button variant="primary" onClick={() => (window.location.href = "/inventory/register")}>
            + Register System
          </Button>
        }
      />

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
        <Input
          placeholder="Search by name..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <Select
          value={euFilter}
          onChange={(e) => {
            setEuFilter(e.target.value);
            setPage(1);
          }}
          options={[
            { value: "", label: "All EU Tiers" },
            { value: "prohibited", label: "Prohibited" },
            { value: "high", label: "High" },
            { value: "limited", label: "Limited" },
            { value: "minimal", label: "Minimal" },
          ]}
        />
        <Select
          value={usFilter}
          onChange={(e) => {
            setUsFilter(e.target.value);
            setPage(1);
          }}
          options={[
            { value: "", label: "All US Designations" },
            { value: "high_impact", label: "High-Impact" },
            { value: "standard", label: "Standard" },
          ]}
        />
        <Select
          value={sectorFilter}
          onChange={(e) => {
            setSectorFilter(e.target.value);
            setPage(1);
          }}
          options={[
            { value: "", label: "All Sectors" },
            { value: "healthcare", label: "Healthcare" },
            { value: "finance", label: "Finance" },
            { value: "education", label: "Education" },
            { value: "employment", label: "Employment" },
            { value: "law_enforcement", label: "Law Enforcement" },
            { value: "government", label: "Government" },
            { value: "insurance", label: "Insurance" },
            { value: "consumer", label: "Consumer" },
          ]}
        />
        <Select
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value);
            setPage(1);
          }}
          options={[
            { value: "", label: "All Statuses" },
            { value: "draft", label: "Draft" },
            { value: "active", label: "Active" },
            { value: "under_review", label: "Under Review" },
            { value: "retired", label: "Retired" },
          ]}
        />
      </div>

      {/* Table */}
      <ErrorBoundary>
        {data?.items.length === 0 && !loading ? (
          <EmptyState
            icon="🔍"
            title="No Systems Found"
            description="No AI systems match your search criteria"
            action={{
              label: "Clear Filters",
              onClick: () => {
                setSearch("");
                setEuFilter("");
                setUsFilter("");
                setSectorFilter("");
                setStatusFilter("");
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
              <DataTable<AISystemListItem>
                columns={columns}
                data={data?.items ?? []}
                loading={loading}
                onRowClick={handleRowClick}
                emptyMessage="No AI systems found"
              />
            </div>

            {/* Pagination */}
            {data && data.total_pages > 1 && (
              <div className="mt-6 flex items-center justify-between">
                <div className="text-sm text-gray-600">
                  Page {data.page} of {data.total_pages} ({data.total} systems)
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
