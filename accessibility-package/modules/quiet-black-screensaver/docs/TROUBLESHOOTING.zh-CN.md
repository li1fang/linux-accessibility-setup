# 故障排查

## 现象 1：仍然锁屏而不是黑屏
检查：
```bash
qbsctl doctor
kreadconfig6 --file kscreenlockerrc --group Daemon --key Autolock
kreadconfig6 --file kscreenlockerrc --group Daemon --key Timeout
```
建议：
- 自动锁屏关掉（Autolock=false, Timeout=0）
- 确保 `QBS_INHIBIT_SCREENSAVER=1`
- 重启服务：`qbsctl restart`

## 现象 2：10 分钟不触发
检查：
```bash
qbsctl logs
```
看是否有：
- `idle reached: ...`
- `overlay started: ...`

若无，可能是输入设备噪声导致一直不 idle。

## 现象 3：黑屏后不恢复
检查输入设备权限：
```bash
ls -l /dev/input/event*
groups
```
需要用户在 `input` 组（或具备等效权限）。

## 现象 4：服务跑着但没有日志
检查：
```bash
systemctl --user status quiet-black-screensaver.service --no-pager
```
并确认配置中的 `QBS_LOG_PATH` 可写。
