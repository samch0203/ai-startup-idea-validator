import { MODULES } from "../config.js";

const ACRONYMS = { mvp: "MVP", swot: "SWOT", gtm: "GTM", ai: "AI", url: "URL" };
const pretty = (key) =>
  String(key)
    .replace(/[_-]+/g, " ")
    .trim()
    .split(" ")
    .map((w, i) => ACRONYMS[w.toLowerCase()] ?? (i === 0 ? w.charAt(0).toUpperCase() + w.slice(1) : w))
    .join(" ");

function renderValue(value, level) {
  if (value === null || value === undefined || value === "") return "";
  if (typeof value === "string") return `${value}\n\n`;
  if (typeof value !== "object") return `${String(value)}\n\n`;
  if (Array.isArray(value)) {
    if (value.every((x) => x === null || typeof x !== "object")) {
      return `${value.map((x) => `- ${x}`).join("\n")}\n\n`;
    }
    return value.map((x) => renderValue(x, level)).join("");
  }
  return Object.entries(value)
    .map(([k, v]) => `${"#".repeat(Math.min(level, 6))} ${pretty(k)}\n\n${renderValue(v, level + 1)}`)
    .join("");
}

function renderSources(items) {
  return `${items
    .map((s) => `- [${s?.title || s?.url}](${s?.url})${s?.content ? `: ${s.content}` : ""}`)
    .join("\n")}\n\n`;
}

function findSection(result, keys) {
  if (!result || typeof result !== "object") return undefined;
  const key = keys.find((k) => result[k] !== undefined && result[k] !== null);
  return key ? result[key] : undefined;
}

export function buildReportMarkdown(item) {
  const { form, result } = item;
  const out = [`# ${form.name || "Startup idea"}: validation report\n\n`];

  out.push(`## Your idea\n\n`);
  out.push(`- Industry: ${form.industry}\n- Target customers: ${form.target_customers}\n`);
  if (form.location) out.push(`- Location: ${form.location}\n`);
  if (form.budget) out.push(`- Budget: ${form.budget}\n`);
  out.push(`\n${form.description}\n\n`);
  if (form.details) out.push(`${form.details}\n\n`);

  for (const m of MODULES) {
    if (m.id === "extraction") continue;
    const data = findSection(result, m.keys);
    if (data === undefined) continue;
    out.push(`## ${m.label}\n\n`);
    out.push(m.id === "search" && Array.isArray(data) ? renderSources(data) : renderValue(data, 3));
  }

  const live = result?.web_search_agent;
  if (live && Array.isArray(live.results) && live.results.length > 0) {
    out.push(`## Live web search\n\n`, renderSources(live.results));
  }

  out.push(`---\nReports are decision support, not proof that an idea will succeed.\n`);
  return out.join("");
}

export function downloadReport(item) {
  try {
    const slug =
      String(item.form.name || "startup-idea")
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-|-$/g, "") || "startup-idea";
    const blob = new Blob([buildReportMarkdown(item)], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${slug}-report.md`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  } catch {
    /* download is a convenience; ignore failures */
  }
}
