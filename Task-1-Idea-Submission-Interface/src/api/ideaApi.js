import { config, buildPayload, MODULES } from "../config.js";
import { ApiError, request } from "./client.js";
import { mockSubmitIdea, mockSearchWeb, mockAdvisorReply } from "./mock.js";

// A reply is usable only if it is a JSON object with at least one report section
// (market analysis, SWOT and so on). Anything else becomes a clear error message
// instead of an empty report page.
function assertReadable(data) {
  const isObject = data && typeof data === "object" && !Array.isArray(data);
  const hasSection =
    isObject && MODULES.some((m) => m.id !== "extraction" && m.keys.some((k) => data[k] !== undefined && data[k] !== null));
  if (!hasSection) {
    throw new ApiError(
      "The server replied, but the answer was not in the expected format. Please try again, or ask the backend team to check the /validate response."
    );
  }
  return data;
}

export async function submitIdea(form) {
  const payload = buildPayload(form);
  if (config.useMock) return mockSubmitIdea(payload);
  return assertReadable(await request(config.endpoints.submitIdea, { method: "POST", body: payload }));
}

// Optional: Task 3's web search agent (POST /api/web-search, body { startup_idea }).
export async function searchWeb(form) {
  if (config.useMock) return mockSearchWeb(form);
  const startup_idea =
    `${form.name.trim()}: ${form.description.trim()} ` +
    `Industry: ${form.industry}. Target customers: ${form.target_customers.trim()}.`;
  return request(config.endpoints.webSearch, {
    method: "POST",
    body: { startup_idea: startup_idea.slice(0, 1500) },
  });
}

export async function askAdvisor(message, ideaId) {
  if (config.useMock) return mockAdvisorReply(message);
  if (!config.endpoints.advisor) {
    throw new ApiError("The advisor is not available yet. It will work once the backend adds it.");
  }
  return request(config.endpoints.advisor, {
    method: "POST",
    body: { message, idea_id: ideaId },
  });
}
