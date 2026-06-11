<!-- src/components/InteractionPreview.vue -->
<script setup>
import { computed } from "vue";

const props = defineProps({
  interactions: { type: Array, default: () => [] },
  title: { type: String, default: "Recent Interaction" },
  limit: { type: Number, default: 8 },
});

function fmt(ts) {
  if (!ts) return "—";
  const d = new Date(ts);
  if (Number.isNaN(d.getTime())) return String(ts);
  return d.toLocaleString();
}

function modeIcon(m) {
  if (m === "voice") return "🎙️";
  if (m === "text") return "⌨️";
  if (m === "button") return "🧷";
  return "🧩";
}

const items = computed(() => props.interactions.slice(0, props.limit));
</script>

<template>
  <div class="card">
    <div class="head">
      <div class="title">{{ title }}</div>
      <router-link class="link" to="/interaction">open</router-link>
    </div>

    <div v-if="items.length === 0" class="empty">No interactions</div>

    <div class="list" v-else>
      <div class="row" v-for="it in items" :key="it.interaction_id || it.ts">
        <div class="left">
          <div class="top">
            <span class="icon">{{ modeIcon(it.input_mode) }}</span>
            <span class="type">{{ it.type || "—" }}</span>
            <span class="pill soft" v-if="it.result">{{ it.result }}</span>
          </div>
          <div class="sub">
            <span class="mono" v-if="it.target_area">target: {{ it.target_area }}</span>
            <span class="mono" v-if="it.task_id">task: {{ it.task_id }}</span>
          </div>
        </div>
        <div class="time">{{ fmt(it.ts) }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 16px;
  padding: 14px;
  backdrop-filter: blur(10px);
}
.head { display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; }
.title { font-weight:700; font-size:14px; }
.link { font-size: 12px; opacity:.85; text-decoration:none; }
.link:hover { opacity: 1; text-decoration: underline; }
.empty { opacity:.7; font-size:12px; padding: 12px 0; }
.list {
  display:flex;
  flex-direction:column;
  gap:8px;
  min-height: 0;
  overflow: auto;
}
.row { display:flex; justify-content:space-between; gap:12px; padding: 10px 12px; border-radius: 14px; border: 1px solid rgba(255,255,255,0.10); background: rgba(0,0,0,0.10); }
.left { min-width:0; }
.top { display:flex; gap:8px; align-items:center; flex-wrap:wrap; }
.icon { font-size: 14px; }
.type { font-size: 13px; font-weight: 700; letter-spacing:.2px; }
.pill {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(255,255,255,0.06);
}
.pill.soft { opacity:.85; }
.sub { margin-top: 4px; display:flex; gap:10px; flex-wrap:wrap; opacity:.8; font-size: 11px; }
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }
.time { font-size: 11px; opacity:.75; white-space: nowrap; }
</style>
