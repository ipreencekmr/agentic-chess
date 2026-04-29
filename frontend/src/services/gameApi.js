const BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";
const TIMEOUT = 10000;

/**
 * Fetch with timeout using AbortController.
 * @param {string} resource - The resource URL.
 * @param {object} options - Fetch options, may include timeout.
 * @returns {Promise<any>} - Parsed JSON response.
 */
async function fetchWithTimeout(resource, options = {}) {
  const { timeout = TIMEOUT } = options;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(resource, {
      ...options,
      signal: controller.signal
    });
    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } finally {
    clearTimeout(timeoutId);
  }
}

/**
 * Start a new game.
 * @param {object} payload - Game start payload.
 * @returns {Promise<any>}
 */
export async function startGame(payload) {
  return await fetchWithTimeout(`${BASE_URL}/game/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
}

/**
 * Get health status of the API.
 * @returns {Promise<any>}
 */
export async function getHealth() {
  return await fetchWithTimeout(`${BASE_URL}/health`);
}

/**
 * Get game state by ID.
 * @param {string} gameId - Game identifier.
 * @returns {Promise<any>}
 */
export async function getGame(gameId) {
  return await fetchWithTimeout(`${BASE_URL}/game/${gameId}`);
}

/**
 * Make a move in the game.
 * @param {string} gameId - Game identifier.
 * @param {string} moveUci - Move in UCI format.
 * @returns {Promise<any>}
 */
export async function move(gameId, moveUci) {
  return await fetchWithTimeout(`${BASE_URL}/game/${gameId}/move`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ move: moveUci })
  });
}

/**
 * Request agent to make a move.
 * @param {string} gameId - Game identifier.
 * @returns {Promise<any>}
 */
export async function agentMove(gameId) {
  return await fetchWithTimeout(`${BASE_URL}/game/${gameId}/agent-move`, {
    method: "POST"
  });
}

/**
 * Reset the game state.
 * @param {string} gameId - Game identifier.
 * @returns {Promise<any>}
 */
export async function reset(gameId) {
  return await fetchWithTimeout(`${BASE_URL}/game/${gameId}/reset`, {
    method: "POST"
  });
}

/**
 * Undo the last move in the game.
 * @param {string} gameId - Game identifier.
 * @returns {Promise<any>}
 */
export async function undo(gameId) {
  return await fetchWithTimeout(`${BASE_URL}/game/${gameId}/undo`, {
    method: "POST"
  });
}


export async function explainMove(gameId) {
  return await fetchWithTimeout(`${BASE_URL}/game/${gameId}/explain-move`, {
    method: "POST",
    timeout: 30000  // 30 seconds for LLM explanation
  });
}
