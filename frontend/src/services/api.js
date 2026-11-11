const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Erreur HTTP ${response.status}`);
  }
  return response.json();
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
