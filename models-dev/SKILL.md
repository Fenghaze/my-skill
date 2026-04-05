---
name: models-dev
description: 查询、对比AI大模型信息。当用户询问模型规格、能力对比、模型推荐，或提到以下场景时使用：查询某模型的上下文窗口/Token限制/支持的模态/推理能力；对比多个模型的优劣；根据场景推荐合适的模型；了解某提供商有哪些模型；筛选支持tool_call/open_weights/多模态的模型。注意：Models.dev 仅提供模型规格和技术能力数据，不包含价格信息。
version: 1.0.0
author: fenghaze
---

# Models.dev

查询、对比AI大模型信息的工具。

## 功能

- **查询单个模型**：获取模型的详细信息（上下文窗口、Token限制、支持的模态、推理能力等）
- **对比多个模型**：并排对比多个模型的规格和能力
- **列出提供商模型**：查看某提供商的所有可用模型

## 使用方法

### 查询单个模型
```
query: "claude"  # 模型名称、ID或关键词
```

### 对比多个模型
```
models: "claude-opus-4,gpt-4o,gemini-2-pro"  # 用逗号分隔
```

### 列出提供商模型
```
provider: "anthropic"  # 提供商名称
```

## 触发场景

**关键词：** 模型、models.dev、上下文窗口、token限制、支持的模态、推理能力、工具调用、tool_call、开源模型、open_weights、多模态、vision、对比模型、模型对比、模型推荐、AI模型、大模型、LLM

**模式匹配：**
- `(gpt|claude|gemini|llama|deepseek|qwen|mistral|anthropic|openai|google).*(模型|model)`
- `(上下文|context|token|window)`
- `(推理|reasoning)`
- `(开源|open.?weights)`
- `(多模态|vision|multimodal)`

## 示例

- 查询 Claude Opus 4 的上下文窗口和支持的模态
- 对比 gpt-4o 和 gemini-2-pro 的能力
- 列出 anthropic 提供商的所有模型

## 配置

无需额外设置，直接使用 Models.dev 公开 API：https://models.dev/api.json
