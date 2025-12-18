<script setup>
import { computed, onMounted, ref } from "vue";

// ---- state ----
const robots = ref([]);
const tasks = ref([]);
const events = ref([]);
const loading = ref(true);
const err = ref("");

// ---- fetch helpers ----
async function fetchJSON(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${url} ${r.status}`);
  return r.json();
}

async function refresh() {
  try {
    err.value = "";
    loading.value = true;
    const [r, t, e] = await Promise.all([
      fetchJSON("/api/robots"),
      fetchJSON("/api/tasks"),
      fetchJSON("/api/events"),
    ]);
    robots.value = r || [];
    tasks.value = t || [];
    events.value = e || [];
  } catch (e) {
    err.value = e?.message || String(e);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  // ✅ 자동 폴링 없음: 처음 1번만
  refresh();
});

// ---- computed ----
const agv = computed(() => robots.value.find(x => x.robot_id === "agv1") || null);

function stateText(state, error) {
  if (error) return "오류";
  if (state === "running") return "이동 중";
  if (state === "idle") return "대기 중";
  if (state === "charging") return "충전 중";
  if (state === "done") return "완료";
  return state || "알 수 없음";
}

function stateEmoji(state, error) {
  if (error) return "🔴";
  if (state === "running") return "🚚";
  if (state === "idle") return "🟢";
  if (state === "charging") return "🔌";
  if (state === "done") return "✅";
  return "⚪";
}

function areaLabel(a) {
  const map = { USER1: "사용자 구역 1", USER2: "사용자 구역 2", DOCK: "도킹", BASE: "베이스" };
  return map[a] || a || "—";
}

function taskLabel(type) {
  const map = { deliver_water: "☕ 물 배달", collect_cup: "🥤 컵 회수", collect_laundry: "🧹 환경 정리" };
  return map[type] || type || "작업";
}

// 현재 진행 task 찾기: robot.task_id 우선
const currentTask = computed(() => {
  const r = agv.value;
  if (!r) return null;
  if (r.task_id) return tasks.value.find(t => t.task_id === r.task_id) || null;
  return tasks.value.find(t => t.assigned_robot === "agv1" && (t.status === "running" || t.status === "assigned")) || null;
});

// 남은시간(초): expected_duration_ms - elapsed
const etaSec = computed(() => {
  const t = currentTask.value;
  const r = agv.value;
  if (!t || !r) return null;

  const expected = Number(t.expected_duration_ms || 0);
  const started = Number(t.started_at || t.created_at || 0);
  if (!expected || !started) return null;

  const elapsed = (t.status === "running" || r.state === "running") ? (Date.now() - started) : 0;
  const remain = Math.max(0, expected - elapsed);
  return Math.ceil(remain / 1000);
});

const recentEvents = computed(() => {
  const e = [...events.value].slice(-5).reverse();
  return e.map(x => {
    let msg = "상태 업데이트";
    if (x.state === "running") msg = "출발했어요";
    else if (x.state === "done") msg = "작업을 완료했어요";
    else if (x.state === "error") msg = "문제가 발생했어요";
    return {
      ts: x.ts,
      text: `${msg}${x.target_area ? ` (${areaLabel(x.target_area)})` : ""}`,
    };
  });
});

function fmtTime(ts) {
  if (!ts) return "";
  const d = new Date(ts);
  return d.toLocaleTimeString();
}
</script>

<template>
  <div class="wrap">
    <div class="header">
      <div class="title">AGV 사용자 앱</div>
      <button class="btn" @click="refresh">↻ 새로고침</button>
    </div>

    <div v-if="err" class="err">⚠️ {{ err }}</div>
    <div v-if="loading" class="muted">불러오는 중…</div>

    <!-- 상태 카드 -->
    <div v-if="agv" class="card">
      <div class="row">
        <div class="big">{{ stateEmoji(agv.state, agv.error_code) }} {{ stateText(agv.state, agv.error_code) }}</div>
        <div class="big">🔋 {{ agv.battery ?? "—" }}%</div>
      </div>
      <div class="muted">📌 현재 위치: {{ areaLabel(agv.area) }}</div>
      <div v-if="agv.error_code" class="errText">원인: {{ agv.error_code }}</div>
    </div>

    <!-- 진행 작업 카드 -->
    <div class="card">
      <div class="sectionTitle">진행 중 작업</div>

      <div v-if="!currentTask" class="muted">없음</div>

      <div v-else>
        <div class="taskTitle">
          {{ taskLabel(currentTask.type) }} → {{ areaLabel(currentTask.target_area) }}
        </div>
        <div v-if="etaSec != null" class="eta">
          ⏳ 예상 남은 시간: <b>{{ etaSec }}초</b>
        </div>
        <div v-else class="muted">⏳ 예상 시간 계산 중</div>
      </div>
    </div>

    <!-- 최근 알림 -->
    <div class="card">
      <div class="sectionTitle">최근 알림</div>
      <div v-if="recentEvents.length === 0" class="muted">아직 알림이 없어요.</div>
      <div v-else class="list">
        <div v-for="(e, i) in recentEvents" :key="i" class="listRow">
          <div>{{ e.text }}</div>
          <div class="time">{{ fmtTime(e.ts) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.wrap{
  max-width: 520px;
  margin: 0 auto;
  padding: 18px;
  color: #fff;
  font-family: system-ui;
}
.header{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:12px;
  margin-bottom:12px;
}
.title{ font-size:18px; font-weight:800; }
.btn{
  border:1px solid rgba(255,255,255,0.15);
  background: rgba(0,0,0,0.25);
  color:#fff;
  padding:8px 12px;
  border-radius:12px;
  cursor:pointer;
}
.card{
  border:1px solid rgba(255,255,255,0.12);
  background: rgba(0,0,0,0.22);
  border-radius:16px;
  padding:14px;
  margin-bottom:12px;
}
.row{ display:flex; justify-content:space-between; gap:12px; }
.big{ font-size:16px; font-weight:800; }
.sectionTitle{ font-weight:800; margin-bottom:8px; }
.taskTitle{ font-weight:800; }
.eta{ margin-top:8px; }
.muted{ opacity:0.7; }
.err{
  border:1px solid rgba(255,0,0,0.35);
  background: rgba(255,0,0,0.10);
  padding:10px;
  border-radius:12px;
  margin-bottom:12px;
}
.errText{ color: #ffb3b3; margin-top: 6px; }
.list{ display:flex; flex-direction:column; gap:8px; }
.listRow{ display:flex; justify-content:space-between; gap:12px; }
.time{ opacity:0.55; }
</style>
