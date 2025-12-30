<!-- src/components/BRobotPanel.vue -->
<script setup>
import { computed } from "vue";

const props = defineProps({
  robot: { type: Object, default: null },
  tasks: { type: Array, default: () => [] }, // activeTask 찾기용
});

function pick(obj, keys, fallback = null) {
  for (const k of keys) {
    const v = obj?.[k];
    if (v !== undefined && v !== null && v !== "") return v;
  }
  return fallback;
}

const robotId = computed(() => pick(props.robot, ["robot_id", "id"], "—"));
const state = computed(() => pick(props.robot, ["state", "status", "robot_state"], "—"));
const battery = computed(() => {
  const v = pick(props.robot, ["battery", "battery_pct", "batteryPercent"]);
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
});
const area = computed(() => pick(props.robot, ["area", "place", "zone"], "—"));
const taskId = computed(() => pick(props.robot, ["task_id", "current_task_id"], null));
const errorCode = computed(() => pick(props.robot, ["error_code", "errorCode"], null));
const updatedAt = computed(() => pick(props.robot, ["updated_at", "ts", "timestamp", "last_update"], null));

const activeTask = computed(() => {
  if (!taskId.value) return null;
  return props.tasks.find((t) => t.task_id === taskId.value) || null;
});

const updatedText = computed(() => {
  if (!updatedAt.value) return "—";
  const d = new Date(updatedAt.value);
  if (Number.isNaN(d.getTime())) return String(updatedAt.value);
  return d.toLocaleString();
});

const batteryClass = computed(() => {
  if (battery.value == null) return "soft";
  if (battery.value <= 15) return "bad";
  if (battery.value <= 30) return "warn";
  return "good";
});
</script>

<template>
  <div class="card">
    <div class="head">
      <div class="title">Robot</div>
      <div class="row">
        <span class="pill">{{ robotId }}</span>
        <span class="pill soft">{{ state }}</span>
      </div>
    </div>

    <div class="grid">
      <div class="item">
        <div class="k">Battery</div>
        <div class="v">
          <span class="pill" :class="batteryClass">
            {{ battery == null ? "—" : `${battery}%` }}
          </span>
        </div>
      </div>
      <div class="item">
        <div class="k">Area</div>
        <div class="v">{{ area }}</div>
      </div>
      <div class="item">
        <div class="k">Task</div>
        <div class="v mono">
          {{ taskId || "—" }}
          <span v-if="activeTask?.status" class="pill soft" style="margin-left:6px;">{{ activeTask.status }}</span>
        </div>
      </div>
      <div class="item">
        <div class="k">Error</div>
        <div class="v mono">{{ errorCode || "—" }}</div>
      </div>
      <div class="item full">
        <div class="k">Updated</div>
        <div class="v">{{ updatedText }}</div>
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
.head { display:flex; justify-content:space-between; align-items:flex-start; gap:12px; margin-bottom:10px; }
.title { font-weight:700; font-size:14px; }
.row { display:flex; gap:6px; flex-wrap:wrap; justify-content:flex-end; }
.pill {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(255,255,255,0.06);
}
.pill.soft { opacity:.85; }
.pill.good { border-color: rgba(120,255,200,0.35); }
.pill.warn { border-color: rgba(255,220,120,0.35); }
.pill.bad  { border-color: rgba(255,120,120,0.45); }
.grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
.item { background: rgba(0,0,0,0.12); border: 1px solid rgba(255,255,255,0.08); border-radius: 14px; padding: 10px; }
.item.full { grid-column: 1 / -1; }
.k { font-size: 11px; opacity: .78; margin-bottom: 6px; }
.v { font-size: 13px; font-weight: 650; }
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-size: 12px; font-weight: 600; }
</style>
