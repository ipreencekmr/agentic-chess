import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: 10000
});

export async function startGame(payload) {
  const { data } = await api.post("/game/start", payload);
  return data;
}

export async function getHealth() {
  const { data } = await api.get("/health");
  return data;
}

export async function getGame(gameId) {
  const { data } = await api.get(`/game/${gameId}`);
  return data;
}

export async function move(gameId, moveUci) {
  const { data } = await api.post(`/game/${gameId}/move`, { move: moveUci });
  return data;
}

export async function agentMove(gameId) {
  const { data } = await api.post(`/game/${gameId}/agent-move`);
  return data;
}

export async function reset(gameId) {
  const { data } = await api.post(`/game/${gameId}/reset`);
  return data;
}

export async function undo(gameId) {
  const { data } = await api.post(`/game/${gameId}/undo`);
  return data;
}
