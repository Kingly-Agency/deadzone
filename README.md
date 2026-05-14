<div align="center">
  <h1>🎯 DeadZone</h1>
  <p><strong>Real-time crowd-intelligence platform. Mock → Replay → Live → Mesh.</strong></p>
  
  <p>
    <a href="#features">Features</a> •
    <a href="#architecture">Architecture</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#engineering-principles">Principles</a>
  </p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.11+-blue.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
    <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React">
    <img src="https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript">
    <img src="https://img.shields.io/badge/Vite-B73BFE?style=for-the-badge&logo=vite&logoColor=FFD62E" alt="Vite">
  </p>
</div>

<br/>

> **DeadZone** is an observability layer for physical spaces. Live crowd density, movement flow, congestion zones, and dead Wi-Fi areas — without attendee apps, accounts, QR codes, or interaction. Passive RF sensing only.

---

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| 🗺️ **Spatial Intelligence** | Real-time visual heatmaps and drifting device-level particles overlaid on venue floor plans. |
| 🔄 **Multi-Mode Engine** | Operate seamlessly across `Mock`, `Replay`, `Live (BLE)`, and `Mesh` data sources. |
| 📡 **Live Telemetry** | Granular observation of sensed MAC hashes, RSSI values, and zone assignments via WebSockets. |
| 🚨 **Alerting & Diagnostics** | Automated alerts based on density thresholds and real-time mesh link quality. |

---

## 🏗️ Architecture

DeadZone is built on a modern, decoupled architecture designed for high throughput and low-latency rendering of spatial data.

### System Topology

```mermaid
graph TD
    %% Styling
    classDef source fill:#f9f9f9,stroke:#333,stroke-width:2px,color:#000;
    classDef engine fill:#e1f5fe,stroke:#0288d1,stroke-width:2px,color:#000;
    classDef ui fill:#f3e5f5,stroke:#8e24aa,stroke-width:2px,color:#000;
    classDef ws fill:#fff8e1,stroke:#ffa000,stroke-width:2px,stroke-dasharray: 5 5,color:#000;

    %% Nodes
    subgraph Edge["📡 Data Sources (Edge)"]
        S1["📶 BLE Scanner"]:::source
        S2["🛜 Scapy Wi-Fi"]:::source
        S3["🕸️ Meshtastic LoRa"]:::source
    end

    subgraph Core["⚙️ FastAPI Engine (Core)"]
        E1("🔀 Data Ingestion Router"):::engine
        E2{"🎛️ Mode Controller"}:::engine
        E3[("💾 Local Trace Records")]:::engine
        M["🪄 Mock Generator"]:::engine
        
        E1 --> E2
        E3 -.->|Replay Mode| E2
        M -.->|Mock Mode| E2
    end

    subgraph Client["💻 React Frontend (Client)"]
        UI1["🗺️ Spatial Map Canvas"]:::ui
        UI2["📋 Device Event Table"]:::ui
        UI3["📊 Metrics Dashboard"]:::ui
    end

    %% Connections
    S1 -->|Raw Telemetry| E1
    S2 -->|Raw Telemetry| E1
    S3 -->|Mesh Packets| E1
    
    E2 -->|Processed Events| WS(("⚡ WebSocket Stream")):::ws
    
    WS ===>|JSON Payloads| UI1
    WS ===>|JSON Payloads| UI2
    WS ===>|JSON Payloads| UI3
```

### Data Flow Sequence

How a device ping is processed and visualized in real-time:

```mermaid
sequenceDiagram
    participant Device as 📱 Attendee Device
    participant Scanner as 📡 Edge Scanner
    participant Engine as ⚙️ FastAPI Engine
    participant WS as 🔌 WebSocket
    participant UI as 💻 Frontend Map

    Device-->>Scanner: Broadcasts BLE/Wi-Fi Probe
    Scanner->>Engine: Raw Telemetry (MAC Hash, RSSI)
    
    rect rgb(240, 248, 255)
        note right of Engine: Processing Phase
        Engine->>Engine: Anonymize & Hash MAC
        Engine->>Engine: Calculate distance via RSSI
        Engine->>Engine: Assign to spatial zone
    end
    
    Engine->>WS: Emit formatted `DeviceEvent`
    WS->>UI: Broadcast JSON payload
    
    rect rgb(255, 240, 245)
        note right of UI: Rendering Phase
        UI->>UI: Update spatial particle state
        UI->>UI: Recalculate heatmap density
        UI->>UI: Trigger UI animations
    end
```

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

Run the entire stack with a single command:

```bash
docker compose up
```

Then open `http://localhost:3000`. You should see an animated crowd heatmap with a badge indicating the current data mode (Mock by default).

### Option 2: Local Development

If you prefer to run the components separately or work on the codebase:

```bash
# Install all dependencies (frontend & backend)
npm run install:all

# Start both frontend (Vite) and backend (FastAPI) in development mode
npm run dev
```

---

## 🧠 Engineering Principles

We adhere strictly to the following principles to ensure reliability and privacy:

```mermaid
mindmap
  root((Principles))
    Deterministic First
      Stable demos
      Repeatable outputs
    Privacy by Design
      Aggregate over Identity
      Never transmit raw MACs
      No persistent tracking
    Event-Driven Core
      Single data pipeline
      Reusable across modes
    Honest Provenance
      Clear mode indicators
      No hidden simulation
```

---

## 📂 Repository Structure

| Directory | Description | Technology Stack |
| :--- | :--- | :--- |
| 📁 `backend/` | FastAPI application, domain models, runtime engine, and data sources. | Python 3.11, asyncio, Bleak |
| 📁 `frontend/` | React components, state management, and spatial SVG rendering. | React, TypeScript, Vite |
| 📁 `.lev/` | Project management specifications, task plans, and UX artifacts. | Markdown |

---

<div align="center">
  <p><small>Proprietary — Kingly Agency © 2026</small></p>
</div>
