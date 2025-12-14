<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { getTasks, getEvents } from "@/api/agv";

const tasks = ref([]);
const events = ref([]);

const selected = ref(null);

// filters
const fStatus = ref("");     // "", pending, running, done, failed
const fType = ref("");       // "", deliver_water, collect_cup, collect_laundry
const fArea = ref("");       // "", USER1, USER2, DOCK, BASE
const q = ref("");           // task_id 검색

function tsToText(ts) {
  if (!ts) return "—";
  const d = new Date(ts);
  return d.toLocaleString();
}

function durationText(t) {
  const s = t.started_at;
  const e = t.finished_at;
  if (!s || !e || e < s) return "—";
  const sec = Math.round((e - s) / 1000);
  if (sec < 60) return `${sec}s`;
  return `${Math.round(sec / 60)}m`;
}

const filtered = computed(() => {
  const list = tasks.value || [];
  return list.filter(t => {
    if (fStatus.value && t.status !== fStatus.value) return false;
    if (fType.value && t.type !== fType.value) return false;
    if (fArea.value && t.target_area !== fArea.value) return false;
    if (q.value && !(t.task_id || "").toLowerCase().includes(q.value.toLowerCase())) return false;
    return true;
  });
});

const selectedEvents = computed(() => {
  if (!selected.value?.task_id) return [];
  const tid = selected.value.task_id;
  return (events.value || []).filter(e => e.task_id === tid).slice(0, 20);
});

// KPI (today)
const kpi = computed(() => {
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  const start = now.getTime();

  const today = (tasks.value || []).filter(t => (t.created_at || 0) >= start);
  const done = today.filter(t => t.status === "done");
  const failed = today.filter(t => t.status === "failed");

  const totalDoneOrFail = done.length + failed.length;
  const successRate = totalDoneOrFail === 0 ? "—" : `${Math.round((done.length / totalDoneOrFail) * 100)}%`;

  const finished = done.filter(t => t.started_at && t.finished_at && t.finished_at >= t.started_at);
  const avgMs = finished.length
    ? finished.reduce((sum, t) => sum + (t.finished_at - t.started_at), 0) / finished.length
    : null;

  const avg = avgMs == null ? "—" : (avgMs < 60000 ? `${Math.round(avgMs/1000)}s` : `${Math.round(avgMs/60000)}m`);

  return {
    todayCount: today.length,
    successRate,
    avgDuration: avg,
    failures: failed.length
  };
});

async function refresh() {
  tasks.value = (await getTasks({ limit: 300 })) || [];
  // Events는 디테일용이니 최근만
  events.value = (await getEvents({ limit: 200 })) || [];

  // 선택된 task가 목록에서 사라졌으면 닫기
  if (selected.value?.task_id) {
    const still = tasks.value.find(t => t.task_id === selected.value.task_id);
    if (!still) selected.value = null;
    else selected.value = still; // 최신 값으로 갱신
  }
}

let timer = null;
onMounted(async () => {
  await refresh();
  timer = setInterval(refresh, 2000);
});
onBeforeUnmount(() => timer && clearInterval(timer));

function selectTask(t) {
  selected.value = t;
}
function closeDetail() {
  selected.value = null;
}
</script>

<template>
  <div class="tasks">
    <!-- Header -->
    <div class="head">
      <div>
        <h2>Tasks</h2>
        <p class="sub">Operations dashboard for job tickets</p>
      </div>
      <div class="kpi">
        <div class="k">
          <div class="v">{{ kpi.todayCount }}</div>
          <div class="l">Today</div>
        </div>
        <div class="k">
          <div class="v">{{ kpi.successRate }}</div>
          <div class="l">Success</div>
        </div>
        <div class="k">
          <div class="v">{{ kpi.avgDuration }}</div>
          <div class="l">Avg</div>
        </div>
        <div class="k danger">
          <div class="v">{{ kpi.failures }}</div>
          <div class="l">Failures</div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters">
      <input class="search" v-model="q" placeholder="Search task_id..." />

      <select v-model="fStatus" class="sel">
        <option value="">All status</option>
        <option value="pending">pending</option>
        <option value="running">running</option>
        <option value="done">done</option>
        <option value="failed">failed</option>
      </select>

      <select v-model="fType" class="sel">
        <option value="">All type</option>
        <option value="deliver_water">deliver_water</option>
        <option value="collect_cup">collect_cup</option>
        <option value="collect_laundry">collect_laundry</option>
      </select>

      <select v-model="fArea" class="sel">
        <option value="">All area</option>
        <option value="BASE">BASE</option>
        <option value="DOCK">DOCK</option>
        <option value="USER1">USER1</option>
        <option value="USER2">USER2</option>
      </select>
    </div>

    <!-- Body: Table + Detail -->
    <div class="body">
      <section class="tableCard">
        <header class="cardHead">
          <h3>Task List</h3>
          <span class="meta">{{ filtered.length }} items</span>
        </header>

        <div class="tableWrap">
          <table class="tbl">
            <thead>
              <tr>
                <th>Status</th>
                <th>Type</th>
                <th>Target</th>
                <th>Duration</th>
                <th>Created</th>
                <th class="mono">Task ID</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="t in filtered"
                :key="t.task_id"
                class="row"
                :class="{ active: selected?.task_id === t.task_id }"
                @click="selectTask(t)"
              >
                <td>
                  <span class="pill" :data-s="t.status">{{ t.status }}</span>
                </td>
                <td>{{ t.type }}</td>
                <td>{{ t.target_area }}</td>
                <td>{{ durationText(t) }}</td>
                <td>{{ tsToText(t.created_at) }}</td>
                <td class="mono">{{ t.task_id }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <aside class="detailCard" :class="{ open: !!selected }">
        <header class="cardHead detailHead">
          <h3>Task Detail</h3>
          <button class="x" @click="closeDetail">×</button>
        </header>

        <div v-if="!selected" class="empty">
          Select a task to inspect details.
        </div>

        <div v-else class="detail">
          <div class="grid">
            <div class="kv"><div class="k">Status</div><div class="v"><span class="pill" :data-s="selected.status">{{ selected.status }}</span></div></div>
            <div class="kv"><div class="k">Type</div><div class="v">{{ selected.type }}</div></div>
            <div class="kv"><div class="k">Target</div><div class="v">{{ selected.target_area }}</div></div>
            <div class="kv"><div class="k">Robot</div><div class="v">{{ selected.assigned_robot || "—" }}</div></div>
            <div class="kv"><div class="k">Created</div><div class="v">{{ tsToText(selected.created_at) }}</div></div>
            <div class="kv"><div class="k">Started</div><div class="v">{{ tsToText(selected.started_at) }}</div></div>
            <div class="kv"><div class="k">Finished</div><div class="v">{{ tsToText(selected.finished_at) }}</div></div>
            <div class="kv"><div class="k">Duration</div><div class="v">{{ durationText(selected) }}</div></div>
            <div class="kv"><div class="k">Error</div><div class="v">{{ selected.error_code || "—" }}</div></div>
            <div class="kv wide"><div class="k">Task ID</div><div class="v mono">{{ selected.task_id }}</div></div>
          </div>

          <div class="divider" />

          <div class="evHead">
            <h4>Related Events</h4>
            <span class="meta">{{ selectedEvents.length }} shown</span>
          </div>

          <div class="evList">
            <div v-for="(e, i) in selectedEvents" :key="i" class="ev">
              <div class="ts">{{ tsToText(e.ts) }}</div>
              <div class="msg">
                <span class="pill mini" :data-s="e.state || 'unknown'">{{ e.type }}</span>
                <span class="mono">{{ e.task_id }}</span>
                <span class="dim">{{ e.area || "-" }}</span>
                <span v-if="e.error_code" class="err">ERR {{ e.error_code }}</span>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<style scoped>
/* 페이지 자체는 화면 높이를 넘지 않게 */
.tasks{
  height: calc(100vh - 88px);
  overflow: hidden;

  display: grid;
  grid-template-rows: auto auto 1fr; /* head / filters / body */
  gap: 14px;
}

.head{
  display:flex;
  justify-content:space-between;
  align-items:flex-end;
  gap: 16px;
}

h2{ margin:0; font-size: 22px; letter-spacing:-0.2px; }
.sub{ margin:6px 0 0; color: rgba(255,255,255,0.55); font-size: 13px; }

.kpi{
  display:grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  padding: 12px 14px;
  border-radius: 18px;
  background: rgba(10,12,20,0.55);
  border: 1px solid rgba(255,255,255,0.10);
  backdrop-filter: blur(10px);
  min-width: 420px;
}
.k{ display:flex; flex-direction:column; gap: 2px; }
.v{ font-size: 22px; font-weight: 800; }
.l{ font-size: 12px; color: rgba(255,255,255,0.55); }
.k.danger .v{ color: rgba(255,90,90,0.95); }

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

.search{
  flex: 1;
  min-width: 220px;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(0,0,0,0.25);
  color: rgba(255,255,255,0.9);
  outline: none;
}
.sel{
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(0,0,0,0.25);
  color: rgba(255,255,255,0.9);
  outline:none;
}

/* body가 화면 안에서만 레이아웃 잡게 */
.body{
  display: grid;
  grid-template-columns: 1.6fr 1fr;
  gap: 14px;
  align-items: stretch;

  min-height: 0;   /* 중요: 자식 overflow가 제대로 먹게 */
  overflow: hidden;
}

.tableCard{
  border-radius: 18px;
  background: rgba(10,12,20,0.55);
  border: 1px solid rgba(255,255,255,0.10);
  backdrop-filter: blur(10px);
  overflow: hidden;

  display: flex;
  flex-direction: column;
  min-height: 0; /* 중요 */
}

/* 오른쪽 디테일 카드 내부에서만 스크롤 가능하게 */
.detailCard{
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 0; /* 중요 */
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

.tableWrap{
  flex: 1;
  overflow: auto;
  min-height: 0;
  max-height: unset; /* 560px 고정 제거 */
}

.tbl{
  width:100%;
  border-collapse: collapse;
  font-size: 13px;
}
.tbl th{
  position: sticky;
  top: 0;
  text-align:left;
  padding: 10px 12px;
  background: rgba(6,8,16,0.85);
  color: rgba(255,255,255,0.6);
  font-weight: 600;
}
.tbl td{
  padding: 10px 12px;
  border-top: 1px solid rgba(255,255,255,0.06);
  color: rgba(255,255,255,0.85);
}
.row{ cursor: pointer; }
.row:hover td{ background: rgba(255,255,255,0.03); }
.row.active td{ background: rgba(120,130,255,0.10); }

.detailHead{ gap: 10px; }
.x{
  width: 30px; height: 30px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(0,0,0,0.25);
  color: rgba(255,255,255,0.8);
  cursor: pointer;
}
.empty{
  padding: 16px 14px;
  color: rgba(255,255,255,0.55);
  font-size: 13px;
}
/* detail 내용이 남는 공간을 먹고, 그 안에서 스크롤 */
.detail{
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.grid{
  display:grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px 12px;
}
.kv .k{ font-size: 12px; color: rgba(255,255,255,0.55); }
.kv .v{ font-size: 13px; font-weight: 600; }
.kv.wide{ grid-column: 1 / -1; }

.divider{
  height: 1px;
  background: rgba(255,255,255,0.08);
  margin: 12px 0;
}

.evHead{
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-bottom: 8px;
}
.evHead h4{ margin:0; font-size: 13px; }

/* Related Events 리스트만 스크롤 */
.evList{
  flex: 1;
  overflow: auto;
  padding-right: 6px; /* 스크롤바 공간 살짝 */
}
.ev{
  padding: 10px 10px;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(0,0,0,0.20);
}
.ts{ font-size: 12px; color: rgba(255,255,255,0.55); margin-bottom: 6px; }
.msg{ display:flex; flex-wrap:wrap; gap: 8px; align-items:center; font-size: 12px; }
.dim{ color: rgba(255,255,255,0.55); }
.err{ color: rgba(255,90,90,0.95); font-weight: 700; }

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
.pill.mini{ font-size: 11px; padding: 3px 7px; }
.pill[data-s="running"]{ color: rgba(0,220,180,0.95); }
.pill[data-s="done"]{ color: rgba(255,255,255,0.85); }
.pill[data-s="failed"]{ color: rgba(255,90,90,0.95); }
.pill[data-s="pending"]{ color: rgba(255,200,80,0.95); }

.mono{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }

@media (max-width: 1100px){
  .head{ flex-direction: column; align-items: flex-start; }
  .kpi{ min-width: unset; width: 100%; grid-template-columns: repeat(2, 1fr); }
  .body{ grid-template-columns: 1fr; }
  .detailCard{ min-height: unset; }
}
</style>
