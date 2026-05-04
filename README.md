<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/output-single%20HTML-green" alt="Output">
  <img src="https://img.shields.io/badge/deps-none-brightgreen" alt="Deps">
  <img src="https://img.shields.io/badge/license-MIT-lightgrey" alt="License">
</p>

# Project Structure Viewer / 项目结构图生成器

**One command → one HTML file → your entire codebase as an interactive horizontal tree map.**

**一行命令 → 一个 HTML 文件 → 整个项目变成可交互的水平树状思维导图。**

[English](#english) | [中文](#中文)

---

## English

### What It Does

You get a new codebase. Dozens of folders, hundreds of files. Where do you start?

Project Structure Viewer scans the entire directory and produces a **single, self-contained HTML file** that renders the complete project as a **left-to-right horizontal tree diagram** — like an org chart for your code.

Every file is clickable — opens directly in your editor via `file://` links. No install, no dependencies, no build step.

### Features

- **Horizontal tree layout** — root on the left, each directory level expands to the right with elbow connector lines
- **Pan & zoom** — drag to move, scroll to zoom (tuned for both mouse wheels and trackpads)
- **Full-text search** — type to filter; dropdown shows matching files with paths, click to jump
- **Expand / collapse** — click folders to drill down; "Expand All" / "Collapse" buttons
- **Reading guide** — auto-detects key files (entry points, routers, schemas, pages) and describes each one's role
- **Bilingual UI** — toggle between English and Chinese with one click
- **Black background, white text** — minimal, clean, no distractions
- **Zero dependencies** — the output is a single HTML file with embedded CSS and JS

### Quick Start

```bash
git clone https://github.com/1m01m0/project-structure-viewer.git
cd project-structure-viewer

# Run against any project
python3 generate.py ~/my-project ~/my-project ~/my-project

# Open the result
open ~/my-project/structure.html
```

### Usage

```
python3 generate.py <scanPath> <linkRoot> <outputDir>
```

| Argument | Description |
|----------|-------------|
| `scanPath` | Directory to scan (filesystem path) |
| `linkRoot` | Host path for `file://` links (usually same as scanPath) |
| `outputDir` | Where to write `structure.html` (usually same as scanPath) |

### How It Works

1. `os.listdir()` recursively walks the directory
2. Files/dirs are sorted (dirs first, alphabetically)
3. Ignore patterns filter out noise (node_modules, .git, etc.)
4. Key files are auto-detected by name/path heuristics
5. Compact JSON tree is embedded in the HTML
6. JavaScript renders the horizontal tree with SVG connector lines, search, and interactions

### Configuration

Edit the `IGNORE` list in `generate.py` to customize filtered patterns:

```python
IGNORE = [
    'node_modules', '.git', '__pycache__', '.pnpm',
    '*.pyc', '*.pyo', '.DS_Store', 'Thumbs.db',
    # ... add your own patterns
]
```

Edit `flow_set()` to customize which files are highlighted as key files.

### File Structure

```
project-structure-viewer/
├── README.md          ← You are here
├── SKILL.md           ← Codex skill definition
├── generate.py        ← The generator script (all you need)
└── LICENSE            ← MIT license
```

### Codex Skill

Also available as a Codex skill. Install once, then say "help me understand this project" — the skill handles path resolution and generates the HTML automatically.

### License

MIT

---

## 中文

### 这是什么

拿到一个新项目，几十个文件夹、几百个文件，从哪看起？

项目结构图生成器扫描整个目录，生成一个**自包含的 HTML 文件**，以**从左到右的水平树状图**呈现完整的项目结构——就像代码的组织架构图。

每个文件节点都可以点击，通过 `file://` 链接直接在编辑器中打开。无需安装，无依赖，无构建步骤。

### 功能特性

- **水平树状布局** — 根目录在左侧，每级目录向右延伸，父子节点用直角肘形连线
- **拖拽平移 & 滚轮缩放** — 鼠标拖拽移动，滚轮缩放（已针对鼠标和触控板分别调优）
- **全文搜索** — 输入即过滤，下拉列表显示匹配文件及路径，点击跳转
- **展开 / 收起** — 点击文件夹展开子目录，提供「全部展开」「全部收起」按钮
- **阅读路线图** — 自动识别关键文件（入口点、路由、数据模型、页面组件），逐一描述作用
- **中英文切换** — 一键切换界面语言，阅读路线图内容同步翻译
- **黑底白字** — 极简风格，无干扰
- **零依赖** — 输出为单个 HTML 文件，CSS 和 JS 全部内嵌

### 快速开始

```bash
git clone https://github.com/1m01m0/project-structure-viewer.git
cd project-structure-viewer

# 对任意项目运行
python3 generate.py ~/my-project ~/my-project ~/my-project

# 打开生成的文件
open ~/my-project/structure.html
```

### 用法

```
python3 generate.py <扫描路径> <链接根路径> <输出目录>
```

| 参数 | 说明 |
|------|------|
| `扫描路径` | 要扫描的目录（文件系统路径） |
| `链接根路径` | `file://` 链接使用的主机路径（通常与扫描路径相同） |
| `输出目录` | `structure.html` 的写入位置（通常与扫描路径相同） |

如果脚本运行在沙箱/VM 环境中，扫描路径和链接路径可能不同：

```bash
python3 generate.py \
  /sessions/abc/mnt/Desktop/myproject \
  /Users/emo/Desktop/myproject \
  /sessions/abc/mnt/Desktop/myproject
```

### 工作原理

1. `os.listdir()` 递归遍历目录
2. 文件/目录排序（目录优先，字母顺序）
3. 忽略规则过滤噪声文件（node_modules、.git 等）
4. 通过文件名/路径模式自动识别关键文件
5. 将紧凑 JSON 树嵌入 HTML
6. JavaScript 渲染水平树、SVG 连线、搜索和交互

### 自定义配置

编辑 `generate.py` 中的 `IGNORE` 列表来定制过滤规则：

```python
IGNORE = [
    'node_modules', '.git', '__pycache__', '.pnpm',
    '*.pyc', '*.pyo', '.DS_Store', 'Thumbs.db',
    # ... 添加你自己的规则
]
```

编辑 `flow_set()` 函数来自定义哪些文件被标记为关键文件。

### 文件结构

```
project-structure-viewer/
├── README.md          ← 你正在看
├── SKILL.md           ← Codex 技能定义
├── generate.py        ← 生成器脚本（唯一需要的文件）
└── LICENSE            ← MIT 许可证
```

### Codex 技能

同时支持作为 Codex 技能使用。安装一次后，说「帮我理解这个项目结构」即可自动生成。

### 许可证

MIT

---

<p align="center">
  <sub>Built for developers who open a new codebase and think "...where do I even start?"</sub><br>
  <sub>为每次打开新项目不知道从哪看起的开发者而建</sub>
</p>
