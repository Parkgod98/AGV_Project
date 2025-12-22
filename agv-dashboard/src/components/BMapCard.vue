<script setup>
import { computed, onMounted, ref } from "vue";

const props = defineProps({
  robot: { type: Object, default: null },
  currentTask: { type: Object, default: null },
});

// UserApp과 동일한 fallback
const AREA_POS_UI = {
  CHARGE: { x: 50, y: 10 },
  WATER:  { x: 18, y: 28 },
  DROP:   { x: 82, y: 42 },
  RES_A:  { x: 20, y: 70 },
  RES_B:  { x: 42, y: 82 },
  RES_C:  { x: 70, y: 82 },
};
const AREA_FALLBACK = AREA_POS_UI;

const dotPos = computed(() => {
  const p = props.robot?.pose;
  if (p && typeof p.x === "number" && typeof p.y === "number") {
    return { x: p.x, y: p.y };
  }
  const a = String(props.robot?.area || "CHARGE").toUpperCase();
  return AREA_FALLBACK[a] || { x: 50, y: 50 };
});

// UserApp과 동일: localStorage 트랙
const LS_KEY = "agv_track_v1";
const trackDense = ref([]);

onMounted(() => {
  try {
    const raw = localStorage.getItem(LS_KEY);
    if (!raw) return;
    const parsed = JSON.parse(raw);
    trackDense.value = Array.isArray(parsed?.dense) ? parsed.dense : [];
  } catch {}
});

const trackSvgPoints = computed(() =>
  trackDense.value.map(p => `${p.x},${p.y}`).join(" ")
);
</script>

<template>
  <div class="card mapCard">
    <div class="head">
      <div class="title">Digital Twin</div>
      <div class="pills">
        <span class="pill">{{ props.robot?.robot_id || "agv1" }}</span>
        <span class="pill muted">{{ props.robot?.state || "unknown" }}</span>
      </div>
    </div>

    <!-- ✅ 클래스명 전부 dt-*로 변경해서 전역 CSS 충돌 차단 -->
    <div class="dtMap">
      <!-- Track SVG -->
      <svg class="dtTrack" viewBox="0 0 100 100" preserveAspectRatio="none">
        <!-- 글로우 레이어 -->
        <polyline
          v-if="trackDense.length >= 2"
          :points="trackSvgPoints"
          class="track-line glow"
        />
        <polyline
          v-if="trackDense.length >= 2"
          :points="trackSvgPoints"
          class="track-line main"
        />
      </svg>

      <!-- Zones -->
      <div class="dtZone z-charge">충전소</div>
      <div class="dtZone z-water">정수기</div>
      <div class="dtZone z-drop">정리함</div>
      <div class="dtZone z-a">룸 1</div>
      <div class="dtZone z-b">룸 2</div>
      <div class="dtZone z-c">룸 3</div>

      <!-- Robot dot -->
      <div class="dot sonar" :style="{ left: `${dotPos.x}%`, top: `${dotPos.y}%` }">
        <div class="dot-inner"></div>
        <div class="dot-label">{{ props.robot?.robot_id || "agv1" }}</div>
      </div>
    </div>

    <!-- <div class="foot"> -->
      <!-- <span class="mutedFoot">Telemetry powered by MQTT · Firestore</span> -->
    <!-- </div> -->
  </div>
</template>

<style scoped>
.mapCard{
  height: 100%;
  min-height: 0;
  display:flex;
  flex-direction:column;

  --accent: rgba(120,200,255,0.95);
  --accent2: rgba(0,255,180,0.55);
}

/* header */
.head{
  display:flex;
  align-items:center;
  justify-content:space-between;
  margin-bottom: 10px;
}
.title{
  font-weight: 900;
  letter-spacing: -0.02em;
}
.pills{ display:flex; gap: 8px; }
.pill{
  font-size: 11px;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(255,255,255,0.04);
}
.pill.muted{ opacity: .75; }

/* ✅ 여기부터가 “허연 맵” 종결 스타일 */
.dtMap{
  position: relative;
  flex: 1;
  min-height: 0;

  border-radius: 18px;
  border: 1px solid rgba(255,255,255,0.10);

  /* 완전 다크 베이스 + 은은한 컬러 포켓 */
  background:
    radial-gradient(circle at 18% 78%, rgba(120,200,255,0.18), transparent 56%),
    radial-gradient(circle at 84% 26%, rgba(0,255,180,0.08), transparent 58%),
    linear-gradient(180deg, rgba(255,255,255,0.05), rgba(0,0,0,0.34)),
    rgba(8,10,14,0.94);

  backdrop-filter: blur(10px) saturate(140%);
  overflow: hidden;
}

/* HUD grid + vignette + texture */
.dtMap::before{
  content:"";
  position:absolute;
  inset:-2px;
  background:
    /* subtle grid */
    linear-gradient(to right, rgba(255,255,255,0.045) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(255,255,255,0.035) 1px, transparent 1px);
  background-size: 28px 28px;
  opacity: .20;
  pointer-events:none;
}

.dtMap::after{
  content:"";
  position:absolute;
  inset:0;
  background:
    radial-gradient(circle at 50% 40%, transparent 38%, rgba(0,0,0,0.46) 78%),
    radial-gradient(circle at 30% 30%, rgba(255,255,255,0.05), transparent 42%),
    radial-gradient(circle at 70% 70%, rgba(255,255,255,0.03), transparent 50%);
  opacity: .85;
  pointer-events:none;
}

/* track svg */
.dtTrack{
  position:absolute;
  inset:0;
  width:100%;
  height:100%;
  pointer-events:none;
}

/* track line 2 layers */
.track-line{
  fill:none;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.track-line.glow{
  stroke: rgba(120,200,255,0.22);
  stroke-width: 3.8;
  filter: blur(0.4px) drop-shadow(0 0 14px rgba(120,200,255,0.22));
}
.track-line.main{
  stroke: rgba(120,200,255,0.52);
  stroke-width: 1.6;
  filter: drop-shadow(0 0 8px rgba(120,200,255,0.18));
}

/* zones */
.dtZone{
  position:absolute;
  padding: 10px 12px;
  border-radius: 14px;

  /* ✅ 테두리 선명하게 + 2겹 느낌 */
  border: 1px solid rgba(255,255,255,0.18);
  box-shadow:
    inset 0 0 0 1px rgba(0,0,0,0.35),
    0 12px 26px rgba(0,0,0,0.22),
    0 0 0 1px rgba(120,200,255,0.10); /* 은은한 링 */

  /* ✅ 배경을 조금 더 밝게 + 유리 느낌 */
  background:
    linear-gradient(180deg, rgba(255,255,255,0.10), rgba(255,255,255,0.04)),
    rgba(18,26,40,0.55);

  backdrop-filter: blur(12px) saturate(140%);

  /* ✅ 텍스트 대비 강화 */
  color: rgba(255,255,255,0.96);
  font-weight: 950;
  font-size: 13px;
  letter-spacing: .35px;

  /* ✅ 라벨이 배경에 묻지 않게 */
  text-shadow: 0 8px 18px rgba(0,0,0,0.65);
}
/* .dtZone::before{
  content:"";
  position:absolute;
  left:10px; right:10px; top:8px;
  height: 2px;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(120,200,255,0.45), rgba(0,255,180,0.22));
  opacity: .55;
  pointer-events:none;
} */

.dtZone::after{
  content:"";
  position:absolute;
  inset:-1px;
  border-radius: 14px;
  box-shadow: 0 0 18px rgba(120,200,255,0.10);
  opacity: .6;
  pointer-events:none;
}

/* positions */
.z-charge{ left: 40%; top: 6%;  width: 20%; height: 12%; text-align:center; }
.z-water { left: 8%;  top: 22%; width: 22%; height: 16%; }
.z-drop  { left: 70%; top: 30%; width: 22%; height: 16%; }
.z-a{ left: 10%; top: 66%; width: 24%; height: 18%; }
.z-b{ left: 38%; top: 74%; width: 24%; height: 18%; }
.z-c{ left: 66%; top: 66%; width: 24%; height: 18%; }

/* robot dot */
.dot{
  position:absolute;
  transform: translate(-50%, -50%);
  transition: left 0.26s linear, top 0.26s linear;
}

.dot-inner{
  width: 14px; height: 14px;
  border-radius: 999px;
  background: var(--accent);
  border: 2px solid rgba(0,0,0,0.22);
  box-shadow:
    0 0 0 7px rgba(120,200,255,0.14),
    0 0 18px rgba(120,200,255,0.18);
}

.dot-label{
  margin-top: 8px;
  font-size: 11px;
  color: rgba(235,245,255,0.88);
  text-align: center;
  opacity: .95;
  text-shadow: 0 4px 14px rgba(0,0,0,0.42);
}

/* sonar pulse */
.sonar::before, .sonar::after{
  content:"";
  position:absolute;
  left:50%; top:50%;
  transform: translate(-50%, -50%);
  width:10px; height:10px;
  border-radius:999px;
  border: 2px solid rgba(120,200,255,0.34);
  animation: pulse 2.1s infinite;
}
.sonar::after{
  animation-delay: 1.05s;
  border-color: rgba(0,255,180,0.16);
}

@keyframes pulse{
  0%   { width:10px; height:10px; opacity:0.9; }
  100% { width:170px; height:170px; opacity:0; }
}

.foot{ margin-top: 10px; }
.mutedFoot{ font-size: 11px; opacity: .65; }
</style>
