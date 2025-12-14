<script setup>
const props = defineProps({
  robot: { type: Object, default: null },
  currentTask: { type: Object, default: null },
});
</script>

<template>
  <section class="panel">
    <header class="head">
      <h4>Robot</h4>
      <span class="id">AGV-1</span>
    </header>

    <div class="grid">
      <div class="row"><span class="k">State</span><span class="v">{{ robot?.state || "—" }}</span></div>
      <div class="row"><span class="k">Battery</span><span class="v">{{ robot?.battery != null ? robot.battery + "%" : "—" }}</span></div>
      <div class="row"><span class="k">Area</span><span class="v">{{ robot?.area || "—" }}</span></div>
      <div class="row"><span class="k">Target</span><span class="v">{{ currentTask?.target_area || robot?.target_area || "—" }}</span></div>
      <div class="row"><span class="k">Task</span><span class="v mono">{{ robot?.task_id || currentTask?.task_id || "—" }}</span></div>
    </div>
  </section>
</template>

<style scoped>
.panel{
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(10, 12, 20, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.10);
  backdrop-filter: blur(10px);
}
.head{
  display:flex; align-items:baseline; justify-content:space-between;
  margin-bottom: 10px;
}
.head h4{ margin:0; font-size:14px; }
.id{ font-size:12px; color: rgba(255,255,255,0.55); }
.grid{ display:flex; flex-direction:column; gap: 8px; }
.row{ display:flex; justify-content:space-between; gap: 10px; }
.k{ font-size:12px; color: rgba(255,255,255,0.55); }
.v{ font-size:13px; font-weight:600; color: rgba(255,255,255,0.85); }
.mono{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size:12px; }
</style>
