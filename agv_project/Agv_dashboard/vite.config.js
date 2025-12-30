import { fileURLToPath, URL } from "node:url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
// import vueDevTools from "vite-plugin-vue-devtools";

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },

  // ✅ 추가: dev 서버 설정 + /api 프록시
  server: {
    host: true,
    port: 5173,

    // ✅ Cloudflare trycloudflare 도메인 허용 (둘 중 하나 선택)
    allowedHosts: [
      "muscles-arising-operation-timely.trycloudflare.com",
      ".trycloudflare.com", // 이 줄까지 넣으면 다음번 URL 바뀌어도 OK
    ],

    proxy: {
      "/api": {
        target: "http://127.0.0.1:1880",
        changeOrigin: true,
      },
    },
  },
});
