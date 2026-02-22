# Contributing / 贡献指南

Thanks for helping improve this project.

## English

## Scope
This repository focuses on Linux accessibility and stability workflows.
Please keep contributions aligned with:
- practical usability improvements
- safe defaults
- clear rollback paths

## How to contribute
1. Fork the repository.
2. Create a branch: `feat/<name>` or `fix/<name>`.
3. Keep changes focused (one topic per PR).
4. Add or update docs when behavior changes.
5. Open a Pull Request with:
   - problem statement
   - change summary
   - test/verification steps

## Coding and script guidelines
- Prefer portable shell (`bash`) and explicit error handling (`set -euo pipefail`).
- Avoid hardcoded home paths.
- Document risk for privileged operations.

## Commit style (recommended)
- `feat: ...`
- `fix: ...`
- `docs: ...`
- `chore: ...`

## 中文

## 范围
本仓库聚焦 Linux 无障碍与稳定性实践，提交内容请尽量满足：
- 真实可用
- 默认安全或可回滚
- 文档同步更新

## 提交流程
1. Fork 仓库
2. 新建分支：`feat/<name>` 或 `fix/<name>`
3. 每次只做一个主题
4. 行为变化必须更新文档
5. 发起 PR，写清：问题、改动、验证步骤

## 脚本规范
- 建议使用 `bash` 并启用 `set -euo pipefail`
- 禁止硬编码用户目录
- 涉及提权操作必须标注风险与回滚方式
