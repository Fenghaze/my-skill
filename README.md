# my-skill

> Auto-synced from `~/.claude/skills` • Last updated: 2026/4/3 10:54:03

[📦 View on GitHub](https://github.com/Fenghaze/my-skill)

---

## Available Skills

| Skill | Description | Version | Author |
|-------|-------------|---------|--------|
| `auto-upload-skill` | 本地skill创建后自动上传到GitHub的自动化工具 | 1.0.0 | fenghaze |
| `enhance-chat-skill` | 增强型规划技能，使用设计树方法论进行严谨的软件设计 | 1.0.0 | fenghaze |
| `find-skill` | Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill. | - | - |
| `knowledge-review-skill` | "当用户希望回顾刚实现的功能、总结学习要点、分析设计思路或代码实现时触发。适用于'/review'、'帮我总结这个功能'、'讲解一下这段代码'、'回顾一下'等请求。此技能会根据用户对相关知识点的掌握程度定制化总结内容。" | 1.0.0 | fenghaze |

---

## Quick Start

### Install a Skill

```bash
# Copy skill to your Claude Code skills directory
cp -r SKILL_NAME ~/.claude/skills/
```

### Available Commands

| Command | Description |
|---------|-------------|
| `/skills` | List all installed skills |
| `/SKILL_NAME` | Invoke specific skill |

---

## Individual Skill Docs

### `auto-upload-skill`
> 本地skill创建后自动上传到GitHub的自动化工具

>
># Auto Upload Skill
>
>自动化skill同步工具 - 当您在 `~/.claude/skills/` 目录创建新skill时，自动将其上传到 GitHub 仓库。
>
>## 功能
>
>- 文件监视：持续监控 `~/.claude/skills/` 目录变化
>- 自动同步：检测到新的或修改的skill时，自动Git add/commit/push
>- 后台运行：daemon模式在后台持续运行
>
>## 使用方法
>
>### 启动同步服务
>
>首次使用需要启动daemon：
>```
>node C:/Users/Administrator/.claude/skill-sync/daemon.js --daemon
>```
>
>建议使用 PM2 或 Windows任务计划程序保持后台运行。
>
>### 查看同步状态
>
>```
>node C:/Users/Administrator/.claude/skill-sync/daemon.js
>```
>
>### 手动同步
>

> ... *(truncated)*

---

### `enhance-chat-skill`
> 增强型规划技能，使用设计树方法论进行严谨的软件设计

>
># 增强对话规划技能
>
>## 概述
>
>本技能通过严谨的设计树方法论增强规划模式下的规划过程。它系统性地探索需求、提出详细问题、并确保完整的功能规范，从而最小化从设计到实现过程中的 bug。
>
>## 使用时机
>
>当以下情况时自动触发此技能：
>1. 用户进入规划模式进行软件设计任务
>2. 用户请求功能或系统的实施规划
>3. 用户询问架构设计或系统规划
>
>## 设计树方法论
>
>设计树将需求从高层目标分解为具体的、可测试的规范：
>
>```
>目标（用户目标）
>  └─ 领域分析
>       └─ 用例场景
>            └─ 功能点
>                 └─ 需求细节
>                      └─ 边界情况
>                           └─ 异常处理
>```
>
>## 规划工作流程
>

> ... *(truncated)*

---

### `find-skill`
> Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill.

>
># Find Skills
>
>This skill helps you discover and install skills from the open agent skills ecosystem.
>
>## When to Use This Skill
>
>Use this skill when the user:
>
>- Asks "how do I do X" where X might be a common task with an existing skill
>- Says "find a skill for X" or "is there a skill for X"
>- Asks "can you do X" where X is a specialized capability
>- Expresses interest in extending agent capabilities
>- Wants to search for tools, templates, or workflows
>- Mentions they wish they had help with a specific domain (design, testing, deployment, etc.)
>
>## What is the Skills CLI?
>
>The Skills CLI (`npx skills`) is the package manager for the open agent skills ecosystem. Skills are modular packages that extend agent capabilities with specialized knowledge, workflows, and tools.
>
>**Key commands:**
>
>- `npx skills find [query]` - Search for skills interactively or by keyword
>- `npx skills add <package>` - Install a skill from GitHub or other sources
>- `npx skills check` - Check for skill updates
>- `npx skills update` - Update all installed skills
>
>**Browse skills at:** https://skills.sh/
>
>## How to Help Users Find Skills

> ... *(truncated)*

---

### `knowledge-review-skill`
> "当用户希望回顾刚实现的功能、总结学习要点、分析设计思路或代码实现时触发。适用于'/review'、'帮我总结这个功能'、'讲解一下这段代码'、'回顾一下'等请求。此技能会根据用户对相关知识点的掌握程度定制化总结内容。"

>
># 知识回顾技能
>
>## 概述
>
>本技能帮助用户在 AI 实现功能后，有针对性地总结学习要点。核心特点是**根据用户对相关知识点的掌握程度定制化总结内容**，避免在已掌握内容上浪费时间，聚焦于薄弱环节。
>
>## 使用时机
>
>当用户请求以下内容时触发：
>- `/review` - 触发知识回顾
>- "帮我总结这个功能"
>- "讲解一下这段代码"
>- "回顾一下今天学的"
>
>## 工作流程
>
>### 阶段1：需求收集
>
>**步骤1：确定回顾范围**
>请用户提供想要回顾的内容（功能描述、代码片段或文件路径）。
>
>**步骤2：识别相关知识点**
>根据代码内容，列出涉及的知识点供用户选择。
>
>**步骤3：评估掌握程度**
>对于用户选中的每个知识点，询问掌握程度：
>- 了解：听过概念，不清楚原理
>- 熟悉：能基本使用，不了解底层
>- 掌握：能熟练使用，了解原理

> ... *(truncated)*

---

