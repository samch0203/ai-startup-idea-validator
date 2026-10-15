// Saves submitted ideas in the browser (localStorage) so the Workspace works
// without any backend database. Every access is wrapped: storage can be blocked.

const KEY = "idea-validator.workspace.v1";

function readAll() {
  try {
    const raw = localStorage.getItem(KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function writeAll(items) {
  try {
    localStorage.setItem(KEY, JSON.stringify(items));
  } catch {
    /* ignore: storage full or blocked */
  }
}

export function listIdeas() {
  return readAll();
}

export function getIdea(id) {
  return readAll().find((i) => i.id === id) || null;
}

export function saveIdea({ form, result }) {
  const item = {
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    createdAt: new Date().toISOString(),
    form,
    result,
  };
  writeAll([item, ...readAll()]);
  return item;
}

export function deleteIdea(id) {
  writeAll(readAll().filter((i) => i.id !== id));
}
