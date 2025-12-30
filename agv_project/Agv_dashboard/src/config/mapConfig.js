// 격자 좌표계: (1,1) ~ (12,8) 정도로 생각
export const GRID = { cols: 12, rows: 8 };

// area -> 격자 좌표 매핑 (중앙값)
export const AREAS = {
  BASE:  { x: 2,  y: 7 },
  DOCK:  { x: 2,  y: 2 },
  USER1: { x: 9,  y: 3 },
  USER2: { x: 10, y: 6 },
};

// 미니맵에 표시할 라벨 (원하면 늘려도 됨)
export const AREA_LABELS = Object.entries(AREAS).map(([name, pos]) => ({
  name, ...pos
}));
