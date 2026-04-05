#!/usr/bin/env python3
"""
Models.dev API 数据解析脚本
用于解析和处理 models.dev API 返回的 JSON 数据
"""

import json
import sys
import time
import random
import io
from typing import Optional, Dict
from pathlib import Path

# 设置 UTF-8 输出（Windows 兼容）
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


# 提供商定价页面映射
PROVIDER_PRICING_URLS = {
    "anthropic": "https://www.anthropic.com/pricing",
    "openai": "https://openai.com/api/pricing",
    "google": "https://ai.google.dev/pricing",
    "meta": "https://llama.meta.com",
    "deepseek": "https://platform.deepseek.com/pricing",
    "mistral": "https://mistral.ai/news/price-update/",
    "groq": "https://console.groq.com/pricing",
    "cerebras": "https://cerebras.ai/product",
    "openrouter": "https://openrouter.ai/models",
    # 国产厂商
    "kimi": "https://platform.moonshot.cn/pricing",
    "moonshot": "https://platform.moonshot.cn/pricing",
    "glm": "https://zhipuai.cn/pricing",
    "zhipu": "https://zhipuai.cn/pricing",
    "qwen": "https://help.aliyun.com/document_detail/279926.html",
    "alibaba": "https://help.aliyun.com/document_detail/279926.html",
    "baidu": "https://cloud.baidu.com/doc/wenxin/sim2m2aSh",
    "ernie": "https://cloud.baidu.com/doc/wenxin/sim2m2aSh",
    "tencent": "https://cloud.tencent.com/document/product/1729",
    "yi": "https://platform.lingyiwanwu.com",
    "step": "https://platform.stepfun.com",
    "minimax": "https://www.minimaxi.com/price",
    "tongyi": "https://help.aliyun.com/document_detail/279926.html",
}

# 模型ID到提供商的映射（用于价格查询）
MODEL_PROVIDER_MAP = {
    "claude": "anthropic",
    "gpt": "openai",
    "gemini": "google",
    "llama": "meta",
    "deepseek": "deepseek",
    "mistral": "mistral",
    "qwen": "qwen",  # 通义千问
    "kimi": "kimi",  # Kimi
    "moonshot": "kimi",
    "glm": "glm",  # 智谱
    "zhipu": "glm",
    "zhipuai": "glm",
    "yi": "yi",  # 零一万物
    "step": "step",  # 阶跃星辰
    "ernie": "baidu",  # 百度文心
    "minimax": "minimax",
    "tongyi": "alibaba",
    "azure": "openai",
    "claude-3-5-sonnet": "anthropic",
    "claude-3-opus": "anthropic",
    "gpt-4": "openai",
    "gpt-3-5": "openai",
}


def fetch_models(url: str = "https://models.dev/api.json", use_cache: bool = True) -> dict:
    """获取模型数据，带缓存和UA伪装"""
    import urllib.request

    cache_dir = Path(__file__).parent.parent / ".cache"
    cache_file = cache_dir / "models_api.json"
    cache_ttl = 3600  # 缓存1小时

    # 检查缓存
    if use_cache and cache_file.exists():
        try:
            cache_age = time.time() - cache_file.stat().st_mtime
            if cache_age < cache_ttl:
                print(f"📦 使用缓存数据 ({(cache_age/60):.1f}分钟前)", file=sys.stderr)
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass

    # 随机UA，避免被限流
    ua_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    headers = {
        "User-Agent": random.choice(ua_list),
        "Accept": "application/json",
        "Connection": "keep-alive",
    }

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))

            # 保存缓存
            try:
                cache_dir.mkdir(exist_ok=True)
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False)
            except Exception:
                pass  # 缓存失败不影响主流程

            return data
    except urllib.error.HTTPError as e:
        if e.code == 403 or e.code == 429:
            # 被限流，尝试用缓存
            if cache_file.exists():
                print(f"⚠️ API请求失败({e.code})，使用过期缓存", file=sys.stderr)
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        raise


def find_model(data: dict, query: str) -> list:
    """根据名称或ID搜索模型"""
    query_lower = query.lower()
    results = []

    for provider_id, provider in data.items():
        if provider_id == "id" or not isinstance(provider, dict):
            continue

        models = provider.get("models", {})
        for model_id, model in models.items():
            if (query_lower in model_id.lower() or
                query_lower in model.get("name", "").lower() or
                query_lower in model.get("family", "").lower()):
                model_copy = model.copy()
                model_copy["_provider_id"] = provider_id
                model_copy["_provider_name"] = provider.get("name", provider_id)
                results.append(model_copy)

    return results


def filter_models(
    data: dict,
    reasoning: Optional[bool] = None,
    tool_call: Optional[bool] = None,
    open_weights: Optional[bool] = None,
    has_vision: Optional[bool] = None
) -> list:
    """根据条件筛选模型"""
    results = []

    for provider_id, provider in data.items():
        if provider_id == "id" or not isinstance(provider, dict):
            continue

        models = provider.get("models", {})
        for model_id, model in models.items():
            if reasoning is not None and model.get("reasoning") != reasoning:
                continue
            if tool_call is not None and model.get("tool_call") != tool_call:
                continue
            if open_weights is not None and model.get("open_weights") != open_weights:
                continue
            if has_vision is not None:
                modalities = model.get("modalities", {})
                input_mods = modalities.get("input", [])
                has_image = "image" in input_mods
                if has_image != has_vision:
                    continue

            model_copy = model.copy()
            model_copy["_provider_id"] = provider_id
            model_copy["_provider_name"] = provider.get("name", provider_id)
            results.append(model_copy)

    return results


def format_model_summary(model: dict) -> str:
    """格式化单个模型信息"""
    lines = [
        f"## {model.get('name', model.get('id'))}",
        f"",
        f"| 参数 | 值 |",
        f"|------|-----|",
        f"| 提供商 | {model.get('_provider_name', 'N/A')} |",
        f"| 模型ID | {model.get('id', 'N/A')} |",
        f"| 上下文窗口 | {model.get('limit', {}).get('context', 'N/A')} tokens |",
        f"| 输出限制 | {model.get('limit', {}).get('output', 'N/A')} tokens |",
    ]

    modalities = model.get("modalities", {})
    input_mods = ", ".join(modalities.get("input", []))
    output_mods = ", ".join(modalities.get("output", []))
    lines.append(f"| 支持输入 | {input_mods} |")
    lines.append(f"| 支持输出 | {output_mods} |")
    lines.append(f"| 推理能力 | {'✅' if model.get('reasoning') else '❌'} |")
    lines.append(f"| 工具调用 | {'✅' if model.get('tool_call') else '❌'} |")
    lines.append(f"| 开源 | {'✅' if model.get('open_weights') else '❌'} |")
    lines.append(f"| 发布日期 | {model.get('release_date', 'N/A')} |")
    lines.append(f"|")
    lines.append(f"| **应用场景** | {get_use_cases(model)} |")

    return "\n".join(lines)


def format_comparison_table(models: list) -> str:
    """格式化对比表格"""
    if not models:
        return "未找到匹配的模型"

    lines = [
        "| 对比项 | " + " | ".join([m.get("name", m.get("id", "")) for m in models]) + " |",
        "|" + "---|" * (len(models) + 1),
    ]

    # 上下文窗口
    contexts = [m.get("limit", {}).get("context", "N/A") for m in models]
    lines.append("| 上下文窗口 | " + " | ".join([str(c) for c in contexts]) + " |")

    # 输出限制
    outputs = [m.get("limit", {}).get("output", "N/A") for m in models]
    lines.append("| 输出限制 | " + " | ".join([str(o) for o in outputs]) + " |")

    # 推理
    reasoning = ["✅" if m.get("reasoning") else "❌" for m in models]
    lines.append("| 推理能力 | " + " | ".join(reasoning) + " |")

    # 工具调用
    tool_call = ["✅" if m.get("tool_call") else "❌" for m in models]
    lines.append("| 工具调用 | " + " | ".join(tool_call) + " |")

    # 开源
    open_weights = ["✅" if m.get("open_weights") else "❌" for m in models]
    lines.append("| 开源 | " + " | ".join(open_weights) + " |")

    # 提供商
    providers = [m.get("_provider_name", "N/A") for m in models]
    lines.append("| 提供商 | " + " | ".join(providers) + " |")

    return "\n".join(lines)


def get_provider_from_model(model_id: str) -> Optional[str]:
    """根据模型ID推断提供商"""
    model_lower = model_id.lower()
    for prefix, provider in MODEL_PROVIDER_MAP.items():
        if prefix in model_lower:
            return provider
    return None


def get_pricing_urls(models: list) -> Dict[str, str]:
    """获取模型的价格查询URL"""
    urls = {}
    for model in models:
        model_id = model.get("id", "")
        provider = model.get("_provider_id", "").lower()

        # 先尝试从模型ID推断提供商
        inferred = get_provider_from_model(model_id)
        if inferred:
            provider = inferred

        if provider in PROVIDER_PRICING_URLS:
            urls[model.get("name", model_id)] = PROVIDER_PRICING_URLS[provider]
        elif provider == "ollama-cloud":
            urls[model.get("name", model_id)] = "https://ollama.com/pricing"
        elif provider == "groq" or provider == "cerebras":
            urls[model.get("name", model_id)] = f"https://{provider}.ai/product"

    return urls


def get_use_cases(model: dict) -> str:
    """根据模型特性生成应用场景推荐"""
    cases = []

    # 推理能力
    if model.get("reasoning"):
        cases.append("复杂推理/数学/代码调试")

    # 工具调用
    if model.get("tool_call"):
        cases.append("Agent系统/自动化工作流")

    # 多模态
    modalities = model.get("modalities", {})
    if "image" in modalities.get("input", []):
        cases.append("图文理解/文档分析")

    # 开源
    if model.get("open_weights"):
        cases.append("本地部署/研究微调")

    # 上下文长度
    context = model.get("limit", {}).get("context", 0)
    if isinstance(context, int):
        if context >= 200000:
            cases.append("长文档总结/代码库分析")
        elif context >= 100000:
            cases.append("中等长度对话/文档处理")

    # 参数规模（从ID推断）
    model_id = model.get("id", "").lower()
    if "mini" in model_id or "small" in model_id or "8b" in model_id or "7b" in model_id:
        cases.append("端侧部署/快速响应")
    elif "large" in model_id or "675b" in model_id or "405b" in model_id or "70b" in model_id:
        cases.append("高性能推理/复杂任务")

    return " / ".join(cases) if cases else "通用对话/文本生成"


if __name__ == "__main__":
    # 简单命令行接口
    if len(sys.argv) < 2:
        print("用法: python parse_models.py <command> [args]")
        print("命令:")
        print("  search <query>     - 搜索模型")
        print("  filter [--reasoning] [--tool-call] [--open-weights] [--vision] - 筛选模型")
        print("  compare <id1,id2,...> - 对比模型（包含价格查询URL）")
        print("  price <id1,id2,...>  - 获取模型价格查询URL")
        sys.exit(1)

    command = sys.argv[1]
    data = fetch_models()

    if command == "search":
        if len(sys.argv) < 3:
            print("请提供搜索关键词")
            sys.exit(1)
        results = find_model(data, sys.argv[2])
        for model in results:
            print(format_model_summary(model))
            print()
        # 同时显示价格查询URL
        if results:
            print("\n💰 价格查询：")
            urls = get_pricing_urls(results)
            for name, url in urls.items():
                print(f"  - {name}: {url}")

    elif command == "filter":
        kwargs = {}
        for arg in sys.argv[2:]:
            if arg == "--reasoning":
                kwargs["reasoning"] = True
            elif arg == "--tool-call":
                kwargs["tool_call"] = True
            elif arg == "--open-weights":
                kwargs["open_weights"] = True
            elif arg == "--vision":
                kwargs["has_vision"] = True
        results = filter_models(data, **kwargs)
        print(f"找到 {len(results)} 个符合条件的模型:\n")
        for model in results:
            name = model.get("name", model.get("id", ""))
            provider = model.get("_provider_name", "")
            ctx = model.get("limit", {}).get("context", "N/A")
            use_cases = get_use_cases(model)
            print(f"- **{name}** ({provider}) | 上下文: {ctx}")
            print(f"  场景: {use_cases}")
        # 同时显示价格查询URL
        if results:
            print("\n💰 价格查询：")
            urls = get_pricing_urls(results)
            for name, url in urls.items():
                print(f"  - {name}: {url}")

    elif command == "compare":
        if len(sys.argv) < 3:
            print("请提供模型ID列表（逗号分隔）")
            sys.exit(1)
        ids = [id.strip() for id in sys.argv[2].split(",")]
        models = []
        for provider_id, provider in data.items():
            if provider_id == "id" or not isinstance(provider, dict):
                continue
            for mid, model in provider.get("models", {}).items():
                if mid in ids:
                    model_copy = model.copy()
                    model_copy["_provider_id"] = provider_id
                    model_copy["_provider_name"] = provider.get("name", provider_id)
                    models.append(model_copy)
        print(format_comparison_table(models))
        # 同时显示价格查询URL
        if models:
            print("\n💰 价格查询链接：")
            urls = get_pricing_urls(models)
            for name, url in urls.items():
                print(f"  - {name}: {url}")
            if not urls:
                print("  （开源模型请自行查询托管平台价格，如 Groq、Cerebras）")

    elif command == "price":
        if len(sys.argv) < 3:
            print("请提供模型ID列表（逗号分隔）")
            sys.exit(1)
        ids = [id.strip() for id in sys.argv[2].split(",")]
        models = []
        for provider_id, provider in data.items():
            if provider_id == "id" or not isinstance(provider, dict):
                continue
            for mid, model in provider.get("models", {}).items():
                if mid in ids:
                    model_copy = model.copy()
                    model_copy["_provider_id"] = provider_id
                    model_copy["_provider_name"] = provider.get("name", provider_id)
                    models.append(model_copy)

        urls = get_pricing_urls(models)
        if urls:
            print("💰 价格查询链接：")
            for name, url in urls.items():
                print(f"  - {name}: {url}")
        else:
            print("未找到价格信息，请尝试以下方式：")
            print("  - 开源模型：查询 Groq (console.groq.com)、Cerebras (cerebras.ai)、Modal 等托管平台")
            print("  - 其他模型：直接访问模型提供商官网")

    else:
        print(f"未知命令: {command}")
        sys.exit(1)
