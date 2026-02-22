# HDR In Browser Postmortem (2026-02-12)

## Goal
Enable and use HDR video playback in a web browser (primarily YouTube) on Linux.

## Hardware
- GPU: NVIDIA GeForce RTX 4090
- Driver: NVIDIA 590.48.01
- Display: LG C5 55 (OLED)
- Connection: HDMI 2.1

## OS / Desktop
- OS: Ubuntu 25.10 (questing)
- Kernel: 6.17.0-14-generic
- Session: Wayland
- Desktop: KDE Plasma 6.4.5
- Compositor: KWin 6.4.5

## System-Level HDR Status (Working)
We verified HDR is enabled and supported end-to-end at the OS/display stack level.

Evidence:
- DRM/KMS exposes HDR capabilities on the active connector (HDMI-A-1):
  - `HDR_OUTPUT_METADATA` property exists
  - `Colorspace` supports BT2020
  - `vrr_capable=1` is also present (not directly related to HDR)
- KDE output state shows HDR enabled:
  - `kscreen-doctor -o` reports:
    - Output: HDMI-A-1
    - HDR: enabled
    - Wide Color Gamut: enabled
    - Peak brightness: 2000 nits (override set to 2000 nits)
    - SDR brightness: 200 nits

## Browser Situation
### Observed problem
- YouTube HDR option is not available during playback.
- "Stats for nerds" confirms YouTube delivers SDR video streams:
  - Codecs: `vp09.00...` (VP9 Profile 0, SDR)
  - Color: `bt709 / bt709` (SDR)

Even when the YouTube UI indicates an HDR video ("4K HDR" label), the actual stream
remains SDR according to the codec/color fields.

### Browsers tested
- Brave (deb) via custom launchers
- Brave (snap) (removed later)
- Chromium (snap)
- Google Chrome (deb) (kept installed but hidden; was unreliable)
- Firefox (no HDR option observed either)

## Key Diagnostics
### Network / TLS not the issue
- `curl -4 -I https://example.com` succeeded (HTTP/2 200)
- `openssl s_client` to example.com verified TLS OK

### HDR decode capability is present (not the blocker)
Installed and verified VA-API/NVDEC support:
- Packages installed:
  - `nvidia-vaapi-driver`
  - `vainfo`
- `vainfo` (Wayland display) reports NVDEC VA-API driver and supports HDR-relevant profiles:
  - `VAProfileVP9Profile2` (YouTube HDR commonly uses VP9 Profile 2)
  - `VAProfileHEVCMain10`
  - `VAProfileAV1Profile0`

This indicates the machine can decode HDR-capable formats.

## Methods Attempted
### 1) Brave "Safe" launcher (stable browsing)
A stable launcher was created to make web browsing reliable:
- `Brave Browser (Safe)`
- Included `--disable-gpu` to avoid graphics/DRM issues seen with snap-based builds.

Result:
- Browsing works.
- HDR in YouTube not available (expected: software rendering path typically prevents HDR pipeline).

### 2) Brave HDR test launcher (GPU enabled)
Created a launcher without `--disable-gpu`:
- `Brave Browser (HDR Test)`

Result:
- Browsing works.
- YouTube still delivers SDR streams (`vp09.00`, `bt709`).

### 3) Brave VA-API / NVDEC enablement
Created a launcher with VA-API/NVDEC related env/flags:
- `Brave Browser (HDR/VAAPI)`
- Key settings:
  - `LIBVA_DRIVER_NAME=nvidia`
  - `NVD_BACKEND=direct`
  - `--enable-features=VaapiVideoDecoder`
  - `--ignore-gpu-blocklist`
  - `--enable-zero-copy`
  - `--use-gl=egl`

Result:
- Browsing works.
- YouTube still delivers SDR streams (`vp09.00`, `bt709`).

### 4) Firefox check
- No YouTube HDR option observed.

## Why We Stopped (Conclusion)
- The OS/driver/display stack clearly supports HDR and HDR metadata.
- Hardware decode capability for HDR-relevant formats exists.
- Despite that, YouTube does not provide HDR streams to the browser in this environment
  (confirmed repeatedly via "Stats for nerds" showing SDR codec/profile and bt709 color).

Given the time cost and diminishing returns, we decided to stop pursuing web browser HDR
video playback (YouTube HDR) on this Linux setup for now.

## What Still Makes Sense
- Focus HDR efforts on native/Steam gaming (e.g., Cyberpunk 2077) where HDR enablement
  depends more on Proton/gamescope/HDR runtime path than on YouTube/browser policies.

## Notes / Cleanup Performed
- Removed snap Brave to reduce confusion and avoid snap DRM/AppArmor graphics issues.
- Hid extra browser desktop entries so only the known-good launcher remains visible.

