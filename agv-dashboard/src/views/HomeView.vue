<script setup>
import { onMounted, onBeforeUnmount, ref } from "vue";

import HomeHero from "@/components/HomeHero.vue";
import KpiStrip from "@/components/KpiStrip.vue";

import BMapCard from "@/components/BMapCard.vue";
import BRobotPanel from "@/components/BRobotPanel.vue";

import AlertsPanel from "@/components/AlertsPanel.vue";
import EventsPreview from "@/components/EventsPreview.vue";

import { getRobots, getTasks, getEvents } from "@/api/agv";

const robot = ref(null);
const tasks = ref([]);
const events = ref([]);
const currentTask = ref(null);

async function refreshFast() {
  const robots = await getRobots({ limit: 1 });
  robot.value = robots?.[0] || null;

  events.value = (await getEvents({ limit: 12 })) || [];

  if (robot.value?.task_id) {
    currentTask.value =
      tasks.value.find(t => t.task_id === robot.value.task_id) || null;
  } else {
    currentTask.value = null;
  }
}

async function refreshSlow() {
  tasks.value = (await getTasks({ limit: 200 })) || [];

  if (robot.value?.task_id && !currentTask.value) {
    currentTask.value =
      tasks.value.find(t => t.task_id === robot.value.task_id) || null;
  }
}

let fastTimer = null;
let slowTimer = null;

onMounted(async () => {
  await refreshSlow();
  await refreshFast();
  fastTimer = setInterval(refreshFast, 2000);
  slowTimer = setInterval(refreshSlow, 10000);
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

      <EventsPreview class="events" :events="events" />
    </div>
  </div>
</template>

<style scoped>
.overview {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.bde {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  grid-template-rows: auto auto;
  gap: 14px;
}

.bmap {
  grid-row: 1 / span 2;
}

.rightTop {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
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
