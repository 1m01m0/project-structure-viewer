# Project Structure Viewer

Project Structure Viewer 是一个 Agent Skill，用于读取项目并生成可交互的 `structure.html` 结构图。入口是 [SKILL.md](SKILL.md)，确定性生成器位于 [scripts/generate.py](scripts/generate.py)。

## 安装

推荐用 `npx skills` 从 GitHub 安装：

```bash
npx skills add 1m01m0/project-structure-viewer
```

只安装到指定 agent：

```bash
npx skills add 1m01m0/project-structure-viewer \
  -a claude-code -a codex -a opencode
```

全局安装：

```bash
npx skills add 1m01m0/project-structure-viewer -g
```

先查看仓库里可安装的 skill：

```bash
npx skills add 1m01m0/project-structure-viewer --list
```

如果你不使用 `npx skills`，也可以手动 clone 后放到任一兼容目录：

```text
~/.claude/skills/project-structure-viewer/SKILL.md
~/.agents/skills/project-structure-viewer/SKILL.md
~/.config/opencode/skills/project-structure-viewer/SKILL.md
```

## 手动运行脚本

通常不需要手动运行，agent 会按 `SKILL.md` 调用。需要调试时可以执行：

```bash
python3 scripts/generate.py <scanPath> <linkRoot> <outputDir>
```

示例：

```bash
python3 scripts/generate.py ~/my-project ~/my-project ~/my-project
open ~/my-project/structure.html
```

参数：

| 参数 | 说明 |
| --- | --- |
| `scanPath` | 要扫描的真实项目路径 |
| `linkRoot` | HTML 里 `file://` 链接使用的本机路径，通常等于 `scanPath` |
| `outputDir` | `structure.html` 输出目录，不存在时自动创建 |

## 使用

在任意项目里对 agent 说：

```text
帮我理解这个项目结构，生成一个可交互结构图
```

或者：

```text
Use project-structure-viewer to map this repository.
```

skill 会要求 agent：

1. 先读真实项目文件，而不是只扫文件名
2. 判断项目类型和阅读阶段，不强行套前端/后端模板
3. 调用 `scripts/generate.py`
4. 生成 `<project>/structure.html`
5. 返回结构图路径和简短项目导览

生成出的 HTML 支持：

- 左到右项目树
- 展开 / 收起目录
- 搜索文件并跳转
- 平移 / 缩放
- 中英文界面切换
- `file://` 点击打开本机文件
- 自动标记关键文件

## 标准目录结构

这个仓库本身就是一个 skill 目录，符合 [Agent Skills](https://agentskills.io/home) 规范：

```text
project-structure-viewer/
├── SKILL.md                    # 必需：skill 元数据和工作流
├── scripts/
│   └── generate.py             # 可执行生成器脚本
├── references/
│   └── project-taxonomy.md     # 通用项目类型参考
├── agents/
│   └── openai.yaml             # Codex/OpenAI UI 元数据
├── README.md
├── LICENSE
└── package.json
```

`npx skills` 会识别根目录的 `SKILL.md`，因此可以直接安装：

```bash
npx skills add 1m01m0/project-structure-viewer
```

## 为什么更通用

这个 skill 不再只围绕前后端项目组织阅读路径。它会提示 agent 根据实际仓库识别：

- JavaScript / TypeScript 应用、库、monorepo
- Python 包、CLI、服务、数据/ML 项目
- Go / Rust / Java / Kotlin / Swift 项目
- Flutter / React Native / 移动端项目
- Terraform / Kubernetes / Helm / Docker 等基础设施仓库
- 文档站、内容仓库、示例集合
- 混合型 workspace

核心原则是：先看 manifest、入口、配置、测试、自动化和核心模块，再生成结构图。

## 和 fireworks-tech-graph 的关系

`project-structure-viewer` 默认产出交互式 HTML 项目树，适合浏览代码库。

如果你想要发布级 SVG/PNG 架构图、流程图或系统图，可以搭配：

```bash
npx skills add yizhiyanhua-ai/fireworks-tech-graph
```

典型组合是：先用本 skill 生成项目结构和阅读阶段，再用 `fireworks-tech-graph` 把关键架构/流程画成静态图。

## 参考

- [Agent Skills](https://agentskills.io/home)
- [npx skills CLI](https://github.com/vercel-labs/skills)
- [OpenCode Agent Skills](https://opencode.ai/docs/skills)
- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [Codex Agent Skills](https://developers.openai.com/codex/skills)

## License

MIT
