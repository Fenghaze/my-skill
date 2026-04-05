# Save-Doc Skill

将 Claude 返回的长文档内容保存到文件中。

## 触发场景

- 用户需要保存 Claude 输出的指南、教程、方案、总结等文档
- 用户不想手动复制粘贴，想要快速保存

## 工作流程

### 阶段1：文档检测

Claude 通过 `SessionStop` Hook 自动检测符合条件的输出：

**检测条件（满足任一）：**
- 输出超过 500 字符
- 输出包含文档类标记：`# ` (一级标题)、`##` (二级标题)
- 输出包含文档类型关键词：`指南`、`教程`、`方案`、`总结`、`文档`

**检测到后，发送 prompt 询问：**
```
📄 检测到文档输出，是否保存？
  1. 保存到 .claude/docs/ (自动生成文件名)
  2. 保存到项目根目录 (自动生成文件名)
  3. 指定保存路径
  4. 不保存
```

### 阶段2：文件名生成

- 提取文档的第一个 `# ` 标题作为文件名
- 过滤非法字符（`/\:*?"<>|`）
- 空格替换为 `-`
- 保留 `.md` 扩展名
- 超长截断至 100 字符

**示例：**
- 输入：`# Claude Code 高效上手新项目指南`
- 输出：`Claude-Code-高效上手新项目指南.md`

### 阶段3：保存执行

**路径选项：**
- 选项1：`.claude/docs/` (默认)
- 选项2：当前项目根目录
- 选项3：用户指定路径

**写入流程：**
1. 如果文件已存在 → 追加 `-1`, `-2` 后缀
2. 如果目录不存在 → 自动创建
3. 写入文件
4. 返回保存成功消息（含文件路径）

### 阶段4：失败处理

| 失败场景 | 处理方式 |
|---------|---------|
| 目录无写权限 | 降级到当前项目根目录 |
| 路径无效 | 提示用户输入有效路径 |
| 磁盘空间不足 | 提示用户检查磁盘空间 |
| Hook 执行失败 | 静默失败，不影响主流程 |

## 目录结构

```
.claude/
├── docs/                    # 默认保存目录
│   └── [自动生成的文件].md
└── memory/
    └── MEMORY.md
```

## 交互示例

### 示例1：保存到默认目录

```
用户：入职新公司，如何用 Claude Code 高效上手一个陌生的前端项目

Claude：<输出长文档指南>

[SessionStop Hook 触发]
Claude：📄 检测到文档输出，是否保存？
  1. 保存到 .claude/docs/ (自动生成文件名)
  2. 保存到项目根目录
  3. 指定保存路径
  4. 不保存

用户：1

Claude：✅ 已保存到 C:/Users/Administrator/.claude/docs/Claude-Code-高效上手新项目指南.md
```

### 示例2：指定路径

```
用户：1

Claude：📄 检测到文档输出，是否保存？
  1. 保存到 .claude/docs/ (自动生成文件名)
  2. 保存到项目根目录
  3. 指定保存路径
  4. 不保存

用户：3

Claude：请输入保存路径（绝对路径或相对于当前项目的路径）：

用户：D:/my-docs/前端开发指南.md

Claude：✅ 已保存到 D:/my-docs/前端开发指南.md
```

## 技术实现

### Hook 配置

在 `settings.json` 中配置 `SessionStop` Hook：

```json
{
  "hooks": {
    "SessionStop": [{
      "matcher": "*",
      "hooks": [{
        "type": "prompt",
        "prompt": "检测 Claude 的最后一条输出是否为文档（超过500字符或包含 # 标题）。如果是，询问用户是否保存。"
      }]
    }]
  }
}
```

### 文档识别算法

```typescript
function isDocument(output: string): boolean {
  const hasLength = output.length > 500;
  const hasHeading = /^#+ /.test(output);
  const hasKeywords = /指南|教程|方案|总结|文档/.test(output);
  return hasLength && (hasHeading || hasKeywords);
}

function extractTitle(output: string): string {
  const match = output.match(/^#\s+(.+)$/m);
  return match ? match[1] : '未命名文档';
}

function sanitizeFilename(title: string): string {
  return title
    .replace(/[/\:*?"<>|]/g, '-')
    .replace(/\s+/g, '-')
    .slice(0, 100) + '.md';
}
```

## 注意事项

- Hook 只在检测到文档输出时才触发 prompt，不会每次都询问
- 默认保存目录 `.claude/docs/` 需要预先创建
- 文件名冲突时会自动添加序号后缀
- Hook 执行失败时静默降级，不影响正常对话流程
