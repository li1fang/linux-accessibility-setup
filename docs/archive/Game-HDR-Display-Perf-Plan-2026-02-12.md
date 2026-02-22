# Game HDR + Display + Performance Plan (2026-02-12)

## Objective
Get a stable, repeatable "best display" Linux setup for gaming on RTX 4090 + LG C5 (HDMI 2.1), with:
- HDR working in games (starting with Cyberpunk 2077)
- Smooth frame pacing (no flicker/stutter)
- Correct refresh rate and VRR behavior
- A short verification checklist so upgrades don’t break the setup silently

Non-goal (for now): HDR video playback in web browsers (YouTube HDR).
- Decision recorded in `HDR-Browser-Postmortem-2026-02-12.md`.

## Current Baseline (Known Good)
- OS: Ubuntu 25.10 (questing)
- Kernel: 6.17.0-14-generic
- Desktop: KDE Plasma 6.4.5, KWin 6.4.5
- Session: Wayland
- GPU driver: NVIDIA 590.48.01
- Display output: HDMI-A-1, 3840x2160@144
- System HDR: enabled in KDE (verified via `kscreen-doctor -o`)

## Workstreams

### 1) Display Stack Baseline (Lock it down)
Goal: Ensure the OS-level output mode and HDR/WCG configuration is correct and stays consistent.

Tasks
- Confirm and set preferred mode (e.g., 3840x2160@120 or @144) and scaling.
- Decide VRR policy (KDE shows `Vrr: Never` currently):
  - Option A: VRR "Automatic" / "Always" (preferred for gaming)
  - Option B: VRR off (if it causes instability)
- Confirm HDR settings:
  - HDR enabled
  - SDR brightness mapping: choose a stable value (e.g., 200 nits)
  - Peak brightness override: set appropriately for LG C5

Acceptance
- `kscreen-doctor -o` shows:
  - correct resolution/refresh
  - HDR: enabled
  - WCG: enabled
  - VRR policy matches chosen setting

Rollback
- If any flicker/stutter returns: turn VRR off first, then reduce refresh (e.g., 120 -> 60) to isolate.


### 2) NVIDIA / DRM / Wayland Reliability
Goal: Avoid fallback render paths, keep presentation stable.

Tasks
- Confirm NVIDIA DRM driver is in use and stable.
- Confirm the active connector exposes HDR metadata properties.
- Keep changes minimal: prefer compositor settings over kernel params.

Acceptance
- No recurring flicker/stutter in common scenarios (browser full-screen video, desktop animations).
- No failed services; `systemctl --failed` is empty.

Rollback
- Revert only the last changed knob (VRR policy, compositor setting, launch flags).


### 3) Steam + Proton HDR Path (Core)
Goal: Cyberpunk 2077 shows HDR options and outputs HDR correctly.

Inputs needed (from user)
- Cyberpunk 2077 Steam Launch Options (current)
- Proton version (official vs Proton-GE)
- Target mode (choose one):
  - 4K60 HDR
  - 4K120 HDR
  - 4K144 SDR (HDR optional / per-title)

Approach
- Prefer a known-stable HDR path:
  - Option A (recommended): `gamescope` HDR
  - Option B: "native" Proton HDR (if stable on this stack)

Tasks
- Install/verify `gamescope` availability.
- Set per-game launch options for 2077:
  - enable Wayland for Proton
  - enable HDR env flags
  - optional: enforce refresh / fullscreen / tearing policy
- Validate in-game:
  - HDR toggle appears in graphics settings
  - TV/OSD indicates HDR mode
  - Visual check: highlight roll-off / tone mapping behaves as expected

Acceptance
- HDR option is available and functional inside Cyberpunk 2077.
- No major stutter or frame pacing regressions compared to SDR.

Rollback
- Remove gamescope/proton env flags and return to baseline SDR launch.


### 4) Performance Tuning (After HDR Works)
Goal: Stable frame pacing and sensible settings.

Tasks
- Choose FPS cap strategy:
  - in-game cap vs driver cap vs gamescope cap
- Enable and verify VRR behavior in games.
- Add optional tooling:
  - MangoHud for metrics
  - Gamemode (optional)

Acceptance
- Stable frame time graph under load.
- No compositor-induced stutter.

Rollback
- Remove overlays/caps first.


### 5) Verification Checklist (10-minute health check)
Goal: After any update (kernel, driver, Plasma), verify quickly.

Checklist
- Display:
  - `kscreen-doctor -o` shows expected mode + HDR enabled
- GPU:
  - `nvidia-smi` shows correct driver and active display
- Steam:
  - 2077 launches
  - HDR option present
- Visual:
  - no flicker/stutter in desktop and game


## Next Step (Immediate)
Collect the missing inputs for Workstream 3:
- 2077 Steam launch options (current)
- Proton version in use
- Desired target (4K60 HDR / 4K120 HDR / other)


## Update (2026-02-13)
Root cause for intermittent black screen is now confirmed as VRR/Adaptive Sync path instability in current stack.

Policy update:
- Keep VRR disabled (`Never`) as the stable baseline.
- Do not enable Adaptive Sync "Always" in current environment.
- Continue HDR/perf tuning only on top of VRR-off baseline.

## Update (2026-02-13, VRR threshold finding)
New finding refines the root cause:
- VRR instability is tied to **global output refresh above ~120Hz**.
- Per-game FPS cap alone is insufficient.
- Stable VRR baseline requires system-level refresh at ~119.88Hz.

Plan adjustment:
- If VRR is required, set system refresh to 119.88Hz first.
- Keep 144Hz as desktop profile only (non-VRR or accepted risk).
- Add future automation task: game-mode script for profile switching.
