<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import { getRobots } from "@/api/agv";

const robots = ref([]);
const loading = ref(true);
const error = ref(null);
const lastUpdated = ref(null);

let timerId = null;

async function load() {
  loading.value = true;
  error.value = null;

  try {
    const data = await getRobots();
    robots.value = data || [];
    lastUpdated.value = new Date();
  } catch (e) {
    console.error(e);
    error.value = "로봇 정보를 불러오지 못했습니다.";
  } finally {
    loading.value = false;
  }
}

function formatTime(ts) {
  if (!ts) return "-";
  return new Date(ts).toLocaleTimeString();
}

onMounted(() => {
  load();
  // 자동 새로고침 (원하면 주기 조절)
  // timerId = setInterval(load, 2000);
});

onBeforeUnmount(() => {
  // if (timerId) clearInterval(timerId);
});
</script>

<template>
  <div class="robots-page">
    <div class="page-header">
      <h2>Robots</h2>
      <div class="controls">
        <button @click="load">↻ Refresh</button>
        <span v-if="lastUpdated" class="updated">
          Updated: {{ formatTime(lastUpdated) }}
        </span>
      </div>
    </div>

    <div v-if="loading" class="status">Loading robots...</div>
    <div v-else-if="error" class="status error">{{ error }}</div>

    <div v-else class="robots-wrapper">
      <div
        v-if="robots.length"
        v-for="r in robots"
        :key="r.robot_id"
        class="robot-card"
        :class="(r.state || 'unknown').toLowerCase()"
      >
        <div class="robot-header">
          <span class="robot-id">{{ r.robot_id }}</span>
          <span
            class="state-pill"
            :class="(r.state || 'unknown').toLowerCase()"
          >
            {{ (r.state || "unknown").toUpperCase() }}
          </span>
        </div>

        <div class="robot-main">
          <div>🔋 {{ r.battery != null ? r.battery + "%" : "-" }}</div>
          <div>📍 {{ r.area || "-" }}</div>
          <div>🧾 {{ r.task_id || "-" }}</div>
          <div v-if="r.error_code" class="error">
            ⚠ ERROR: {{ r.error_code }}
          </div>
        </div>

        <div class="robot-footer">
          <span>UPDATED</span>
          <span>{{ formatTime(r.updated_at) }}</span>
        </div>
      </div>

      <div v-if="!robots.length" class="empty">No robot data yet.</div>
    </div>
  </div>
</template>

<style scoped>
.robots-page {
  max-width: 1100px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.page-header h2 {
  font-size: 22px;
  font-weight: 700;
}

.controls {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.controls button {
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid #4b5563;
  background: #020617;
  color: #e5e7eb;
  cursor: pointer;
  font-size: 12px;
}
.controls button:hover {
  background: #111827;
}

.updated {
  color: #9ca3af;
}

.status {
  margin-top: 8px;
  font-size: 13px;
}
.status.error {
  color: #f97316;
}

.robots-wrapper {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 12px;
}

.robot-card {
  width: 230px;
  background: radial-gradient(circle at top left, #0f172a, #020617);
  border-radius: 16px;
  padding: 12px 14px;
  box-shadow: 0 0 18px rgba(15, 23, 42, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.35);
  color: #e5e7eb;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.robot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.robot-id {
  font-weight: 700;
  font-size: 15px;
}

.state-pill {
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 600;
  border: 1px solid rgba(148, 163, 184, 0.5);
}

.state-pill.idle {
  background: rgba(148, 163, 184, 0.15);
  border-color: #9ca3af;
}
.state-pill.running {
  background: rgba(34, 197, 94, 0.15);
  border-color: #22c55e;
  color: #bbf7d0;
}
.state-pill.charging {
  background: rgba(234, 179, 8, 0.12);
  border-color: #eab308;
  color: #fef9c3;
}
.state-pill.error,
.state-pill.failed,
.state-pill.fault {
  background: rgba(239, 68, 68, 0.16);
  border-color: #ef4444;
  color: #fecaca;
}
.state-pill.unknown {
  background: rgba(59, 130, 246, 0.12);
  border-color: #3b82f6;
  color: #bfdbfe;
}

.robot-main {
  font-size: 13px;
  line-height: 1.4;
  margin: 4px 0 8px;
}
.robot-main > div {
  margin: 2px 0;
}
.robot-main .error {
  color: #fca5a5;
  font-size: 12px;
}

.robot-footer {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: #9ca3af;
  border-top: 1px dashed rgba(55, 65, 81, 0.8);
  padding-top: 4px;
  margin-top: 4px;
}

.empty {
  font-size: 12px;
  color: #9ca3af;
  padding: 8px;
}
</style>
