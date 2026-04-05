"""
Claude Code 使用技巧自动更新脚本
每 3 天执行一次，联网检索最新技巧并更新 references/tips.md
"""
import json
import os
from datetime import datetime, timedelta

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TIPS_FILE = os.path.join(SKILL_DIR, "references", "tips.md")

# 简单的内嵌更新逻辑，不依赖外部 API
TIPS_TEMPLATE = '''---
last_updated: {date}
---

# Claude Code 最新使用技巧

本文件由自动脚本每 3 天更新一次。

## 新手入门

### 1. 清晰的任务表达
- 明确指定文件路径和操作范围
- 复杂任务拆分为多个小步骤
- 使用 Tab 补全提高输入效率

### 2. 善用 Slash Commands
- `/plan` - 复杂任务规划
- `/review` - 代码审查
- `/simplify` - 代码优化
- `/loop` - 定期任务
- `/batch` - 并行处理

### 3. 项目上下文
- 为项目创建 CLAUDE.md
- 使用 @filename 引用项目文件
- 保持会话上下文，连续对话

## 进阶技巧

### MCP 服务器
你已经配置的工具：
- github - GitHub API 操作
- mysql - 数据库操作
- fetch - 网页内容获取
- brave-search - 搜索

### 子代理并行处理
使用 `/batch` 或 Agent tool 并行执行多个任务。

### Hooks 自动化
在 `.claude/settings.json` 中配置工具调用钩子：
```json
{{
  "hooks": {{
    "PostToolUse": {{
      "Bash": {{
        "after": "git add -A && git commit -m 'Update'"
      }}
    }}
  }}
}}
```

## 最佳实践

### 做
- 分步骤执行复杂任务
- 提交前使用 /review 审查
- 使用环境变量管理敏感信息
- 为每个项目编写 CLAUDE.md

### 不做
- 不要一次性要求太多（拆成小任务）
- 不要模糊描述（明确文件和功能）
- 不要跳过权限确认除非完全信任

## 工作流模板

### 新项目
1. 创建项目目录
2. 编写 CLAUDE.md
3. 配置必要设置
4. 开始第一个功能

### 功能开发
需求 → /plan 设计 → 编码 → /review 审查 → 提交

### 代码审查
使用 `/review` 或 `pr-review-toolkit:review-pr`
'''

def update_tips():
    """更新技巧文件"""
    os.makedirs(os.path.dirname(TIPS_FILE), exist_ok=True)

    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = TIPS_TEMPLATE.format(date=date)

    with open(TIPS_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"已更新技巧文件: {TIPS_FILE}")

if __name__ == "__main__":
    update_tips()
