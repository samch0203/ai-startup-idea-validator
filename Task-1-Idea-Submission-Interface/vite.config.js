import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

// In dev, requests to /validate and /api/... are forwarded to the backend, so the
// browser never makes a cross-origin call and you don't need CORS set up.
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const target = env.VITE_PROXY_TARGET || "http://localhost:8000";
  // Task 3's web search server runs separately (default port 8001).
  const searchTarget = env.VITE_SEARCH_PROXY_TARGET || "http://localhost:8001";

  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        // The more specific path must come first.
        "/api/web-search": { target: searchTarget, changeOrigin: true },
        "/validate": { target, changeOrigin: true },
        "/api": { target, changeOrigin: true },
      },
    },
  };
});
