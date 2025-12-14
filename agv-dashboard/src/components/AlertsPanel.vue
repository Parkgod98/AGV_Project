<script setup>
import { computed } from "vue";

const props = defineProps({
  robot: { type: Object, default: null },
  tasks: { type: Array, default: () => [] },
  events: { type: Array, default: () => [] },
});

const alerts = computed(() => {
  const list = [];

  // 1) 로봇 오프라인
  if (props.robot?.updated_at) {
    const diff = Date.now() - props.robot.updated_at;
    if (diff > 8000) {
      list.push({
        type: "offline",
        msg: "AGV telemetry disconnected",
      });
    }
  }

  // 2) 로봇 에러 상태
  if (props.robot?.state === "error") {
    list.push({
      type: "error",
      msg: `Robot error (${props.robot.error_code || "unknown"})`,
    });
  }

  // 3) 배터리 낮음
  if (props.robot?.battery != null && props.robot.battery < 20) {
    list.push({
      type: "battery",
      msg: `Low battery (${props.robot.battery}%)`,
    });
  }

  // 4) 최근 실패 태스크
  const recentFail = props.tasks.find(t => t.status === "failed");
  if (recentFail) {
    list.push({
      type: "task",
      msg: `Task failed (${recentFail.task_id})`,
    });
  }

  return list;
});
</script>

<template>
  <section class="alerts">
    <header class="head">
      <h4>Alerts</h4>
    </header>

    <div v-if="alerts.length === 0" class="ok">
      <span class="dot" />
      All systems normal
    </div>

    <ul v-else class="list">
      <li v-for="(a, i) in alerts" :key="i" class="item">
        <span class="badge">!</span>
        <span class="text">{{ a.msg }}</span>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.alerts {
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(10, 12, 20, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.10);
  backdrop-filter: blur(10px);
}

.head h4 {
  margin: 0 0 10px;
  font-size: 14px;
}

.ok {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.65);
  font-size: 13px;
}

.ok .dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: rgba(0, 220, 180, 0.9);
  box-shadow: 0 0 0 5px rgba(0, 220, 180, 0.12);
}

.list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  font-size: 13px;
}

.badge {
  display: inline-flex;
  width: 18px;
  height: 18px;
  border-radius: 6px;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  color: #fff;
  background: rgba(255, 80, 80, 0.9);
}

.text {
  color: rgba(255, 255, 255, 0.85);
}
</style>
