<script setup>
import { RouterLink, RouterView, useRoute } from "vue-router";

const route = useRoute();
</script>

<template>
  <div class="app">
    <!-- subtle background ornaments -->
    <div class="bg-orb orb-a" />
    <div class="bg-orb orb-b" />
    <div class="bg-noise" />

    <header class="topbar">
      <div class="brand">
        <div class="brand-mark" aria-hidden="true" />
        <div class="brand-text">
          <div class="brand-title">AGV Control Center</div>
          <div class="brand-sub">Mission control dashboard</div>
        </div>
      </div>

      <nav class="nav">
        <RouterLink class="nav-link" to="/">Overview</RouterLink>
        <RouterLink class="nav-link" to="/robots">Robots</RouterLink>
        <RouterLink class="nav-link" to="/tasks">Tasks</RouterLink>
        <RouterLink class="nav-link" to="/events">Events</RouterLink>
        <span class="nav-indicator" :data-path="route.path" />
      </nav>
    </header>

    <main class="page">
      <div class="page-inner">
        <RouterView />
      </div>
    </main>

    <footer class="footer">
      <span class="footer-dot" aria-hidden="true" />
      <span>Telemetry powered by MQTT · Firestore</span>
    </footer>
  </div>
</template>

<style>
/* ---------- Global-ish base (NO scoped) ---------- */
:root {
  --bg-0: #05060b;
  --bg-1: #070a12;
  --panel: rgba(10, 12, 20, 0.55);
  --panel-2: rgba(12, 14, 24, 0.7);
  --border: rgba(255, 255, 255, 0.10);
  --border-2: rgba(255, 255, 255, 0.06);
  --text: rgba(255, 255, 255, 0.92);
  --muted: rgba(255, 255, 255, 0.64);
  --muted2: rgba(255, 255, 255, 0.48);
  --shadow: 0 12px 40px rgba(0, 0, 0, 0.45);
  --radius: 16px;
}

/* full screen background lives here */
html,
body,
#app {
  height: 100%;
}

body {
  margin: 0;
  color: var(--text);
  background:
    radial-gradient(1200px 620px at 20% -10%, rgba(90, 120, 255, 0.18), transparent 60%),
    radial-gradient(920px 520px at 80% 0%, rgba(0, 220, 180, 0.10), transparent 55%),
    linear-gradient(180deg, var(--bg-1) 0%, var(--bg-0) 100%);
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial,
    "Apple Color Emoji", "Segoe UI Emoji";
}

* {
  box-sizing: border-box;
}

a {
  color: inherit;
}

/* ---------- App shell ---------- */
.app {
  height: 100vh;     /* ✅ min-height 말고 height로 고정 */
  min-height: 0;     /* ✅ flex 자식 스크롤 필수 */
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* ornaments */
.bg-orb {
  position: absolute;
  width: 760px;
  height: 760px;
  border-radius: 999px;
  filter: blur(42px);
  opacity: 0.85;
  pointer-events: none;
  mix-blend-mode: screen;
}

.orb-a {
  left: -220px;
  top: -260px;
  background: radial-gradient(circle at 30% 30%, rgba(120, 130, 255, 0.50), transparent 60%);
}

.orb-b {
  right: -260px;
  top: -260px;
  background: radial-gradient(circle at 60% 30%, rgba(0, 220, 180, 0.35), transparent 60%);
}

.bg-noise {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.055;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='120' height='120' filter='url(%23n)' opacity='.35'/%3E%3C/svg%3E");
}

/* ---------- Topbar ---------- */
.topbar {
  position: sticky;
  top: 0;
  z-index: 50;

  display: flex;
  align-items: center;
  justify-content: space-between;

  padding: 14px 26px;

  background: var(--panel);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-2);
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 280px;
}

.brand-mark {
  width: 14px;
  height: 14px;
  border-radius: 6px;
  background: linear-gradient(135deg, rgba(120, 130, 255, 0.95), rgba(0, 220, 180, 0.75));
  box-shadow: 0 0 0 4px rgba(255, 255, 255, 0.04);
}

.brand-title {
  font-weight: 800;
  letter-spacing: 0.2px;
  font-size: 14px;
  line-height: 1.1;
}

.brand-sub {
  margin-top: 2px;
  font-size: 12px;
  color: var(--muted2);
}

/* ---------- Nav ---------- */
.nav {
  position: relative;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px;
  border: 1px solid var(--border-2);
  border-radius: 999px;
  background: rgba(8, 10, 16, 0.45);
}

.nav-link {
  position: relative;
  padding: 8px 12px;
  border-radius: 999px;
  font-size: 13px;
  text-decoration: none;
  color: var(--muted);
  transition: background 120ms ease, color 120ms ease, transform 120ms ease;
}

.nav-link:hover {
  color: rgba(255, 255, 255, 0.86);
  background: rgba(255, 255, 255, 0.06);
}

.nav-link.router-link-active {
  color: rgba(255, 255, 255, 0.95);
}

/* little underline for active tab (pure CSS, simple) */
.nav-link.router-link-active::after {
  content: "";
  position: absolute;
  left: 12px;
  right: 12px;
  bottom: 6px;
  height: 2px;
  border-radius: 2px;
  background: linear-gradient(90deg, rgba(120, 130, 255, 0.95), rgba(0, 220, 180, 0.75));
  opacity: 0.9;
}

/* ---------- Page ---------- */
.page {
  flex: 1;
  min-height: 0;
  overflow: hidden;

  position: relative;
  z-index: 1;

  /* padding은 page-inner로 옮김 */
  padding: 0;
  
}

.page-inner{
  height: 100%;
  min-height: 0;
  overflow: hidden;

  padding: 22px 28px 22px;
}

/* ---------- Footer ---------- */
.footer {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 10px;

  padding: 14px 26px;
  color: var(--muted2);
  border-top: 1px solid var(--border-2);
  background: rgba(8, 10, 16, 0.35);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.footer-dot {
  width: 8px;
  height: 8px;
  border-radius: 99px;
  background: rgba(0, 220, 180, 0.75);
  box-shadow: 0 0 0 4px rgba(0, 220, 180, 0.10);
}

/* ---------- Small screen ---------- */
@media (max-width: 780px) {
  .topbar {
    padding: 12px 14px;
    gap: 10px;
  }
  .brand {
    min-width: auto;
  }
  .brand-sub {
    display: none;
  }
  .page {
    padding: 16px 14px 28px;
  }
}
</style>
