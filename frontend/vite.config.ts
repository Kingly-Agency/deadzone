import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const apiTarget = process.env.VITE_API_TARGET ?? "http://127.0.0.1:8000";
const wsTarget = apiTarget.replace(/^http/, "ws");

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
    proxy: {
      "/ws": { target: wsTarget, ws: true, changeOrigin: true },
      "/healthz": { target: apiTarget, changeOrigin: true },
      "/health": { target: apiTarget, changeOrigin: true },
      "/modes": { target: apiTarget, changeOrigin: true },
      "/api": { target: apiTarget, changeOrigin: true },
    },
  },
});
