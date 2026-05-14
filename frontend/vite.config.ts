import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
    proxy: {
      "/ws": { target: "ws://localhost:8000", ws: true, changeOrigin: true },
      "/health": { target: "http://localhost:8000", changeOrigin: true },
      "/api": { target: "http://localhost:8000", changeOrigin: true },
      "/mesh": { target: "http://localhost:8001", changeOrigin: true, ws: false },
    },
  },
});
