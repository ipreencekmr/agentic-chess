const BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";
const TIMEOUT = 10000;

async function fetchWithTimeout(resource, options = {}) {
  const { timeout = TIMEOUT } = options;
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);
  try {
    const response = await fetch(resource, {
      ...options,
      signal: controller.signal
    });
    clearTimeout(id);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } finally {
    clearTimeout(id);
  }
}

export async function startGame(payload) {
  return await fetchWithTimeout(`${BASE_URL}/game/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
}

export async function getHealth() {
  return await fetchWithTimeout(`${BASE_URL}/health`);
}

export async function getGame(gameId) {
  return await fetchWithTimeout(`${BASE_URL}/game/${gameId}`);
}

export async function move(gameId, moveUci) {
  return await fetchWithTimeout(`${BASE_URL}/game/${gameId}/move`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ move: moveUci })
  });
}

export async function agentMove(gameId) {
  return await fetchWithTimeout(`${BASE_URL}/game/${gameId}/agent-move`, {
    method: "POST"
  });
}

export async function reset(gameId) {
  return await fetchWithTimeout(`${BASE_URL}/game/${gameId}/reset`, {
    method: "POST"
  });
}

export async function undo(gameId) {
  return await fetchWithTimeout(`${BASE_URL}/game/${gameId}/undo`, {
    method: "POST"
  });
}