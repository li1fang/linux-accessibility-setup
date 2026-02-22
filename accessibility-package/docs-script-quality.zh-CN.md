# scripts 目录质量评估（初版）

目录：`accessibility-package/scripts/`

## 结果概览
- 语法检查（shell）通过：`autoyes.sh`、`autoinput.sh`、`auto-sudo.sh`、`easy-menu.sh`
- expect 脚本存在，但当前机器未安装 `expect` / `dialog`，运行前需补齐依赖。

## 风险等级
- 低：`autoyes.sh`、`autoinput.sh`
- 中：`autoexpect.exp`（会自动确认提示）
- 中：`auto-ssh.exp`（密码交互自动化，不建议长期）
- 高：`auto-sudo.sh`、`easy-menu.sh`（涉及提权与系统操作）

## 已修复问题
- 修复了硬编码路径 `/home/whipc/...`，改为通过命令查找 `autoexpect` / `auto-ssh`。

## 建议
1. 对外开源时给“高风险脚本”加醒目警示。
2. 将 `expect`、`dialog`、`openssh-client` 写入依赖清单。
3. 后续逐步替换“自动 yes”策略为明确确认模式。
