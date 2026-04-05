#!/bin/bash
# Claude Code 状态栏插件
# 功能: 显示用户、目录、模型、风格、权限模式和上下文使用率
# 效果示例: @fenghaze /d/coding:[claude-sonnet-4-6|Explanatory|auto](83%)

/d/Miniconda/python.exe -c "
import sys, json, subprocess

MODE_LABELS = {
    'default': 'ask',
    'acceptEdits': 'acceptEdits',
    'auto': 'auto',
    'dontAsk': 'dontAsk',
    'plan': 'plan',
    'bypassPermissions': 'bypass',
}

try:
    data = json.loads(sys.stdin.read())

    username = subprocess.check_output(['git', 'config', '--global', 'user.name'], stderr=subprocess.DEVNULL).decode().strip() or '?'

    cwd = data.get('cwd', '')
    cwd_display = cwd if cwd else '?'

    model = data.get('model', {})
    model_display = model.get('display_name') or model.get('id') or '?'
    if not model_display or model_display == 'null':
        model_display = '?'

    context_window = data.get('context_window', {})
    remaining = context_window.get('remaining_percentage')
    context_pct = remaining if remaining is not None else 100
    context_info = f'{context_pct:.0f}%'

    # 根据剩余上下文选择颜色
    if context_pct > 50:
        ctx_color = '32'   # 绿色 - 充裕
    elif context_pct > 20:
        ctx_color = '33'   # 黄色 - 警告
    else:
        ctx_color = '31'   # 红色 - 紧张

    output_style = data.get('output_style', {})
    style_name = output_style.get('name') if isinstance(output_style, dict) else None
    if not style_name or style_name == 'null':
        style_name = 'default'

    tool_mode = data.get('permission_mode', 'default')
    mode_label = MODE_LABELS.get(tool_mode, tool_mode)

    print(f'\033[35m@{username}\033[0m \033[36m{cwd_display}\033[0m:[\033[34m{model_display}\033[0m|\033[33m{style_name}\033[0m|\033[32m{mode_label}\033[0m]\033[{ctx_color}m({context_info})\033[0m')

except Exception:
    print(f'\033[31m@?\033[0m \033[36m?\033[0m:[\033[31mError\033[0m|\033[35m?\033[0m|\033[31m?\033[0m]\033[33m(100%)\033[0m')
"
