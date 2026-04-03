---
name: auto-upload-skill
description: 本地skill创建后自动上传到GitHub的自动化工具
version: 1.1.0
author: fenghaze
---

# Auto Upload Skill

自动化skill同步工具 - 当您在 `~/.claude/skills/` 目录创建新skill时，自动将其上传到 GitHub 仓库。

## 功能

- 文件监视：持续监控 `~/.claude/skills/` 目录变化
- 自动同步：检测到新的或修改的skill时，自动Git add/commit/push
- **自动生成README**：每次同步后自动更新仓库README，包含所有skills的描述和使用方法
- 后台运行：daemon模式在后台持续运行

## 使用方法

### 启动同步服务

首次使用需要启动daemon：
```
node C:/Users/Administrator/.claude/skill-sync/daemon.js --daemon
```

建议使用 PM2 或 Windows任务计划程序保持后台运行。

### 查看同步状态

```
node C:/Users/Administrator/.claude/skill-sync/daemon.js
```

### 手动同步

手动触发所有skills的同步（不使用daemon）：
```
node C:/Users/Administrator/.claude/skill-sync/daemon.js
```

## 配置

配置文件位于：`C:/Users/Administrator/.claude/skill-sync/config.json`

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| skillsDir | 监视的skills目录 | ~/.claude/skills |
| repoDir | 本地git仓库目录 | ~/.claude/skills-sync-repo |
| githubRepo | GitHub仓库 | Fenghaze/my-skill |
| debounceMs | 防抖延迟(ms) | 5000 |

## 工作原理

1. daemon使用chokidar监视 `~/.claude/skills/*/SKILL.md` 文件
2. 检测到变化后，等待5秒防抖
3. 将变化的skill复制到本地git仓库
4. **解析所有skill的SKILL.md，生成/更新README.md**（包含表格和详细文档）
5. 执行 git add → commit → push
6. 更新同步记录

## README自动生成内容

每次同步后，仓库的README.md会自动更新：

- **头部信息**：仓库名、最后更新时间、GitHub链接
- **Skills表格**：所有skill的名称、描述、版本、作者
- **Quick Start**：安装指南和常用命令
- **Individual Skill Docs**：每个skill的详细文档预览（前30行）

## 验证同步成功

访问 GitHub 仓库确认提交记录：
https://github.com/Fenghaze/my-skill

## 故障排除

**SSH认证失败**
- 确认 `~/.ssh/id_rsa.pub` 已添加到 GitHub
- 测试： `ssh -T git@github.com`

**daemon无响应**
- 检查日志： `C:/Users/Administrator/.claude/skill-sync/sync.log`
- 重启daemon
