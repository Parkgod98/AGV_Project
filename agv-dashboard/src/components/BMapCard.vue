<script setup>
import MiniMap from "@/components/MiniMap.vue";

const props = defineProps({
  robot: { type: Object, default: null },
  currentTask: { type: Object, default: null },
});
</script>

<template>
  <section class="mapcard">
    <header class="head">
      <h4>Digital Twin</h4>
      <span class="sub">pose / target</span>
    </header>

    <div class="mapwrap">
      <MiniMap
        :pose="robot?.pose"
        :currentArea="robot?.area || ''"
        :targetArea="currentTask?.target_area || robot?.target_area || ''"
        :large="true"
      />
    </div>
  </section>
</template>

<style scoped>
.mapcard{
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(10, 12, 20, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.10);
  backdrop-filter: blur(10px);
  height: 100%;
}
.head{ display:flex; gap:10px; align-items:baseline; margin-bottom: 10px; }
.head h4{ margin:0; font-size:14px; }
.sub{ font-size:12px; color: rgba(255,255,255,0.55); }

/* 핵심: 맵은 정사각 유지 + 가운데 */
.mapwrap{
  height: 100%;
  min-height: 360px;      /* 필요하면 320~420 사이 조절 */
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.06);
  background: rgba(0,0,0,0.25);
  overflow: hidden;
  display: grid;
}
</style>
