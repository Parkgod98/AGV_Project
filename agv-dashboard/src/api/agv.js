import axios from "axios";

// 일단 하드코딩, 나중에 .env로 빼도 됨
// const BASE_URL = "http://localhost:1880/api";
const BASE_URL = "/api";

export async function getRobots({ limit } = {}) {
  const params = {};
  if (limit) params.limit = limit;
  const res = await axios.get(`${BASE_URL}/robots`, { params });
  return res.data.robots;
}

export async function getTasks({ status, limit } = {}) {
  const params = {};
  if (status) params.status = status;
  if (limit) params.limit = limit;
  const res = await axios.get(`${BASE_URL}/tasks`, { params });
  return res.data.tasks;
}

export async function getEvents({ limit } = {}) {
  const params = {};
  if (limit) params.limit = limit;
  const res = await axios.get(`${BASE_URL}/events`, { params });
  return res.data.events;
}

export async function getSummary() {
  const res = await axios.get(`${BASE_URL}/summary`);
  return res.data; // { robots: {...}, tasks: {...}, meta? }
}

/**
 * Report 브리핑(LLM)
 * - user_id 없이 공용
 * - range: "day" | "week"
 * - refresh: 1이면 강제 재생성(서버 캐시 무시)
 */
export async function getUserBrief({ range = "day", refresh = 0 } = {}) {
  const params = { range };
  if (refresh) params.refresh = 1;
  const res = await axios.get(`${BASE_URL}/user/brief`, { params });
  return res.data; // { range, cached, brief, ... }
}

/**
 * (선택) 사용자 요청 생성
 * - user_id 없이 공용
 */
export async function requestTask({ type, target_area, meta } = {}) {
  const payload = {
    type,
    target_area: target_area || null,
    meta: meta || {},
  };
  const res = await axios.post(`${BASE_URL}/user/request`, payload);
  return res.data;
}


export async function getAppSettings() {
  const res = await axios.get(`${BASE_URL}/app/settings`);
  return res.data;
}

export async function saveAppSettings({ settings }) {
  const res = await axios.post(`${BASE_URL}/app/settings`, { settings });
  return res.data;
}

// ✅ Interaction 목록
export async function getInteractions({ limit, type, input_mode, result, q } = {}) {
  const params = {};
  if (limit) params.limit = limit;
  if (type) params.type = type;
  if (input_mode) params.input_mode = input_mode;
  if (result) params.result = result;
  if (q) params.q = q;

  const res = await axios.get(`${BASE_URL}/interactions`, { params });
  return res.data; // { interactions, stats }
}

// ✅ Interaction 인사이트(LLM)
export async function getInteractionInsight({ range = "week", refresh = false } = {}) {
  const params = { range };
  if (refresh) params.refresh = "1";
  const res = await axios.get(`${BASE_URL}/interactions/insight`, { params });
  return res.data; // { range, stats, insight, cached }
}