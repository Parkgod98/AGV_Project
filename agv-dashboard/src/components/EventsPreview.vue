<script setup>
const props = defineProps({
  events: { type: Array, default: () => [] },
});

function format(ts) {
  const d = new Date(ts);
  return d.toLocaleTimeString();
}
</script>

<template>
  <section class="events">
    <header class="head">
      <h4>Recent Events</h4>
      <RouterLink to="/events" class="more">View all</RouterLink>
    </header>

    <ul class="list">
      <li v-for="e in events.slice(0, 8)" :key="e.ts" class="row">
        <span class="time">{{ format(e.ts) }}</span>
        <span class="msg">
          {{ e.type }} · {{ e.state }} · {{ e.area || "-" }}
        </span>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.events {
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(10, 12, 20, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.10);
  backdrop-filter: blur(10px);
}

.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.head h4 {
  margin: 0;
  font-size: 14px;
}

.more {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.55);
  text-decoration: none;
}

.more:hover {
  color: rgba(255, 255, 255, 0.9);
}

.list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.row {
  display: grid;
  grid-template-columns: 64px 1fr;
  gap: 10px;
  padding: 6px 0;
  font-size: 12px;
}

.time {
  color: rgba(255, 255, 255, 0.45);
}

.msg {
  color: rgba(255, 255, 255, 0.8);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
