<!-- src/views/InteractionView.vue -->
<script setup>
import { computed, onMounted, ref } from "vue";
import { getInteractions, getInteractionInsight } from "@/api/agv";

const interactions = ref([]);
const stats = ref(null);

const q = ref("");
const fType = ref("");
const fMode = ref("");
const fResult = ref("");

const insight = ref(null);
const insightLoading = ref(false);
const range = ref("week"); // day | week

function fmt(ts) {
  if (!ts) return "—";
  const d = new Date(ts);
  if (Number.isNaN(d.getTime())) return String(ts);
  return d.toLocaleString();
}

function modeIcon(m) {
  if (m === "voice") return "🎙️";
  if (m === "text") return "⌨️";
  if (m === "button") return "🧷";
  return "🧩";
}

async function load() {
  const res = await getInteractions({
    limit: 300,
    type: fType.value || undefined,
    input_mode: fMode.value || undefined,
    result: fResult.value || undefined,
    q: q.value || undefined,
  });
  interactions.value = res.interactions || [];
  stats.value = res.stats || null;
}

const filtered = computed(() => interactions.value);

const typeOptions = computed(() => {
  const s = new Set(interactions.value.map((x) => x.type).filter(Boolean));
  return ["", ...Array.from(s)];
});
const modeOptions = computed(() => {
  const s = new Set(interactions.value.map((x) => x.input_mode).filter(Boolean));
  return ["", ...Array.from(s)];
});
const resultOptions = computed(() => {
  const s = new Set(interactions.value.map((x) => x.result).filter(Boolean));
  return ["", ...Array.from(s)];
});

async function generateInsight(force = false) {
  insightLoading.value = true;
  try {
    const res = await getInteractionInsight({ range: range.value, refresh: force });
    insight.value = res;
  } finally {
    insightLoading.value = false;
  }
}

onMounted(async () => {
  await load();
  // 첫 진입에 캐시 인사이트 불러오기(있으면 빠르게 뜸)
  await generateInsight(false);
});
</script>

<template>
  <div class="page">
    <div class="head">
      <div>
        <div class="h1">Interaction</div>
        <div class="sub">사용자 입력(버튼/텍스트/보이스) 로그 + 인사이트</div>
      </div>
      <div class="actions">
        <button class="btn" @click="load">Reload</button>
      </div>
    </div>

    <div class="grid">
      <div class="card">
        <div class="cardTitle">Filters</div>
        <div class="filters">
          <input class="inp" v-model="q" placeholder="search raw_text / type / target_area ..." @keydown.enter="load" />
          <select class="inp" v-model="fType" @change="load">
            <option v-for="t in typeOptions" :key="t" :value="t">{{ t === "" ? "type: all" : t }}</option>
          </select>
          <select class="inp" v-model="fMode" @change="load">
            <option v-for="m in modeOptions" :key="m" :value="m">{{ m === "" ? "mode: all" : m }}</option>
          </select>
          <select class="inp" v-model="fResult" @change="load">
            <option v-for="r in resultOptions" :key="r" :value="r">{{ r === "" ? "result: all" : r }}</option>
          </select>
        </div>

        <div class="kpis" v-if="stats">
          <div class="kpi">
            <div class="k">Total</div>
            <div class="v">{{ stats.total }}</div>
          </div>
          <div class="kpi">
            <div class="k">Modes</div>
            <div class="v mono">{{ JSON.stringify(stats.by_mode || {}) }}</div>
          </div>
          <div class="kpi">
            <div class="k">Types</div>
            <div class="v mono">{{ JSON.stringify(stats.by_type || {}) }}</div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="cardHead">
          <div class="cardTitle">LLM Insight</div>
          <div class="row">
            <select class="inp" v-model="range">
              <option value="day">day</option>
              <option value="week">week</option>
            </select>
            <button class="btn" :disabled="insightLoading" @click="generateInsight(false)">
              {{ insightLoading ? "Loading..." : "Refresh (cache)" }}
            </button>
            <button class="btn danger" :disabled="insightLoading" @click="generateInsight(true)">
              Force
            </button>
          </div>
        </div>

        <div v-if="!insight" class="empty">No insight yet</div>
        <div v-else class="insight">
          <div class="meta">
            <span class="pill">range: {{ insight.range }}</span>
            <span class="pill soft">{{ insight.cached ? "cached" : "fresh" }}</span>
          </div>

          <div class="block" v-if="insight.insight?.summary">
            <div class="bTitle">Summary</div>
            <div class="bText">{{ insight.insight.summary }}</div>
          </div>

          <div class="block" v-if="Array.isArray(insight.insight?.insights)">
            <div class="bTitle">Insights</div>
            <ul class="ul">
              <li v-for="(x, i) in insight.insight.insights" :key="i">{{ x }}</li>
            </ul>
          </div>

          <div class="block" v-if="Array.isArray(insight.insight?.actions)">
            <div class="bTitle">Recommended actions</div>
            <ul class="ul">
              <li v-for="(x, i) in insight.insight.actions" :key="i">{{ x }}</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="card full">
        <div class="cardTitle">Logs</div>

        <!-- ✅ 내부 스크롤 컨테이너 -->
        <div class="tableWrap">
            <div class="table">
            <div class="tr head">
                <div class="cell">time</div>
                <div class="cell">mode</div>
                <div class="cell">type</div>
                <div class="cell">target</div>
                <div class="cell">result</div>
                <div class="cell">task</div>
                <div class="cell">raw</div>
            </div>

            <div class="tr" v-for="it in filtered" :key="it.interaction_id || it.ts">
                <div class="cell mono">{{ fmt(it.ts) }}</div>
                <div class="cell">{{ modeIcon(it.input_mode) }} {{ it.input_mode || "—" }}</div>
                <div class="cell mono">{{ it.type || "—" }}</div>
                <div class="cell mono">{{ it.target_area || "—" }}</div>
                <div class="cell mono">{{ it.result || "—" }}</div>

                <!-- ✅ task도 ellipsis -->
                <div class="cell mono ellipsis" :title="it.task_id || ''">{{ it.task_id || "—" }}</div>

                <!-- ✅ raw도 ellipsis -->
                <div class="cell mono ellipsis" :title="it.raw_text || ''">{{ it.raw_text || "—" }}</div>
            </div>
            </div>
        </div>
        </div>
    </div>
  </div>
</template>

<style scoped>
.page { padding: 18px; }
.head { display:flex; justify-content:space-between; align-items:flex-start; gap:14px; margin-bottom:14px; }
.h1 { font-weight: 900; font-size: 18px; letter-spacing:.2px; }
.sub { font-size: 12px; opacity:.75; margin-top:4px; }
.actions { display:flex; gap:8px; }
.grid { display:grid; grid-template-columns: 1fr 1fr; gap:12px; }
.full { grid-column: 1 / -1; }

.card {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 16px;
  padding: 10px;
  backdrop-filter: blur(10px);
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
.cardTitle { font-weight: 800; font-size: 14px; margin-bottom: 10px; }
.cardHead { display:flex; justify-content:space-between; align-items:center; gap:10px; margin-bottom:10px; }
.row { display:flex; gap:8px; align-items:center; flex-wrap:wrap; }

.filters { display:grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap:8px; }
.inp {
  padding: 10px 10px;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(0,0,0,0.18);
  color: inherit;
  outline: none;
}

/* ✅ 버튼 수정: 튀는 색 제거, 밝기와 테두리로만 구분 (세련된 느낌) */
.btn {
  padding: 10px 14px;
  border-radius: 12px;
  
  /* 배경은 투명하지만 테두리를 살짝 밝게 해서 버튼임을 명확히 함 */
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2); 
  color: rgba(255, 255, 255, 0.9);
  
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

/* 호버 시 배경을 살짝 밝혀서 인터랙션 피드백 */
.btn:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.4);
}
.btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* ✅ Force 버튼: 빨간색 배경 대신, 텍스트와 테두리만 은은한 붉은빛 */
.btn.danger {
  color: #ffcfcf;
  border-color: rgba(255, 100, 100, 0.35);
  background: rgba(255, 0, 0, 0.05); /* 아주 연한 붉은 틴트 */
}
.btn.danger:hover {
  background: rgba(255, 0, 0, 0.15);
  border-color: rgba(255, 100, 100, 0.6);
}

.kpis { display:grid; grid-template-columns: 1fr 1fr 1fr; gap:8px; margin-top:10px; }
.kpi { padding: 10px; border-radius: 14px; border: 1px solid rgba(255,255,255,0.10); background: rgba(0,0,0,0.10); }
.k { font-size: 11px; opacity:.75; margin-bottom:6px; }
.v { font-weight: 800; font-size: 14px; }
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono","Courier New", monospace; font-size: 12px; }

/* Logs 내부 스크롤 */
.tableWrap{
  max-height: 520px;
  overflow: auto;
  padding-right: 2px;
}
.table{
  min-width: 1100px;
  display:flex;
  flex-direction:column;
  gap:6px;
}
.tr { display:grid; grid-template-columns: 150px 90px 120px 110px 110px 260px 1fr; gap:10px; padding: 10px 12px; border-radius: 14px; border: 1px solid rgba(255,255,255,0.10); background: rgba(0,0,0,0.10); }

/* ✅ 헤더 수정: 회색 대신 '아주 짙은 어둠'을 사용하여 이질감 최소화 */
.tr.head{
  position: sticky;
  top: 0;
  z-index: 2;
  font-size: 11px;
  font-weight: 800;
  
  /* #131518은 일반적인 다크모드 배경색과 거의 흡사하여 튀지 않음 */
  background: #131518; 
  
  /* 테두리를 아주 연하게 줘서 구분선 역할만 수행 */
  border-bottom: 1px solid rgba(255,255,255,0.15);
}

.tr > .cell{
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.ellipsis { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.pill {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(255,255,255,0.06);
}
.pill.soft { opacity:.85; }

.empty { opacity:.7; font-size:12px; padding: 8px 0; }

.insight .meta { display:flex; gap:8px; margin-bottom:10px; flex-wrap:wrap; }
.block { padding: 10px 12px; border-radius: 14px; border: 1px solid rgba(255,255,255,0.10); background: rgba(0,0,0,0.10); margin-bottom: 8px; }
.bTitle { font-weight: 900; font-size: 12px; margin-bottom: 6px; opacity:.9; }
.bText { font-size: 12px; opacity:.88; line-height: 1.5; }
.ul { margin: 0; padding-left: 16px; opacity:.9; font-size: 12px; line-height: 1.55; }
</style>