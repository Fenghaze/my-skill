---
name: auto-upload-skill
description: 本地skill创建后自动上传到GitHub的自动化工具。当用户说"上传skills"、"同步skills"、"push skills"、"/push-skills"或希望将本地skill推送到GitHub时触发。
version: 1.3.0
author: fenghaze
---

# Auto Upload Skill

自动化skill同步工具 - 当您在 `~/.claude/skills/` 目录创建新skill时，自动将其上传到 GitHub 仓库。

## 功能

- **定时自动同步**：支持24小时（可配置）自动上传所有skills到GitHub
- 文件监视：持续监控 `~/.claude/skills/` 目录变化
- **交互确认**：检测到skill变化时，先询问是否上传，确认后执行Git add/commit/push
- **自动生成README**：每次同步后自动更新仓库README，包含所有skills的描述和使用方法
- 后台运行：daemon模式在后台持续运行，可随时选择停止

## 使用方法

### Python 版本（推荐）

**安装依赖：**
```bash
pip install -r C:/Users/Administrator/.claude/skills/auto-upload-skill/scripts/requirements.txt
```

**启动定时自动同步（每24小时）：**
```bash
python C:/Users/Administrator/.claude/skills/auto-upload-skill/scripts/sync.py --schedule
```

**启动定时自动同步（自定义间隔）：**
```bash
python C:/Users/Administrator/.claude/skills/auto-upload-skill/scripts/sync.py --schedule --interval 12
```
自定义间隔单位为小时，例如 `--interval 12` 表示每12小时同步一次。

**启动交互式监视：**
```bash
python C:/Users/Administrator/.claude/skills/auto-upload-skill/scripts/sync.py --daemon
```

当检测到skill变化时，会提示：
```
[auto-upload-skill] Skill 'xxx' 已更新，是否上传到 GitHub？[Y/n]:
```
- 输入 `Y` 或回车：上传并继续监视
- 输入 `n`：跳过上传，询问是否继续监视

**手动同步所有skills：**
```bash
python C:/Users/Administrator/.claude/skills/auto-upload-skill/scripts/sync.py
```

## 配置

配置文件位于：`C:/Users/Administrator/.claude/skills/auto-upload-skill/scripts/config.json`

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| skillsDir | 监视的skills目录 | ~/.claude/skills |
| repoDir | 本地git仓库目录 | ~/.claude/skills-sync-repo |
| githubRepo | GitHub仓库 | Fenghaze/my-skill |
| debounceMs | 防抖延迟(ms) | 5000 |

## 工作原理

### 定时同步模式 (--schedule)
1. 启动后立即执行首次同步
2. 每隔指定间隔（默认24小时）自动执行同步
3. 将所有skills复制到本地git仓库
4. 解析所有skill的SKILL.md，生成/更新README.md
5. 执行 git add → commit → push
6. 记录下次同步时间，可通过 Ctrl+C 停止

### 交互式监视模式 (--daemon)
1. daemon使用 watchdog 监视 `~/.claude/skills/*/SKILL.md` 文件
2. 检测到变化后，等待5秒防抖
3. **询问用户是否确认上传**（跳过自动上传）
4. 用户确认后，将变化的skill复制到本地git仓库
5. **解析所有skill的SKILL.md，生成/更新README.md**（包含表格和详细文档）
6. 执行 git add → commit → push
7. 询问用户是否继续监视，可随时选择退出

## README自动生成内容

每次同步后，仓库的README.md会自动更新：

- **头部信息**：仓库名、最后更新时间、GitHub链接
- **Skills表格**：所有skill的名称、描述、版本、作者
- **Quick Start**：安装指南和常用命令
- **Individual Skill Docs**：每个skill的详细文档预览（前30行）

## 验证同步成功

访问 GitHub 仓库确认提交记录：
https://github.com/Fenghaze/my-skill

## 故障排除

**SSH认证失败**
- 确认 `~/.ssh/id_rsa.pub` 已添加到 GitHub
- 测试： `ssh -T git@github.com`

**daemon无响应**
- 检查日志： `C:/Users/Administrator/.claude/skills/auto-upload-skill/scripts/sync.log`
- 重启daemon
