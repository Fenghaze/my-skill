# my-skill

> Auto-synced from `~/.claude/skills` • Last updated: 2026/4/3 11:08:04

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

本技能通过严谨的设计树方法论增强规划模式下的规划过程。它系统性地探索需求、提出详细问题、并确保完整的功能规范，从而最小化从设计到实现过程中的 bug。


当以下情况时自动触发此技能：
1. 用户进入规划模式进行软件设计任务
2. 用户请求功能或系统的实施规划
3. 用户询问架构设计或系统规划

---

## `find-skill`

Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill.

Use this skill when the user:

- Asks "how do I do X" where X might be a common task with an existing skill
- Says "find a skill for X" or "is there a skill for X"
- Asks "can you do X" where X is a specialized capability
- Expresses interest in extending agent capabilities
- Wants to search for tools, templates, or workflows
- Mentions they wish they had help with a specific domain (design, testing, deployment, etc.)

---

## `knowledge-review-skill`

"当用户希望回顾刚实现的功能、总结学习要点、分析设计思路或代码实现时触发。适用于'/review'、'帮我总结这个功能'、'讲解一下这段代码'、'回顾一下'等请求。此技能会根据用户对相关知识点的掌握程度定制化总结内容。"

本技能帮助用户在 AI 实现功能后，有针对性地总结学习要点。核心特点是**根据用户对相关知识点的掌握程度定制化总结内容**，避免在已掌握内容上浪费时间，聚焦于薄弱环节。


当用户请求以下内容时触发：
- `/review` - 触发知识回顾
- "帮我总结这个功能"
- "讲解一下这段代码"
- "回顾一下今天学的"

---

