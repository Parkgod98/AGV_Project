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
