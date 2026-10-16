// Sample backend used when VITE_USE_MOCK=true. Lets you build and demo the UI
// without any server. It mimics the response shape of the team's backend
// (Task-4 `ValidationReport`), so switching to the real backend changes nothing in the UI.

const wait = (ms) => new Promise((r) => setTimeout(r, ms));

export async function mockSubmitIdea(payload) {
  await wait(2400);
  return {
    startup_idea: {
      location: "India",
      budget: "Not specified",
      ...payload,
    },
    market_analysis: {
      potential_demand: "Requires customer validation",
      target_customers: payload.target_market,
      opportunities: ["Interview potential customers", "Test demand with a landing page"],
      evidence_limit: "Sample data; no verified market data used.",
    },
    competitor_analysis: {
      direct_competitors: "Not yet verified",
      indirect_competitors: "Existing alternatives customers use",
      differentiation_questions: ["What problem is solved better?", "Why would customers switch?"],
      evidence_limit: "Sample data; competitor names not verified.",
    },
    swot_and_risks: {
      strengths: ["A defined target customer can guide testing"],
      weaknesses: ["Demand and costs are not yet validated"],
      opportunities: ["Test a focused solution with early users"],
      threats: ["Competition and low willingness to pay"],
      risks: ["Customer demand risk", "Technical feasibility risk", "Financial sustainability risk"],
    },
    mvp_recommendation: {
      mvp_features: [
        "One core feature solving the main customer problem",
        "Simple onboarding",
        "A feedback collection mechanism",
      ],
      validation_plan: ["Interview 10 potential customers", "Build a clickable prototype", "Measure interest before scaling"],
      success_metric: "Set a measurable target after initial interviews",
    },
    sources: [
      {
        title: `Market research for ${payload.industry}`,
        url: "https://example.com/market-research",
        content: "Placeholder research. Replace with verified web research.",
      },
    ],
    final_summary: `Preliminary validation for ${payload.name}: this is an initial hypothesis, not proof of business viability. Validate customer demand, willingness to pay, competitors, costs and technical feasibility before investing.`,
  };
}

// Same shape as Task 3's POST /api/web-search response.
export async function mockSearchWeb(form) {
  await wait(600);
  return {
    startup_idea: form.description,
    generated_queries: [`${form.industry} market trends and industry analysis`, `competitors offering ${form.name}`],
    total_results: 1,
    results: [
      {
        title: `Sample result for ${form.industry}`,
        url: "https://example.com/sample-search-result",
        content: "Placeholder search result used in demo mode.",
        score: 0.5,
        search_query: `${form.industry} market trends and industry analysis`,
      },
    ],
    failed_queries: [],
    status: "success",
  };
}

export async function mockAdvisorReply(message) {
  await wait(600);
  return { reply: `Demo reply to: "${message}". The real advisor will answer once the backend supports it.` };
}
