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
    context_info = f'{remaining:.0f}%' if remaining is not None else '100%'

    output_style = data.get('output_style', {})
    style_name = output_style.get('name') if isinstance(output_style, dict) else None
    if not style_name or style_name == 'null':
        style_name = 'default'

    tool_mode = data.get('permission_mode', 'default')
    mode_label = MODE_LABELS.get(tool_mode, tool_mode)

    print(f'@{username} {cwd_display}:[{model_display}|{style_name}|{mode_label}]({context_info})')

except Exception:
    print(f'@? ?:[?|default|?](100%)')
"
