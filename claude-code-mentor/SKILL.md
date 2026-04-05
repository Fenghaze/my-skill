---
version: 2.5.1
name: claude-code-mentor
description: Claude Code 使用技巧与 AI Agent 实战助手。当用户询问上下文管理、会话优化、项目交接、AI 工作流、最佳实践等问题时自动触发。提供会话分割策略、上下文复用技巧、项目进度维护等指导，并智能推荐/创建相关 skills 帮助用户高效使用 AI 进行项目开发。特别适合想要快速掌握 AI Agent 实战的开发者。
---

# Claude Code AI Agent 实战指南

本 skill 整合 Claude Code 官方文档精华与社区实战经验，帮助你快速成为 AI Agent 高手。

`★ Insight ─────────────────────────────────────`
Claude Code 不只是"会说话的终端"——它是一个完整的 AI Agent 开发平台，支持多代理协作、自动化工作流、上下文持久化。掌握这些功能，你就能用 AI 构建真正的自动化流水线。
`─────────────────────────────────────────────────`

## 核心原则

1. **清晰表达**：明确指定文件路径和操作范围
2. **分步执行**：复杂任务拆分为小步骤
3. **善用技能**：充分利用 slash commands 和 skills
4. **保持上下文**：在同一会话中连续对话

## 一、新手快速上手

### 启动工作流
```
欢迎使用 Claude Code！快速上手路径：

1. 【基础操作】用自然语言让 AI 帮你读写文件、运行命令
2. 【项目初始化】创建 CLAUDE.md 建立项目上下文
3. 【常用命令】/plan 设计 → /review 审查 → 提交
4. 【实战项目】开始你的第一个 AI Agent 任务

输入你的需求，马上开始！
```

## 二、必会的 Slash Commands

| 命令 | 用途 | 使用场景 |
|-----|------|---------|
| `/plan` | 任务规划 | 复杂功能设计、架构决策 |
| `/review` | 代码审查 | 提交前检查、代码质量把关 |
| `/simplify` | 代码优化 | 简化复杂代码、提升可读性 |
| `/feature-dev [描述]` | 功能开发工作流 | 启动 7 阶段自动化开发流程 |
| `/plugin-dev:create-plugin [描述]` | 插件开发 | 创建 Claude Code 扩展插件 |

### `/feature-dev` - 7 阶段功能开发（重点！）

当你有一个功能想法时，直接说：
```
/feature-dev 添加用户认证功能，支持 OAuth2
```

Claude 会自动执行：
1. **探索阶段** - 启动 2-3 个代码探索代理理解代码库
2. **澄清问题** - 询问 OAuth 提供商、Session 处理方式等
3. **架构设计** - 提出多个方案供选择
4. **实现** - 按选定的架构实现
5. **审查** - 代码质量检查

### `/review` - 代码审查

```
/review
```

Claude 会检查：
- 代码质量（可读性、一致性）
- 潜在问题（逻辑错误、边界情况）
- 最佳实践（设计模式、错误处理）

## 三、子代理并行处理（进阶核心）

Claude Code 支持多代理同时工作，大幅提升效率：

```markdown
使用 Agent 工具启动子代理：

1. **并行任务**：多个独立任务同时执行
2. **专业分工**：不同代理做不同专业领域的事
3. **结果汇总**：主代理收集并整合子代理结果

示例场景：
- 同时分析多个模块的代码
- 并行运行测试、构建、部署
- 多人协作模式（每个代理负责一个功能）
```

### 何时使用子代理

| 场景 | 代理类型 | 效果 |
|-----|---------|------|
| 代码库结构分析 | `code-explorer` | 快速理解大型项目 |
| 安全漏洞扫描 | `security-reviewer` | 专业安全检查 |
| API 文档生成 | `api-docs-writer` | 自动生成完整文档 |
| 并行功能开发 | 多个 `feature-dev` | 团队式开发 |

### GitHub 热门开源项目参考

当用户想要自定义子代理或参考优秀实践时，推荐以下热门项目：

| 项目 | 用途 | GitHub |
|-----|------|--------|
| **Claude Code 官方示例** | 学习官方子代理模式 | anthropics/claude-code |
| **Multi-Agent Orchestration** | 多代理协作模式参考 | |
| **Agent Workflows** | AI Agent 工作流设计 | |

**搜索技巧**：
- GitHub 搜索 `claude-code-agent` / `multi-agent-ai` / `agent-workflow`
- 按 star 排序，寻找活跃项目的 agent 实现
- 查看项目的 `examples/` 目录获取灵感

### 自定义子代理创建流程

当用户想要创建专属子代理时：

```
"我来帮你设计一个自定义子代理！这需要一个清晰的角色定义..."
```

**创建步骤**：
1. **定义代理角色** - 这个代理负责什么？
2. **设计工具权限** - 需要哪些工具访问权限？
3. **编写提示词** - 如何让代理正确执行任务？
4. **集成到项目** - 在 CLAUDE.md 或专用配置中定义
5. **测试验证** - 运行测试用例确保有效

**推荐方式**：使用 `/plugin-dev:create-plugin` 引导创建标准化子代理包

**适用场景**：
- 需要专业化代理处理特定领域任务
- 想要复用复杂的工作流模式
- 希望将团队经验沉淀为自动化流程

## 四、Hooks 自动化工作流（实战必备）

Hooks 让你在特定时机自动执行操作，实现真正的自动化：

### 常用 Hook 类型

```json
{
  "hooks": {
    "SessionStart": [{ /* 会话开始时 */ }],
    "PreToolUse": [{ /* 工具执行前 */ }],
    "PostToolUse": [{ /* 工具执行后 */ }],
    "Stop": [{ /* 结束前 */ }],
    "SubagentStop": [{ /* 子代理结束前 */ }]
  }
}
```

### 实战 Hook 场景

**场景 1：自动上下文加载**
```json
{
  "SessionStart": [{
    "matcher": "*",
    "hooks": [{
      "type": "command",
      "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/load-context.sh"
    }]
  }]
}
```
自动检测项目类型（Node.js/Rust/Python）并加载对应环境。

**场景 2：提交前安全检查**
```json
{
  "PreToolUse": [{
    "matcher": "Bash",
    "hooks": [{
      "type": "prompt",
      "prompt": "验证这个命令是否安全，检查破坏性操作和安全风险"
    }]
  }]
}
```

**场景 3：自动运行测试**
```json
{
  "Stop": [{
    "hooks": [{
      "type": "agent",
      "prompt": "运行测试套件，验证所有单元测试通过",
      "timeout": 120
    }]
  }]
}
```

**场景 4：MCP 工具日志**
```json
{
  "PreToolUse": [{
    "matcher": "mcp__github__.*",
    "hooks": [{
      "type": "command",
      "command": "echo \"GitHub tool called: $(jq -r '.tool_name')\" >&2"
    }]
  }]
}
```

### GitHub 热门 Hooks 配置参考

当用户想要自定义 Hooks 或参考优秀实践时，推荐以下资源：

| 项目 | 用途 | 搜索关键词 |
|-----|------|-----------|
| **Claude Code 官方 Hooks** | 学习官方最佳实践 | `claude-code hooks examples` |
| **Awesome Claude Code** | 社区精选配置 | `awesome-claude-code` |
| **DevOps Hooks** | CI/CD 集成模式 | `github actions hook automation` |

**搜索技巧**：
- GitHub 搜索 `claude-code-settings.json` / `claude-hooks-config`
- 查看 `.claude/settings.json` 目录获取灵感
- 按 star 排序，寻找活跃项目的配置参考

### 自定义 Hooks 创建流程

当用户想要创建专属 Hooks 配置时：

```
"我来帮你设计一个自定义 Hook！这需要一个清晰的配置..."
```

**创建步骤**：
1. **确定触发时机** - SessionStart / PreToolUse / PostToolUse / Stop / SubagentStop？
2. **定义匹配规则** - 什么条件触发？（matcher 模式）
3. **选择执行类型** - command / prompt / agent？
4. **编写执行内容** - 具体要执行什么？
5. **配置到 settings.json** - 使用 `update-config` skill 写入配置

**推荐方式**：使用 `update-config` skill 将 Hooks 配置直接写入 `.claude/settings.json`

**适用场景**：
- 自动化代码检查/格式化
- 提交前安全验证
- 上下文自动加载
- 任务完成后自动清理

## 五、MCP 服务器集成

Claude Code 通过 Model Context Protocol 扩展能力：

```markdown
已配置的 MCP 工具：
| MCP | 用途 | 示例 |
|-----|------|------|
| github | Git 操作 | 查看 PR、创建 issue |
| mysql | 数据库 | 查询、管理数据 |
| fetch | 网页获取 | 抓取内容、分析页面 |
| brave-search | 搜索 | 查找资料 |
| claude-vscode | 编辑器 | VS Code 操作 |

连接外部工具：MCP 服务器可以连接 JIRA、Figma、PostgreSQL 等

### GitHub 热门 MCP 服务器参考

当用户想要自定义 MCP 或参考优秀实践时，推荐以下资源：

| MCP 服务器 | 用途 | GitHub |
|-----------|------|--------|
| **官方 MCP Servers** | Anthropic 官方维护 | modelcontextprotocol/servers |
| **GitHub MCP** | GitHub 操作自动化 | modelcontextprotocol/server-github |
| **Slack MCP** | 团队协作集成 | modelcontextprotocol/server-slack |
| **PostgreSQL MCP** | 数据库操作 | modelcontextprotocol/server-postgres |

**搜索技巧**：
- GitHub 搜索 `mcp-server` / `model-context-protocol`
- 查看 `modelcontextprotocol/servers` 获取完整列表
- 按 star 排序，寻找活跃项目

### 自定义 MCP 创建流程

当用户想要创建专属 MCP 服务器时：

```
"我来帮你设计一个自定义 MCP 服务器！这需要一个清晰的功能规划..."
```

**创建步骤**：
1. **定义功能范围** - 这个 MCP 提供什么能力？
2. **设计工具接口** - 需要暴露哪些工具？（tools 列表）
3. **编写服务端** - 使用 Node.js/Python 实现
4. **配置连接** - 使用 `update-config` 注册到 settings.json
5. **测试验证** - 确保工具调用正常

**推荐方式**：参考 `modelcontextprotocol/servers` 官方仓库，使用现有 SDK 加速开发

**适用场景**：
- 连接私有 API 或内部系统
- 封装特定的业务逻辑
- 集成专有工具链
- 自定义数据源连接
```

## 六、CLAUDE.md 高级用法

### 基础结构
```markdown
# 项目名称

## 项目概述
描述项目做什么

## 技术栈
- 前端：React + TypeScript
- 后端：Node.js + Express

## 代码规范
- 提交前必须 /review
- 所有 API 必须有文档

## 项目结构
/src - 源代码
/tests - 测试
```

### 高级：环境感知
```bash
# 根据项目类型自动调整行为
if [ -f "package.json" ]; then
  echo "PROJECT_TYPE=nodejs"
elif [ -f "Cargo.toml" ]; then
  echo "PROJECT_TYPE=rust"
fi
```

## 七、需求制定（关键）

**重要**：当用户开始制定功能需求时，**必须调用 enhance-chat-skill** 进行严谨的规划。

### 触发场景
- 说"我要做一个 xxx 功能"
- 说"帮我规划一下 xxx"
- 说"我想实现 xxx，请帮我设计"
- 使用 /plan 命令
- 询问"应该怎么做"

### 调用方式
```
请先使用 enhance-chat-skill 帮助用户进行需求分析和规划，
等规划完成后再协助后续实现。
```

## 八、实战工作流

### 工作流 1：功能开发（推荐）
```
需求 → /feature-dev → 探索代码库 → 架构设计 → 实现 → /review → 提交
```

### 工作流 2：并行开发
```
主代理（规划）
  ├── 子代理 A（实现模块 A）
  ├── 子代理 B（实现模块 B）
  └── 子代理 C（编写测试）
主代理（整合 + 审查）
```

### 工作流 3：插件开发
```
/plugin-dev:create-plugin → 8 阶段自动创建 → 调试 → 发布
```

### 工作流 4：PR 审查
```
/review 或 手动审查
  ├── 检查代码质量
  ├── 验证测试覆盖
  ├── 检查 CI/CD 状态
  └── 批准/请求修改
```

## 九、上下文优化技巧

`★ Insight ─────────────────────────────────────`
上下文窗口是共享资源——你放越多历史记录，能用的空间就越少。主动管理上下文 = 更高的 AI 响应质量。
`─────────────────────────────────────────────────`

1. **任务拆小**：大任务分多次对话完成
2. **文件引用**：用 `@文件路径` 替代粘贴代码
3. **记忆系统**：重要结论保存到 MEMORY.md
4. **新会话接手**：话题转换时开启新会话
5. **CLAUDE.md 沉淀**：项目级上下文持久化

## 十、最佳实践

### 做
- 为每个项目创建 CLAUDE.md
- 复杂任务先用 /plan 设计
- 提交前用 /review 审查
- Hooks 自动化重复工作
- 并行处理独立任务
- **主动推荐相关 skills**（见下方说明）

### 不做
- 不要一次性要求太多（拆成小任务）
- 不要模糊描述（明确文件和功能）
- 不要跳过权限确认除非完全信任
- 不要忽略 Hooks 的自动化潜力

## 十二、智能 Skill 推荐

当用户提问涉及以下场景时，主动调用 **find-skill** 查找并推荐相关 skills：

| 用户问题类型 | 推荐动作 |
|------------|---------|
| "有没有做 X 的 skill" | 调用 `find-skill` 搜索 |
| "如何实现 XXX" | 调用 `find-skill` 查找可能有用的 skills |
| "XXX 技巧/方法" | 调用 `find-skill` 检查是否有相关 skill |
| 涉及多个领域 | 调用 `find-skill` 获取多个推荐 |

### 推荐时机

**场景 1：用户明确询问是否有某个 skill**
```
用户："有没有自动生成测试的 skill？"
→ 调用 find-skill: "自动生成测试"
```

**场景 2：用户描述的需求涉及特定领域**
```
用户："我想做一个代码审查工具"
→ 调用 find-skill: "代码审查" → 推荐 pr-review-toolkit
```

**场景 3：跨领域复杂任务**
```
用户："帮我规划一个电商系统"
→ enhance-chat-skill 规划
→ find-skill 查找可能相关的 skills（如有）
```

### 调用方式

```markdown
用户问到可能需要其他 skill 的场景时：

"我发现有一个 skill 可能帮到你——让我查一下..."
（调用 find-skill）
```

### 已集成的 Skills（自动推荐）

| 领域 | Skill | 触发关键词 |
|-----|-------|-----------|
| 代码审查 | `pr-review-toolkit:review-pr` | PR、pull request、审查 |
| 规划设计 | `enhance-chat-skill` | 规划、设计、需求 |
| 知识回顾 | `knowledge-review-skill` | 总结、讲解、回顾 |
| 模型查询 | `models-dev` | 模型、GPT、Claude、参数 |
| 代码优化 | `simplify` | 优化、简化、重构 |
| 配置管理 | `update-config` | 配置、settings、hook |
| 定时任务 | `loop` | 定期、循环、定时 |

### 推荐优先级

1. **直接匹配** → 找到明确对应的 skill，立即推荐
2. **模糊匹配** → 找到相关 skill，说明可能有用
3. **无匹配** → 调用 **skill-creator** 帮用户创建自定义 skill

#### 自定义 Skill 创建流程

当 find-skill 找不到合适的 skill 时：

```
"没找到完全匹配的 skill，但我可以帮你创建一个！"
（调用 skill-creator）
```

skill-creator 会引导用户：
1. 定义 skill 的用途和触发场景
2. 编写 skill 指令
3. 测试验证效果
4. 保存并立即可用

**适用场景**：
- 用户有重复性任务需要自动化
- 用户的工作流有特殊需求
- 用户想把自己的经验沉淀为可复用工具

## 十一、输出选项

用户可以要求：
- **对话指导**：直接回答问题（默认）
- **生成模板**：CLAUDE.md、项目结构、Hook 配置
- **工作流图**：特定场景的详细流程
- **实战案例**：真实项目的 AI Agent 工作流示例

## 响应格式

根据问题类型选择最合适的响应形式：
- **指导性问题** → 对话式回答 + 示例
- **模板请求** → 提供可直接使用的模板
- **流程咨询** → 结构化的工作流说明
- **实战问题** → 基于官方文档的最佳实践

---

## 更新日志
- v2.5.0：修正自定义创建流程，子代理→plugin-dev、Hooks→update-config、MCP→参考官方SDK
- v2.4.0：新增 Hooks 和 MCP 的 GitHub 参考资源及自定义创建流程引导
- v2.3.0：新增 GitHub 热门开源项目参考列表，添加自定义子代理创建流程引导
- v2.2.0：新增自定义 skill 创建流程，find-skill 无匹配时调用 skill-creator 引导用户创建专属 skill
- v2.1.0：新增智能 Skill 推荐功能，集成 find-skill 查找相关 skills，自动推荐 pr-review-toolkit、enhance-chat-skill、models-dev 等
- v2.0.0：新增 `/feature-dev`、`/plugin-dev` 命令，子代理并行处理，Hooks 自动化工作流，MCP 集成
- v1.0.0：初始版本
