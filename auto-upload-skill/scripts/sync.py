#!/usr/bin/env python3
"""
Auto Upload Skill - 同步脚本
当本地skills目录有变化时，自动将其同步到GitHub仓库
"""

import os
import sys
import json
import time
import shutil
import logging
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent


# ============ 配置 ============
CONFIG_PATH = Path(__file__).parent / "config.json"

def load_config():
    """加载配置文件"""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "skillsDir": os.path.expanduser("~/.claude/skills"),
        "commandsDir": os.path.expanduser("~/.claude/commands"),
        "repoDir": os.path.expanduser("~/.claude/skills-sync-repo"),
        "githubRepo": "Fenghaze/my-skill",
        "branch": "main",
        "debounceMs": 5000,
        "logFile": os.path.join(os.path.dirname(__file__), "sync.log")
    }

CONFIG = load_config()

# ============ 日志配置 ============
def setup_logging():
    log_file = CONFIG.get("logFile")
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


# ============ Git 操作 ============
def run_git(cmd, cwd=None):
    """执行git命令"""
    result = subprocess.run(
        cmd, shell=True, cwd=cwd,
        capture_output=True, text=True
    )
    return result.returncode, result.stdout, result.stderr


def git_add_commit_push(message):
    """Git add -> commit -> push"""
    repo_dir = CONFIG["repoDir"]

    # Add all changes
    rc, stdout, stderr = run_git("git add -A", cwd=repo_dir)
    if rc != 0:
        logger.error(f"git add failed: {stderr}")
        return False

    # Check if there are changes to commit
    rc, stdout, stderr = run_git("git status --porcelain", cwd=repo_dir)
    if not stdout.strip():
        logger.info("No changes to commit")
        return True

    # Commit
    rc, stdout, stderr = run_git(f'git commit -m "{message}"', cwd=repo_dir)
    if rc != 0:
        logger.error(f"git commit failed: {stderr}")
        return False

    # Push
    rc, stdout, stderr = run_git(f"git push origin {CONFIG['branch']}", cwd=repo_dir)
    if rc != 0:
        logger.error(f"git push failed: {stderr}")
        return False

    logger.info("Successfully pushed to GitHub")
    return True


# ============ Skill 同步 ============
def get_all_skills():
    """获取所有skill信息"""
    skills_dir = Path(CONFIG["skillsDir"])
    skills = []

    if not skills_dir.exists():
        return skills

    for skill_path in skills_dir.iterdir():
        if skill_path.is_dir() and (skill_path / "SKILL.md").exists():
            skill_md = skill_path / "SKILL.md"
            try:
                content = skill_md.read_text(encoding='utf-8')
                skill_info = parse_skill_md(content)
                skill_info['name'] = skill_path.name
                skill_info['path'] = str(skill_path)
                skills.append(skill_info)
            except Exception as e:
                logger.warning(f"Failed to parse {skill_path.name}/SKILL.md: {e}")

    return skills


def get_all_commands():
    """获取所有command文件信息"""
    commands_dir = Path(CONFIG["commandsDir"])
    commands = []

    if not commands_dir.exists():
        return commands

    for cmd_path in commands_dir.iterdir():
        if cmd_path.is_file() and not is_excluded(str(cmd_path)):
            cmd_info = {
                'name': cmd_path.name,
                'path': str(cmd_path),
                'description': ''
            }
            # 尝试读取文件前几行作为描述
            try:
                content = cmd_path.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')
                # 取第一行非空行作为描述
                for line in lines:
                    stripped = line.strip()
                    if stripped and not stripped.startswith('#'):
                        cmd_info['description'] = stripped[:100]
                        break
                    elif stripped.startswith('#'):
                        # 跳过注释行，继续找
                        continue
            except Exception as e:
                logger.warning(f"Failed to read {cmd_path.name}: {e}")
            commands.append(cmd_info)

    return commands


def parse_skill_md(content):
    """解析SKILL.md内容，提取frontmatter信息"""
    info = {
        'name': '',
        'description': '',
        'version': '',
        'author': ''
    }

    lines = content.split('\n')
    in_frontmatter = False
    frontmatter_lines = []

    for line in lines:
        if line.strip() == '---':
            if in_frontmatter:
                # End of frontmatter
                break
            in_frontmatter = True
            continue

        if in_frontmatter:
            frontmatter_lines.append(line)

    # 解析frontmatter
    for line in frontmatter_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key in info:
                info[key] = value

    return info


# 排除的文件模式
EXCLUDE_PATTERNS = {
    # 日志文件
    '.log', '*.log',
    # 敏感信息
    '.env', '.env.*', 'credentials.json', '*.pem', '*.key', '*.p12', '*.pfx',
    'id_rsa', 'id_rsa.*', '*.secret', '*.token',
    # 临时文件
    '.tmp', '*.tmp', '.cache', '__pycache__', '*.pyc',
    # 系统文件
    '.DS_Store', 'Thumbs.db', 'desktop.ini',
    # 本地配置
    '.claude', '.vscode', '.idea',
}

def is_excluded(path):
    """检查路径是否应该被排除"""
    name = os.path.basename(path)

    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith('*'):
            # 通配符匹配
            if name.endswith(pattern[1:]):
                return True
        elif name == pattern or name.startswith(pattern):
            return True

    # 检查路径中是否包含敏感关键词
    sensitive_keywords = ['password', 'secret', 'token', 'credential', 'private', 'api_key']
    path_lower = path.lower()
    for keyword in sensitive_keywords:
        if keyword in path_lower:
            return True

    return False


def increment_version(content):
    """递增版本号，返回新内容和是否更新"""
    lines = content.split('\n')
    new_lines = []
    version_found = False
    updated = False

    for line in lines:
        if line.strip().startswith('version:'):
            version_found = True
            # 解析版本号
            parts = line.split(':', 1)
            if len(parts) == 2:
                old_version = parts[1].strip().strip('"').strip("'")
                try:
                    # 尝试解析 x.x.x 格式
                    ver_parts = old_version.split('.')
                    if len(ver_parts) == 3:
                        # 递增 patch 版本
                        patch = int(ver_parts[2]) + 1
                        new_version = f"{ver_parts[0]}.{ver_parts[1]}.{patch}"
                        new_line = line.replace(old_version, new_version)
                        new_lines.append(new_line)
                        logger.info(f"Version updated: {old_version} -> {new_version}")
                        updated = True
                        continue
                except (ValueError, IndexError):
                    pass
        new_lines.append(line)

    if not version_found:
        # 如果没有版本号，在frontmatter开头添加
        new_lines.insert(1, "version: 1.0.0")
        updated = True
        logger.info("Added version: 1.0.0")

    return '\n'.join(new_lines), updated


def copy_skill_to_repo(skill_name):
    """复制skill到git仓库，如有变化则更新版本号"""
    skills_dir = Path(CONFIG["skillsDir"])
    repo_dir = Path(CONFIG["repoDir"])

    src = skills_dir / skill_name
    dst = repo_dir / skill_name

    if not src.exists():
        logger.warning(f"Skill {skill_name} not found in {skills_dir}")
        return False

    # 检查 SKILL.md 是否有变化（对比源和目标）
    src_skill_md = src / "SKILL.md"
    dst_skill_md = dst / "SKILL.md" if dst.exists() else None

    version_updated = False
    if src_skill_md.exists():
        src_content = src_skill_md.read_text(encoding='utf-8')
        if dst_skill_md and dst_skill_md.exists():
            dst_content = dst_skill_md.read_text(encoding='utf-8')
            if src_content != dst_content:
                # 有变化，递增版本号
                new_content, version_updated = increment_version(src_content)
                if version_updated:
                    src_skill_md.write_text(new_content, encoding='utf-8')
                    logger.info(f"Auto-incremented version for '{skill_name}'")

    # 删除旧版本
    if dst.exists():
        shutil.rmtree(dst)

    # 复制新版本（排除敏感文件）
    os.makedirs(dst)

    for root, dirs, files in os.walk(src):
        # 排除目录
        dirs[:] = [d for d in dirs if not is_excluded(os.path.join(root, d))]

        for file in files:
            src_file = os.path.join(root, file)
            rel_path = os.path.relpath(src_file, src)

            if is_excluded(src_file):
                logger.info(f"Skipping excluded file: {skill_name}/{rel_path}")
                continue

            dst_file = os.path.join(dst, rel_path)
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
            shutil.copy2(src_file, dst_file)

    logger.info(f"Copied skill '{skill_name}' to repo")
    return True


def copy_command_to_repo(cmd_name):
    """复制command到git仓库的commands目录"""
    commands_dir = Path(CONFIG["commandsDir"])
    repo_dir = Path(CONFIG["repoDir"])

    src = commands_dir / cmd_name
    dst = repo_dir / "commands" / cmd_name

    if not src.exists():
        logger.warning(f"Command {cmd_name} not found in {commands_dir}")
        return False

    # 删除旧版本
    if dst.exists():
        shutil.rmtree(dst)

    # 复制文件（排除敏感文件）
    if is_excluded(str(src)):
        logger.info(f"Skipping excluded command: {cmd_name}")
        return False

    os.makedirs(dst.parent, exist_ok=True)
    shutil.copy2(src, dst)

    logger.info(f"Copied command '{cmd_name}' to repo")
    return True


def sync_all():
    """同步所有skills和commands到仓库"""
    skills = get_all_skills()
    logger.info(f"Found {len(skills)} skills to sync")

    # 复制每个skill到仓库
    for skill in skills:
        copy_skill_to_repo(skill['name'])

    # 同步commands
    commands = get_all_commands()
    logger.info(f"Found {len(commands)} commands to sync")

    # 删除旧的commands目录，重新同步
    repo_dir = Path(CONFIG["repoDir"])
    commands_repo_dir = repo_dir / "commands"
    if commands_repo_dir.exists():
        shutil.rmtree(commands_repo_dir)

    for cmd in commands:
        copy_command_to_repo(cmd['name'])

    # 生成README
    generate_readme(skills, commands)

    # Git提交
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"Sync skills and commands - {timestamp}"
    return git_add_commit_push(message)


def sync_single_skill(skill_name):
    """同步单个skill到仓库"""
    logger.info(f"Syncing single skill: {skill_name}")

    # 复制单个skill到仓库
    if not copy_skill_to_repo(skill_name):
        return False

    # 获取所有skills来生成README
    skills = get_all_skills()
    commands = get_all_commands()
    generate_readme(skills, commands)

    # Git提交
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"Update skill: {skill_name} - {timestamp}"
    return git_add_commit_push(message)


def sync_single_command(cmd_name):
    """同步单个command到仓库"""
    logger.info(f"Syncing single command: {cmd_name}")

    # 复制单个command到仓库
    if not copy_command_to_repo(cmd_name):
        return False

    # 获取所有skills和commands来生成README
    skills = get_all_skills()
    commands = get_all_commands()
    generate_readme(skills, commands)

    # Git提交
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"Update command: {cmd_name} - {timestamp}"
    return git_add_commit_push(message)


def extract_section(content, section_name):
    """提取指定section的内容"""
    lines = content.split('\n')
    section_lines = []
    in_section = False

    for i, line in enumerate(lines):
        # 匹配section标题
        if line.startswith('## ') and section_name in line:
            in_section = True
            continue

        if in_section:
            # 遇到同级或更高级标题时结束（## 开头的标题）
            if line.startswith('## ') and not line.startswith('###'):
                break
            # 跳过开头和结尾的空行
            if not line.strip():
                if not section_lines:
                    continue
                section_lines.append(line)
            else:
                section_lines.append(line.lstrip())

    # 移除结尾的空行
    while section_lines and not section_lines[-1].strip():
        section_lines.pop()

    return '\n'.join(section_lines)


def get_usage_content(skill_md_path):
    """获取skill的使用说明内容"""
    if not skill_md_path.exists():
        return ""

    content = skill_md_path.read_text(encoding='utf-8')

    # 先尝试中文"使用"章节
    usage = extract_section(content, '使用')
    if usage:
        return usage

    # 尝试英文"When to Use"章节
    usage = extract_section(content, 'When to Use')
    if usage:
        return usage

    # 尝试"How to"章节
    usage = extract_section(content, 'How to')
    return usage


def generate_readme(skills, commands=None):
    """生成仓库README.md"""
    if commands is None:
        commands = []
    repo_dir = Path(CONFIG["repoDir"])
    github_repo = CONFIG["githubRepo"]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    readme_path = repo_dir / "README.md"

    # 构建简化的README
    skills_lines = []
    for skill in skills:
        name = skill.get('name', '')
        desc = skill.get('description', '')
        version = skill.get('version', '')

        skills_lines.append(f"### {name}")
        skills_lines.append(f"**描述：** {desc}")
        skills_lines.append("")

        # 读取skill的SKILL.md
        skill_md_path = Path(skill.get('path', '')) / "SKILL.md"
        usage = get_usage_content(skill_md_path)
        if usage:
            # 将 ### 子标题降级为普通文本（加粗）
            usage_lines = []
            for line in usage.split('\n'):
                if line.startswith('### '):
                    usage_lines.append(f"**{line[4:]}**")
                elif line.startswith('**') and not line.startswith('**安装') and not line.startswith('**启动') and not line.startswith('**手动') and not line.startswith('**搜索') and not line.startswith('**查看') and not line.startswith('**更新'):
                    usage_lines.append(line)
                else:
                    usage_lines.append(line)

            skills_lines.append("**使用方法：**")
            skills_lines.extend(usage_lines)

        skills_lines.append("")

    # Commands部分
    commands_lines = []
    if commands:
        commands_lines.append("## Commands")
        commands_lines.append("")
        commands_lines.append("| 命令 | 描述 |")
        commands_lines.append("|------|------|")
        for cmd in commands:
            name = cmd.get('name', '')
            desc = cmd.get('description', '')
            commands_lines.append(f"| `{name}` | {desc} |")
        commands_lines.append("")

    readme_content = f"""# My Skills

自动化skill同步仓库 - 最后更新时间: {timestamp}

## Skills

{chr(10).join(skills_lines)}

{chr(10).join(commands_lines)}
---
_Generated by auto-upload-skill_
"""

    readme_path.write_text(readme_content, encoding='utf-8')
    logger.info(f"Generated README.md with {len(skills)} skills")


# ============ 文件监视 ============
class SkillHandler(FileSystemEventHandler):
    """Skill文件变化处理"""
    def __init__(self):
        super().__init__()
        self.pending_sync = False
        self.last_sync_time = 0
        self.debounce_ms = CONFIG.get("debounceMs", 5000)

    def on_any_event(self, event):
        if event.is_directory:
            return

        # 检查是skill还是command
        skills_dir = CONFIG["skillsDir"].replace('\\', '/')
        commands_dir = CONFIG["commandsDir"].replace('\\', '/')

        # 只关心SKILL.md文件或commands目录下的文件
        is_skill = event.src_path.endswith('/SKILL.md') or event.src_path.endswith('\\SKILL.md')
        is_command = event.src_path.startswith(skills_dir) or event.src_path.startswith(commands_dir)

        if not (is_skill or (is_command and not is_skill)):
            # 如果不是SKILL.md，也不是commands目录下的文件，则忽略
            return

        # 忽略auto-upload-skill自身的SKILL.md
        if 'auto-upload-skill' in event.src_path:
            return

        logger.info(f"Detected change: {event.src_path} ({event.event_type})")

        # 提取skill或command名称
        if is_skill:
            if '/' in event.src_path:
                parts = event.src_path.split('/')
                for i, part in enumerate(parts):
                    if part == 'skills' and i + 1 < len(parts):
                        skill_name = parts[i + 1]
                        if skill_name != 'auto-upload-skill':
                            self.pending_sync = True
                            self.trigger_sync(skill_name=skill_name)
                        break
        else:
            # command文件变化
            if '/' in event.src_path:
                parts = event.src_path.split('/')
                for i, part in enumerate(parts):
                    if part == 'commands' and i + 1 < len(parts):
                        cmd_name = parts[i + 1]
                        self.pending_sync = True
                        self.trigger_sync(cmd_name=cmd_name)
                        break

    def trigger_sync(self, skill_name=None, cmd_name=None):
        """触发同步（带防抖和用户确认）"""
        current_time = time.time() * 1000
        name = skill_name or cmd_name
        item_type = "Skill" if skill_name else "Command"

        if current_time - self.last_sync_time < self.debounce_ms:
            logger.info(f"Debouncing sync for {name}")
            return

        self.last_sync_time = current_time
        self.pending_sync = False

        logger.info(f"Detected change in {item_type.lower()}: {name}")

        # 询问用户是否上传
        try:
            response = input(f"\n[auto-upload-skill] {item_type} '{name}' 已更新，是否上传到 GitHub？[Y/n]: ").strip().lower()
        except EOFError:
            logger.info("No terminal input available, skipping upload")
            return

        if response == 'n':
            logger.info("Upload skipped by user")
            # 询问是否继续监视
            try:
                continue_response = input(f"[auto-upload-skill] 是否继续监视其他变化？[y/N]: ").strip().lower()
            except EOFError:
                continue_response = 'n'

            if continue_response != 'y':
                logger.info("Stopping watcher as requested by user")
                # 通过设置一个标志来停止watcher
                self.stop_watcher = True
            return

        # 执行同步
        if skill_name:
            logger.info(f"Uploading skill: {skill_name}")
            success = sync_single_skill(skill_name)
            item_name = skill_name
        else:
            logger.info(f"Uploading command: {cmd_name}")
            success = sync_single_command(cmd_name)
            item_name = cmd_name

        if success:
            print(f"[auto-upload-skill] ✓ {item_type} '{item_name}' 已成功上传到 GitHub")
        else:
            print(f"[auto-upload-skill] ✗ {item_type} '{item_name}' 上传失败，请查看日志")

        # 询问是否继续监视
        try:
            continue_response = input(f"[auto-upload-skill] 是否继续监视其他变化？[y/N]: ").strip().lower()
        except EOFError:
            continue_response = 'n'

        if continue_response != 'y':
            logger.info("Stopping watcher as requested by user")
            self.stop_watcher = True

    def stop_watcher_request(self):
        """请求停止watcher"""
        self.stop_watcher = True


def start_watcher():
    """启动文件监视"""
    skills_dir = CONFIG["skillsDir"]
    commands_dir = CONFIG["commandsDir"]

    if not os.path.exists(skills_dir):
        logger.error(f"Skills directory not found: {skills_dir}")
        return

    logger.info(f"Starting watcher on: {skills_dir}")
    if os.path.exists(commands_dir):
        logger.info(f"Starting watcher on: {commands_dir}")

    event_handler = SkillHandler()
    event_handler.stop_watcher = False
    observer = Observer()
    observer.schedule(event_handler, skills_dir, recursive=True)
    if os.path.exists(commands_dir):
        observer.schedule(event_handler, commands_dir, recursive=False)
    observer.start()

    try:
        while not event_handler.stop_watcher:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping watcher...")
        event_handler.stop_watcher = True
    observer.stop()
    observer.join()
    logger.info("Watcher stopped")


# ============ 定时同步 ============
def ensure_repo():
    """确保git仓库存在"""
    repo_dir = Path(CONFIG["repoDir"])
    if not repo_dir.exists():
        logger.info(f"Cloning repository to {repo_dir}")
        os.makedirs(repo_dir, exist_ok=True)
        rc, stdout, stderr = run_git(f"git clone https://github.com/{CONFIG['githubRepo']}.git .", cwd=repo_dir)
        if rc != 0:
            logger.error(f"Failed to clone repo: {stderr}")
            return False
    return True


def run_scheduled_sync(interval_hours=24):
    """定时同步所有skills"""
    interval_seconds = interval_hours * 3600
    logger.info(f"Starting scheduled sync every {interval_hours} hours")

    # 首次同步
    logger.info("Running initial sync...")
    if not ensure_repo():
        return
    sync_all()

    next_sync_time = time.time() + interval_seconds
    logger.info(f"Next sync scheduled at: {datetime.fromtimestamp(next_sync_time).strftime('%Y-%m-%d %H:%M:%S')}")

    while True:
        try:
            time.sleep(10)  # 每10秒检查一次

            current_time = time.time()
            if current_time >= next_sync_time:
                logger.info("Scheduled sync triggered")
                sync_all()
                next_sync_time = current_time + interval_seconds
                logger.info(f"Next sync scheduled at: {datetime.fromtimestamp(next_sync_time).strftime('%Y-%m-%d %H:%M:%S')}")

        except KeyboardInterrupt:
            logger.info("Stopping scheduled sync...")
            break

    logger.info("Scheduled sync stopped")


# ============ 主程序 ============
def main():
    parser = argparse.ArgumentParser(description='Auto Upload Skill Sync')
    parser.add_argument('--daemon', action='store_true', help='交互式文件监视模式')
    parser.add_argument('--schedule', action='store_true', help='定时自动同步模式')
    parser.add_argument('--interval', type=int, default=24, help='定时同步间隔（小时），默认24小时')
    args = parser.parse_args()

    setup_logging()

    if args.daemon:
        logger.info("Starting sync daemon...")
        if not ensure_repo():
            sys.exit(1)
        start_watcher()
    elif args.schedule:
        logger.info(f"Starting scheduled sync with {args.interval} hour interval...")
        run_scheduled_sync(args.interval)
    else:
        logger.info("Running single sync...")
        if not ensure_repo():
            sys.exit(1)
        success = sync_all()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
