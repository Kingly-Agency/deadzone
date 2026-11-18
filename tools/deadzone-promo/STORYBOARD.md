# STORYBOARD

## Scene 1 (0:00–0:04) — Hook
Hero frame: giant uppercase "WHEN A CROWD GETS DANGEROUS," in `.display-xl` (80px / 700) centered-left on pure black. Sub "every second of warning matters." in body 300/24px below. Tiny 4px M-stripe top-left corner.
Entrance: words stagger in 0.08s apart, slide up 20px from below, fade in (`power3.out`).
Transition out: `flash-through-white` into Scene 2.

## Scene 2 (0:04–0:08) — Brand
Hero frame: full-width 4px M-tricolor stripe centered vertically; "DEADZONE" wordmark in 120px display below; "Live crowd intelligence." in body 300/20px under that.
Entrance: stripe draws left→right over 0.6s; wordmark fades up; sub fades in.
Transition out: stripe expands to fill screen → wipe to black for Scene 3.

## Scene 3 (0:08–0:14) — Dashboard
Hero frame: full-bleed dashboard screenshot, slow Ken Burns zoom (1.0 → 1.06 over 6s). Caption pill top-right corner: "LIVE BLE  /  4 ZONES  /  4 ACTIVE ALERTS" in label-uppercase 16px / 1.5px tracking, white text on transparent border. Sub at bottom: "Bluetooth signals → zone density → alerts. In real time."
Entrance: image fades in + scales from 1.02 to 1.0 (0.6s); pill fades in 0.4s late; sub fades in 1s late.
Transition out: blur crossfade into Scene 4.

## Scene 4 (0:14–0:20) — Heatmap
Hero frame: heatmap screenshot, horizontal pan from left to right (translateX -40px → 0). Caption top-left: "DENSITY REDSHIFT" in display-md (40px / 700 / uppercase). Sub below: "Cool zones fade. Hot zones glow red."
Entrance: image slides in from right; caption + sub stagger in.
Transition out: `flash-through-white` into Scene 5.

## Scene 5 (0:20–0:24) — Promise
Hero frame: three label-uppercase lines stacked, each ~32px / 700 / uppercase / 1.5px tracking:
  - BLE-FIRST.
  - MESH-READY.
  - PRIVACY-PRESERVING.
Black canvas, M-red 2px underline animates across each line as it appears.
Entrance: each line slides up 30px + fades in, 0.4s apart. Underline draws left-to-right 0.3s after line.
Transition out: blur fade into Scene 6.

## Scene 6 (0:24–0:28) — Sign-off
Hero frame: M-tricolor stripe redraws (4px). Wordmark "DEADZONE" below in display 80px. URL "github.com/Kingly-Agency/deadzone" in body 300/16px.
Entrance: stripe draws L→R 0.5s; wordmark fades up; URL fades in.
Exit: whole composition fades to black over the last 0.5s.
