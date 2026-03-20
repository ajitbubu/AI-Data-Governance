"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui";

export interface ChangesDiffProps {
  changes: {
    before?: Record<string, unknown>;
    after?: Record<string, unknown>;
  } | null;
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined) {
    return "—";
  }
  if (typeof value === "object") {
    return JSON.stringify(value);
  }
  return String(value);
}

export function ChangesDiff({ changes }: ChangesDiffProps) {
  if (!changes) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-gray-500 text-center py-4">No changes recorded</p>
        </CardContent>
      </Card>
    );
  }

  const before = changes.before || {};
  const after = changes.after || {};

  // Collect all unique keys
  const allKeys = new Set([...Object.keys(before), ...Object.keys(after)]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Changes</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-medium text-gray-700 bg-gray-50 w-1/4">Field</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700 bg-gray-50 w-3/8">Before</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700 bg-gray-50 w-3/8">After</th>
              </tr>
            </thead>
            <tbody>
              {Array.from(allKeys)
                .sort()
                .map((key) => {
                  const beforeValue = before[key];
                  const afterValue = after[key];
                  const hasChanged = JSON.stringify(beforeValue) !== JSON.stringify(afterValue);

                  return (
                    <tr key={key} className="border-b border-gray-200 hover:bg-gray-50">
                      <td className="py-3 px-4 font-mono text-xs text-gray-900">{key}</td>
                      <td
                        className={`py-3 px-4 font-mono text-xs whitespace-pre-wrap break-words ${
                          hasChanged ? "bg-yellow-50" : ""
                        }`}
                      >
                        {formatValue(beforeValue)}
                      </td>
                      <td
                        className={`py-3 px-4 font-mono text-xs whitespace-pre-wrap break-words ${
                          hasChanged ? "bg-yellow-50" : ""
                        }`}
                      >
                        {formatValue(afterValue)}
                      </td>
                    </tr>
                  );
                })}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
