<script setup>
import { onMounted, onBeforeUnmount, ref } from "vue";

import HomeHero from "@/components/HomeHero.vue";
import KpiStrip from "@/components/KpiStrip.vue";

import BMapCard from "@/components/BMapCard.vue";
import BRobotPanel from "@/components/BRobotPanel.vue";

import AlertsPanel from "@/components/AlertsPanel.vue";
import InteractionPreview from "@/components/InteractionPreview.vue";

import { getRobots, getTasks, getEvents, getInteractions } from "@/api/agv";

const robot = ref(null);
const tasks = ref([]);
const events = ref([]);
const currentTask = ref(null);
const interactions = ref([]);
let fastTimer = null;
let slowTimer = null;
let fastBusy = false;
let slowBusy = false;
async function refreshFast() {
  if (fastBusy) return;
  fastBusy = true;
  try {
    const robots = await getRobots({ limit: 1 });
    robot.value = robots?.[0] || null;

    events.value = (await getEvents({ limit: 12 })) || [];

    // ✅ Recent Interaction 데이터
    interactions.value = (await getInteractions({ limit: 8 }))?.interactions || [];

    if (robot.value?.task_id) {
      currentTask.value = tasks.value.find(t => t.task_id === robot.value.task_id) || null;
    } else {
      currentTask.value = null;
    }
  } finally {
    fastBusy = false;
  }
}

async function refreshSlow() {
  if (slowBusy) return;
  slowBusy = true;
  try {
    tasks.value = (await getTasks({ limit: 200 })) || [];

    if (robot.value?.task_id && !currentTask.value) {
      currentTask.value = tasks.value.find(t => t.task_id === robot.value.task_id) || null;
    }
  } finally {
    slowBusy = false;
  }
}


async function refreshAll() {
  await refreshSlow();
  await refreshFast();
}

onMounted(async () => {
  await refreshAll();

  // ✅ UserApp처럼 로봇은 빠르게(부드럽게), 태스크는 느리게
  fastTimer = setInterval(refreshFast, 200);
  slowTimer = setInterval(refreshSlow, 400);
});

onBeforeUnmount(() => {
  if (fastTimer) clearInterval(fastTimer);
  if (slowTimer) clearInterval(slowTimer);
});
</script>

<template>
  <div class="overview">
    <!-- A -->
    <HomeHero :robot="robot" :currentTask="currentTask" />

    <!-- C -->
    <KpiStrip :tasks="tasks" />

    <!-- BMap + (BRobot + D) + E -->
    <div class="bde">
      <BMapCard class="bmap" :robot="robot" :currentTask="currentTask" />

      <div class="rightTop">
        <BRobotPanel :robot="robot" :currentTask="currentTask" />
        <AlertsPanel :robot="robot" :tasks="tasks" :events="events" />
      </div>

      <InteractionPreview class="events" :interactions="interactions" />
    </div>
  </div>
</template>

<style scoped>
.overview{
  height: 100%;
  min-height: 0;
  overflow: hidden;

  display:flex;
  flex-direction:column;
  gap: 12px;           /* 기존 16이면 줄여 */
}

.bde{
  flex: 1;
  min-height: 0;

  display: grid;
  grid-template-columns: 1.4fr 1fr;
  /* ✅ auto 쓰면 내용만큼 커져서 잘림 → fr로 고정 */
  grid-template-rows: auto minmax(0, 1fr);
  gap: 12px;
}

.bmap{
  grid-row: 1 / span 2;
  height: 100%;
  min-height: 0;
}

.rightTop{
  display:grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;

  /* ✅ row1이 auto라서 큰 의미는 없지만 안전빵 */
  align-self: start;
}

.events{
  min-height: 0;
  height: 100%;
}

@media (max-width: 1100px) {
  .bde {
    grid-template-columns: 1fr;
  }
  .bmap {
    grid-row: auto;
  }
  .rightTop {
    grid-template-columns: 1fr;
  }
}
</style>
