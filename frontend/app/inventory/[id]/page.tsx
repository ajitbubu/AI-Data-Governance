"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api, type AISystem, type RiskClassification } from "@/lib/api";
import { PageHeader, EmptyState } from "@/components/shared";
import { EURiskBadge, USDesignationBadge, RiskScoreBadge } from "@/components/shared/risk-badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Button,
  ErrorBoundary,
  useToast,
  SkeletonCard,
} from "@/components/ui";
import { EU_TIER_COLORS, US_DESIGNATION_COLORS, STATUS_COLORS } from "@/lib/utils";

export default function SystemDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const toast = useToast();

  const [system, setSystem] = useState<AISystem | null>(null);
  const [classification, setClassification] = useState<RiskClassification | null>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<"overview" | "classification" | "history" | "approvals">("overview");
  const [loading, setLoading] = useState(true);
  const [reclassifying, setReclassifying] = useState(false);

  useEffect(() => {
    if (!id) return;
    const loadData = async () => {
      setLoading(true);
      try {
        const [sysData, classData, histData] = await Promise.all([
          api.getSystem(id),
          api.getClassification(id).catch(() => null),
          api.getVersionHistory(id).catch(() => []),
        ]);
        setSystem(sysData);
        setClassification(classData);
        setHistory(histData);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to load system details";
        toast.error(message);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [id, toast]);

  const handleReclassify = async () => {
    setReclassifying(true);
    try {
      const updated = await api.classifySystem(id);
      setSystem(updated);
      const cls = await api.getClassification(id);
      setClassification(cls);
      toast.success("System reclassified successfully");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to reclassify";
      toast.error(message);
    } finally {
      setReclassifying(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8">
        <PageHeader title="Loading..." />
        <div className="space-y-6">
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </div>
    );
  }

  if (!system) {
    return (
      <div className="p-8">
        <PageHeader title="System Not Found" />
        <EmptyState
          icon="❌"
          title="AI System Not Found"
          description="The system you're looking for doesn't exist or has been deleted."
          action={{ label: "Back to Inventory", href: "/inventory" }}
        />
      </div>
    );
  }

  const eu = EU_TIER_COLORS[system.eu_risk_tier] || EU_TIER_COLORS.not_classified;
  const us = US_DESIGNATION_COLORS[system.us_designation] || US_DESIGNATION_COLORS.not_classified;
  const st = STATUS_COLORS[system.status] || STATUS_COLORS.draft;

  return (
    <div className="p-8">
      <PageHeader
        title={system.name}
        description={system.description || "No description available"}
        breadcrumbs={[
          { label: "Inventory", href: "/inventory" },
          { label: system.name },
        ]}
        actions={
          <Button
            variant="outline"
            onClick={handleReclassify}
            disabled={reclassifying}
          >
            {reclassifying ? "Classifying..." : "Re-classify"}
          </Button>
        }
      />

      {/* Classification Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <ErrorBoundary>
          <Card>
            <CardHeader className="pb-3">
              <CardDescription>EU AI Act Risk Tier</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold mb-2">
                <EURiskBadge tier={system.eu_risk_tier} />
              </div>
            </CardContent>
          </Card>
        </ErrorBoundary>

        <ErrorBoundary>
          <Card>
            <CardHeader className="pb-3">
              <CardDescription>US OMB M-25-21</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold mb-2">
                <USDesignationBadge designation={system.us_designation} />
              </div>
            </CardContent>
          </Card>
        </ErrorBoundary>

        <ErrorBoundary>
          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Risk Score</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold mb-2">
                <RiskScoreBadge score={system.risk_score ?? 0} />
              </div>
              <p className="text-xs text-gray-500">
                Confidence: {system.classification_confidence || "N/A"}
              </p>
            </CardContent>
          </Card>
        </ErrorBoundary>

        <ErrorBoundary>
          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Status</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-sm font-bold capitalize">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${st.bg} ${st.text}`}>
                  {system.status}
                </span>
              </div>
            </CardContent>
          </Card>
        </ErrorBoundary>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex gap-6">
          {(["overview", "classification", "history", "approvals"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-3 text-sm font-medium capitalize transition-colors ${
                activeTab === tab
                  ? "border-b-2 border-blue-600 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              {tab}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <ErrorBoundary>
        {activeTab === "overview" && (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>System Information</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-6">
                  <InfoField label="Model Type" value={system.model_type} />
                  <InfoField label="Sector" value={system.sector} />
                  <InfoField label="Deployment Environment" value={system.deployment_env} />
                  <InfoField label="Decision Automation" value={system.decision_automation} />
                  <InfoField label="Data Sensitivity" value={system.data_sensitivity} />
                  <InfoField
                    label="Deployment Geography"
                    value={(system.deployment_geo || []).join(", ") || "Not specified"}
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Purpose & Impact</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <InfoField label="Purpose Statement" value={system.purpose_statement} />
                {system.affected_population && (
                  <InfoField label="Affected Population" value={system.affected_population} />
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Metadata</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                  <div>
                    <p className="text-xs font-medium text-gray-500 mb-1">Created</p>
                    <p>{new Date(system.created_at).toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-xs font-medium text-gray-500 mb-1">Last Updated</p>
                    <p>{new Date(system.updated_at).toLocaleString()}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {activeTab === "classification" && classification && (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>EU AI Act Classification</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-gray-50 rounded-lg p-4 font-mono text-xs overflow-x-auto max-h-96 overflow-y-auto">
                  <pre>{JSON.stringify(classification.eu_rationale, null, 2)}</pre>
                </div>
                {classification.matched_annex_iii_categories && classification.matched_annex_iii_categories.length > 0 && (
                  <div className="mt-4">
                    <p className="text-sm font-medium text-gray-700 mb-2">Matched Annex III Categories:</p>
                    <div className="flex flex-wrap gap-2">
                      {classification.matched_annex_iii_categories.map((cat, i) => (
                        <span key={i} className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                          {cat}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>US OMB M-25-21 Classification</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-gray-50 rounded-lg p-4 font-mono text-xs overflow-x-auto max-h-96 overflow-y-auto">
                  <pre>{JSON.stringify(classification.us_rationale, null, 2)}</pre>
                </div>
                {classification.matched_omb_categories && classification.matched_omb_categories.length > 0 && (
                  <div className="mt-4">
                    <p className="text-sm font-medium text-gray-700 mb-2">Matched OMB Categories:</p>
                    <div className="flex flex-wrap gap-2">
                      {classification.matched_omb_categories.map((cat, i) => (
                        <span key={i} className="px-2 py-1 bg-red-100 text-red-800 rounded text-xs">
                          {cat}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="text-xs text-gray-500 space-y-1">
                  <p>Classified: {new Date(classification.classified_at).toLocaleString()}</p>
                  <p>By: {classification.classified_by}</p>
                  <p>Classifier Version: {classification.classifier_version}</p>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {activeTab === "history" && (
          <Card>
            <CardHeader>
              <CardTitle>Version History</CardTitle>
            </CardHeader>
            <CardContent>
              {history.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No version history available</p>
              ) : (
                <div className="space-y-4">
                  {history.map((version, idx) => (
                    <div
                      key={version.id}
                      className={`border-l-4 border-blue-500 pl-4 py-3 ${idx !== history.length - 1 ? "border-b pb-4" : ""}`}
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <p className="font-mono text-sm font-bold text-gray-900">
                            v{version.version_number}
                          </p>
                          <p className="text-sm text-gray-600 mt-1">
                            {version.change_summary || "No description"}
                          </p>
                          {version.snapshot && (
                            <div className="mt-2 text-xs text-gray-500">
                              <p>
                                EU: <span className="font-mono">{version.snapshot.eu_risk_tier}</span> | US:{" "}
                                <span className="font-mono">{version.snapshot.us_designation}</span>
                              </p>
                            </div>
                          )}
                        </div>
                        <div className="text-xs text-gray-500 whitespace-nowrap">
                          {new Date(version.created_at).toLocaleString()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {activeTab === "approvals" && (
          <Card>
            <CardHeader>
              <CardTitle>Approvals & Workflows</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-500 text-center py-8">
                Approval workflows coming soon
              </p>
            </CardContent>
          </Card>
        )}
      </ErrorBoundary>
    </div>
  );
}

function InfoField({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs font-medium text-gray-500 mb-1">{label}</p>
      <p className="text-sm text-gray-900 capitalize">{value.replace(/_/g, " ")}</p>
    </div>
  );
}
