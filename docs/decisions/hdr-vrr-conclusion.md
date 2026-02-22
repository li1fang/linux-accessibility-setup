# HDR / VRR 结论（Linux，2026-02）

## 中文结论
在当前硬件与系统组合（RTX 4090 + LG C5 + Ubuntu 25.10 + KDE Wayland）下：

1. 浏览器 HDR：阶段性放弃
- YouTube 实际下发 SDR（`vp09.00` + `bt709`），并非网络故障。
- 已做多浏览器与多参数验证，未形成稳定可复现的浏览器 HDR 方案。

2. 游戏 HDR：仅部分可见，不稳定
- 在部分参数组合下游戏内可见 HDR 选项，但存在发白、色彩异常、链路状态不一致等问题。

3. VRR 黑屏：已定位到刷新率阈值相关
- 全局刷新率高于约 120Hz 时，VRR 易触发黑屏/闪烁。
- 全局限制到约 119.88Hz 时可显著稳定。

4. 阶段性策略
- 以“稳定可用”优先：优先 SDR + 稳定显示链路。
- HDR/VRR 继续作为实验项，不作为默认配置。

## English Summary
On this setup (RTX 4090 + LG C5 + Ubuntu 25.10 + KDE Wayland), full HDR/VRR is not yet production-stable.

- Browser HDR: not reliably available (YouTube streams still delivered as SDR in tests).
- Game HDR: partially exposed but inconsistent (washed-out colors / unstable pipeline).
- VRR: black-screen/flicker strongly correlated with refresh rates above ~120Hz.
- Current strategy: prioritize stable SDR workflow; keep HDR/VRR as optional experimental profile.
