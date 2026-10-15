// =====================================================================
// THE ONLY FILE YOU EDIT WHEN THE BACKEND CHANGES.
// Everything that depends on the backend's choices lives here.
//
// Currently matches Task-4-Multi-Agent-Architecture (POST /validate).
// =====================================================================

export const config = {
  // "" = same origin (dev proxy forwards /validate and /api to the backend).
  apiBaseUrl: import.meta.env.VITE_API_URL || "",

  // true = sample responses, no backend needed.
  useMock: import.meta.env.VITE_USE_MOCK === "true",

  // true = also call Task 3's web search server after /validate (see README).
  enableWebSearch: import.meta.env.VITE_ENABLE_WEB_SEARCH === "true",

  // Endpoint paths (see the backend's /docs page).
  endpoints: {
    submitIdea: "/validate",
    webSearch: "/api/web-search",
    advisor: null, // no advisor endpoint exists in the backend yet
  },
};

// Converts our form into the JSON the backend expects.
// Backend model (Task 4 `StartupIdea`):
//   name, description, target_market, industry  = required
//   location, budget                            = optional (backend has defaults)
// The backend has no "details" field, so those notes are appended to the description.
export function buildPayload(form) {
  const description = form.details.trim()
    ? `${form.description.trim()}\n\nAdditional details: ${form.details.trim()}`
    : form.description.trim();

  const payload = {
    name: form.name.trim(),
    description,
    target_market: form.target_customers.trim(),
    industry: form.industry,
  };
  if (form.location.trim()) payload.location = form.location.trim();
  if (form.budget.trim()) payload.budget = form.budget.trim();
  return payload;
}

// The six agents, in the order the backend runs them.
export const AGENTS = [
  { id: "search", name: "Web search", job: "Finds market data and competitor pages online." },
  { id: "market", name: "Market analysis", job: "Estimates demand, trends and customer segments." },
  { id: "competitors", name: "Competitor analysis", job: "Finds similar companies and where they fall short." },
  { id: "swot", name: "SWOT and risk", job: "Lists strengths, weaknesses, opportunities, threats and risks." },
  { id: "mvp", name: "MVP recommendation", job: "Picks the smallest set of features to build first." },
  { id: "report", name: "Report", job: "Combines everything into one summary." },
];

// Sections of the report.
// `keys` = possible names of that section in the backend's JSON response.
// The first one found is used. Add more names if the backend uses different ones.
export const MODULES = [
  { id: "extraction", label: "Your idea", keys: ["startup_idea", "extracted_idea", "structured_idea", "extraction", "idea"] },
  { id: "search", label: "Web search", keys: ["sources", "search_results", "web_search"] },
  { id: "market", label: "Market analysis", keys: ["market_analysis", "market"] },
  { id: "competitors", label: "Competitors", keys: ["competitor_analysis", "competitors"] },
  { id: "swot", label: "SWOT and risks", keys: ["swot_and_risks", "swot", "swot_analysis", "risks"] },
  { id: "mvp", label: "MVP features", keys: ["mvp_recommendation", "mvp", "mvp_recommendations"] },
  { id: "gtm", label: "Go-to-market", keys: ["go_to_market", "gtm", "gtm_strategy"] },
  { id: "report", label: "Summary", keys: ["final_summary", "report", "final_report"] },
];

export const INDUSTRIES = [
  "Healthcare",
  "Fintech",
  "EdTech",
  "E-commerce",
  "Agriculture",
  "SaaS / Software",
  "Food & Beverage",
  "Travel & Hospitality",
  "Logistics",
  "Entertainment",
  "Other",
];
