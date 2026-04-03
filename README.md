# my-skill

> Auto-synced from `~/.claude/skills` • Last updated: 2026/4/3 11:05:45

[📦 GitHub](https://github.com/Fenghaze/my-skill)

---

## `auto-upload-skill`

本地skill创建后自动上传到GitHub的自动化工具

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

---

## `enhance-chat-skill`

增强型规划技能，使用设计树方法论进行严谨的软件设计

---

## `find-skill`

Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill.

---

## `knowledge-review-skill`

"当用户希望回顾刚实现的功能、总结学习要点、分析设计思路或代码实现时触发。适用于'/review'、'帮我总结这个功能'、'讲解一下这段代码'、'回顾一下'等请求。此技能会根据用户对相关知识点的掌握程度定制化总结内容。"

---

