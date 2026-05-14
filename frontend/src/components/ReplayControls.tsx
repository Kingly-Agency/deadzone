import { useState, useEffect, useCallback } from "react";
import { useStore } from "../store";
import { api } from "../api";
import type { ReplayScenario } from "../types";

function formatTime(s: number): string {
  const m = Math.floor(s / 60);
  const sec = Math.floor(s % 60);
  return `${m}:${sec.toString().padStart(2, "0")}`;
}

const SPEEDS = [0.25, 0.5, 1, 2, 4];

export function ReplayControls() {
  const { snapshot } = useStore();
  const [scenarios, setScenarios] = useState<ReplayScenario[]>([]);
  const [activeScenario, setActiveScenario] = useState<string | null>(null);
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(1);

  const isReplay = snapshot?.stream.mode === "replay";
  const position = snapshot?.stream.clock.replay_position_s ?? 0;
  const duration = scenarios.find((s) => s.id === activeScenario)?.duration_s ?? 1;

  useEffect(() => {
    if (isReplay) {
      api.replayScenarios().then(setScenarios).catch(() => {});
    }
  }, [isReplay]);

  const loadScenario = useCallback(async (id: string) => {
    await api.replayControl({ action: "load", scenario_id: id });
    setActiveScenario(id);
    setPlaying(false);
  }, []);

  const togglePlay = useCallback(async () => {
    if (playing) {
      await api.replayControl({ action: "pause" });
      setPlaying(false);
    } else {
      await api.replayControl({ action: "play" });
      setPlaying(true);
    }
  }, [playing]);

  const restart = useCallback(async () => {
    await api.replayControl({ action: "restart" });
    setPlaying(true);
  }, []);

  const changeSpeed = useCallback(async (s: number) => {
    await api.replayControl({ action: "set_speed", speed: s });
    setSpeed(s);
  }, []);

  const seek = useCallback(async (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const pct = (e.clientX - rect.left) / rect.width;
    const pos = pct * duration;
    await api.replayControl({ action: "seek", position_s: pos });
  }, [duration]);

  if (!isReplay) return null;

  const progress = duration > 0 ? (position / duration) * 100 : 0;

  return (
    <div className="replay-bar">
      {!activeScenario && (
        <>
          <div className="replay-header">
            <span>Choose a Scenario to Replay</span>
          </div>
          <div className="scenario-picker">
            {scenarios.map((sc) => (
              <div
                key={sc.id}
                className={`scenario-card ${activeScenario === sc.id ? "active" : ""}`}
                onClick={() => loadScenario(sc.id)}
              >
                <div className="scenario-name">{sc.name}</div>
                <div className="scenario-desc">{sc.description}</div>
                <div className="scenario-meta">Duration: {formatTime(sc.duration_s)}</div>
              </div>
            ))}
          </div>
        </>
      )}

      {activeScenario && (
        <>
          <div className="replay-header">
            <span>Replaying: {scenarios.find((s) => s.id === activeScenario)?.name}</span>
            <span className="replay-time">{formatTime(position)} / {formatTime(duration)}</span>
          </div>
          <div className="replay-controls">
            <button className="replay-btn primary" onClick={togglePlay}>
              {playing ? "❚❚ Pause" : "▶ Play"}
            </button>
            <button className="replay-btn" onClick={restart}>↺ Restart</button>

            <div className="scrubber" onClick={seek}>
              <div className="scrubber-fill" style={{ width: `${progress}%` }} />
              <div className="scrubber-thumb" style={{ left: `${progress}%` }} />
            </div>

            <div className="speed-selector">
              {SPEEDS.map((s) => (
                <button
                  key={s}
                  className={`speed-btn ${speed === s ? "active" : ""}`}
                  onClick={() => changeSpeed(s)}
                >
                  {s}x
                </button>
              ))}
            </div>

            <button
              className="replay-btn"
              onClick={() => { setActiveScenario(null); setPlaying(false); }}
            >
              ◼ Stop
            </button>
          </div>
        </>
      )}
    </div>
  );
}
