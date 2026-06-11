<!-- src/components/AlertsPanel.vue -->
<script setup>
import { computed } from "vue";

const props = defineProps({
  robot: { type: Object, default: null },
  tasks: { type: Array, default: () => [] },
});

function pick(obj, keys, fallback = null) {
  for (const k of keys) {
    const v = obj?.[k];
    if (v !== undefined && v !== null && v !== "") return v;
  }
  return fallback;
}

const battery = computed(() => {
  const v = pick(props.robot, ["battery", "battery_pct", "batteryPercent"]);
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
});
const errorCode = computed(() => pick(props.robot, ["error_code", "errorCode"], null));
const updatedAt = computed(() => pick(props.robot, ["updated_at", "ts", "timestamp", "last_update"], null));
const state = computed(() => pick(props.robot, ["state", "status", "robot_state"], null));
const taskId = computed(() => pick(props.robot, ["task_id", "current_task_id"], null));

const now = computed(() => Date.now());
const staleMs = computed(() => {
  if (!updatedAt.value) return null;
  const t = Number(updatedAt.value);
  if (!Number.isFinite(t)) return null;
  return now.value - t;
});

const runningTasks = computed(() => props.tasks.filter((t) => t.status === "running"));
const pendingTasks = computed(() => props.tasks.filter((t) => t.status === "pending"));

const alerts = computed(() => {
  const list = [];

  if (errorCode.value) list.push({ sev: "error", title: "Robot error_code set", detail: String(errorCode.value) });
  if (battery.value != null && battery.value <= 20) list.push({ sev: "warn", title: "Low battery", detail: `${battery.value}%` });

  if (staleMs.value != null && staleMs.value > 15_000) {
    list.push({ sev: "warn", title: "Robot status stale", detail: `${Math.floor(staleMs.value / 1000)}s ago` });
  }

  if (state.value === "running" && !taskId.value) {
    list.push({ sev: "warn", title: "Running but task_id is empty", detail: "Check status/task sync" });
  }

  if (runningTasks.value.length > 1) {
    list.push({ sev: "warn", title: "Multiple running tasks", detail: `count=${runningTasks.value.length}` });
  }

  if (pendingTasks.value.length > 0) {
    list.push({ sev: "info", title: "Pending tasks", detail: `count=${pendingTasks.value.length}` });
  }

  if (list.length === 0) list.push({ sev: "ok", title: "All good", detail: "No alerts" });
  return list;
});
</script>

<template>
  <div class="card">
    <div class="head">
      <div class="title">Alerts</div>
      <span class="pill soft">{{ alerts.length }}</span>
    </div>

    <div class="list">
      <div v-for="(a, idx) in alerts" :key="idx" class="a" :class="a.sev">
        <div class="aTitle">{{ a.title }}</div>
        <div class="aDetail">{{ a.detail }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 16px;
  padding: 14px;
  backdrop-filter: blur(10px);
}
.head { display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; }
.title { font-weight:700; font-size:14px; }
.pill {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(255,255,255,0.06);
}
.pill.soft { opacity:.85; }
.list { display:flex; flex-direction:column; gap:8px; }
.a { padding: 10px 12px; border-radius: 14px; border: 1px solid rgba(255,255,255,0.10); background: rgba(0,0,0,0.10); }
.aTitle { font-size: 12px; font-weight: 700; }
.aDetail { font-size: 11px; opacity: .80; margin-top: 2px; }
.a.ok    { border-color: rgba(120,255,200,0.25); }
.a.info  { border-color: rgba(120,200,255,0.25); }
.a.warn  { border-color: rgba(255,220,120,0.30); }
.a.error { border-color: rgba(255,120,120,0.40); }
</style>
