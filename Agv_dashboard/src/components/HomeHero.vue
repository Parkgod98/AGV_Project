<script setup>
import { computed } from "vue";

/**
 * props.robot: { state, battery, area, task_id, updated_at, error_code, ... }
 * props.currentTask: { type, target_area, status, ... } | null
 */
const props = defineProps({
  robot: { type: Object, default: null },
  currentTask: { type: Object, default: null },
});

const now = () => Date.now();

const isOffline = computed(() => {
  const ts = props.robot?.updated_at;
  if (!ts) return true;
  return now() - ts > 8000; // 8s 넘으면 offline 처리
});

const statusKind = computed(() => {
  if (!props.robot) return "offline";
  if (props.robot?.state === "error") return "error";
  if (isOffline.value) return "offline";
  if (props.robot?.state === "running") return "running";
  if (props.robot?.state === "charging") return "charging";
  return "idle";
});

const badgeText = computed(() => {
  switch (statusKind.value) {
    case "running": return "RUNNING";
    case "idle": return "IDLE";
    case "charging": return "CHARGING";
    case "error": return "ERROR";
    default: return "OFFLINE";
  }
});

const taskLabel = (t) => {
  if (!t) return "Task";
  const map = {
    deliver_water: "Delivering water",
    collect_cup: "Collecting cups",
    collect_laundry: "Collecting laundry",
  };
  return map[t] || t;
};

const headline = computed(() => {
  if (statusKind.value === "offline") return "AGV is not responding.";
  if (statusKind.value === "error") return "System error detected.";
  if (statusKind.value === "charging") return "Charging at dock.";
  if (statusKind.value === "running") {
    const t = props.currentTask?.type;
    const a = props.currentTask?.target_area || props.robot?.target_area;
    if (t && a) return `${taskLabel(t)} → ${a}`;
    if (t) return `${taskLabel(t)}`;
    return "Executing mission…";
  }
  return `Standing by at ${props.robot?.area || "—"}`;
});

const metaLine = computed(() => {
  const r = props.robot || {};
  const batt = (r.battery ?? null) !== null ? `${r.battery}%` : "—";
  const area = r.area || "—";
  const taskId = r.task_id || props.currentTask?.task_id || "—";
  const updated = r.updated_at ? formatAgo(r.updated_at) : "—";
  return `AGV-1 · Battery ${batt} · Area ${area} · Task ${taskId} · Updated ${updated}`;
});

function formatAgo(ts) {
  const diff = Math.max(0, now() - ts);
  const s = Math.floor(diff / 1000);
  if (s < 60) return `${s}s ago`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  return `${h}h ago`;
}
</script>

<template>
  <section class="hero" :data-kind="statusKind">
    <div class="hero-inner">
      <div class="hero-top">
        <div class="badge">{{ badgeText }}</div>

        <div class="right">
          <div class="pill">
            <span class="dot" />
            <span>{{ isOffline ? "Disconnected" : "Live telemetry" }}</span>
          </div>
        </div>
      </div>

      <div class="hero-main">
        <h2 class="headline">{{ headline }}</h2>
        <p class="meta">{{ metaLine }}</p>

        <div v-if="statusKind === 'error'" class="errorline">
          <span class="label">error_code</span>
          <span class="code">{{ robot?.error_code ?? "unknown" }}</span>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero {
  width: 100%;
  border-radius: 22px;
  padding: 18px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  background:
    radial-gradient(900px 280px at 10% 0%, rgba(120, 130, 255, 0.20), transparent 60%),
    radial-gradient(820px 260px at 90% 0%, rgba(0, 220, 180, 0.14), transparent 55%),
    rgba(10, 12, 20, 0.55);
  backdrop-filter: blur(12px);
  box-shadow: 0 18px 60px rgba(0, 0, 0, 0.35);
}

.hero-inner {
  padding: 10px 10px 6px;
}

.hero-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.badge {
  display: inline-flex;
  align-items: center;
  height: 34px;
  padding: 0 12px;
  border-radius: 999px;
  font-weight: 800;
  font-size: 12px;
  letter-spacing: 0.6px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.06);
}

/* 상태별 “세련된” 강조: 과하게 색칠하지 말고 테두리/글로우만 */
.hero[data-kind="running"] .badge {
  border-color: rgba(0, 220, 180, 0.35);
  box-shadow: 0 0 0 6px rgba(0, 220, 180, 0.08);
}
.hero[data-kind="error"] .badge {
  border-color: rgba(255, 80, 80, 0.40);
  box-shadow: 0 0 0 6px rgba(255, 80, 80, 0.08);
}
.hero[data-kind="offline"] .badge {
  border-color: rgba(255, 255, 255, 0.18);
  opacity: 0.85;
}

.pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 34px;
  padding: 0 12px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  background: rgba(0, 0, 0, 0.20);
  color: rgba(255, 255, 255, 0.75);
  font-size: 12px;
}

.dot {
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: rgba(0, 220, 180, 0.85);
  box-shadow: 0 0 0 5px rgba(0, 220, 180, 0.10);
}

.hero[data-kind="offline"] .dot {
  background: rgba(255, 255, 255, 0.45);
  box-shadow: 0 0 0 5px rgba(255, 255, 255, 0.08);
}
.hero[data-kind="error"] .dot {
  background: rgba(255, 80, 80, 0.85);
  box-shadow: 0 0 0 5px rgba(255, 80, 80, 0.10);
}

.hero-main {
  margin-top: 14px;
}

.headline {
  margin: 0;
  font-size: 30px;
  line-height: 1.15;
  letter-spacing: -0.2px;
}

.meta {
  margin: 10px 0 0;
  color: rgba(255, 255, 255, 0.62);
  font-size: 13px;
}

.errorline {
  margin-top: 12px;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 12px;
  border: 1px solid rgba(255, 80, 80, 0.22);
  background: rgba(255, 80, 80, 0.07);
}

.errorline .label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.70);
  letter-spacing: 0.2px;
}

.errorline .code {
  font-weight: 700;
  letter-spacing: 0.2px;
}

@media (max-width: 820px) {
  .headline { font-size: 24px; }
}
</style>
