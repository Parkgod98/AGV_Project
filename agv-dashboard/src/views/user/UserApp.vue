<script setup>
import { computed, onMounted, ref } from "vue";
import { getSummary, getTasks } from "@/api/agv";

// ---- 상태 ----
const loading = ref(false);
const err = ref(null);
const lastUpdatedAt = ref(null);

const robot = ref(null);      // agv1
const myTasks = ref([]);      // 사용자 요청 작업(가능하면)
const activeTask = ref(null); // 현재 진행 중 task(있으면)

// ---- Telegram user_id 가져오기(웹에서 실행 시 fallback) ----
function getTelegramUserId() {
  try {
    const tg = window?.Telegram?.WebApp;
    const uid = tg?.initDataUnsafe?.user?.id;
    if (uid) return `tg_${uid}`;
  } catch (e) {}
  return null;
}
const myUserId = ref(getTelegramUserId());

// ---- 라벨 ----
const AREA_LABEL = { BASE: "베이스", DOCK: "도킹", USER1: "사용자 구역 1", USER2: "사용자 구역 2" };
const TASK_LABEL = { deliver_water: "☕ 물 배달", collect_cup: "🥤 컵 회수", collect_laundry: "🧹 환경 정리" };

const prettyState = computed(() => {
  const r = robot.value;
  if (!r) return "연결 안 됨";
  const state = String(r.state || "").toLowerCase();

  if (r.error_code) return "오류 ❗";
  if (state === "running") return "이동 중 🚚";
  if (state === "idle") return "대기 중 ✅";
  if (state === "charging") return "충전 중 🔌";
  return state || "unknown";
});

function areaName(a) {
  return AREA_LABEL[a] || a || "—";
}

function taskName(t) {
  return TASK_LABEL[t?.type] || t?.type || "작업";
}

function formatTime(ts) {
  if (!ts) return "—";
  return new Date(ts).toLocaleTimeString("ko-KR", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

// ---- 남은시간(초) 계산 ----
const remainSec = computed(() => {
  const t = activeTask.value;
  const r = robot.value;
  if (!t || !r) return null;

  const expectedMs = Number(t.expected_duration_ms || 0);
  const startedAt = Number(t.started_at || t.created_at || 0);

  if (expectedMs <= 0 || startedAt <= 0) return null;

  const elapsed = Date.now() - startedAt;
  const remainMs = Math.max(0, expectedMs - elapsed);
  return Math.ceil(remainMs / 1000);
});

// ---- 데이터 로딩(자동 새로고침 X, 버튼 눌러서만) ----
async function refresh() {
  loading.value = true;
  err.value = null;

  try {
    const s = await getSummary();
    // summary 구조가 다를 수 있어서 방어적으로
    const r = (s?.robots?.agv1) || (s?.robots?.["agv1"]) || null;
    robot.value = r;

    // 최근 tasks는 20개만 (과금/호출 폭주 방지)
    const tasks = await getTasks({ limit: 20 });

    // 내 user_id가 있으면 그거 기준으로 필터 (없으면 전체 중 최근만 표시)
    const uid = myUserId.value;
    const mine = uid ? tasks.filter(t => t.user_id === uid) : tasks;

    myTasks.value = mine;

    // 진행 중 작업 찾기 (로봇 task_id 우선)
    let t = null;
    if (r?.task_id) t = tasks.find(x => x.task_id === r.task_id) || null;
    if (!t) t = tasks.find(x => x.assigned_robot === "agv1" && x.status === "running") || null;
    activeTask.value = t;

    lastUpdatedAt.value = Date.now();
  } catch (e) {
    err.value = String(e?.message || e);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  refresh(); // 첫 로드 1회만
});
</script>

<template>
  <div class="u">
    <!-- Header -->
    <header class="u-top">
      <div class="u-title">
        <div class="u-logo" aria-hidden="true" />
        <div>
          <div class="u-h1">AGV 서비스</div>
          <div class="u-sub">현재 상태 · 진행 중 작업 · 최근 요청</div>
        </div>
      </div>

      <button class="u-btn" @click="refresh" :disabled="loading">
        {{ loading ? "새로고침 중…" : "새로고침" }}
      </button>
    </header>

    <div class="u-meta">
      <span v-if="lastUpdatedAt" class="u-meta-chip">Updated: {{ formatTime(lastUpdatedAt) }}</span>
      <span v-if="myUserId" class="u-meta-chip">Me: {{ myUserId }}</span>
    </div>

    <!-- Error -->
    <div v-if="err" class="u-error">
      <div class="u-error-title">에러</div>
      <div class="u-error-msg">{{ err }}</div>
    </div>

    <!-- Main cards -->
    <section class="u-grid">
      <!-- Status card -->
      <div class="card">
        <div class="card-h">
          <div class="card-t">현재 상태</div>
          <div class="pill">{{ prettyState }}</div>
        </div>

        <div class="kv">
          <div class="k">배터리</div>
          <div class="v">{{ robot?.battery ?? "—" }}%</div>

          <div class="k">위치</div>
          <div class="v">{{ areaName(robot?.area) }}</div>

          <div class="k">오류</div>
          <div class="v">{{ robot?.error_code ?? "없음" }}</div>
        </div>
      </div>

      <!-- Active task -->
      <div class="card">
        <div class="card-h">
          <div class="card-t">진행 중 작업</div>
          <div class="pill" v-if="activeTask">{{ taskName(activeTask) }}</div>
          <div class="pill pill-mute" v-else>없음</div>
        </div>

        <div v-if="activeTask" class="taskbox">
          <div class="taskline">
            <span class="muted">목적지</span>
            <span class="strong">{{ areaName(activeTask.target_area) }}</span>
          </div>
          <div class="taskline">
            <span class="muted">상태</span>
            <span class="strong">{{ activeTask.status }}</span>
          </div>
          <div class="taskline" v-if="remainSec != null">
            <span class="muted">남은 시간</span>
            <span class="strong">약 {{ remainSec }}초</span>
          </div>

          <div v-if="remainSec != null" class="bar">
            <div class="bar-in" :style="{ width: remainSec === 0 ? '100%' : '65%' }"></div>
          </div>

          <div class="hint">
            * 남은 시간은 “기대시간(expected) - 경과시간”으로 계산돼요.
          </div>
        </div>

        <div v-else class="empty">
          현재 진행 중인 작업이 없어요.
        </div>
      </div>
    </section>

    <!-- Recent requests -->
    <section class="card">
      <div class="card-h">
        <div class="card-t">최근 요청</div>
        <div class="pill pill-mute">최근 {{ Math.min(myTasks.length, 10) }}개</div>
      </div>

      <div v-if="myTasks.length === 0" class="empty">
        아직 요청 기록이 없어요.
      </div>

      <div v-else class="list">
        <div v-for="t in myTasks.slice(0, 10)" :key="t.task_id" class="row">
          <div class="row-left">
            <div class="row-title">{{ taskName(t) }} · {{ areaName(t.target_area) }}</div>
            <div class="row-sub">
              {{ t.status }} · {{ formatTime(t.created_at) }}
            </div>
          </div>
          <div class="row-right">
            <span class="tag" :data-s="t.status">{{ t.status }}</span>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.u{
  max-width: 760px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.u-top{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.u-title{
  display: flex;
  align-items: center;
  gap: 12px;
}

.u-logo{
  width: 44px;
  height: 44px;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(120,130,255,.95), rgba(0,220,180,.75));
  box-shadow: 0 12px 40px rgba(0,0,0,.35);
}

.u-h1{ font-size: 18px; font-weight: 900; letter-spacing: .2px; }
.u-sub{ margin-top: 2px; font-size: 12px; opacity: .72; }

.u-btn{
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,.10);
  background: rgba(10, 12, 20, .55);
  color: rgba(255,255,255,.92);
  cursor: pointer;
}
.u-btn:disabled{ opacity: .6; cursor: not-allowed; }

.u-meta{ display: flex; gap: 8px; flex-wrap: wrap; }
.u-meta-chip{
  font-size: 12px;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,.08);
  background: rgba(8,10,16,.35);
  opacity: .85;
}

.u-error{
  border: 1px solid rgba(255,80,80,.25);
  background: rgba(255,80,80,.08);
  border-radius: 14px;
  padding: 12px;
}
.u-error-title{ font-weight: 800; margin-bottom: 4px; }
.u-error-msg{ font-size: 12px; opacity: .85; word-break: break-word; }

.u-grid{
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}
@media (min-width: 720px){
  .u-grid{ grid-template-columns: 1fr 1fr; }
}

.card{
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,.08);
  background: rgba(10, 12, 20, .55);
  backdrop-filter: blur(12px);
  padding: 14px;
  box-shadow: 0 12px 40px rgba(0,0,0,.25);
}

.card-h{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 12px;
}
.card-t{ font-weight: 900; letter-spacing: .2px; }

.pill{
  font-size: 12px;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,.10);
  background: rgba(8,10,16,.35);
}
.pill-mute{ opacity: .72; }

.kv{
  display: grid;
  grid-template-columns: 90px 1fr;
  row-gap: 8px;
  column-gap: 10px;
}
.k{ font-size: 12px; opacity: .72; }
.v{ font-weight: 800; }

.taskbox{ display: flex; flex-direction: column; gap: 8px; }
.taskline{ display: flex; align-items: center; justify-content: space-between; }
.muted{ font-size: 12px; opacity: .72; }
.strong{ font-weight: 900; }

.bar{
  height: 10px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,.10);
  background: rgba(255,255,255,.06);
  overflow: hidden;
}
.bar-in{
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(120,130,255,.95), rgba(0,220,180,.75));
}

.hint{
  font-size: 11px;
  opacity: .6;
}

.empty{
  font-size: 13px;
  opacity: .75;
  padding: 10px 0 2px;
}

.list{ display: flex; flex-direction: column; gap: 10px; }
.row{
  display: flex;
  justify-content: space-between;
  gap: 10px;
  padding: 10px 10px;
  border-radius: 14px;
  border: 1px solid rgba(255,255,255,.06);
  background: rgba(8,10,16,.25);
}
.row-title{ font-weight: 900; }
.row-sub{ font-size: 12px; opacity: .7; margin-top: 2px; }
.tag{
  font-size: 12px;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,.10);
  opacity: .9;
}
</style>
