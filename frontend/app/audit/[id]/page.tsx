"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api, type AuditEvent, type AuditEventListItem } from "@/lib/api";
import { PageHeader, EmptyState, AuditEventBadge, ChangesDiff } from "@/components/shared";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  ErrorBoundary,
  useToast,
  SkeletonCard,
  Button,
} from "@/components/ui";

export default function AuditEventDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const toast = useToast();

  const [event, setEvent] = useState<AuditEvent | null>(null);
  const [timeline, setTimeline] = useState<AuditEventListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    const loadData = async () => {
      setLoading(true);
      try {
        const eventData = await api.getAuditEvent(id);
        setEvent(eventData);

        // Fetch timeline for related events
        const timelineData = await api.getEntityTimeline(eventData.entity_type, eventData.entity_id).catch(
          () => []
        );
        setTimeline(timelineData);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to load audit event details";
        toast.error(message);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [id, toast]);

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

  if (!event) {
    return (
      <div className="p-8">
        <PageHeader title="Event Not Found" />
        <EmptyState
          icon="❌"
          title="Audit Event Not Found"
          description="The event you're looking for doesn't exist or has been deleted."
          action={{ label: "Back to Audit Trail", href: "/audit" }}
        />
      </div>
    );
  }

  const isAiSystem = event.entity_type === "ai_system";

  return (
    <div className="p-8">
      <PageHeader
        title="Event Details"
        description={`ID: ${event.id}`}
        breadcrumbs={[
          { label: "Audit Trail", href: "/audit" },
          { label: "Event Detail" },
        ]}
      />

      {/* Event Summary Card */}
      <ErrorBoundary>
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Event Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
              <div>
                <p className="text-xs font-medium text-gray-500 mb-2">Event Type</p>
                <AuditEventBadge eventType={event.event_type} />
              </div>
              <div>
                <p className="text-xs font-medium text-gray-500 mb-2">Entity Type</p>
                <p className="text-sm font-medium text-gray-900 capitalize">
                  {event.entity_type.replace(/_/g, " ")}
                </p>
              </div>
              <div>
                <p className="text-xs font-medium text-gray-500 mb-2">Entity ID</p>
                {isAiSystem ? (
                  <a
                    href={`/inventory/${event.entity_id}`}
                    className="text-sm font-mono text-blue-600 hover:underline"
                  >
                    {event.entity_id}
                  </a>
                ) : (
                  <p className="text-sm font-mono text-gray-900">{event.entity_id}</p>
                )}
              </div>
              <div>
                <p className="text-xs font-medium text-gray-500 mb-2">Action</p>
                <p className="text-sm font-medium text-gray-900 capitalize">
                  {event.action.replace(/_/g, " ")}
                </p>
              </div>
              <div>
                <p className="text-xs font-medium text-gray-500 mb-2">Actor</p>
                <p className="text-sm text-gray-900">{event.actor_email || "System"}</p>
              </div>
              <div>
                <p className="text-xs font-medium text-gray-500 mb-2">Timestamp</p>
                <p className="text-sm text-gray-900">{new Date(event.created_at).toLocaleString()}</p>
              </div>
              <div>
                <p className="text-xs font-medium text-gray-500 mb-2">Request ID</p>
                <p className="text-sm font-mono text-gray-700 truncate">{event.request_id}</p>
              </div>
              <div>
                <p className="text-xs font-medium text-gray-500 mb-2">IP Address</p>
                <p className="text-sm font-mono text-gray-700">{event.ip_address}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </ErrorBoundary>

      {/* Changes Section */}
      {event.changes && (
        <ErrorBoundary>
          <div className="mb-8">
            <ChangesDiff changes={event.changes} />
          </div>
        </ErrorBoundary>
      )}

      {/* Metadata Section */}
      {event.metadata && Object.keys(event.metadata).length > 0 && (
        <ErrorBoundary>
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Metadata</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="bg-gray-50 rounded-lg p-4 font-mono text-xs overflow-x-auto max-h-96 overflow-y-auto">
                <pre>{JSON.stringify(event.metadata, null, 2)}</pre>
              </div>
            </CardContent>
          </Card>
        </ErrorBoundary>
      )}

      {/* Related Events Timeline */}
      {timeline.length > 0 && (
        <ErrorBoundary>
          <Card>
            <CardHeader>
              <CardTitle>Entity Timeline</CardTitle>
              <CardDescription>Other events for this {event.entity_type.replace(/_/g, " ")}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {timeline.map((timelineEvent, idx) => (
                  <div
                    key={timelineEvent.id}
                    className={`border-l-4 border-blue-500 pl-4 py-3 ${
                      idx !== timeline.length - 1 ? "border-b pb-4" : ""
                    }`}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <AuditEventBadge eventType={timelineEvent.event_type} size="sm" />
                          <span className="text-sm font-medium text-gray-700">
                            {timelineEvent.action.replace(/_/g, " ")}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600">
                          by {timelineEvent.actor_email || "System"}
                        </p>
                      </div>
                      <div className="flex flex-col items-end gap-2">
                        <p className="text-xs text-gray-500 whitespace-nowrap">
                          {new Date(timelineEvent.created_at).toLocaleString()}
                        </p>
                        {timelineEvent.id !== event.id && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              window.location.href = `/audit/${timelineEvent.id}`;
                            }}
                          >
                            View
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </ErrorBoundary>
      )}
    </div>
  );
}
