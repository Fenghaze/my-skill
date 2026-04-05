#!/bin/bash
# Claude Code Status Line Plugin
# 格式: 工作目录:[模型|风格|Ctx:%|模式]

/d/Miniconda/python.exe -c "
import sys, json, subprocess

MODE_LABELS = {
    'default': '\033[33mask\033[0m',
    'acceptEdits': '\033[32macceptEdits\033[0m',
    'auto': '\033[32mauto\033[0m',
    'dontAsk': '\033[31mdontAsk\033[0m',
    'plan': '\033[36mplan\033[0m',
    'bypassPermissions': '\033[35mbypass\033[0m',
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
    mode_label = MODE_LABELS.get(tool_mode, f'\033[33m{tool_mode}\033[0m')

    print(f'\033[33m@{username}\033[0m \033[36m{cwd_display}\033[0m:[\033[33m{model_display}\033[0m|\033[35m{style_name}\033[0m|{mode_label}]\033[32m({context_info})\033[0m')

except Exception:
    print(f'\033[33m@\033[0m \033[36m?\033[0m:[\033[31mError\033[0m|\033[33mdefault\033[0m]\033[32m(100%)\033[0m')
"
