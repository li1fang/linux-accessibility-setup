# Accessibility Package / 无障碍工具包

## 中文

这是一个面向 Linux 桌面用户的无障碍与低摩擦操作工具包，目标是：
- 降低命令行交互门槛（自动确认、输入辅助、菜单化入口）
- 提供稳定的桌面体验模块（例如安静黑色屏保）

### 功能清单
- `autoyes`：自动回答 yes
- `autoinput`：向命令注入固定输入
- `autoexpect`：自动处理常见交互提示
- `auto-sudo`：sudo 辅助封装
- `auto-ssh`：SSH 连接交互辅助
- `easy-menu`：dialog 菜单化系统操作
- `qbsctl`：安静黑色屏保控制工具（user systemd）

### 安装
```bash
cd accessibility-package
sudo ./install.sh
```

### 安静黑色屏保（推荐模块）
用于 KDE Wayland + HDMI 电视场景，避免“无信号幻灯片”：
- 闲置后纯黑覆盖层
- 不断 HDMI 信号
- 默认不锁屏（可配置）

快速使用：
```bash
qbsctl install
qbsctl enable
qbsctl doctor
qbsctl doctor --json
qbsctl enable --fix
```

文档：
- `modules/quiet-black-screensaver/docs/README.zh-CN.md`
- `modules/quiet-black-screensaver/docs/TROUBLESHOOTING.zh-CN.md`
- `modules/quiet-black-screensaver/docs/SECURITY-NOTES.zh-CN.md`

### 脚本质量与风险
详见：`docs-script-quality.zh-CN.md`

要点：
- 已修复旧版硬编码路径问题（`/home/whipc/...`）
- `auto-sudo` / `easy-menu` 涉及高权限操作，需谨慎
- `expect`、`dialog` 为关键依赖

---

## English

A Linux accessibility and low-friction operations package for desktop usage.

### Included tools
- `autoyes`: auto-answer yes prompts
- `autoinput`: pipe predefined input into commands
- `autoexpect`: handle interactive prompts
- `auto-sudo`: sudo helper wrapper
- `auto-ssh`: SSH interaction helper
- `easy-menu`: dialog-based operations menu
- `qbsctl`: quiet black screensaver controller (user systemd)

### Install
```bash
cd accessibility-package
sudo ./install.sh
```

### Quiet Black Screensaver
Designed for KDE Wayland + HDMI TV workflows:
- Pure black idle overlay
- Keep HDMI signal alive
- No lock by default (configurable)

Quick start:
```bash
qbsctl install
qbsctl enable
qbsctl doctor
qbsctl doctor --json
qbsctl enable --fix
```

Related docs:
- `modules/quiet-black-screensaver/docs/README.zh-CN.md`
- `modules/quiet-black-screensaver/docs/TROUBLESHOOTING.zh-CN.md`
- `modules/quiet-black-screensaver/docs/SECURITY-NOTES.zh-CN.md`
