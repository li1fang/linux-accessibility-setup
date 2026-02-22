# Linux Accessibility Setup / Linux 无障碍与稳定性工具集

## 中文
这是一个围绕 Linux 桌面可用性与无障碍体验的实践仓库，重点包括：

- 安静黑色屏保（KDE Wayland，保持 HDMI 信号，不锁屏）
- 命令行辅助脚本（自动确认、交互辅助、菜单化操作）
- 系统问题复盘（HDR/VRR 等高复杂度主题）

### 当前状态
- 已产品化模块：`accessibility-package/modules/quiet-black-screensaver`
- HDR/VRR 阶段结论：见 `docs/decisions/hdr-vrr-conclusion.md`

### 快速入口
- 主包说明：`accessibility-package/README.md`
- 使用指南：`accessibility-package/指南.md`
- 黑色屏保文档：`accessibility-package/modules/quiet-black-screensaver/docs/README.zh-CN.md`

### 脚本质量简评（`accessibility-package/scripts/`）
- `autoyes.sh`：可用，简单稳定。
- `autoinput.sh`：可用，简单稳定。
- `autoexpect.exp`：可用但策略激进（自动回答 yes），适合受控场景。
- `auto-ssh.exp`：可用但不建议长期密码模式，推荐 SSH key。
- `auto-sudo.sh`：已修正硬编码路径，依赖 `autoexpect`。
- `easy-menu.sh`：已修正硬编码路径，仍属高权限操作入口，建议谨慎使用。

## English
This repository focuses on practical Linux accessibility and usability workflows:

- Quiet black screensaver for KDE Wayland (keep HDMI signal alive, no lock by default)
- CLI helper scripts for reduced interactive friction
- Incident notes and technical conclusions (e.g., HDR/VRR experiments)

### Current status
- Productized module: `accessibility-package/modules/quiet-black-screensaver`
- HDR/VRR conclusion: `docs/decisions/hdr-vrr-conclusion.md`

### Entry points
- Package overview: `accessibility-package/README.md`
- User guide: `accessibility-package/指南.md`
- Screensaver docs: `accessibility-package/modules/quiet-black-screensaver/docs/README.zh-CN.md`

### Script quality notes
Most scripts are usable for personal environments. For public usage, strongly document risk boundaries, especially for elevated operations and auto-confirm behaviors.
