<template>
  <div class="ua">
    <!-- Header -->
    <header class="ua-header">
      <div class="h-left">
        <div class="title">AGV</div>
        <div class="sub">{{ headerSub }}</div>
      </div>
      <div class="h-right">
        <button class="btn" @click="refreshAll" :disabled="loading">
          {{ loading ? "Loading…" : "새로고침" }}
        </button>
      </div>
    </header>

    <!-- Content -->
    <main class="ua-main" :key="tab">
      <!-- HOME -->
      <section v-if="tab==='home'" class="page">
        <div class="grid">
          <div class="card">
            <div class="card-title">로봇 상태</div>
            <div class="kvs">
              <div class="kv">
                <span>상태</span>
                <b :class="robotStateClass(robot?.state)">{{ uiRobotState(robot?.state) }}</b>
              </div>
              <div class="kv">
                <span>현재 위치</span>
                <b>{{ uiPlace(currentPlaceKey) }}</b>
              </div>
              <div class="kv">
                <span>다음 목적지</span>
                <b>{{ nextTargetLabel }}</b>
              </div>
              <div class="kv">
                <span>배터리</span>
                <b>{{ robot?.battery ?? "—" }}%</b>
              </div>
            </div>
            <div v-if="moveLine" class="muted">이동: <b>{{ moveLine }}</b></div>
          </div>

          <div class="card">
            <div class="card-title">진행 중</div>

            <div v-if="myNowTask" class="nowbox">
              <div class="now-main">
                <b>{{ labelType(myNowTask.type) }}</b>
                <span class="pill">{{ uiArea(myNowTask.target_area) }}</span>
              </div>

              <div class="progress">
                <div class="bar" :style="{ width: `${Math.min(100, myNowProgressPct)}%` }"></div>
              </div>
              <div class="muted">
                남은 시간 약 {{ myNowEtaS }}초 · {{ Math.round(myNowProgressPct) }}%
              </div>
            </div>

            <div v-else-if="robot?.state === 'running'" class="muted">
              로봇이 다른 작업을 수행 중이에요.
            </div>

            <div v-else class="muted">현재 진행 중인 작업이 없습니다.</div>
          </div>

          <div class="card">
            <div class="card-title">요약</div>
            <div class="kvs">
              <div class="kv"><span>대기 작업</span><b>{{ pendingCount }}</b></div>
              <div class="kv"><span>오늘 완료</span><b>{{ today.done }}</b></div>
              <div class="kv"><span>오늘 평균 소요</span><b>{{ today.avg_duration_s }}s</b></div>
            </div>
          </div>

          <div class="card">
            <div class="card-title">물 섭취(추정)</div>
            <div class="kvs">
              <div class="kv"><span>오늘 물 배달</span><b>{{ today.water_count }}회</b></div>
              <div class="kv"><span>오늘 섭취량</span><b>{{ today.water_ml }}ml</b></div>
              <div class="kv"><span>이번 주 누적</span><b>{{ week.water_ml }}ml</b></div>
            </div>
            <div class="muted">* 추정 = 물 배달 횟수 × {{ waterCupMl }}ml</div>

            <div v-if="settings.water_goal_ml > 0" class="muted">
              목표 {{ settings.water_goal_ml }}ml · 달성 {{ waterGoalPct }}%
            </div>
            <div v-if="settings.water_goal_ml > 0" class="progress mt2">
              <div class="bar" :style="{ width: waterGoalPct + '%' }"></div>
            </div>
          </div>

          <div class="card wide">
            <div class="card-title">작업별 평균 소요(오늘/이번 주)</div>
            <div class="chips">
              <div class="chip">
                <span>물 배달</span><b>{{ avgByType.deliver_water ?? "—" }}s</b>
              </div>
              <div class="chip">
                <span>컵 수거</span><b>{{ avgByType.collect_cup ?? "—" }}s</b>
              </div>
              <div class="chip">
                <span>환경 정리</span><b>{{ avgByType.collect_laundry ?? "—" }}s</b>
              </div>
            </div>
          </div>

          <div class="card wide">
            <div class="card-title">신뢰도</div>
            <div class="kvs">
              <div class="kv">
                <span>오늘 완료율</span>
                <b>{{ today.total ? Math.round((today.done / today.total) * 100) : 0 }}%</b>
              </div>
              <div class="kv">
                <span>최근 10건 오류</span>
                <b>{{ last10ErrorCount }}건</b>
              </div>
              <div class="kv">
                <span>최근 완료</span>
                <b>{{ lastDoneText }}</b>
              </div>
            </div>
          </div>

          <!-- ✅ Home 맨 아래 루틴 카드: Settings에서 만든 루틴 표시 -->
          <div class="card wide">
            <div class="card-title">루틴(예약)</div>

            <div class="actions" style="margin-top:0">
              <button class="btn sm" @click="tab='settings'">Settings 열기</button>
            </div>

            <div v-if="routinesPreview.length === 0" class="muted">
              아직 등록된 루틴이 없습니다. <b>Settings</b> 탭에서 추가해보세요.
            </div>

            <div v-else class="list">
              <div v-for="r in routinesPreview" :key="r.id" class="item">
                <div class="item-top">
                  <b>{{ r.time }}</b>
                  <span class="pill">{{ routineRepeatText(r) }}</span>
                </div>
                <div class="item-sub muted">
                  {{ labelType(r.action_type) }} → {{ uiPlace(routineTargetArea(r)) }}
                </div>
              </div>
            </div>

            <div v-if="settings.routines.length > routinesPreview.length" class="muted">
              + {{ settings.routines.length - routinesPreview.length }}개 더 있음 (Settings에서 확인)
            </div>

            <div class="muted">
              * 실제 자동 실행(앱 꺼져도 동작)은 다음 단계에서 Node-RED 스케줄러로 붙일게요.
            </div>
          </div>
        </div>
      </section>

      <!-- MAP -->
      <section v-else-if="tab==='map'" class="page">
        <div class="card">
          <div class="card-title">로봇 위치</div>
          <div class="muted">
            로봇이 이동하는 경로를 표시합니다.
          </div>

          <!-- ✅ 맵 -->
          <div
            ref="mapRef"
            class="map"
            @pointerdown.prevent="onMapPointerDown"
          >
            <!-- Track SVG (dense points) -->
            <svg class="track-svg" viewBox="0 0 100 100" preserveAspectRatio="none">
              <polyline
                v-if="trackDense.length >= 2"
                :points="trackSvgPoints"
                class="track-line"
              />
              <!-- calibration preview: anchors line -->
              <polyline
                v-if="calib.on && calibAnchors.length >= 2"
                :points="anchorSvgPoints"
                class="anchor-line"
              />

              <!-- anchor dots (only in calib mode) -->
              <circle
                v-for="(p, idx) in calibAnchors"
                :key="'a'+idx"
                :cx="p.x"
                :cy="p.y"
                r="0.9"
                class="anchor-dot"
              />
            </svg>

            <!-- Zones -->
            <div class="zone z-charge">충전소</div>
            <div class="zone z-water">정수기</div>
            <div class="zone z-drop">정리함</div>

            <div class="zone z-a">룸 1</div>
            <div class="zone z-b">룸 2</div>
            <div class="zone z-c">룸 3</div>

            <!-- Robot dot -->
            <div class="dot sonar" :style="{ left: `${dotPos.x}%`, top: `${dotPos.y}%` }">
              <div class="dot-inner"></div>
              <div class="dot-label">agv1</div>
            </div>
          </div>

          <!-- 캘리 패널(개발자용: 5번 연속 탭으로 진입) -->
          <div v-if="calib.on" class="calib-panel">
            <div class="calib-row">
              <b class="calib-title">Calibration Mode</b>
              <span class="calib-sub">앵커 {{ calibAnchors.length }}개</span>
            </div>

            <div class="calib-row">
              <button class="btn sm" @click="calibUndo" :disabled="calibAnchors.length===0">Undo</button>
              <button class="btn sm" @click="calibClear" :disabled="calibAnchors.length===0">Clear</button>
              <button class="btn sm primary" @click="calibSave">Save (Auto 800)</button>
              <button class="btn sm" @click="calibCopyJson" :disabled="trackDense.length<2">Copy JSON</button>
              <button class="btn sm" @click="calibExit">Exit</button>
            </div>

            <div class="muted">
              - 앵커만 10~30개 찍고 Save 누르면 800개로 자동 보간됩니다.<br/>
              - Copy JSON은 Node-RED에 TRACK_POINTS로 붙이기 위한 개발용 기능입니다.
            </div>
          </div>
        </div>

        <div class="card mt">
          <div class="card-title">상세</div>
          <div class="kvs">
            <div class="kv"><span>구역</span><b>{{ uiArea(robot?.area) }}</b></div>
            <div class="kv"><span>Pose</span><b>{{ poseText }}</b></div>
          </div>
        </div>
      </section>

      <!-- REPORT -->
      <section v-else-if="tab==='report'" class="page">
        <div class="card">
          <div class="card-title">리포트</div>
          <div class="seg">
            <button class="segbtn" :class="{ on: reportRange==='day' }" @click="setReportRange('day')">일간</button>
            <button class="segbtn" :class="{ on: reportRange==='week' }" @click="setReportRange('week')">주간</button>
          </div>

          <div class="grid mt2">
            <div class="card inner">
              <div class="card-title">요청</div>
              <div class="kvs">
                <div class="kv"><span>총</span><b>{{ R.total }}</b></div>
                <div class="kv"><span>완료</span><b>{{ R.done }}</b></div>
                <div class="kv"><span>완료율</span><b>{{ R.total ? Math.round((R.done / R.total) * 100) : 0 }}%</b></div>
              </div>
            </div>

            <div class="card inner">
              <div class="card-title">시간/물</div>
              <div class="kvs">
                <div class="kv"><span>평균 소요</span><b>{{ R.avg_duration_s }}s</b></div>
                <div class="kv"><span>물 배달</span><b>{{ R.water_count }}회</b></div>
                <div class="kv"><span>섭취량(추정)</span><b>{{ R.water_ml }}ml</b></div>
              </div>
            </div>

            <div class="card inner wide">
              <div class="card-title">브리핑</div>
              <div class="brief">{{ briefText }}</div>
              <div class="actions">
                 <button class="btn" @click="generateBrief(true)" :disabled="briefLoading">
                  {{ briefLoading ? "생성 중…" : "브리핑 갱신" }}
                 </button>
              </div>
              <div class="muted">
                * 브리핑은 /api/user/brief(LLM) 호출 → 실패 시 로컬 템플릿으로 대체합니다.
              </div>
            </div>
          </div>

          <div class="card mt">
            <div class="card-title">
              {{ reportRange==='day' ? "시간대별 요청(오늘)" : "요일별 요청(이번 주)" }}
            </div>

            <div class="chart-wrap" :class="{ week: reportRange==='week' }">
              <div class="chart" :class="{ week: reportRange==='week' }">
                <div v-for="(v, i) in chartSeries" :key="i" class="barcol">
                  <div class="barbox">
                    <div class="bar2" :style="{ height: `${barHeight(v)}%` }"></div>
                  </div>
                  <div class="xlabel">{{ chartLabel(i) }}</div>
                </div>
              </div>
            </div>

            <div v-if="chartSeries.every(v => v===0)" class="muted">
              아직 집계할 요청이 없습니다.
            </div>
          </div>
        </div>
      </section>

      <!-- HISTORY -->
      <section v-else-if="tab==='history'" class="page">
        <div class="card">
          <div class="card-title">작업 기록</div>

          <div class="hist-filters">
            <button class="fbtn" :class="{ on: histFilter==='all' }" @click="histFilter='all'">전체</button>
            <button class="fbtn" :class="{ on: histFilter==='deliver_water' }" @click="histFilter='deliver_water'">물</button>
            <button class="fbtn" :class="{ on: histFilter==='collect_cup' }" @click="histFilter='collect_cup'">컵</button>
            <button class="fbtn" :class="{ on: histFilter==='collect_laundry' }" @click="histFilter='collect_laundry'">환경정리</button>
          </div>

          <div v-if="filteredHistoryTasks.length === 0" class="muted">아직 작업 기록이 없습니다.</div>

          <div class="list">
            <div v-for="t in filteredHistoryTasks" :key="t.task_id" class="item">
              <div class="item-top">
                <b>{{ labelType(t.type) }}</b>
                <span class="pill" :class="statusClass(t.status)">{{ uiTaskStatus(t.status) }}</span>
              </div>
              <div class="item-sub">
                <span>{{ uiArea(t.target_area) }}</span>
                <span>·</span>
                <span>{{ timeText(t._created_ms || t.created_at) }}</span>
              </div>
              <div class="item-sub muted">
                소요: {{ durationS(t) }}s
                <span v-if="t.error_code"> · 오류: {{ t.error_code }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ✅ SETTINGS -->
      <section v-else="tab==='settings'" class="page">
        <div class="grid">
          <div class="card">
            <div class="card-title">Settings</div>

            <div class="kvs">
              <div class="kv">
                <span>현재 위치(수동)</span>
                <select v-model="settings.user_place" class="ctl">
                  <option v-for="k in placeKeysAll" :key="k" :value="k">{{ uiPlace(k) }}</option>
                </select>
              </div>

              <div class="kv">
                <span>수분 목표(ml/일)</span>
                <input class="ctl" type="number" min="0" step="50" v-model.number="settings.water_goal_ml" />
              </div>
            </div>

            <div class="muted">
              오늘 추정 섭취: <b>{{ today.water_ml }}ml</b>
              <span v-if="settings.water_goal_ml > 0">
                / 목표 <b>{{ settings.water_goal_ml }}ml</b> ({{ waterGoalPct }}%)
              </span>
            </div>

            <div v-if="settings.water_goal_ml > 0" class="progress mt2">
              <div class="bar" :style="{ width: waterGoalPct + '%' }"></div>
            </div>
          </div>

          <div class="card wide">
            <div class="card-title">Routines (시간 기반)</div>

            <div class="kvs">
              <div class="kv">
                <span>시간</span>
                <input class="ctl" type="time" v-model="routineDraft.time" />
              </div>

              <div class="kv">
                <span>반복</span>
                <div class="seg2">
                  <button class="fbtn" :class="{ on: routineDraft.repeat==='daily' }" @click="routineDraft.repeat='daily'">매일</button>
                  <button class="fbtn" :class="{ on: routineDraft.repeat==='weekly' }" @click="routineDraft.repeat='weekly'">매주</button>
                </div>
              </div>

              <div v-if="routineDraft.repeat==='weekly'" class="days">
                <button
                  v-for="(d, idx) in weekDayLabels"
                  :key="idx"
                  class="fbtn"
                  :class="{ on: routineDraft.days.includes(idx) }"
                  @click="toggleDraftDay(idx)"
                >{{ d }}</button>
              </div>

              <div class="kv">
                <span>액션</span>
                <select class="ctl" v-model="routineDraft.action_type">
                  <option value="deliver_water">물 배달</option>
                  <option value="collect_cup">컵 수거</option>
                  <option value="collect_laundry">환경 정리</option>
                </select>
              </div>

              <div class="kv">
                <span>목적지</span>
                <select class="ctl" v-model="routineDraft.target_mode">
                  <option value="my">내 위치(설정)</option>
                  <option value="custom">직접 선택</option>
                </select>
              </div>

              <div v-if="routineDraft.target_mode==='custom'" class="kv">
                <span>직접 선택</span>
                <select class="ctl" v-model="routineDraft.target_area">
                  <option v-for="k in placeKeysTargets" :key="k" :value="k">{{ uiPlace(k) }}</option>
                </select>
              </div>
            </div>

            <div class="actions mt2">
              <button class="btn" @click="addRoutine">루틴 추가</button>
            </div>

            <div v-if="routinesSorted.length === 0" class="muted">
              아직 루틴이 없습니다. 위에서 추가해보세요.
            </div>

            <div v-else class="list">
              <div v-for="r in routinesSorted" :key="r.id" class="item">
                <div class="item-top">
                  <div>
                    <b>{{ r.time }}</b>
                    <span class="muted" style="margin-left:8px">· {{ routineRepeatText(r) }}</span>
                  </div>
                  <div class="routine-actions">
                    <button class="fbtn" :class="{ on: r.enabled }" @click="toggleRoutine(r)">{{ r.enabled ? "ON" : "OFF" }}</button>
                    <button class="fbtn" @click="removeRoutine(r.id)">삭제</button>
                  </div>
                </div>
                <div class="item-sub muted">
                  {{ labelType(r.action_type) }} → {{ uiPlace(routineTargetArea(r)) }}
                </div>
              </div>
            </div>

            <div class="muted">
              * 자동 실행은 다음 단계에서 Node-RED 스케줄러로 구현합니다(앱이 꺼져 있어도 동작).
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- Bottom Tabs -->
    <nav class="ua-tabs">
      <button class="tab" :class="{ on: tab==='home' }" @click="tab='home'">Home</button>
      <button class="tab" :class="{ on: tab==='map' }" @click="tab='map'">Map</button>
      <button class="tab" :class="{ on: tab==='report' }" @click="tab='report'">Report</button>
      <button class="tab" :class="{ on: tab==='history' }" @click="tab='history'">History</button>
      <button class="tab" :class="{ on: tab==='settings' }" @click="tab='settings'">Settings</button>
    </nav>

    <!-- Toast -->
    <div v-if="toast" class="toast">{{ toast }}</div>
  </div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref, watch } from "vue";
import { getRobots, getTasks, getUserBrief } from "@/api/agv";
import { getAppSettings, saveAppSettings } from "@/api/agv";

/** -----------------------------
 *  UI state
 *  ----------------------------- */
function pad2(n) { return String(n).padStart(2, "0"); }

function tsFile() {
  const d = new Date();
  const y = d.getFullYear();
  const mo = pad2(d.getMonth() + 1);
  const da = pad2(d.getDate());
  const hh = pad2(d.getHours());
  const mm = pad2(d.getMinutes());
  const ss = pad2(d.getSeconds());
  return `${y}${mo}${da}_${hh}${mm}${ss}`;
}

async function saveJsonFile(obj, filename) {
  const text = JSON.stringify(obj, null, 2);

  // 1) Chrome/Edge(Chromium) 지원: 저장 위치 선택 가능
  if (window.showSaveFilePicker) {
    const handle = await window.showSaveFilePicker({
      suggestedName: filename,
      types: [
        {
          description: "JSON",
          accept: { "application/json": [".json"] },
        },
      ],
    });
    const writable = await handle.createWritable();
    await writable.write(text);
    await writable.close();
    return;
  }

  // 2) fallback: 다운로드(브라우저 기본 다운로드 폴더로)
  const blob = new Blob([text], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

const tab = ref("home");
const loading = ref(false);

const toast = ref("");
let toastTimer = null;
function showToast(t) {
  toast.value = t;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (toast.value = ""), 1800);
}

/** -----------------------------
 *  Settings (localStorage)
 *  ----------------------------- */
const SETTINGS_LS_KEY = "AGV_UA_SETTINGS_V1";

// 장소 키 (UI 표기용)
const placeKeysAll = ["HALL", "CHARGE", "WATER", "DROP", "RES_A", "RES_B", "RES_C"];
const placeKeysTargets = ["CHARGE", "WATER", "DROP", "RES_A", "RES_B", "RES_C"];

// 주간 요일(월=0 ~ 일=6)
const weekDayLabels = ["월", "화", "수", "목", "금", "토", "일"];

function loadSettings() {
  try {
    const raw = localStorage.getItem(SETTINGS_LS_KEY);
    if (!raw) return { user_place: "RES_A", water_goal_ml: 500, routines: [] };
    const obj = JSON.parse(raw);
    return {
      user_place: String(obj?.user_place || "RES_A"),
      water_goal_ml: Number(obj?.water_goal_ml || 0) || 0,
      routines: Array.isArray(obj?.routines) ? obj.routines : [],
    };
  } catch {
    return { user_place: "RES_A", water_goal_ml: 500, routines: [] };
  }
}

function saveSettings() {
  try {
    localStorage.setItem(SETTINGS_LS_KEY, JSON.stringify(settings.value));
  } catch {}
}

const settings = ref(loadSettings());
let globalSaveTimer = null;

watch(settings, () => {
  clearTimeout(globalSaveTimer);
  globalSaveTimer = setTimeout(async () => {
    try {
      await saveAppSettings({ settings: settings.value });
    } catch (e) {
      console.warn("saveAppSettings failed:", e);
    }
  }, 500);
}, { deep: true });

// 루틴 draft
const routineDraft = ref({
  time: "10:00",
  repeat: "daily",      // daily | weekly
  days: [],             // weekly일 때만 (월=0..일=6)
  action_type: "deliver_water",
  target_mode: "my",    // my | custom
  target_area: "RES_A",
});

function toggleDraftDay(idx) {
  const days = routineDraft.value.days;
  const i = days.indexOf(idx);
  if (i >= 0) days.splice(i, 1);
  else days.push(idx);
  days.sort((a, b) => a - b);
}

function normalizeTime(t) {
  const m = String(t || "").match(/^([0-2]\d):([0-5]\d)$/);
  if (!m) return "";
  const hh = Number(m[1]);
  const mm = Number(m[2]);
  if (hh > 23) return "";
  return `${pad2(hh)}:${pad2(mm)}`;
}

function addRoutine() {
  const time = normalizeTime(routineDraft.value.time);
  if (!time) {
    showToast("시간을 올바르게 설정해줘 (예: 10:00)");
    return;
  }

  const repeat = (routineDraft.value.repeat === "weekly") ? "weekly" : "daily";
  let days = [];
  if (repeat === "weekly") {
    days = Array.isArray(routineDraft.value.days) ? [...routineDraft.value.days] : [];
    if (days.length === 0) {
      const d = new Date().getDay(); // 0=일..6=토
      const mon0 = (d + 6) % 7;      // 월=0..일=6
      days = [mon0];
    }
  }

  const action_type = String(routineDraft.value.action_type || "deliver_water");
  const target_mode = (routineDraft.value.target_mode === "custom") ? "custom" : "my";
  const target_area = (target_mode === "custom")
    ? String(routineDraft.value.target_area || settings.value.user_place || "RES_A")
    : String(settings.value.user_place || "RES_A");

  const r = {
    id: `rt_${Date.now()}`,
    enabled: true,
    time,
    repeat,
    days,
    action_type,
    target_mode,
    target_area,
    created_at: Date.now(),
  };

  settings.value.routines.push(r);

  // draft 일부 초기화(시간은 유지)
  routineDraft.value.repeat = "daily";
  routineDraft.value.days = [];
  routineDraft.value.action_type = action_type;
  routineDraft.value.target_mode = "my";
  routineDraft.value.target_area = settings.value.user_place || "RES_A";

  showToast("루틴이 추가됐어요");
}

function removeRoutine(id) {
  settings.value.routines = settings.value.routines.filter(r => r.id !== id);
  showToast("삭제했어요");
}

function toggleRoutine(r) {
  r.enabled = !r.enabled;
}

function routineTargetArea(r) {
  return (r?.target_mode === "custom")
    ? (r.target_area || "RES_A")
    : (settings.value.user_place || "RES_A");
}

function routineRepeatText(r) {
  if (!r) return "";
  if (r.repeat === "weekly") {
    const days = Array.isArray(r.days) ? r.days : [];
    const names = days.map(i => weekDayLabels[i]).filter(Boolean);
    return names.length ? `매주(${names.join(",")})` : "매주";
  }
  return "매일";
}

const routinesSorted = computed(() => {
  const list = Array.isArray(settings.value.routines) ? settings.value.routines : [];
  return list.slice().sort((a, b) => String(a.time).localeCompare(String(b.time)));
});

const routinesPreview = computed(() => {
  return routinesSorted.value.filter(r => r.enabled).slice(0, 3);
});

/** -----------------------------
 *  Telegram WebApp user
 *  ----------------------------- */
const userId = ref("");     // ex) "tg_6802468707"
const userName = ref("");   // display name

function initTelegramUser() {
  const tg = window?.Telegram?.WebApp;
  const u = tg?.initDataUnsafe?.user;
  if (u?.id) {
    userId.value = `tg_${u.id}`;
    userName.value = (u.first_name || u.username || "사용자");
  } else {
    userId.value = ""; // demo mode
    userName.value = "Demo";
  }
}

async function loadGlobalSettings() {
  try {
    const res = await getAppSettings();
    if (res?.settings) {
      // 서버값이 있으면 그걸로 덮어쓰기(전역이니까)
      settings.value = { ...settings.value, ...res.settings };
    } else {
      // 서버에 아무것도 없으면(처음) 현재 로컬값을 서버에 올려서 시드
      await saveAppSettings({ settings: settings.value });
    }
  } catch (e) {
    console.warn("loadGlobalSettings failed:", e);
  }
}

/** -----------------------------
 *  Data
 *  ----------------------------- */
const robots = ref([]);
const tasks = ref([]);

const waterCupMl = 250;
const reportRange = ref("day");
const briefText = ref("");
const lastFetchAt = ref(0);

/** Telegram WebApp UX */
let prevBodyOverflow = "";
let prevHtmlOverflow = "";

/** -----------------------------
 *  Helpers: time normalize
 *  ----------------------------- */
function toMs(v) {
  if (!v) return 0;
  if (typeof v === "number") return v;
  if (typeof v === "string") {
    const n = Number(v);
    if (Number.isFinite(n)) return n;
    const d = Date.parse(v);
    return Number.isFinite(d) ? d : 0;
  }
  if (typeof v === "object") {
    if (typeof v.toMillis === "function") return v.toMillis();
    if (typeof v.seconds === "number") return v.seconds * 1000;
  }
  return 0;
}

function normalizeTask(t) {
  const x = { ...t };
  x.status = String(x.status || "").toLowerCase();
  x._created_ms = toMs(x.created_at);
  x._started_ms = toMs(x.started_at);
  x._finished_ms = toMs(x.finished_at || x.completed_at || x.ended_at);

  const actual = Number(x.actual_duration_ms || 0);
  x._actual_ms =
    Number.isFinite(actual) && actual > 0
      ? actual
      : (x._finished_ms && x._started_ms ? (x._finished_ms - x._started_ms) : 0);

  if (!x.status) {
    if (x._finished_ms) x.status = "done";
    else if (x._started_ms) x.status = "running";
    else x.status = "pending";
  }
  return x;
}

function durationS(t) {
  const ms = Number(t?._actual_ms || 0);
  if (ms > 0) return Math.round(ms / 1000);
  const exp = Number(t?.expected_duration_ms || 0);
  return exp ? Math.round(exp / 1000) : 0;
}

/** -----------------------------
 *  UI label mapping (user-friendly)
 *  ----------------------------- */
function labelType(type) {
  if (type === "deliver_water") return "물 배달";
  if (type === "collect_cup") return "컵 수거";
  if (type === "collect_laundry") return "환경 정리";
  return type || "기타";
}

function uiTaskStatus(st) {
  st = String(st || "").toLowerCase();
  if (st === "done") return "완료";
  if (st === "running") return "진행 중";
  if (st === "failed" || st === "error") return "오류";
  return "대기";
}

function uiRobotState(st) {
  st = String(st || "").toLowerCase();
  if (st === "running") return "작업 중";
  if (st === "idle") return "대기 중";
  if (st === "done") return "작업 종료";
  return st ? st : "—";
}

function uiArea(area) {
  const a = String(area || "").toUpperCase();
  const map = {
    CHARGE: "충전소",
    WATER: "정수기",
    DROP: "정리함(반납)",
    RES_A: "방 1",
    RES_B: "방 2",
    RES_C: "방 3",
  };
  return map[a] || (a || "—");
}

function uiPlace(key) {
  if (!key) return "—";
  if (key === "HALL") return "복도";
  return uiArea(key);
}

function statusClass(st) {
  st = String(st || "").toLowerCase();
  if (st === "running") return "st-running";
  if (st === "done") return "st-done";
  if (st === "pending" || st === "queued") return "st-pending";
  if (st === "failed" || st === "error") return "st-error";
  return "st-etc";
}
function robotStateClass(st) {
  st = String(st || "").toLowerCase();
  if (st === "running") return "st-running";
  if (st === "idle") return "st-idle";
  if (st === "done") return "st-done";
  return "st-etc";
}

function timeText(ts) {
  const ms = toMs(ts);
  if (!ms) return "—";
  try {
    return new Date(ms).toLocaleString();
  } catch {
    return String(ms);
  }
}

/** -----------------------------
 *  Derived: user-scoped tasks
 *  ----------------------------- */
const myTasks = computed(() => tasks.value);

/** -----------------------------
 *  Derived: robot / tasks
 *  ----------------------------- */
const robot = computed(() => robots.value.find(r => r.robot_id === "agv1") || robots.value[0] || null);

// 현재 로봇이 수행 중인 task(전체 기준)
const activeTask = computed(() => {
  const rid = robot.value?.robot_id || "agv1";
  return tasks.value.find(t => t.status === "running" && t.assigned_robot === rid) || null;
});

// 내 task 중 현재 실행 중
const myNowTask = computed(() => {
  const rid = robot.value?.robot_id || "agv1";
  return myTasks.value.find(t => t.status === "running" && t.assigned_robot === rid) || null;
});

const pendingCount = computed(() => myTasks.value.filter(t => t.status === "pending" || t.status === "queued").length);

const myNowEtaS = computed(() => {
  const t = myNowTask.value;
  if (!t) return 0;

  const expected = Number(t.expected_duration_ms || 0);
  if (!expected || !t._started_ms) return expected ? Math.round(expected / 1000) : 0;

  const remain = Math.max(0, (t._started_ms + expected) - Date.now());
  return Math.round(remain / 1000);
});

const myNowProgressPct = computed(() => {
  const t = myNowTask.value;
  if (!t || !t._started_ms || !t.expected_duration_ms) return 0;
  const elapsed = Date.now() - t._started_ms;
  return (elapsed / t.expected_duration_ms) * 100;
});

/** history */
const historyTasks = computed(() => {
  return myTasks.value.slice().sort((a, b) => (b._created_ms || 0) - (a._created_ms || 0));
});

/** history filtering */
const histFilter = ref("all");
const filteredHistoryTasks = computed(() => {
  if (histFilter.value === "all") return historyTasks.value;
  return historyTasks.value.filter(t => t.type === histFilter.value);
});

/** reliability */
const last10ErrorCount = computed(() => {
  const arr = historyTasks.value.slice(0, 10);
  return arr.filter(t => t.error_code != null && t.error_code !== "").length;
});
const lastDoneText = computed(() => {
  const t = historyTasks.value.find(x => x.status === "done");
  if (!t) return "—";
  return `${labelType(t.type)} · ${durationS(t)}s`;
});

/** -----------------------------
 *  Aggregation: today/week (내 작업 기준)
 *  ----------------------------- */
function startOfToday() {
  const d = new Date();
  d.setHours(0, 0, 0, 0);
  return d.getTime();
}
function startOfWeek() {
  const d = new Date();
  const day = d.getDay(); // 0 Sun
  const diff = (day === 0 ? 6 : day - 1); // Monday start
  d.setDate(d.getDate() - diff);
  d.setHours(0, 0, 0, 0);
  return d.getTime();
}

function aggregate(rangeStartMs) {
  const arr = myTasks.value.filter(t => (t._created_ms || 0) >= rangeStartMs);

  const total = arr.length;
  const doneArr = arr.filter(t => t.status === "done");
  const done = doneArr.length;

  const water_count = doneArr.filter(t => t.type === "deliver_water").length;
  const water_ml = water_count * waterCupMl;

  const durations = doneArr.map(durationS).filter(v => Number.isFinite(v) && v > 0);
  const avg_duration_s = durations.length ? Math.round(durations.reduce((a, b) => a + b, 0) / durations.length) : 0;

  const byType = {};
  for (const t of doneArr) {
    const k = t.type || "unknown";
    (byType[k] ||= []).push(durationS(t));
  }
  const avg_by_type = {};
  for (const [k, list] of Object.entries(byType)) {
    const valid = list.filter(v => v > 0);
    avg_by_type[k] = valid.length ? Math.round(valid.reduce((a, b) => a + b, 0) / valid.length) : 0;
  }

  return { total, done, water_count, water_ml, avg_duration_s, avg_by_type };
}

const today = computed(() => aggregate(startOfToday()));
const week = computed(() => aggregate(startOfWeek()));

const avgByType = computed(() => ({
  ...(today.value.avg_by_type || {}),
  ...(week.value.avg_by_type || {}),
}));

const R = computed(() => (reportRange.value === "day" ? today.value : week.value));

// ✅ 수분 목표 진행률(오늘 기준)
const waterGoalPct = computed(() => {
  const goal = Number(settings.value.water_goal_ml || 0);
  if (!goal || goal <= 0) return 0;
  const cur = Number(today.value?.water_ml || 0);
  const pct = Math.round((cur / goal) * 100);
  return Math.max(0, Math.min(100, pct));
});

/** -----------------------------
 *  Chart series (내 작업 기준)
 *  ----------------------------- */
const chartSeries = computed(() => {
  if (reportRange.value === "day") {
    const bins = Array(24).fill(0);
    const st = startOfToday();
    for (const t of myTasks.value) {
      const c = t._created_ms || 0;
      if (c < st) continue;
      const h = new Date(c).getHours();
      bins[h] += 1;
    }
    return bins;
  } else {
    const bins = Array(7).fill(0);
    const st = startOfWeek();
    for (const t of myTasks.value) {
      const c = t._created_ms || 0;
      if (c < st) continue;
      const d = new Date(c);
      const day = d.getDay();
      const idx = day === 0 ? 6 : day - 1;
      bins[idx] += 1;
    }
    return bins;
  }
});

function barHeight(v) {
  const max = Math.max(...chartSeries.value, 1);
  return (v / max) * 100;
}
function chartLabel(i) {
  if (reportRange.value === "day") return String(i);
  return ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][i] || "";
}

/** -----------------------------
 *  Place inference by pose
 *  - 특정 좌표 근처면 정수기/충전소/룸/정리함, 아니면 "복도"
 *  ----------------------------- */
const AREA_POS_UI = {
  CHARGE: { x: 50, y: 10 },
  WATER:  { x: 18, y: 28 },
  DROP:   { x: 82, y: 42 },
  RES_A:  { x: 20, y: 70 },
  RES_B:  { x: 42, y: 82 },
  RES_C:  { x: 70, y: 82 },
};

function dist(a, b) { return Math.hypot(a.x - b.x, a.y - b.y); }

function inferPlaceByPose(pose) {
  if (!pose || typeof pose !== "object") return null;
  const x = Number(pose.x);
  const y = Number(pose.y);
  if (!Number.isFinite(x) || !Number.isFinite(y)) return null;

  const p = { x, y };
  let bestKey = null;
  let bestD = 1e18;

  for (const [k, v] of Object.entries(AREA_POS_UI)) {
    const d = dist(p, v);
    if (d < bestD) { bestD = d; bestKey = k; }
  }

  // threshold: 0~100 percent 좌표 기준
  return (bestD <= 6.0) ? bestKey : "HALL";
}

const currentPlaceKey = computed(() => inferPlaceByPose(robot.value?.pose) || (robot.value?.area ? String(robot.value.area).toUpperCase() : null));

const nextTargetKey = computed(() => {
  const k = robot.value?.target_area || activeTask.value?.target_area || null;
  return k ? String(k).toUpperCase() : null;
});
const nextTargetLabel = computed(() => nextTargetKey.value ? uiArea(nextTargetKey.value) : "—");
const moveLine = computed(() => {
  if (!nextTargetKey.value) return "";
  const from = uiPlace(currentPlaceKey.value);
  const to = uiArea(nextTargetKey.value);
  if (!from || !to || from === "—" || to === "—") return "";
  return `${from} → ${to}`;
});

/** -----------------------------
 *  Map / Track (Calibration)
 *  ----------------------------- */
const mapRef = ref(null);

// dot position: pose(%좌표) 우선, 없으면 area fallback
const AREA_FALLBACK = AREA_POS_UI;

const dotPos = computed(() => {
  const p = robot.value?.pose;
  if (p && typeof p.x === "number" && typeof p.y === "number") {
    return { x: p.x, y: p.y };
  }
  const a = String(robot.value?.area || "CHARGE").toUpperCase();
  return AREA_FALLBACK[a] || { x: 50, y: 50 };
});

const poseText = computed(() => {
  const p = robot.value?.pose;
  if (!p) return "—";
  if (typeof p === "string") return p;
  if (typeof p === "object") {
    const x = p.x ?? p[0];
    const y = p.y ?? p[1];
    const th = p.theta ?? p[2];
    return `x:${x ?? "—"}, y:${y ?? "—"}, θ:${th ?? "—"}`;
  }
  return String(p);
});

// ---- track storage ----
const LS_KEY = "agv_track_v1";

// dense points used to render track
const trackDense = ref([]);
// anchors used only in calibration mode
const calibAnchors = ref([]);

const calib = ref({
  on: false,
  tapCount: 0,
  lastTapAt: 0,
});

function defaultTrackAnchors() {
  return [
    { x: 50, y: 10 }, // CHARGE
    { x: 38, y: 14 },
    { x: 28, y: 20 },
    { x: 18, y: 28 }, // WATER
    { x: 18, y: 40 },
    { x: 20, y: 55 },
    { x: 20, y: 70 }, // RES_A
    { x: 32, y: 78 },
    { x: 42, y: 82 }, // RES_B
    { x: 55, y: 80 },
    { x: 70, y: 82 }, // RES_C
    { x: 78, y: 72 },
    { x: 82, y: 42 }, // DROP
    { x: 78, y: 26 },
    { x: 65, y: 16 },
    { x: 50, y: 10 }, // close
  ];
}

function loadTrack() {
  try {
    const raw = localStorage.getItem(LS_KEY);
    if (raw) {
      const obj = JSON.parse(raw);
      const a = Array.isArray(obj?.anchors) ? obj.anchors : null;
      const d = Array.isArray(obj?.dense) ? obj.dense : null;
      if (a && a.length >= 2) calibAnchors.value = a;
      if (d && d.length >= 2) trackDense.value = d;
    }
  } catch {}

  // 아무것도 없으면 기본값 세팅
  if (trackDense.value.length < 2) {
    const a = defaultTrackAnchors();
    calibAnchors.value = a.slice(0, Math.min(a.length, 24));
    trackDense.value = densifyCatmullRom(a, 800, true);
    saveTrackLocal();
  }
}

function saveTrackLocal() {
  const payload = {
    anchors: calibAnchors.value,
    dense: trackDense.value,
    saved_at: Date.now(),
  };
  localStorage.setItem(LS_KEY, JSON.stringify(payload));
}

const trackSvgPoints = computed(() => trackDense.value.map(p => `${p.x},${p.y}`).join(" "));
const anchorSvgPoints = computed(() => calibAnchors.value.map(p => `${p.x},${p.y}`).join(" "));

// ---- secret enter calibration: 5 taps ----
function onMapPointerDown(ev) {
  // 캘리 모드 ON이면: 앵커 찍기
  if (calib.value.on) {
    const pt = pointerToPercent(ev);
    if (!pt) return;
    calibAnchors.value.push(pt);
    // 앵커 찍을 때마다 미리보기 업데이트(가벼운 보간)
    trackDense.value = densifyCatmullRom(calibAnchors.value, 200, true);
    return;
  }

  // 캘리 모드 OFF면: 5연속 탭 감지
  const now = Date.now();
  if (now - calib.value.lastTapAt <= 800) calib.value.tapCount += 1;
  else calib.value.tapCount = 1;

  calib.value.lastTapAt = now;

  if (calib.value.tapCount >= 5) {
    calib.value.tapCount = 0;
    calibEnter();
  }
}

function pointerToPercent(ev) {
  const el = mapRef.value;
  if (!el) return null;
  const r = el.getBoundingClientRect();
  const x = ((ev.clientX - r.left) / r.width) * 100;
  const y = ((ev.clientY - r.top) / r.height) * 100;
  const cx = Math.max(0, Math.min(100, x));
  const cy = Math.max(0, Math.min(100, y));
  return { x: Number(cx.toFixed(2)), y: Number(cy.toFixed(2)) };
}

function calibEnter() {
  calib.value.on = true;
  showToast("Calibration Mode ON");
}
function calibExit() {
  calib.value.on = false;
  showToast("Calibration Mode OFF");
}

function calibUndo() {
  if (calibAnchors.value.length === 0) return;
  calibAnchors.value.pop();
  trackDense.value = densifyCatmullRom(calibAnchors.value, 200, true);
}
function calibClear() {
  calibAnchors.value = [];
  trackDense.value = [];
}
async function calibSave() {
  if (calibAnchors.value.length < 3) {
    showToast("앵커가 너무 적음(최소 3개 이상 추천)");
    return;
  }

  // ✅ 800개 자동 보간
  trackDense.value = densifyCatmullRom(calibAnchors.value, 800, true);

  // ✅ 로컬스토리지 저장(기존 로직 유지)
  saveTrackLocal();

  // ✅ 파일로도 저장(추가)
  try {
    const payload = {
      anchors: calibAnchors.value,
      dense: trackDense.value,
      saved_at: Date.now(),
    };
    const filename = `agv_track_${tsFile()}.json`;
    await saveJsonFile(payload, filename);
    showToast("Saved ✅ (local + json file)");
  } catch (e) {
    showToast("파일 저장 실패(브라우저 권한/환경 확인)");
  }
}

async function calibCopyJson() {
  try {
    const text = JSON.stringify(trackDense.value, null, 2);
    await navigator.clipboard.writeText(text);
    showToast("Copied JSON ✅");
  } catch {
    showToast("Copy 실패(브라우저 권한 확인)");
  }
}

// Catmull-Rom densify (loop option)
function densifyCatmullRom(anchors, targetN = 800, loop = true) {
  const pts = (anchors || []).filter(p => p && Number.isFinite(p.x) && Number.isFinite(p.y));
  if (pts.length < 2) return [];

  // if closed already, drop last duplicate for stable loop handling
  let a = pts.slice();
  const isClosed = a.length >= 3 && dist(a[0], a[a.length - 1]) < 0.0001;
  if (loop && isClosed) a = a.slice(0, -1);

  const segCount = loop ? a.length : (a.length - 1);
  if (segCount <= 0) return [];

  // segment lengths for allocation
  const segLen = [];
  let totalLen = 0;
  for (let i = 0; i < segCount; i++) {
    const p1 = a[i];
    const p2 = a[(i + 1) % a.length];
    const d = dist(p1, p2);
    segLen.push(d);
    totalLen += d;
  }
  if (totalLen <= 0) totalLen = segCount;

  const out = [];
  let remaining = targetN;

  for (let i = 0; i < segCount; i++) {
    const p0 = a[(i - 1 + a.length) % a.length];
    const p1 = a[i];
    const p2 = a[(i + 1) % a.length];
    const p3 = a[(i + 2) % a.length];

    // allocate count for this segment
    const want = Math.max(4, Math.round(targetN * (segLen[i] / totalLen)));
    const n = (i === segCount - 1) ? Math.max(4, remaining) : want;
    remaining -= n;

    // sample [0..1) to avoid duplicate point with next segment
    for (let k = 0; k < n; k++) {
      const t = k / n;
      const x = catmull(p0.x, p1.x, p2.x, p3.x, t);
      const y = catmull(p0.y, p1.y, p2.y, p3.y, t);
      out.push({ x: clamp01to100(x), y: clamp01to100(y) });
    }
  }

  // close
  if (loop && out.length) out.push({ ...out[0] });
  return out;
}

function catmull(p0, p1, p2, p3, t) {
  const t2 = t * t;
  const t3 = t2 * t;
  return 0.5 * (
    (2 * p1) +
    (-p0 + p2) * t +
    (2*p0 - 5*p1 + 4*p2 - p3) * t2 +
    (-p0 + 3*p1 - 3*p2 + p3) * t3
  );
}

function clamp01to100(v) {
  if (!Number.isFinite(v)) return 0;
  return Math.max(0, Math.min(100, Number(v.toFixed(2))));
}

/** -----------------------------
 *  Brief
 *  ----------------------------- */
function makeLocalBrief() {
  const r = R.value;
  const rangeName = reportRange.value === "day" ? "오늘" : "이번 주";
  const pct = r.total ? Math.round((r.done / r.total) * 100) : 0;

  const peakHint =
    reportRange.value === "day"
      ? (() => {
          const arr = chartSeries.value;
          const mx = Math.max(...arr);
          const idx = arr.indexOf(mx);
          if (mx <= 0) return "요청이 아직 없어요.";
          return `요청이 ${idx}시에 가장 많았습니다.`;
        })()
      : (() => {
          const arr = chartSeries.value;
          const mx = Math.max(...arr);
          const idx = arr.indexOf(mx);
          const label = chartLabel(idx);
          if (mx <= 0) return "요청이 아직 없어요.";
          return `요청이 ${label}에 가장 많았습니다.`;
        })();

  return `${rangeName} 요청은 총 ${r.total}건이며, 완료율은 ${pct}%입니다. ` +
         `물 배달은 ${r.water_count}회로 추정 섭취량 ${r.water_ml}ml 입니다. ` +
         `평균 소요시간은 ${r.avg_duration_s}s 입니다. ` +
         `${peakHint}`;
}

const briefLoading = ref(false);
async function generateBrief(forceRefresh = false) {
  if (briefLoading.value) return;

  briefLoading.value = true;
  try {
    const res = await getUserBrief({
      range: reportRange.value,
      refresh: forceRefresh ? 1 : 0
    });
    briefText.value = res?.brief || "—";
  } catch (e) {
    console.warn("brief failed:", e);
    briefText.value = makeLocalBrief();
  } finally {
    briefLoading.value = false;
  }
}

function setReportRange(v) {
  reportRange.value = v;
}

/** -----------------------------
 *  Fetch
 *  ----------------------------- */
async function refreshRobots() {
  try {
    robots.value = (await getRobots({ limit: 20 })) || [];
  } catch {}
}

async function refreshTasks() {
  try {
    const ts = await getTasks({ limit: 500 });
    tasks.value = (ts || []).map(normalizeTask);
  } catch {}
}

async function refreshAll() {
  loading.value = true;
  try {
    await Promise.all([refreshRobots(), refreshTasks()]);
    lastFetchAt.value = Date.now();
    if (tab.value === "report" && !briefText.value) await generateBrief(false);
  } catch (e) {
    showToast("API 로드 실패 (/api/robots, /api/tasks 확인)");
  } finally {
    loading.value = false;
  }
}

/** Polling */
let pollRobotsTimer = null;
let pollTasksTimer = null;

function setupPolling() {
  clearInterval(pollRobotsTimer);
  clearInterval(pollTasksTimer);
  pollRobotsTimer = null;
  pollTasksTimer = null;

  // robots: 기본 800ms, map에서는 350ms
  const robotInterval = (tab.value === "map") ? 350 : 800;
  pollRobotsTimer = setInterval(refreshRobots, robotInterval);

  // tasks: map이 아닐 때만 2500ms
  if (tab.value !== "map") {
    pollTasksTimer = setInterval(refreshTasks, 2500);
  }
}

watch(tab, async (t) => {
  setupPolling();
  if (t === "report" && !briefText.value) {
    await generateBrief(false);
  }
});

/** report range 변경 시: 브리핑/차트 즉시 반영 */
watch(reportRange, async () => {
  await refreshTasks();
  await generateBrief();
});

/** -----------------------------
 *  Header sub text
 *  ----------------------------- */
const headerSub = computed(() => {
  const name = userName.value ? `${userName.value}님` : "사용자";
  const last = lastFetchAt.value ? new Date(lastFetchAt.value).toLocaleTimeString() : "—";
  const mode = userId.value ? "내 작업" : "Demo";
  return `${name} · ${mode} · 마지막 갱신 ${last}`;
});

/** -----------------------------
 *  Lifecycle
 *  ----------------------------- */
onMounted(async () => {
  initTelegramUser();
  await loadGlobalSettings();
  prevBodyOverflow = document.body.style.overflow;
  prevHtmlOverflow = document.documentElement.style.overflow;

  document.documentElement.style.overflow = "hidden";
  document.body.style.overflow = "hidden";

  const tg = window?.Telegram?.WebApp;
  try {
    tg?.ready?.();
    tg?.expand?.();
    tg?.disableVerticalSwipes?.();
  } catch {}

  loadTrack();
  await refreshAll();
  setupPolling();
});

onBeforeUnmount(() => {
  document.body.style.overflow = prevBodyOverflow;
  document.documentElement.style.overflow = prevHtmlOverflow;

  clearInterval(pollRobotsTimer);
  clearInterval(pollTasksTimer);
  clearTimeout(toastTimer);
});
</script>

<style scoped>
.ua {
  /* Telegram 테마가 있으면 따라가고, 없으면 밝은 기본값 */
  --bg: var(--tg-theme-bg-color, #f4f6fb);
  --fg: var(--tg-theme-text-color, #162033);
  --muted: rgba(22, 32, 51, 0.62);

  --card: rgba(255,255,255,0.86);
  --card2: rgba(255,255,255,0.92);
  --bd: rgba(10, 20, 40, 0.10);

  --accent: var(--tg-theme-button-color, #2f7cff);
  --accentText: var(--tg-theme-button-text-color, #ffffff);

  overflow: hidden;
  height: 100dvh;
  background: radial-gradient(circle at 20% 15%, rgba(47,124,255,0.12), transparent 40%),
              radial-gradient(circle at 80% 10%, rgba(125,255,178,0.14), transparent 45%),
              var(--bg);
  color: var(--fg);
  box-sizing: border-box;
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, "Noto Sans KR", sans-serif;
}

.ua-header{
  position: fixed;
  top: 0; left: 0; right: 0;
  z-index: 9998;
  display:flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 14px;
  background: rgba(255,255,255,0.72);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--bd);
}
.title{ font-size: 18px; font-weight: 900; letter-spacing: .2px; }
.sub{ font-size: 12px; color: var(--muted); margin-top: 2px; }

.ua-main{
  position: fixed;
  top: 64px;
  left: 0;
  right: 0;
  bottom: calc(76px + env(safe-area-inset-bottom));
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  touch-action: pan-y;
  padding: 14px;
}
.page{ max-width: 680px; margin: 0 auto; }

.grid{
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}
@media (min-width: 520px){
  .grid{ grid-template-columns: 1fr 1fr; }
  .wide{ grid-column: 1 / -1; }
}

.card{
  background: var(--card);
  border: 1px solid var(--bd);
  border-radius: 16px;
  padding: 14px;
  box-shadow: 0 10px 26px rgba(10, 20, 40, 0.10);
}
.card.inner{
  padding: 12px;
  background: var(--card2);
}
.card-title{
  font-size: 13px;
  color: var(--muted);
  margin-bottom: 10px;
  font-weight: 900;
}

.kvs{ display:flex; flex-direction: column; gap: 8px; }
.kv{ display:flex; justify-content: space-between; align-items: center; gap: 10px; }
.kv span{ color: var(--muted); font-size: 12px; }
.kv b{ font-size: 13px; }

.mt{ margin-top: 12px; }
.mt2{ margin-top: 10px; }

.btn{
  border: 1px solid var(--bd);
  background: rgba(255,255,255,0.65);
  color: var(--fg);
  padding: 10px 12px;
  border-radius: 12px;
  font-weight: 900;
  cursor: pointer;
  touch-action: manipulation;
}
.btn:disabled{ opacity: .55; cursor: not-allowed; }
.btn.primary{
  background: var(--accent);
  color: var(--accentText);
  border-color: rgba(0,0,0,0.08);
}

.btn.sm{ padding: 8px 10px; border-radius: 10px; font-size: 12px; }

.muted{ color: var(--muted); font-size: 12px; margin-top: 8px; }

.pill{
  font-size: 11px;
  padding: 4px 8px;
  border-radius: 999px;
  border: 1px solid var(--bd);
  background: rgba(255,255,255,0.65);
}

.st-running{ color: #c06b00; }
.st-done{ color: #0a7a3d; }
.st-idle{ color: #1a4aa8; }
.st-pending{ color: #1a4aa8; }
.st-error{ color: #b00020; }
.st-etc{ color: #5b667d; }

/* Now progress */
.nowbox .now-main{
  display:flex; align-items: center; justify-content: space-between;
  gap: 10px;
}
.progress{
  height: 10px;
  background: rgba(10, 20, 40, 0.06);
  border: 1px solid var(--bd);
  border-radius: 999px;
  overflow: hidden;
  margin-top: 10px;
}
.bar{
  height: 100%;
  background: var(--accent);
  width: 0%;
}

/* Chips */
.chips{ display:flex; gap: 10px; flex-wrap: wrap; }
.chip{
  display:flex; align-items: center; justify-content: space-between;
  gap: 10px;
  min-width: 160px;
  padding: 10px 12px;
  border-radius: 14px;
  background: rgba(10, 20, 40, 0.03);
  border: 1px solid var(--bd);
}
.chip span{ color: var(--muted); font-size: 12px; }
.chip b{ font-size: 13px; }

/* Bottom tabs */
.ua-tabs{
  position: fixed;
  left: 0; right: 0; bottom: 0;
  display: grid;
  grid-template-columns: repeat(5, 1fr); /* ✅ 5 tabs */
  gap: 8px;
  padding: 10px 10px 12px;
  background: rgba(255,255,255,0.78);
  border-top: 1px solid var(--bd);
  backdrop-filter: blur(12px);
  z-index: 9999;
  padding-bottom: calc(12px + env(safe-area-inset-bottom));
  touch-action: manipulation;
}
.tab{
  border: 1px solid var(--bd);
  background: rgba(255,255,255,0.70);
  color: var(--fg);
  border-radius: 14px;
  padding: 10px 8px;
  font-weight: 900;
}
.tab.on{
  background: var(--accent);
  color: var(--accentText);
  border-color: rgba(0,0,0,0.10);
}

/* Toast */
.toast{
  position: fixed;
  left: 50%;
  transform: translateX(-50%);
  bottom: 86px;
  background: rgba(20, 28, 40, 0.88);
  border: 1px solid rgba(255,255,255,0.14);
  color: #fff;
  padding: 10px 12px;
  border-radius: 999px;
  font-weight: 900;
  font-size: 12px;
}

/* Map */
.map{
  position: relative;
  height: 340px;
  margin-top: 12px;
  border-radius: 18px;
  border: 1px solid var(--bd);
  background:
    radial-gradient(circle at 20% 80%, rgba(47,124,255,0.14), transparent 45%),
    radial-gradient(circle at 70% 30%, rgba(10,122,61,0.10), transparent 45%),
    rgba(255,255,255,0.70);
  overflow: hidden;
  touch-action: none;
}

.track-svg{
  position:absolute;
  inset:0;
  width:100%;
  height:100%;
  pointer-events: none;
}
.track-line{
  fill: none;
  stroke: rgba(47,124,255,0.65);
  stroke-width: 1.6;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.anchor-line{
  fill: none;
  stroke: rgba(192, 107, 0, 0.70);
  stroke-width: 1.4;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-dasharray: 2.5 2.5;
}
.anchor-dot{
  fill: rgba(192, 107, 0, 0.95);
  stroke: rgba(0,0,0,0.20);
  stroke-width: 0.3;
}

.zone{
  position:absolute;
  padding: 8px 10px;
  border: 1px dashed rgba(10,20,40,0.18);
  border-radius: 14px;
  color: rgba(22,32,51,0.82);
  font-weight: 900;
  font-size: 12px;
  background: rgba(255,255,255,0.55);
}
.z-charge{ left: 40%; top: 6%; width: 20%; height: 12%; text-align:center; }
.z-water { left: 8%;  top: 22%; width: 22%; height: 16%; }
.z-drop  { left: 70%; top: 30%; width: 22%; height: 16%; }

.z-a{ left: 10%; top: 66%; width: 24%; height: 18%; }
.z-b{ left: 38%; top: 74%; width: 24%; height: 18%; }
.z-c{ left: 66%; top: 66%; width: 24%; height: 18%; }

.dot{
  position:absolute;
  transform: translate(-50%, -50%);
  transition: left 0.28s linear, top 0.28s linear;
}
.dot-inner{
  width: 14px; height: 14px;
  border-radius: 999px;
  background: var(--accent);
  border: 2px solid rgba(0,0,0,0.15);
  box-shadow: 0 0 0 6px rgba(47,124,255,0.14);
}
.dot-label{
  margin-top: 8px;
  font-size: 11px;
  color: rgba(22,32,51,0.92);
  text-align: center;
  opacity: .9;
}

/* Sonar pulse */
.sonar::before, .sonar::after{
  content:"";
  position:absolute;
  left: 50%; top: 50%;
  transform: translate(-50%, -50%);
  width: 10px; height: 10px;
  border-radius: 999px;
  border: 2px solid rgba(47,124,255,0.45);
  animation: pulse 2.0s infinite;
}
.sonar::after{
  animation-delay: 1.0s;
  border-color: rgba(47,124,255,0.28);
}
@keyframes pulse{
  0%   { width: 10px; height: 10px; opacity: 0.9; }
  100% { width: 160px; height: 160px; opacity: 0; }
}

/* Calibration panel */
.calib-panel{
  margin-top: 12px;
  border-radius: 16px;
  border: 1px solid var(--bd);
  background: rgba(255,255,255,0.72);
  padding: 12px;
}
.calib-row{
  display:flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 8px;
}
.calib-title{
  font-size: 13px;
}
.calib-sub{
  font-size: 12px;
  color: var(--muted);
}

/* Report */
.seg{
  display:flex; gap: 10px;
}
.segbtn{
  flex: 1;
  border-radius: 14px;
  padding: 10px 8px;
  border: 1px solid var(--bd);
  background: rgba(255,255,255,0.70);
  color: var(--fg);
  font-weight: 900;
}
.segbtn.on{
  background: var(--accent);
  color: var(--accentText);
  border-color: rgba(0,0,0,0.10);
}
.brief{
  font-size: 13px;
  line-height: 1.45;
  padding: 10px 12px;
  border-radius: 14px;
  background: rgba(10,20,40,0.03);
  border: 1px solid var(--bd);
  white-space: pre-line;
}
.actions{ display:flex; gap: 10px; flex-wrap: wrap; }

/* chart */
.chart-wrap{
  margin-top: 8px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}
.chart{
  display:flex;
  align-items: stretch;
  gap: 6px;
  height: 180px;
  padding: 8px;
  min-width: 560px; /* 모바일에서 24시간 막대가 넘치면 가로 스크롤 */
}
/* ✅ week는 min-width 해제 + 7개 꽉 차게 배치 */
.chart.week{
  min-width: 0;
  width: 100%;
  justify-content: space-between;
  gap: 10px;
}
/* ✅ bar 높이의 기준 컨테이너 */
.barbox{
  flex: 1 1 auto;                /* ✅ 남는 높이 전부 */
  width: 100%;
  display:flex;
  align-items: flex-end;         /* 막대 아래 정렬 */
}
.chart.week .barcol{
  width: auto;
  flex: 1 1 0;
  max-width: 44px;
}
/* ✅ week(7개)는 스크롤 제거 + 빈 공간 제거 */
.chart-wrap.week{
  overflow-x: hidden;
}
.barcol{
  width: 18px;
  flex: 0 0 18px;
  height: 100%;                  /* ✅ % height 계산 가능 */
  display:flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}
.bar2{
  width: 100%;
  border-radius: 10px;
  background: rgba(47,124,255,0.75);
  border: 1px solid rgba(10,20,40,0.10);
}
.xlabel{
  flex: 0 0 auto;
  font-size: 10px;
  color: var(--muted);
  white-space: nowrap;
}

/* list */
.list{ margin-top: 10px; display:flex; flex-direction: column; gap: 10px; }
.item{
  padding: 12px;
  border-radius: 16px;
  background: rgba(10,20,40,0.02);
  border: 1px solid var(--bd);
}
.item-top{ display:flex; justify-content: space-between; align-items: center; gap: 10px; }
.item-sub{ margin-top: 6px; display:flex; gap: 8px; font-size: 12px; color: rgba(22,32,51,0.86); }

/* history filters */
.hist-filters{
  display:flex;
  gap: 8px;
  margin-top: 10px;
  flex-wrap: wrap;
}
.fbtn{
  border: 1px solid var(--bd);
  background: rgba(255,255,255,0.70);
  color: var(--fg);
  border-radius: 999px;
  padding: 8px 10px;
  font-weight: 900;
  font-size: 12px;
}
.fbtn.on{
  background: var(--accent);
  color: var(--accentText);
  border-color: rgba(0,0,0,0.10);
}

/* Settings controls */
.ctl{
  border: 1px solid var(--bd);
  background: rgba(255,255,255,0.70);
  color: var(--fg);
  border-radius: 12px;
  padding: 8px 10px;
  font-size: 13px;
  min-width: 160px;
}
.ctl:focus{ outline: none; box-shadow: 0 0 0 3px rgba(47,124,255,0.18); }

.seg2{ display:flex; gap: 8px; justify-content: flex-end; }
.days{ display:flex; flex-wrap: wrap; gap: 8px; justify-content: flex-end; margin-top: 6px; }

.routine-actions{
  display:flex;
  gap: 8px;
  align-items: center;
}
</style>
