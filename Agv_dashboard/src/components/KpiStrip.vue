<script setup>
import { computed } from "vue";

/**
 * props.tasks: 최근 N개 task 배열
 * task: { status, created_at, started_at, finished_at }
 */
const props = defineProps({
  tasks: { type: Array, default: () => [] },
});

// 오늘 00:00 기준
const todayStart = () => {
  const d = new Date();
  d.setHours(0, 0, 0, 0);
  return d.getTime();
};

const todayTasks = computed(() =>
  props.tasks.filter(t => (t.created_at ?? 0) >= todayStart())
);

const doneTasks = computed(() =>
  todayTasks.value.filter(t => t.status === "done")
);

const failedTasks = computed(() =>
  todayTasks.value.filter(t => t.status === "failed")
);

const successRate = computed(() => {
  const total = doneTasks.value.length + failedTasks.value.length;
  if (total === 0) return "—";
  return `${Math.round((doneTasks.value.length / total) * 100)}%`;
});

const avgDuration = computed(() => {
  const finished = doneTasks.value.filter(
    t => t.started_at && t.finished_at
  );
  if (finished.length === 0) return "—";

  const avgMs =
    finished.reduce((sum, t) => sum + (t.finished_at - t.started_at), 0) /
    finished.length;

  const sec = Math.round(avgMs / 1000);
  return sec < 60 ? `${sec}s` : `${Math.round(sec / 60)}m`;
});
</script>

<template>
  <section class="kpi">
    <div class="item">
      <div class="value">{{ todayTasks.length }}</div>
      <div class="label">Today Tasks</div>
    </div>

    <div class="item">
      <div class="value">{{ successRate }}</div>
      <div class="label">Success Rate</div>
    </div>

    <div class="item">
      <div class="value">{{ avgDuration }}</div>
      <div class="label">Avg Duration</div>
    </div>

    <div class="item danger">
      <div class="value">{{ failedTasks.length }}</div>
      <div class="label">Failures</div>
    </div>
  </section>
</template>

<style scoped>
.kpi {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;

  padding: 14px 18px;
  border-radius: 18px;

  background: rgba(12, 14, 24, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
}

.item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.value {
  font-size: 26px;
  font-weight: 800;
  letter-spacing: -0.3px;
}

.label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.55);
}

.item.danger .value {
  color: rgba(255, 90, 90, 0.95);
}

@media (max-width: 900px) {
  .kpi {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
}
</style>
