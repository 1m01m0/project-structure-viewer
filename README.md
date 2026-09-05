# Project Structure Viewer

把项目目录生成可交互的 `structure.html`，帮助开发者快速浏览文件层级、定位入口，并按阅读阶段理解代码。

本仓库是一个 Agent Skill：[SKILL.md](SKILL.md) 定义代理阅读项目、编写导览的工作流，[scripts/generate.py](scripts/generate.py) 提供确定性 HTML 生成器。生成器负责目录树；针对具体项目的说明由代理阅读真实源码后编写。

## 快速开始

生成器需要 **Python 3.10+**，仅使用 Python 标准库。查看结果需要启用 JavaScript 的浏览器，无需启动 Web 服务。

直接运行生成器：

```bash
git clone https://github.com/1m01m0/project-structure-viewer.git
cd project-structure-viewer
python3 scripts/generate.py /path/to/project /path/to/project /path/to/output
```

打开 `/path/to/output/structure.html` 即可查看。建议使用绝对路径；生成器会创建输出目录，并覆盖已有的 `structure.html`。直接运行会保留导览占位内容；需要项目专属阅读指南时，使用下方 Skill 工作流。

## 安装为 Skill

可以使用 `skills` CLI 从 GitHub 安装；这一步需要 Node.js / npm 及网络：

```bash
npx skills add 1m01m0/project-structure-viewer
```

也可以先克隆仓库，再将整个目录放入所用代理支持的 Skill 搜索路径。必须保留 `SKILL.md`、`scripts/` 和 `references/` 的相对位置。不同代理的发现目录和启用方式以其当前配置为准。

安装后向代理提出明确的任务，例如：

```text
使用 project-structure-viewer 阅读当前仓库，生成可交互的结构图，
并按项目概览、运行入口、核心逻辑、测试和部署组织阅读指南。
```

[Skill 工作流](SKILL.md) 要求代理：

1. 确定扫描路径、本机链接路径和输出目录。
2. 阅读项目文档、依赖清单、入口、配置、测试及关键模块，判断项目类型。
3. 将生成器复制到输出目录，在副本中填入基于源码的中英文分阶段导览。
4. 运行副本生成 `structure.html`，删除临时副本并核对结果。
5. 返回输出路径、简短项目说明及扫描限制。

原始生成器应保持不变。导览可覆盖应用、库、CLI、monorepo、数据/ML、基础设施和文档项目，阶段划分以实际文件为依据。

## 交互能力

- 从左到右的目录树，支持展开与收起。
- 文件搜索、结果跳转，以及画布平移和缩放。
- 中英文界面切换。
- 根据文件名与路径规则标记潜在关键文件。
- 使用 `file://` 链接打开本机文件。

HTML 内嵌样式、脚本和目录数据，不依赖 CDN。浏览器可能限制本地文件链接的打开方式；跨设备分享后，原来的绝对路径通常无法使用。

## 生成器参数

```text
python3 scripts/generate.py <scanPath> <linkRoot> <outputDir>
```

| 参数 | 含义 |
| --- | --- |
| `scanPath` | 实际扫描的目录。 |
| `linkRoot` | HTML 文件链接的本机根路径，通常与 `scanPath` 相同。 |
| `outputDir` | 写入 `structure.html` 的目录，不存在时创建。 |

若在容器或远程环境生成，可用 `linkRoot` 指向查看者机器上的同一份项目；目录层级必须对应。这个映射不会复制源码或让远程浏览器获得文件访问权限。

## 范围、隐私与限制

生成器扫描文件名、相对路径和文件大小，不把源码正文嵌入 HTML；代理撰写导览时需要另外读取源码。HTML 包含目录信息、链接根路径和代理写入的说明，共享前请检查是否暴露内部项目名称或本机路径。代理读取源码时的数据处理方式取决于所使用的代理服务。

扫描器使用内置忽略列表，跳过 `.git`、`node_modules`、常见构建目录、精确名称 `.env` 等条目，**不解析项目 `.gitignore`**。其他隐藏文件和 `.env.*` 文件名可能出现在图中。权限不足的目录可能被跳过。

扫描没有目录深度或文件数量上限，并会跟随目录符号链接；包含循环链接或规模很大的目录可能失败或导致浏览器卡顿。请选择合适的扫描根目录。关键文件标记是路径启发式，目录图不是依赖图，也不保证自动识别完整架构。

## 仓库导航与贡献

| 路径 | 用途 |
| --- | --- |
| [SKILL.md](SKILL.md) | Skill 元数据与代理工作流。 |
| [scripts/generate.py](scripts/generate.py) | 文件扫描、HTML 模板及交互代码。 |
| [references/project-taxonomy.md](references/project-taxonomy.md) | 项目分类与阅读阶段参考。 |
| [agents/openai.yaml](agents/openai.yaml) | 代理界面元数据。 |
| [package.json](package.json) | 包元信息，不提供 npm 可执行命令。 |

当前仓库没有自动化测试套件。修改后，可对一个小型临时目录运行生成器，检查树是否完整、忽略项是否生效，以及搜索、缩放、语言切换和文件链接。使用包含空格、中文和特殊字符的文件名验证转义行为。

[提交问题](https://github.com/1m01m0/project-structure-viewer/issues) 时请提供操作系统、Python 和浏览器版本、最小目录结构，以及预期与实际表现。需要静态 SVG/PNG 架构图时，可将此工具生成的项目导览交给其他绘图工具处理。

## 许可证

[MIT](LICENSE)，Copyright © 2026 1m01m0。
