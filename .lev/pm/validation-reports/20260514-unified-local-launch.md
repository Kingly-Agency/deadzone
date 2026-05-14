---
type: validation-report
created: 2026-05-14T12:34:00-07:00
updated: 2026-05-14T12:34:00-07:00
status: validated
domain: product
confidence: 0.95
author: gpt-5.5
related_tasks: []
related_docs:
  - .lev/pm/workstreams/deadzone-mvp/state/workstream.yaml
related_specs:
  - .lev/pm/specs/deadzone-api-contract.yaml
gate_ids:
  - deadzone_servers_stopped
  - unified_launch_smoke
  - backend_mode_contract
  - frontend_build
---

# Validation Report: Unified Local Launch

## Executive Summary

Validated a repo-root `npm run dev` launch command for the local DeadZone stack. The smoke run started backend and frontend, served `/` with `200 OK`, returned config with `active_mode: "ble"` and `available_modes: ["ble", "mock"]`, then the smoke servers were stopped.

## Validation Results

| Requirement | Gate ID | Status | Evidence | Notes |
|-------------|---------|--------|----------|-------|
| Existing local DeadZone servers stopped | deadzone_servers_stopped | PASS | `lsof -nP -iTCP -sTCP:LISTEN` filtered for `3000`, `8000`, `8001`, `8011`, `8021` | No DeadZone listeners remained after cleanup. |
| Unified command starts local stack | unified_launch_smoke | PASS | `DEADZONE_DEV_NO_MACOS_BLUETOOTH_APP=1 npm run dev` | Frontend started after backend health passed. |
| BLE/live default and only BLE/MOCK exposed | backend_mode_contract | PASS | `pytest tests/test_contract_shapes.py tests/test_trace_replay_mock.py tests/test_adapter_modes.py` | 13 focused backend tests passed. |
| Frontend remains valid | frontend_build | PASS | `npm run typecheck && npm run build` in `frontend/` | TypeScript and Vite production build passed. |

## Detailed Evidence

### Backend Tests

```text
tests/test_contract_shapes.py .. 
tests/test_trace_replay_mock.py ......
tests/test_adapter_modes.py .....
13 passed
```

### Frontend Checks

```text
> deadzone-frontend@0.1.0 typecheck
> tsc -b --noEmit

> deadzone-frontend@0.1.0 build
> tsc -b && vite build

✓ 46 modules transformed.
✓ built in 303ms
```

### Smoke Test

```text
GET http://127.0.0.1:3000/ -> 200 OK
GET http://127.0.0.1:3000/api/v1/config -> active_mode "ble", available_modes ["ble", "mock"]
```

## Gaps

- The smoke test used `DEADZONE_DEV_NO_MACOS_BLUETOOTH_APP=1` to avoid launching the macOS Bluetooth permission app during automated verification. The user-facing `npm run dev` command uses the normal permission launcher path by default.
- No commit or push was performed because the user did not explicitly request it.

## Validation Decision

- [x] Validated
- [ ] Needs follow-up plan
- [ ] Needs spec update
- [ ] Needs design revision
