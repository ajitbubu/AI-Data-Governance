"use client";

import { useState } from "react";
import { api, type CreateSystemPayload } from "@/lib/api";

const SECTORS = [
  "healthcare", "finance", "education", "employment", "law_enforcement",
  "immigration", "critical_infrastructure", "government", "insurance",
  "transportation", "consumer", "legal", "other",
];
const MODEL_TYPES = ["classification", "generation", "recommendation", "detection", "regression", "clustering", "other"];
const DEPLOY_ENVS = ["production", "staging", "development"];
const AUTOMATION_LEVELS = ["fully_auto", "semi_auto", "human_assisted", "advisory"];
const DATA_SENSITIVITIES = ["public", "internal", "confidential", "restricted"];
const GEOS = ["US", "EU", "UK", "APAC", "LATAM", "MENA", "Global"];

export default function RegisterPage() {
  const [step, setStep] = useState(1);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState<CreateSystemPayload>({
    name: "",
    description: "",
    purpose_statement: "",
    model_type: "other",
    deployment_env: "development",
    deployment_geo: [],
    affected_population: "",
    decision_automation: "advisory",
    sector: "other",
    data_sensitivity: "internal",
  });

  const set = (field: string, value: any) => setForm(prev => ({ ...prev, [field]: value }));

  const toggleGeo = (geo: string) => {
    const current = form.deployment_geo || [];
    set("deployment_geo", current.includes(geo) ? current.filter(g => g !== geo) : [...current, geo]);
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    setError(null);
    try {
      const system = await api.createSystem(form);
      setResult(system);
      setStep(5);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Register AI System</h1>
      <p className="text-sm text-gray-500 mb-6">
        Step {Math.min(step, 4)} of 4 — The system will be automatically classified after registration.
      </p>

      {/* Progress Bar */}
      <div className="flex gap-2 mb-8">
        {["Basic Info", "Technical Details", "Data & Impact", "Review"].map((label, i) => (
          <div key={i} className="flex-1">
            <div className={`h-2 rounded-full ${i + 1 <= step ? "bg-brand-500" : "bg-gray-200"}`} />
            <p className={`text-xs mt-1 ${i + 1 <= step ? "text-brand-500 font-medium" : "text-gray-400"}`}>{label}</p>
          </div>
        ))}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-md mb-4 text-sm">{error}</div>
      )}

      <div className="bg-white rounded-lg shadow p-6">
        {/* Step 1: Basic Info */}
        {step === 1 && (
          <div className="space-y-4">
            <Field label="System Name *" value={form.name} onChange={v => set("name", v)} placeholder="e.g., Credit Scoring Model v2" />
            <Field label="Description" value={form.description || ""} onChange={v => set("description", v)} placeholder="Brief description of the AI system" multiline />
            <Field label="Purpose Statement *" value={form.purpose_statement} onChange={v => set("purpose_statement", v)}
              placeholder="Describe what this AI system does and who it affects. This is used for Annex III risk classification."
              multiline hint="This field drives automatic risk classification under EU AI Act Annex III. Be specific about the system's purpose, affected population, and decision type." />
            <div className="flex justify-end">
              <button onClick={() => setStep(2)} disabled={!form.name || !form.purpose_statement}
                className="px-4 py-2 bg-brand-500 text-white rounded-md text-sm disabled:opacity-50 hover:bg-brand-600">
                Next: Technical Details
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Technical */}
        {step === 2 && (
          <div className="space-y-4">
            <Select label="Model Type" value={form.model_type} onChange={v => set("model_type", v)} options={MODEL_TYPES} />
            <Select label="Deployment Environment" value={form.deployment_env} onChange={v => set("deployment_env", v)} options={DEPLOY_ENVS} />
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Deployment Geography</label>
              <div className="flex flex-wrap gap-2">
                {GEOS.map(geo => (
                  <button key={geo} onClick={() => toggleGeo(geo)}
                    className={`px-3 py-1 rounded-full text-xs font-medium border transition-colors ${
                      (form.deployment_geo || []).includes(geo)
                        ? "bg-brand-500 text-white border-brand-500"
                        : "bg-white text-gray-600 border-gray-300 hover:border-brand-500"
                    }`}>
                    {geo}
                  </button>
                ))}
              </div>
            </div>
            <div className="flex justify-between">
              <button onClick={() => setStep(1)} className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900">Back</button>
              <button onClick={() => setStep(3)} className="px-4 py-2 bg-brand-500 text-white rounded-md text-sm hover:bg-brand-600">
                Next: Data & Impact
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Data & Impact */}
        {step === 3 && (
          <div className="space-y-4">
            <Select label="Sector" value={form.sector} onChange={v => set("sector", v)} options={SECTORS} />
            <Select label="Decision Automation Level" value={form.decision_automation} onChange={v => set("decision_automation", v)} options={AUTOMATION_LEVELS} />
            <Select label="Data Sensitivity" value={form.data_sensitivity} onChange={v => set("data_sensitivity", v)} options={DATA_SENSITIVITIES} />
            <Field label="Affected Population" value={form.affected_population || ""} onChange={v => set("affected_population", v)}
              placeholder="Describe who is affected by this system's decisions" multiline />
            <div className="flex justify-between">
              <button onClick={() => setStep(2)} className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900">Back</button>
              <button onClick={() => setStep(4)} className="px-4 py-2 bg-brand-500 text-white rounded-md text-sm hover:bg-brand-600">
                Next: Review
              </button>
            </div>
          </div>
        )}

        {/* Step 4: Review */}
        {step === 4 && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Review & Submit</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <ReviewField label="Name" value={form.name} />
              <ReviewField label="Model Type" value={form.model_type} />
              <ReviewField label="Sector" value={form.sector} />
              <ReviewField label="Automation" value={form.decision_automation} />
              <ReviewField label="Environment" value={form.deployment_env} />
              <ReviewField label="Data Sensitivity" value={form.data_sensitivity} />
              <ReviewField label="Geography" value={(form.deployment_geo || []).join(", ") || "Not specified"} />
            </div>
            <div className="border-t pt-4">
              <ReviewField label="Purpose Statement" value={form.purpose_statement} />
            </div>
            <div className="bg-blue-50 border border-blue-200 rounded-md p-3 text-sm text-blue-800">
              Upon submission, the system will automatically run dual risk classification (EU AI Act + US OMB M-25-21). If classified as high-risk, an approval workflow will be triggered.
            </div>
            <div className="flex justify-between">
              <button onClick={() => setStep(3)} className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900">Back</button>
              <button onClick={handleSubmit} disabled={submitting}
                className="px-6 py-2 bg-brand-500 text-white rounded-md text-sm font-medium disabled:opacity-50 hover:bg-brand-600">
                {submitting ? "Classifying..." : "Register & Classify"}
              </button>
            </div>
          </div>
        )}

        {/* Step 5: Result */}
        {step === 5 && result && (
          <div className="space-y-4 text-center">
            <div className="text-4xl">&#9989;</div>
            <h3 className="text-xl font-bold text-gray-900">System Registered Successfully</h3>
            <div className="flex justify-center gap-4 mt-4">
              <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 text-center">
                <p className="text-xs text-gray-500 mb-1">EU AI Act</p>
                <p className="text-lg font-bold capitalize">{result.eu_risk_tier}</p>
              </div>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
                <p className="text-xs text-gray-500 mb-1">US OMB M-25-21</p>
                <p className="text-lg font-bold capitalize">{result.us_designation?.replace("_", " ")}</p>
              </div>
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
                <p className="text-xs text-gray-500 mb-1">Risk Score</p>
                <p className="text-lg font-bold">{result.risk_score?.toFixed(1)}</p>
              </div>
            </div>
            <div className="flex justify-center gap-3 mt-6">
              <a href={`/inventory/${result.id}`} className="px-4 py-2 bg-brand-500 text-white rounded-md text-sm hover:bg-brand-600">
                View System Detail
              </a>
              <a href="/inventory" className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md text-sm hover:bg-gray-50">
                Back to Inventory
              </a>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ── Form Components ──

function Field({ label, value, onChange, placeholder, multiline, hint }: {
  label: string; value: string; onChange: (v: string) => void;
  placeholder?: string; multiline?: boolean; hint?: string;
}) {
  const cls = "w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-brand-500 focus:border-transparent";
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      {multiline
        ? <textarea className={`${cls} min-h-[80px]`} value={value} onChange={e => onChange(e.target.value)} placeholder={placeholder} />
        : <input className={cls} value={value} onChange={e => onChange(e.target.value)} placeholder={placeholder} />}
      {hint && <p className="text-xs text-gray-400 mt-1">{hint}</p>}
    </div>
  );
}

function Select({ label, value, onChange, options }: {
  label: string; value: string; onChange: (v: string) => void; options: string[];
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <select className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm" value={value} onChange={e => onChange(e.target.value)}>
        {options.map(opt => (
          <option key={opt} value={opt}>{opt.replace("_", " ")}</option>
        ))}
      </select>
    </div>
  );
}

function ReviewField({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-sm font-medium text-gray-900 capitalize">{value.replace("_", " ")}</p>
    </div>
  );
}
