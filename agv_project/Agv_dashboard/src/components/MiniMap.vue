<script setup>
import { onMounted, onUnmounted, ref, watch } from "vue";

/**
 * props
 * - pose: { x, y, theta }
 * - currentArea: string
 * - targetArea: string
 * - large: boolean (Overview 전용 대형 모드)
 */
const props = defineProps({
  pose: { type: Object, default: null },
  currentArea: { type: String, default: "" },
  targetArea: { type: String, default: "" },
  large: { type: Boolean, default: false },
});

const canvasRef = ref(null);
let ctx = null;

/* =========================
   가상 맵 정의 (추후 교체 예정)
   ========================= */
const GRID_SIZE = 12; // 12x12 가상 그리드

const AREAS = {
  BASE: { x: 2, y: 9 },
  DOCK: { x: 2, y: 2 },
  USER1: { x: 9, y: 3 },
  USER2: { x: 10, y: 7 },
};

/* trail (이동 흔적) */
const trail = [];

/* =========================
   유틸
   ========================= */
function gridToPx(x, y, size) {
  const cell = size / GRID_SIZE;
  return {
    px: x * cell + cell / 2,
    py: y * cell + cell / 2,
  };
}

/* =========================
   드로잉
   ========================= */
function draw() {
  if (!ctx) return;

  const size = props.large ? 300 : 240;
  ctx.clearRect(0, 0, size, size);

  drawBackground(size);
  drawGrid(size);
  drawAreas(size);
  drawTarget(size);
  drawTrail(size);
  drawRobot(size);
}

/* ----- Background ----- */
function drawBackground(size) {
  const g = ctx.createLinearGradient(0, 0, 0, size);
  g.addColorStop(0, "#060913");
  g.addColorStop(1, "#03050b");
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, size, size);
}

/* ----- Grid ----- */
function drawGrid(size) {
  const cell = size / GRID_SIZE;
  ctx.strokeStyle = "rgba(255,255,255,0.05)";
  ctx.lineWidth = 1;

  for (let i = 0; i <= GRID_SIZE; i++) {
    ctx.beginPath();
    ctx.moveTo(i * cell, 0);
    ctx.lineTo(i * cell, size);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(0, i * cell);
    ctx.lineTo(size, i * cell);
    ctx.stroke();
  }
}

/* ----- Areas ----- */
function drawAreas(size) {
  Object.entries(AREAS).forEach(([name, pos]) => {
    const { px, py } = gridToPx(pos.x, pos.y, size);

    ctx.beginPath();
    ctx.arc(px, py, 6, 0, Math.PI * 2);
    ctx.fillStyle =
      name === props.currentArea
        ? "rgba(0,220,180,0.9)"
        : "rgba(255,255,255,0.35)";
    ctx.fill();

    ctx.font = "11px sans-serif";
    ctx.fillStyle = "rgba(255,255,255,0.6)";
    ctx.fillText(name, px + 8, py - 6);
  });
}

/* ----- Target Marker ----- */
function drawTarget(size) {
  if (!props.targetArea || !AREAS[props.targetArea]) return;
  const { px, py } = gridToPx(
    AREAS[props.targetArea].x,
    AREAS[props.targetArea].y,
    size
  );

  ctx.beginPath();
  ctx.arc(px, py, 10, 0, Math.PI * 2);
  ctx.strokeStyle = "rgba(120,130,255,0.9)";
  ctx.lineWidth = 2;
  ctx.stroke();
}

/* ----- Trail ----- */
function drawTrail(size) {
  if (trail.length < 2) return;

  ctx.beginPath();
  trail.forEach((p, i) => {
    const { px, py } = gridToPx(p.x, p.y, size);
    if (i === 0) ctx.moveTo(px, py);
    else ctx.lineTo(px, py);
  });

  ctx.strokeStyle = "rgba(0,220,180,0.35)";
  ctx.lineWidth = 2;
  ctx.stroke();
}

/* ----- Robot ----- */
function drawRobot(size) {
  if (!props.pose) return;

  const { px, py } = gridToPx(props.pose.x, props.pose.y, size);
  const theta = props.pose.theta || 0;

  // trail 기록
  trail.push({ x: props.pose.x, y: props.pose.y });
  if (trail.length > 25) trail.shift();

  ctx.save();
  ctx.translate(px, py);
  ctx.rotate(theta);

  ctx.beginPath();
  ctx.moveTo(10, 0);
  ctx.lineTo(-6, 6);
  ctx.lineTo(-6, -6);
  ctx.closePath();

  ctx.fillStyle = "rgba(255,255,255,0.95)";
  ctx.fill();

  ctx.restore();
}

/* =========================
   lifecycle
   ========================= */
onMounted(() => {
  const canvas = canvasRef.value;
  const size = props.large ? 300 : 240;
  canvas.width = size;
  canvas.height = size;
  ctx = canvas.getContext("2d");
  draw();
});

watch(
  () => [props.pose, props.currentArea, props.targetArea],
  () => {
    draw();
  },
  { deep: true }
);

onUnmounted(() => {
  trail.length = 0;
});
</script>

<template>
  <div class="map-frame">
    <canvas ref="canvasRef" class="map" />
  </div>
</template>

<style scoped>
.map-frame{
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;      /* ✅ 정사각 캔버스 중앙 배치 */
}

.map{
  width: auto !important;
  height: 100% !important;  /* ✅ 높이에 맞추고 */
  aspect-ratio: 1 / 1;       /* ✅ 항상 정사각형 유지 */
  display: block;
}
</style>
