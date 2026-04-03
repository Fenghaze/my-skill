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


def copy_skill_to_repo(skill_name):
    """复制skill到git仓库"""
    skills_dir = Path(CONFIG["skillsDir"])
    repo_dir = Path(CONFIG["repoDir"])

    src = skills_dir / skill_name
    dst = repo_dir / skill_name

    if not src.exists():
        logger.warning(f"Skill {skill_name} not found in {skills_dir}")
        return False

    # 删除旧版本
    if dst.exists():
        shutil.rmtree(dst)

    # 复制新版本
    shutil.copytree(src, dst)
    logger.info(f"Copied skill '{skill_name}' to repo")
    return True


def sync_all_skills():
    """同步所有skills到仓库"""
    skills = get_all_skills()
    logger.info(f"Found {len(skills)} skills to sync")

    # 复制每个skill到仓库
    for skill in skills:
        copy_skill_to_repo(skill['name'])

    # 生成README
    generate_readme(skills)

    # Git提交
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"Sync skills - {timestamp}"
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


def generate_readme(skills):
    """生成仓库README.md"""
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
        if skill_md_path.exists():
            content = skill_md_path.read_text(encoding='utf-8')

            # 提取 ## 使用时机 或 ## 使用方法 部分
            usage = extract_section(content, '使用')
            if usage:
                # 将 ### 子标题降级为普通文本（加粗）
                usage_lines = []
                for line in usage.split('\n'):
                    if line.startswith('### '):
                        usage_lines.append(f"**{line[4:]}**")
                    elif line.startswith('**') and not line.startswith('**安装') and not line.startswith('**启动') and not line.startswith('**手动'):
                        usage_lines.append(line)
                    else:
                        usage_lines.append(line)

                skills_lines.append("**使用方法：**")
                skills_lines.extend(usage_lines)

        skills_lines.append("")

    readme_content = f"""# My Skills

自动化skill同步仓库 - 最后更新时间: {timestamp}

## Skills

{chr(10).join(skills_lines)}

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

        # 只关心SKILL.md文件
        if not event.src_path.endswith('/SKILL.md') and not event.src_path.endswith('\\SKILL.md'):
            return

        # 忽略auto-upload-skill自身的SKILL.md
        if 'auto-upload-skill' in event.src_path:
            return

        logger.info(f"Detected change: {event.src_path} ({event.event_type})")

        # 提取skill名称
        skills_dir = CONFIG["skillsDir"].replace('\\', '/')
        if '/' in event.src_path:
            parts = event.src_path.split('/')
            for i, part in enumerate(parts):
                if part == 'skills' and i + 1 < len(parts):
                    skill_name = parts[i + 1]
                    if skill_name != 'auto-upload-skill':
                        self.pending_sync = True
                        self.trigger_sync(skill_name)
                    break

    def trigger_sync(self, skill_name):
        """触发同步（带防抖）"""
        current_time = time.time() * 1000
        if current_time - self.last_sync_time < self.debounce_ms:
            logger.info(f"Debouncing sync for {skill_name}")
            return

        self.last_sync_time = current_time
        self.pending_sync = False

        logger.info(f"Syncing skill: {skill_name}")
        sync_all_skills()


def start_watcher():
    """启动文件监视"""
    skills_dir = CONFIG["skillsDir"]

    if not os.path.exists(skills_dir):
        logger.error(f"Skills directory not found: {skills_dir}")
        return

    logger.info(f"Starting watcher on: {skills_dir}")

    event_handler = SkillHandler()
    observer = Observer()
    observer.schedule(event_handler, skills_dir, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping watcher...")
        observer.stop()
    observer.join()


# ============ 主程序 ============
def main():
    parser = argparse.ArgumentParser(description='Auto Upload Skill Sync')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    args = parser.parse_args()

    setup_logging()

    if args.daemon:
        logger.info("Starting sync daemon...")
        # 确保repo存在
        repo_dir = Path(CONFIG["repoDir"])
        if not repo_dir.exists():
            logger.info(f"Cloning repository to {repo_dir}")
            os.makedirs(repo_dir, exist_ok=True)
            run_git(f"git clone https://github.com/{CONFIG['githubRepo']}.git .", cwd=repo_dir)
        start_watcher()
    else:
        logger.info("Running single sync...")
        success = sync_all_skills()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
