const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      headers: { "Content-Type": "application/json", ...options.headers },
      ...options,
    });
  } catch {
    throw new Error(
      "Impossible de contacter le serveur. Vérifiez que l'API est démarrée.",
    );
  }
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(formatError(body.detail, response.status));
  }
  return response.json();
}

function formatError(detail, status) {
  if (!detail) return `Erreur HTTP ${status}`;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg || JSON.stringify(item)).join(" ; ");
  }
  if (Array.isArray(detail.issues)) {
    return `${detail.message || "Scénario invalide"} : ${detail.issues
      .map((issue) => issue.message)
      .join(" ; ")}`;
  }
  return detail.message || JSON.stringify(detail);
}

/** Construit l'URL absolue d'un média servi par l'API. */
export function mediaUrl(path) {
  if (!path) return null;
  if (/^https?:\/\//.test(path)) return path;
  return `${API_BASE}${path}`;
}

export function exportPdfUrl(projectId) {
  return `${API_BASE}/api/v1/projects/${projectId}/export/pdf`;
}

export function exportImagesUrl(projectId) {
  return `${API_BASE}/api/v1/projects/${projectId}/export/images`;
}

export async function generateStory(input) {
  return request("/api/v1/generate", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export async function createProject(payload) {
  return request("/api/v1/projects", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function listProjects() {
  return request("/api/v1/projects");
}

export async function health() {
  return request("/health");
}
