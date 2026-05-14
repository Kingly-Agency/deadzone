# DeadZone Frontend

Vite + React + TypeScript + Leaflet + Heatmap.js. Renders a single-screen dashboard with persistent mode badge, headline metrics, density bars (placeholder for Leaflet floorplan + Heatmap.js layer), and alerts rail.

## Run

```bash
# from this directory
npm install
npm run dev
```

Or from the repo root:

```bash
docker compose up frontend
```

Then open <http://localhost:3000>.

## Architecture Notes

- WebSocket to `/ws/events` (proxied to `backend:8000` in dev/docker)
- ModeChip + ProvenanceBadge are persistent and color-coded per the constraint bundle (`.lev/ux/.../constraint_bundle.yaml`)
- HeatmapLayer requires Legend by composition rule — currently a density-bar placeholder; replace with Leaflet + Heatmap.js when floorplan PNG/SVG arrives
- AlertsPanel has a non-empty zero state per LC-3

## Next

See `.lev/pm/specs/deadzone-frontend-partner-brief.yaml` for the contracted FE scope.
