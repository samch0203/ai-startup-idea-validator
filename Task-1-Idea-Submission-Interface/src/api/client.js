import { config } from "../config.js";

export class ApiError extends Error {
  constructor(message, status = 0, data = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

// Works with FastAPI ({detail: "..."} or {detail: [{msg: "..."}]}) and common shapes.
function extractMessage(data) {
  if (!data || typeof data !== "object") return "";
  const d = data.detail ?? data.message ?? data.error;
  if (typeof d === "string") return d;
  if (Array.isArray(d)) {
    return d
      .map((x) => (typeof x === "string" ? x : x?.msg))
      .filter(Boolean)
      .join("; ");
  }
  return "";
}

export async function request(path, { method = "GET", body, timeoutMs = 120000 } = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const res = await fetch(config.apiBaseUrl + path, {
      method,
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    });

    const text = await res.text();
    let data = null;
    if (text) {
      try {
        data = JSON.parse(text);
      } catch {
        data = { raw: text };
      }
    }

    if (!res.ok) {
      throw new ApiError(
        extractMessage(data) || `The server returned an error (${res.status}).`,
        res.status,
        data
      );
    }
    return data;
  } catch (err) {
    if (err instanceof ApiError) throw err;
    if (err.name === "AbortError") {
      throw new ApiError("The server took too long to respond. Please try again.");
    }
    throw new ApiError("Could not reach the server. Check that the backend is running.");
  } finally {
    clearTimeout(timer);
  }
}
