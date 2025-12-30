<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { getEvents } from "@/api/agv";

const lastUpdatedAt = ref(null);

const lastUpdatedText = computed(() => {
  if (!lastUpdatedAt.value) return "—";
  return new Date(lastUpdatedAt.value).toLocaleTimeString();
});

const events = ref([]);
const qTask = ref("");
const qType = ref("");
const errorOnly = ref(false);

/**
 * 그룹 열림 상태
 * - groupOpen: task 그룹 (key = task_id or "NO_TASK")
 * - itemOpen : 그룹 안의 개별 이벤트 raw 토글 (key = `${groupKey}:${idx}`)
 */
const groupOpen = ref(new Set());
const itemOpen = ref(new Set());

// Copy feedback
const copiedKey = ref(null);
let copiedTimer = null;


function tsToText(ts) {
  if (!ts) return "—";
  return new Date(ts).toLocaleString();
}

async function copyJSON(obj, key) {
  const text = JSON.stringify(obj, null, 2);

  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
    } else {
      const ta = document.createElement("textarea");
      ta.value = text;
      ta.style.position = "fixed";
      ta.style.left = "-9999px";
      document.body.appendChild(ta);
      ta.focus();
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
    }

    copiedKey.value = key;
    if (copiedTimer) clearTimeout(copiedTimer);
    copiedTimer = setTimeout(() => {
      copiedKey.value = null;
    }, 1200);
  } catch (e) {
    console.error("Copy failed", e);
  }
}

const filtered = computed(() => {
  return (events.value || []).filter((e) => {
    if (qTask.value && !(e.task_id || "").toLowerCase().includes(qTask.value.toLowerCase()))
      return false;
    if (qType.value && e.type !== qType.value) return false;
    if (errorOnly.value && !e.error_code) return false;
    return true;
  });
});

/**
 * 그룹핑: task_id 기준
 * - task_id 없는 건 "NO_TASK"로 묶기
 * - 최신 이벤트가 위로 오도록 ts desc 정렬 (이미 서버가 그럴 수도 있지만 안전하게)
 */
const grouped = computed(() => {
  const list = [...(filtered.value || [])].sort((a, b) => (b.ts || 0) - (a.ts || 0));
  const map = new Map();

  for (const e of list) {
    const key = e.task_id || "NO_TASK";
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(e);
  }

  // 그룹을 “최근 이벤트 가진 그룹이 위로”
  const groups = Array.from(map.entries()).map(([taskId, items]) => {
    const latestTs = items[0]?.ts || 0;
    const errCount = items.reduce((acc, it) => acc + (it.error_code ? 1 : 0), 0);
    return { taskId, items, latestTs, errCount };
  });

  groups.sort((a, b) => b.latestTs - a.latestTs);
  return groups;
});

function toggleGroup(key) {
  const s = new Set(groupOpen.value);
  if (s.has(key)) s.delete(key);
  else s.add(key);
  groupOpen.value = s;
}

function toggleItem(key) {
  const s = new Set(itemOpen.value);
  if (s.has(key)) s.delete(key);
  else s.add(key);
  itemOpen.value = s;
}

async function refresh() {
  events.value = (await getEvents({ limit: 500 })) || [];
  lastUpdatedAt.value = Date.now();
}

let timer = null;
onMounted(async () => {
  await refresh();
  // timer = setInterval(refresh, 2000);
});
onBeforeUnmount(() => {
  // timer && clearInterval(timer);
  copiedTimer && clearTimeout(copiedTimer);
});
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

        <div class="rightTools">
          <button class="refreshBtn" @click="refresh">↻ Refresh</button>
          <div class="updated">Updated: {{ lastUpdatedText }}</div>
        </div>
      </div>
    </div>

    <section class="card">
      <header class="cardHead">
        <h3>Grouped by Task</h3>
        <span class="meta">{{ filtered.length }} events · {{ grouped.length }} groups</span>
      </header>

      <div class="list">
        <!-- 그룹 -->
        <div
          v-for="g in grouped"
          :key="g.taskId"
          class="group"
          :class="{ open: groupOpen.has(g.taskId) }"
        >
          <button class="groupHead" @click="toggleGroup(g.taskId)">
            <div class="ghLeft">
              <span class="chev">{{ groupOpen.has(g.taskId) ? "▾" : "▸" }}</span>
              <span class="mono tid">{{ g.taskId === "NO_TASK" ? "(no task_id)" : g.taskId }}</span>
              <span class="pill mini">{{ g.items.length }} events</span>
              <span v-if="g.errCount" class="errTag">ERR {{ g.errCount }}</span>
            </div>
            <div class="ghRight">
              <span class="ts">{{ tsToText(g.latestTs) }}</span>
            </div>
          </button>

          <!-- 그룹 내용 -->
          <div v-if="groupOpen.has(g.taskId)" class="groupBody">
            <div
              v-for="(e, idx) in g.items"
              :key="(e.ts || idx) + '_' + idx"
              class="item"
              :class="{ err: !!e.error_code }"
            >
              <div class="top" @click="toggleItem(`${g.taskId}:${idx}`)">
                <div class="left">
                  <span class="ts">{{ tsToText(e.ts) }}</span>
                  <span class="pill">{{ e.type }}</span>
                  <span class="pill" :data-s="e.state || 'unknown'">{{ e.state || "—" }}</span>
                  <span class="dim">{{ e.area || "-" }}</span>
                </div>

                <div class="right" @click.stop>
                  <span v-if="e.error_code" class="errTagOne">ERR {{ e.error_code }}</span>
                  <button
                    class="btn"
                    @click.stop="copyJSON(e, `${g.taskId}:${idx}`)"
                  >
                    <span v-if="copiedKey === `${g.taskId}:${idx}`" class="copied">
                      Copied!
                    </span>
                    <span v-else>Copy</span>
                  </button>
                  <span class="chev mini">{{ itemOpen.has(`${g.taskId}:${idx}`) ? "▾" : "▸" }}</span>
                </div>
              </div>

              <pre v-if="itemOpen.has(`${g.taskId}:${idx}`)" class="raw">{{
                JSON.stringify(e, null, 2)
              }}</pre>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.eventsPage {
  height: calc(100vh - 88px);
  overflow: hidden;

  display: grid;
  grid-template-rows: auto 1fr;
  gap: 14px;
  min-height: 0;
}

.head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 16px;
}

h2 {
  margin: 0;
  font-size: 22px;
  letter-spacing: -0.2px;
}
.sub {
  margin: 6px 0 0;
  color: rgba(255, 255, 255, 0.55);
  font-size: 13px;
}

.filters {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  padding: 12px 14px;
  border-radius: 18px;
  background: rgba(10, 12, 20, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.10);
  backdrop-filter: blur(10px);
}

.inp {
  min-width: 220px;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  background: rgba(0, 0, 0, 0.25);
  color: rgba(255, 255, 255, 0.9);
  outline: none;
}

.chk {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.75);
  font-size: 12px;
  user-select: none;
}

/* 카드 */
.card {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 0;

  border-radius: 18px;
  background: rgba(10, 12, 20, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.10);
  backdrop-filter: blur(10px);
}

.cardHead {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.cardHead h3 {
  margin: 0;
  font-size: 14px;
}
.meta {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.55);
}

/* 리스트 스크롤 */
.list{
  flex: 1;
  overflow: auto;
  min-height: 0;

  padding: 6px 14px 6px 6px; /* ✅ 오른쪽 padding을 더 줘서 스크롤바가 안 잘림 */
  scrollbar-gutter: stable;  /* ✅ 스크롤바 공간을 항상 예약(지원 브라우저에서) */
}

/* 그룹 */
.group {
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.18);
  margin-bottom: 10px;
}

.groupHead {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  cursor: pointer;

  border: 0;
  background: rgba(255, 255, 255, 0.02);
  color: inherit;
}
.groupHead:hover {
  background: rgba(255, 255, 255, 0.04);
}

.ghLeft {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}
.ghRight {
  display: flex;
  align-items: center;
  gap: 10px;
}

.chev {
  color: rgba(255, 255, 255, 0.55);
}
.chev.mini {
  font-size: 12px;
}

.tid {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 520px;
}

.groupBody{
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;

  max-height: 420px;   /* ✅ 여기 값만 취향으로 조절 (320~520 추천) */
  overflow: auto;      /* ✅ 그룹 내부 스크롤 */
  min-height: 0;
}

/* 아이템 */
.item {
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(0, 0, 0, 0.20);
}
.item.err {
  border-color: rgba(255, 90, 90, 0.25);
  background: rgba(255, 90, 90, 0.06);
}

.top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.left {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.ts {
  color: rgba(255, 255, 255, 0.55);
  font-size: 12px;
}
.dim {
  color: rgba(255, 255, 255, 0.55);
  font-size: 12px;
}

.raw {
  margin: 10px 0 0;
  padding: 12px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(0, 0, 0, 0.25);
  color: rgba(255, 255, 255, 0.85);
  font-size: 12px;
  overflow: auto;
}

/* pill */
.pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 12px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  background: rgba(0, 0, 0, 0.20);
}
.pill.mini {
  font-size: 11px;
  padding: 3px 7px;
}
.pill[data-s="running"] {
  color: rgba(0, 220, 180, 0.95);
}
.pill[data-s="idle"] {
  color: rgba(255, 255, 255, 0.85);
}
.pill[data-s="done"] {
  color: rgba(255, 255, 255, 0.85);
}
.pill[data-s="failed"],
.pill[data-s="error"] {
  color: rgba(255, 90, 90, 0.95);
}

.errTag {
  color: rgba(255, 90, 90, 0.95);
  font-weight: 900;
  font-size: 12px;
}
.errTagOne {
  color: rgba(255, 90, 90, 0.95);
  font-weight: 800;
  font-size: 12px;
}

.btn {
  padding: 6px 10px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  background: rgba(0, 0, 0, 0.25);
  color: rgba(255, 255, 255, 0.85);
  cursor: pointer;
}
.btn:hover {
  background: rgba(255, 255, 255, 0.06);
}

.mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 12px;
}

.copied {
  color: rgba(0, 220, 180, 0.95);
  font-weight: 900;
  letter-spacing: 0.2px;
}

.rightTools{
  margin-left:auto;           /* ✅ 오른쪽 끝으로 밀기 */
  display:flex;
  align-items:center;
  gap:10px;
}

.refreshBtn{
  border:1px solid rgba(255,255,255,0.15);
  background: rgba(0,0,0,0.25);
  color:#fff;
  padding:8px 12px;
  border-radius:12px;
  cursor:pointer;
  font-size:12px;
}
.refreshBtn:hover{ background: rgba(255,255,255,0.06); }

.updated{
  font-size:12px;
  opacity:0.65;
  white-space:nowrap;
}

@media (max-width: 1100px) {
  .head {
    flex-direction: column;
    align-items: flex-start;
  }
  .filters {
    width: 100%;
  }
  .inp {
    min-width: 160px;
    flex: 1;
  }
  .tid {
    max-width: 260px;
  }
}


</style>
