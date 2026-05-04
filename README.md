<p align="center">
  <img src="https://img.shields.io/badge/skill-Agent%20Skills-black" alt="Agent Skills">
  <img src="https://img.shields.io/badge/Claude%20Code-compatible-blue" alt="Claude Code">
  <img src="https://img.shields.io/badge/Codex-compatible-green" alt="Codex">
  <img src="https://img.shields.io/badge/OpenCode-compatible-purple" alt="OpenCode">
  <img src="https://img.shields.io/badge/python-3.10%2B-lightgrey" alt="Python">
</p>

# Project Structure Viewer

**一个可以装进 Claude Code、Codex、OpenCode 的 Agent Skill。**

它的目标很简单：当你打开一个陌生项目时，不用先在几十个目录里迷路。让 agent 先读代码，再生成一个可交互的 `structure.html`，把项目目录、关键文件、阅读顺序和代码流转关系一次性展开。

This repository is skill-first. `SKILL.md` is the product; `generate.py` is the bundled helper script.

---

## 这是什么

Project Structure Viewer 是一个基于 `SKILL.md` 的跨工具 skill 包，适合安装到支持 Agent Skills / SKILL.md 的 coding agent 中。

当你对 agent 说：

```text
帮我理解这个项目结构
生成这个仓库的结构图
Show me the structure of this codebase
Use project-structure-viewer on this repo
```

agent 会按 `SKILL.md` 的流程工作：

1. 读取项目的真实源码和配置，而不是只扫文件名
2. 识别入口、路由、数据层、页面、组件、部署和文档等关键文件
3. 生成分阶段的阅读路线图
4. 调用 `generate.py` 输出单文件 HTML
5. 告诉你 `structure.html` 在哪里打开

---

## 能做什么

- 完整项目树：从根目录向右展开的水平树状图
- 阅读路线图：按阶段组织关键文件，而不是扔给你一坨平铺列表
- 搜索与跳转：搜索文件名，点击结果定位节点
- 展开与收起：快速看全局，也能逐层钻进去
- 平移与缩放：适合大项目浏览
- 点击打开文件：生成 `file://` 链接，方便跳回本机编辑器
- 中英文界面：生成页面自带语言切换
- 单文件输出：HTML 内嵌 CSS / JS，不需要前端构建

---

## 安装

先把这个仓库克隆到一个稳定位置：

```bash
mkdir -p ~/agent-skills
git clone https://github.com/1m01m0/project-structure-viewer.git \
  ~/agent-skills/project-structure-viewer
```

然后按你使用的工具放到对应的 skills 目录。目录结构必须是：

```text
<skills-dir>/project-structure-viewer/SKILL.md
```

### Claude Code

个人全局安装：

```bash
mkdir -p ~/.claude/skills
ln -s ~/agent-skills/project-structure-viewer \
  ~/.claude/skills/project-structure-viewer
```

项目内安装：

```bash
mkdir -p .claude/skills
ln -s ~/agent-skills/project-structure-viewer \
  .claude/skills/project-structure-viewer
```

### Codex

Codex 的官方本地发现目录使用 Agent Skills 标准路径。

个人全局安装：

```bash
mkdir -p ~/.agents/skills
ln -s ~/agent-skills/project-structure-viewer \
  ~/.agents/skills/project-structure-viewer
```

项目内安装：

```bash
mkdir -p .agents/skills
ln -s ~/agent-skills/project-structure-viewer \
  .agents/skills/project-structure-viewer
```

如果你使用 Codex 内置的 skill installer，也可以直接让 Codex 安装这个 GitHub 仓库目录。

### OpenCode

OpenCode 支持自己的 skills 目录，也会读取 Claude-compatible 和 agent-compatible skills 目录。也就是说，如果你已经装到 `~/.agents/skills` 或 `~/.claude/skills`，OpenCode 通常不需要重复安装。

个人全局安装：

```bash
mkdir -p ~/.config/opencode/skills
ln -s ~/agent-skills/project-structure-viewer \
  ~/.config/opencode/skills/project-structure-viewer
```

项目内安装：

```bash
mkdir -p .opencode/skills
ln -s ~/agent-skills/project-structure-viewer \
  .opencode/skills/project-structure-viewer
```

可选的共享安装路径：

```bash
mkdir -p ~/.agents/skills
ln -s ~/agent-skills/project-structure-viewer \
  ~/.agents/skills/project-structure-viewer
```

---

## 更新

如果你按上面的方式克隆到 `~/agent-skills/project-structure-viewer`：

```bash
git -C ~/agent-skills/project-structure-viewer pull
```

如果你的 agent 在启动时扫描 skills，更新后重启一次 agent 最稳。

---

## 使用

在任意代码项目里打开 Claude Code、Codex 或 OpenCode，然后直接描述你的意图：

```text
帮我理解这个项目结构，生成一个可交互的结构图
```

生成结果默认是：

```text
<your-project>/structure.html
```

用浏览器打开即可。页面里的文件节点会使用 `file://` 链接指向你的本机路径。

---

## 手动运行

你也可以不通过 agent，直接运行脚本：

```bash
python3 generate.py <scanPath> <linkRoot> <outputDir>
```

参数说明：

| 参数 | 说明 |
| --- | --- |
| `scanPath` | 要扫描的项目目录 |
| `linkRoot` | 生成 `file://` 链接时使用的本机路径，通常和 `scanPath` 相同 |
| `outputDir` | `structure.html` 的输出目录，不存在时会自动创建 |

示例：

```bash
python3 generate.py ~/my-project ~/my-project ~/my-project
open ~/my-project/structure.html
```

如果 agent 运行在沙箱或容器里，扫描路径和本机链接路径可能不同：

```bash
python3 generate.py \
  /sessions/abc/mnt/Desktop/my-project \
  /Users/you/Desktop/my-project \
  /sessions/abc/mnt/Desktop/my-project
```

---

## 仓库结构

```text
project-structure-viewer/
├── SKILL.md     # skill 入口，定义触发条件和工作流
├── generate.py  # 生成自包含 HTML 的脚本
├── README.md    # 安装与使用说明
└── LICENSE      # MIT license
```

---

## 兼容性说明

这个仓库遵循 Agent Skills 的基本形态：一个包含 `SKILL.md` 的目录，可以携带脚本、参考资料和其他资源。

相关文档：

- [Agent Skills open standard](https://agentskills.io/)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Codex Agent Skills](https://developers.openai.com/codex/skills)
- [OpenAI skills catalog for Codex](https://github.com/openai/skills)
- [OpenCode Agent Skills](https://opencode.ai/docs/skills)

---

## License

MIT
