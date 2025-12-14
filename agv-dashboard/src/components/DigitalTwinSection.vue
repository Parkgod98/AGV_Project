<script setup>
import MiniMap from "@/components/MiniMap.vue";

const props = defineProps({
  robot: { type: Object, default: null },
  currentTask: { type: Object, default: null },
});
</script>

<template>
  <section class="twin">
    <header class="twin-head">
      <h3>Digital Twin</h3>
      <span class="sub">Live position & mission state</span>
    </header>

    <div class="twin-body">
      <!-- MAP -->
      <div class="map-wrap">
        <MiniMap
          :pose="robot?.pose"
          :currentArea="robot?.area || ''"
          :targetArea="currentTask?.target_area || robot?.target_area || ''"
          :large="true"
        />
      </div>

      <!-- AGV INFO PANEL -->
      <aside class="panel">
        <div class="row">
          <span class="label">Robot</span>
          <span class="value">AGV-1</span>
        </div>

        <div class="row">
          <span class="label">State</span>
          <span class="value state" :data-state="robot?.state">
            {{ robot?.state || "unknown" }}
          </span>
        </div>

        <div class="row">
          <span class="label">Battery</span>
          <span class="value">
            {{ robot?.battery != null ? robot.battery + "%" : "—" }}
          </span>
        </div>

        <div class="row">
          <span class="label">Area</span>
          <span class="value">{{ robot?.area || "—" }}</span>
        </div>

        <div class="row">
          <span class="label">Target</span>
          <span class="value">
            {{ currentTask?.target_area || robot?.target_area || "—" }}
          </span>
        </div>

        <div class="row">
          <span class="label">Task ID</span>
          <span class="value mono">
            {{ robot?.task_id || currentTask?.task_id || "—" }}
          </span>
        </div>
      </aside>
    </div>
  </section>
</template>

<style scoped>
.twin {
  width: 100%;
  padding: 16px 18px 18px;
  border-radius: 22px;
  background: rgba(10, 12, 20, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.10);
  backdrop-filter: blur(12px);
}

.twin-head {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 12px;
}

.twin-head h3 {
  margin: 0;
  font-size: 14px;
  letter-spacing: 0.3px;
}

.sub {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.twin-body {
  display: grid;
  grid-template-columns: 2.2fr 1fr;
  gap: 14px;
  align-items: stretch;
}

/* MAP */
.map-wrap {
  position: relative;
  height: 300px;          /* ✅ 핵심: Overview에서 맵 높이 제한 */
  border-radius: 16px;
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.06);
  overflow: hidden;
}

/* PANEL */
.panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 14px 14px;
  border-radius: 16px;
  background: rgba(8, 10, 16, 0.45);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.55);
}

.value {
  font-size: 13px;
  font-weight: 600;
}

.value.mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 12px;
}

/* state color hint (subtle) */
.value.state[data-state="running"] {
  color: rgba(0, 220, 180, 0.95);
}
.value.state[data-state="idle"] {
  color: rgba(255, 255, 255, 0.85);
}
.value.state[data-state="error"] {
  color: rgba(255, 90, 90, 0.95);
}

@media (max-width: 1000px) {
  .twin-body {
    grid-template-columns: 1fr;
  }
}
</style>
