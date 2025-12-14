<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { getEvents } from "@/api/agv";

const events = ref([]);
const qTask = ref("");
const qType = ref("");
const errorOnly = ref(false);

const opened = ref(new Set());

function tsToText(ts) {
  if (!ts) return "—";
  return new Date(ts).toLocaleString();
}

const filtered = computed(() => {
  return (events.value || []).filter(e => {
    if (qTask.value && !(e.task_id || "").toLowerCase().includes(qTask.value.toLowerCase())) return false;
    if (qType.value && e.type !== qType.value) return false;
    if (errorOnly.value && !e.error_code) return false;
    return true;
  });
});

function toggleOpen(key) {
  const s = new Set(opened.value);
  if (s.has(key)) s.delete(key);
  else s.add(key);
  opened.value = s;
}

async function refresh() {
  events.value = (await getEvents({ limit: 300 })) || [];
}

let timer = null;
onMounted(async () => {
  await refresh();
  timer = setInterval(refresh, 2000);
});
onBeforeUnmount(() => timer && clearInterval(timer));
</script>

<template>
  <div class="eventsPage">
    <div class="head">
      <div>
        <h2>Events</h2>
        <p class="sub">Append-only timeline for debugging & reporting</p>
      </div>

      <div class="filters">
        <input class="inp" v-model="qTask" placeholder="Search task_id..." />
        <input class="inp" v-model="qType" placeholder="Filter type (exact)..." />
        <label class="chk">
          <input type="checkbox" v-model="errorOnly" />
          errors only
        </label>
      </div>
    </div>

    <section class="card">
      <header class="cardHead">
        <h3>Recent Events</h3>
        <span class="meta">{{ filtered.length }} items</span>
      </header>

      <div class="list">
        <div
          v-for="(e, idx) in filtered"
          :key="(e.ts || idx) + '_' + idx"
          class="item"
          :class="{ err: !!e.error_code }"
          @click="toggleOpen(idx)"
        >
          <div class="top">
            <div class="left">
              <span class="ts">{{ tsToText(e.ts) }}</span>
              <span class="pill">{{ e.type }}</span>
              <span class="pill" :data-s="e.state || 'unknown'">{{ e.state || "—" }}</span>
              <span class="dim">{{ e.area || "-" }}</span>
              <span v-if="e.task_id" class="mono">{{ e.task_id }}</span>
            </div>

            <div class="right">
              <span v-if="e.error_code" class="errTag">ERR {{ e.error_code }}</span>
              <span class="chev">{{ opened.has(idx) ? "▾" : "▸" }}</span>
            </div>
          </div>

          <pre v-if="opened.has(idx)" class="raw">{{ JSON.stringify(e, null, 2) }}</pre>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.eventsPage{
  height: calc(100vh - 88px);
  overflow: hidden;

  display: grid;
  grid-template-rows: auto 1fr; /* head / card */
  gap: 14px;
  min-height: 0;
}


.head{
  display:flex;
  justify-content:space-between;
  align-items:flex-end;
  gap: 16px;
}

h2{ margin:0; font-size: 22px; letter-spacing:-0.2px; }
.sub{ margin:6px 0 0; color: rgba(255,255,255,0.55); font-size: 13px; }

.filters{
  display:flex;
  gap: 10px;
  flex-wrap: wrap;
  padding: 12px 14px;
  border-radius: 18px;
  background: rgba(10,12,20,0.55);
  border: 1px solid rgba(255,255,255,0.10);
  backdrop-filter: blur(10px);
}

.inp{
  min-width: 220px;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(0,0,0,0.25);
  color: rgba(255,255,255,0.9);
  outline: none;
}

.chk{
  display:flex;
  align-items:center;
  gap: 8px;
  color: rgba(255,255,255,0.75);
  font-size: 12px;
  user-select:none;
}

/* 카드가 화면 안에서 고정 */
.card{
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.cardHead{
  display:flex;
  justify-content:space-between;
  align-items:center;
  padding: 12px 14px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.cardHead h3{ margin:0; font-size: 14px; }
.meta{ font-size: 12px; color: rgba(255,255,255,0.55); }

/* header는 고정, 리스트만 스크롤 */
.list{
  flex: 1;
  overflow: auto;
  min-height: 0;
}

.item{
  padding: 12px 14px;
  border-top: 1px solid rgba(255,255,255,0.06);
  cursor: pointer;
}
.item:hover{ background: rgba(255,255,255,0.03); }
.item.err{ background: rgba(255,90,90,0.05); }

.top{
  display:flex;
  justify-content:space-between;
  align-items:center;
  gap: 10px;
}

.left{
  display:flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items:center;
}

.ts{ color: rgba(255,255,255,0.55); font-size: 12px; }
.dim{ color: rgba(255,255,255,0.55); font-size: 12px; }

.right{ display:flex; align-items:center; gap: 10px; }
.errTag{ color: rgba(255,90,90,0.95); font-weight: 800; font-size: 12px; }
.chev{ color: rgba(255,255,255,0.55); }

.raw{
  margin: 10px 0 0;
  padding: 12px;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(0,0,0,0.25);
  color: rgba(255,255,255,0.85);
  font-size: 12px;
  overflow:auto;
}

.pill{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 12px;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(0,0,0,0.20);
}
.pill[data-s="running"]{ color: rgba(0,220,180,0.95); }
.pill[data-s="idle"]{ color: rgba(255,255,255,0.85); }
.pill[data-s="done"]{ color: rgba(255,255,255,0.85); }
.pill[data-s="failed"], .pill[data-s="error"]{ color: rgba(255,90,90,0.95); }

.mono{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 12px; }

@media (max-width: 1100px){
  .head{ flex-direction: column; align-items:flex-start; }
  .filters{ width: 100%; }
  .inp{ min-width: 160px; flex: 1; }
}
</style>
