# 安静黑色屏保（Quiet Black Screensaver）

## 适用场景
- KDE Plasma Wayland + HDMI 电视（例如 LG OLED）
- 需要闲置后进入纯黑，但不希望丢失 HDMI 信号
- 不希望系统自动锁屏（默认策略）

## 核心机制
- 不是 DPMS 关屏，不是休眠
- 通过全屏黑色覆盖层模拟“熄屏”
- 任意键鼠输入立即恢复

## 快速开始
```bash
qbsctl install
qbsctl enable
qbsctl status
```

## 常用命令
- `qbsctl logs` 查看日志
- `qbsctl doctor` 检查冲突项（锁屏/电源策略/service）
- `qbsctl doctor --json` 输出机器可读诊断 JSON
- `qbsctl enable --fix` 启用前自动修复常见冲突（锁屏 + DPMS/Suspend）
- `qbsctl disable` 停用
- `qbsctl uninstall` 卸载（保留配置与日志）
- `qbsctl uninstall --purge` 彻底清理

## 配置文件
路径：`~/.config/quiet-black-screensaver/config.env`

默认关键项：
- `QBS_IDLE_SECONDS=600`
- `QBS_LOCK_SCREEN=0`
- `QBS_INHIBIT_SCREENSAVER=1`
- `QBS_POWER_PROFILE_ENABLE=0`

修改配置后执行：
```bash
qbsctl restart
```
