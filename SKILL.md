---
name: project-structure-viewer
description: Generate an interactive horizontal tree map of any project directory. Creates a self-contained HTML file with complete file tree, reading guide, search dropdown, pan/zoom, and click-to-open-file links. Use when the user asks to visualize, map, or understand a project's file structure.
---

# Project Structure Viewer

Generate an interactive, self-contained HTML file that renders a project's complete file tree as a left-to-right horizontal tree diagram. Includes a reading guide, search with dropdown results, pan/zoom, and clickable file links that open in the local editor.

## Trigger

Use this skill when the user asks to:
- "Help me understand this project structure"
- "Make a structure diagram / tree map of this codebase"
- "Show me all files in this project"
- "Generate a project overview / file tree"
- Any request to visualize a directory hierarchy

## Workflow

### Step 1 — Confirm paths

Determine TWO paths:
- **scanPath**: filesystem path for scanning
- **linkRoot**: host path for `file://` links

### Step 2 — READ AND ANALYZE THE PROJECT (MANDATORY — DO NOT SKIP)

**You MUST read the actual source files before generating. This is not optional.**

Read at minimum:
1. Root package.json / manifest
2. All entry points (main.tsx, index.html, boot.ts, server.ts, App.tsx, etc.)
3. All router files (router.ts, routes.ts, etc.)
4. All middleware files
5. Database schema files
6. Key config files (tsconfig, vite.config, Dockerfile, etc.)
7. One or two page/component files to understand patterns

### Step 3 — BUILD THE GUIDE (MANDATORY — MUST BE PHASE-BASED)

**CRITICAL: The guide MUST be organized by PHASES (阶段), NOT a flat list. Each phase covers a logical layer of the project.**

Replace the GUIDE placeholder in `generate.py`'s `JS_TPL` variable with your project-specific content. **The generated HTML MUST use this exact structure:**

```javascript
const GUIDE = {
  zh: [
    '<div class="flow-col"><h3>🔷 阶段一：项目概览 (5)</h3>',
    mkS(1,'package.json','Monorepo 项目清单 — 包结构、脚本、技术栈一目了然'),
    mkS(2,'tsconfig.json','TypeScript 编译配置'),
    // ...every file in this phase with SPECIFIC description
    '</div>',
    '<div class="flow-col"><h3>🟢 阶段二：前端启动链 (7)</h3>',
    mkS(1,'src/index.html','SPA 入口 HTML — 声明挂载点，加载入口脚本'),
    mkS(2,'src/main.tsx','React 入口 — BrowserRouter → Provider → App 层层包裹'),
    // ...
    '</div>',
    '<div class="flow-col"><h3>🟠 阶段三：后端请求链 (N)</h3>',
    // ...
    '</div>',
    '<div class="flow-col"><h3>🟣 阶段四：数据层 (N)</h3>',
    // ...
    '</div>',
    '<div class="flow-col"><h3>🟣 关键流转总结</h3>',
    '<div class="flow-note"><b>认证流转：</b>Login → tRPC → auth-router → context<br><b>数据流转：</b>tRPC client → router → middleware → queries → DB</div>',
    '</div>',
  ].join(''),
  en: [
    // SAME structure in English using mkE() instead of mkS()
  ].join('')
};
```

**RULES — YOU MUST FOLLOW ALL OF THESE:**

1. **Phase-based organization**: Group files into logical phases (config → frontend chain → pages → components → backend chain → data → deploy/docs). Each phase is a separate `<div class="flow-col">`.
2. **100% coverage**: Every single file in the project MUST appear in the guide. Count files per phase and put the count in the heading: `(N)`.
3. **Specific descriptions**: Write what each file ACTUALLY does based on reading its contents. "Handles OAuth login via Kimi platform, exchanges code for token" NOT "Auth module". NOT generic pattern matching.
4. **Bilingual**: Both `zh` and `en` arrays. Use `mkS(n, path, desc)` for Chinese, `mkE(n, path, desc)` for English.
5. **Flow summary**: The last column MUST contain a `<div class="flow-note">` with cross-cutting flow descriptions (auth flow, data flow, build flow).
6. **UI library files**: If a directory has 20+ similar files (e.g. shadcn/ui components), summarize them in one `<div class="flow-note">` instead of listing individually. List the directory path and note the count.

**Example of what GOOD looks like (from aiweb):**

```
🔷 阶段一：项目概览 (5)
  1. package.json — Monorepo 项目清单...
  2. tsconfig.json — TypeScript 编译配置
  
🟢 阶段二：前端启动链 (7)
  1. index.html — SPA 入口 HTML...
  2. main.tsx — React 应用入口...

🟠 阶段三：后端请求链 (6)
  1. boot.ts — Hono 服务器入口...

🟣 关键流转总结
  认证流转：Login.tsx → tRPC → auth-router...
```

**Example of what BAD looks like (NEVER DO THIS):**
- Flat list of files without phases
- Generic descriptions like "Component file" or "Utility function"
- Missing files
- No flow summary

### Step 4 — Edit generate.py and run

1. Open `generate.py`
2. Find `const GUIDE={zh:'<div class="flow-col">...`
3. Replace the ENTIRE GUIDE constant with your project-specific version from Step 3
4. Save and run:

```bash
python3 generate.py "<scanPath>" "<linkRoot>" "<outputDir>"
```

### Step 5 — Present the result

File is at `<outputDir>/structure.html`. Tell the user to open it in VS Code or browser.

## Generator Script

Save this script alongside the SKILL.md as `generate.py`. It is self-contained and requires only Python 3.10+.

```python
#!/usr/bin/env python3
"""
generate.py — Project Structure Viewer Generator
==================================================
Scans a project directory and produces a self-contained interactive HTML file
that renders the complete file tree as a left-to-right horizontal diagram.

Usage: python3 generate.py <scanPath> <linkRoot> <outputDir>

Arguments:
  scanPath   — VM path to scan the filesystem
  linkRoot   — macOS host path used for file:// links
  outputDir  — directory where structure.html will be written
"""

import os, sys, json, fnmatch, html as html_mod
from datetime import datetime

IGNORE = [
    'node_modules', '.git', '__pycache__', '.pnpm',
    '*.pyc', '*.pyo', '.DS_Store', 'Thumbs.db',
    '.idea', '.vscode', '*.swp', '*.swo', '*~',
    '.env', '.turbo', 'coverage', '.nyc_output',
    '.pytest_cache', '.mypy_cache', '.tox', '.ruff_cache',
    '.next', '.nuxt', '*.egg-info', '.terraform', '*.log', '.cache',
]


def ok(name):
    for pat in IGNORE:
        if fnmatch.fnmatch(name, pat):
            return False
    return True


def build_tree(directory, root_dir):
    out = []
    try:
        entries = sorted(os.listdir(directory), key=lambda x: (
            not os.path.isdir(os.path.join(directory, x)), x.lower()
        ))
    except (PermissionError, OSError):
        return out

    for entry in entries:
        if not ok(entry):
            continue
        full = os.path.join(directory, entry)
        rel = os.path.relpath(full, root_dir)
        try:
            if os.path.isdir(full):
                children = build_tree(full, root_dir)
                out.append({"n": entry, "t": "d", "p": rel, "c": children})
            elif os.path.isfile(full):
                sz = os.path.getsize(full)
                out.append({"n": entry, "t": "f", "p": rel, "s": sz})
        except OSError:
            continue
    return out


def flow_set(tree):
    """Auto-detect key flow files for the reading guide."""
    files = set()

    def walk(nodes):
        for nd in nodes:
            p = nd["p"]
            name = nd["n"]
            # root-level config files
            if nd["t"] == "f" and "/" not in p:
                if name in ("package.json", "tsconfig.json", "Dockerfile",
                            "Makefile", "Cargo.toml", "go.mod", "pyproject.toml",
                            "Gemfile", "build.gradle", "pom.xml",
                            "pnpm-workspace.yaml", "lerna.json",
                            "AGENTS.md", "CLAUDE.md", "README.md", "PROJECT_GUIDE.md"):
                    files.add(p)
            # entry points
            if name in ("main.tsx", "main.ts", "index.tsx", "index.ts",
                        "App.tsx", "App.ts", "boot.ts", "boot.js",
                        "server.ts", "server.js", "app.ts", "app.js",
                        "index.html", "_app.tsx", "_app.ts",
                        "layout.tsx", "layout.ts"):
                files.add(p)
            # routing
            if name in ("router.ts", "router.tsx", "routes.ts", "routes.tsx",
                        "middleware.ts", "middleware.tsx",
                        "context.ts", "context.tsx"):
                files.add(p)
            # schema / types
            if name in ("schema.ts", "schema.prisma", "types.ts", "types.d.ts"):
                files.add(p)
            # key pages
            if "pages" in p or "routes" in p or "views" in p:
                if nd["t"] == "f" and not p.endswith((".css", ".scss", ".less", ".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx")):
                    files.add(p)
            if nd["t"] == "d":
                walk(nd.get("c", []))
    walk(tree)
    return files


def escape_json_str(s):
    return s.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")


CSS = r'''
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#000;color:#ccc;overflow:hidden;height:100vh;width:100vw;display:flex;flex-direction:column}
.guide-panel{background:#0a0a0a;border-bottom:1px solid #222;max-height:40vh;overflow-y:auto;flex-shrink:0}
.guide-panel.collapsed .guide-body{display:none}
.guide-header{display:flex;align-items:center;gap:10px;padding:10px 20px;cursor:pointer;user-select:none;position:sticky;top:0;background:#0a0a0a;z-index:5}
.guide-header:hover{background:#111}
.guide-header .arrow{transition:transform .2s;font-size:11px;color:#666}
.guide-header.collapsed .arrow{transform:rotate(-90deg)}
.guide-header h2{font-size:14px;color:#e0e0e0;display:flex;align-items:center;gap:8px}
.guide-header h2 .badge{font-size:10px;background:#222;color:#999;padding:2px 8px;border-radius:10px;font-weight:400}
.guide-body{padding:0 20px 16px;display:flex;gap:16px;flex-wrap:wrap}
.flow-col{flex:1;min-width:260px;max-width:420px}
.flow-col h3{font-size:12px;color:#999;margin-bottom:8px;font-weight:500}
.flow-step{display:flex;gap:8px;padding:4px 0;font-size:11px;align-items:flex-start;line-height:1.5}
.flow-step .num{flex-shrink:0;width:18px;height:18px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:700;color:#000;background:#555}
.flow-step .file{color:#aaa;cursor:pointer;font-family:monospace;font-size:10px;word-break:break-all}
.flow-step .file:hover{color:#fff;text-decoration:underline}
.flow-step .desc{color:#666;font-size:10px}
.flow-note{font-size:10px;color:#666;margin-top:8px;padding:10px 12px;background:#0d0d0d;border-radius:6px;line-height:1.7}
.flow-note b{color:#ccc}
.topbar{background:#0a0a0a;border-bottom:1px solid #222;padding:7px 16px;display:flex;align-items:center;gap:10px;z-index:200;flex-shrink:0}
.topbar h1{font-size:13px;color:#ddd;white-space:nowrap}
.topbar .spacer{flex:1}
.topbar .search-wrap{position:relative}
.topbar input{padding:5px 10px;border-radius:5px;border:1px solid #333;background:#000;color:#ccc;font-size:12px;outline:none;width:170px}
.topbar input:focus{border-color:#555}
.topbar button{padding:5px 10px;border-radius:5px;border:1px solid #333;background:#0a0a0a;color:#999;font-size:11px;cursor:pointer;white-space:nowrap}
.topbar button:hover{background:#1a1a1a;color:#ccc}
.topbar button.on{background:#1a1a1a;color:#fff;border-color:#555}
.sr-drop{position:absolute;top:100%;left:0;right:0;background:#111;border:1px solid #333;border-top:none;border-radius:0 0 5px 5px;max-height:240px;overflow-y:auto;z-index:300;display:none}
.sr-drop.show{display:block}
.sr-item{padding:5px 10px;font-size:11px;cursor:pointer;display:flex;align-items:center;gap:6px;border-bottom:1px solid #1a1a1a}
.sr-item:hover{background:#1a1a1a}
.sr-item .sr-name{color:#ccc;font-family:monospace;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.sr-item .sr-path{color:#555;font-size:9px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-left:auto;max-width:50%}
.sr-empty{padding:12px;text-align:center;color:#555;font-size:12px}
.sr-more{padding:6px;text-align:center;color:#666;font-size:10px}
.canvas-wrap{flex:1;overflow:auto;position:relative;cursor:grab}
.canvas-wrap:active{cursor:grabbing}
.canvas{position:relative;transform-origin:0 0;padding:20px 40px 40px 20px}
svg.lns{position:absolute;top:0;left:0;pointer-events:none;z-index:1}
.node{position:absolute;display:flex;align-items:center;gap:4px;padding:5px 10px;border-radius:5px;font-size:11px;white-space:nowrap;cursor:pointer;z-index:10;border:1px solid transparent;user-select:none;width:200px}
.node:hover{z-index:20;border-color:#444}
.node.hl{border-color:#777!important;z-index:25}
.node.dim{opacity:.08;pointer-events:none}
.node.dir{background:#0a0a0a;border-color:#1a1a1a}
.node.dir .ni{color:#bbb;font-weight:500;max-width:140px;overflow:hidden;text-overflow:ellipsis}
.node.dir .ico{font-size:12px;flex-shrink:0}
.node.file{background:#050505;border-color:#141414}
.node.file .ni{color:#aaa;max-width:120px;overflow:hidden;text-overflow:ellipsis}
.node.file .sz{font-size:9px;color:#444;margin-left:auto}
.node.flow{border-color:#555!important;background:#0d0d0d!important}
.node.flow .ni{color:#ddd!important}
.node.root{background:#0d0d0d;border-color:#444;font-weight:600}
.node.root .ni{color:#ddd}
.tt{position:fixed;background:#111;border:1px solid #333;border-radius:6px;padding:6px 10px;font-size:11px;color:#ccc;pointer-events:none;z-index:500;display:none}
.tt .p{color:#666;font-size:10px}
.zm{position:fixed;bottom:14px;right:14px;background:#111;border:1px solid #333;border-radius:5px;padding:5px 10px;font-size:11px;color:#555;z-index:100}
'''

JS = r'''
const DATA = __DATA__;
const PROOT = '__LINKROOT__/';
const FLOW = new Set(__FLOW__);
const NW = 200, NH = 30, LG = 78, NG = 4;
let els = [], sc = 1, exp = new Set(), sq = '';

let LANG = 'zh';
const T = {
  zh: {
    guideTitle:'📖 阅读路线图',guideBadge:'从哪里开始看？',
    guideHint:'点击收起 · 树中灰框节点 = 流程关键文件',
    searchPlaceholder:'🔍 搜索文件...',
    btnExpand:'📂 全部展开',btnCollapse:'📁 全部收起',btnReset:'🔄 重置',
    noMatch:'无匹配文件',more:'...还有 ',more2:' 个匹配',
    tooltipClick:'点击在编辑器中打开',
  },
  en: {
    guideTitle:'📖 Reading Guide',guideBadge:'Where to start?',
    guideHint:'Click to collapse · Gray-bordered nodes = key flow files',
    searchPlaceholder:'🔍 Search files...',
    btnExpand:'📂 Expand All',btnCollapse:'📁 Collapse',btnReset:'🔄 Reset',
    noMatch:'No matching files',more:'...',more2:' more matches',
    tooltipClick:'Click to open in editor',
  }
};

const GUIDE = {
  zh: '<div class="flow-col"><h3>Phase 1: Entry & Configuration</h3>'+buildGuideStepsZh(DATA)+'</div><div class="flow-col"><h3>Phase 2: Core Source Code</h3><div class="flow-note">Use the <b>search box</b> above to filter files. Gray-bordered nodes in the tree are auto-detected key files (entry points, routers, schemas, pages). Click any file node to open it in your editor.<br><br>Tip: Press <b>Ctrl+F</b> to focus the search box, then type a filename to jump directly to it.</div></div>',
  en: '<div class="flow-col"><h3>Phase 1: Entry & Configuration</h3>'+buildGuideStepsEn(DATA)+'</div><div class="flow-col"><h3>Phase 2: Core Source Code</h3><div class="flow-note">Use the <b>search box</b> above to filter files. Gray-bordered nodes in the tree are auto-detected key files (entry points, routers, schemas, pages). Click any file node to open it in your editor.<br><br>Tip: Press <b>Ctrl+F</b> to focus the search box, then type a filename to jump directly to it.</div></div>'
};

function buildGuideStepsZh(nodes, depth) {
  depth = depth || 0;
  let html = '';
  const keyFiles = [];
  function walk(ns, d) {
    for (const n of ns) {
      if (FLOW.has(n.p) && n.t === 'f') keyFiles.push(n);
      if (n.c) walk(n.c, d+1);
    }
  }
  walk(nodes, 0);
  keyFiles.sort((a,b) => a.p.split('/').length - b.p.split('/').length || a.p.localeCompare(b.p));
  const shown = keyFiles.slice(0, 8);
  shown.forEach((f, i) => {
    html += '<div class="flow-step"><span class="num">'+(i+1)+'</span><div><span class="file" onclick="navTo(\''+esc2(f.p)+'\')">'+esc2(f.p)+'</span><div class="desc">'+(f.s ? fmt(f.s) : '')+'</div></div></div>';
  });
  if (keyFiles.length > 8) html += '<div class="flow-step"><span class="num">+</span><div class="desc">...and '+(keyFiles.length-8)+' more key files. Use search to find specific files.</div></div>';
  return html;
}

function buildGuideStepsEn(nodes, depth) {
  depth = depth || 0;
  let html = '';
  const keyFiles = [];
  function walk(ns, d) {
    for (const n of ns) {
      if (FLOW.has(n.p) && n.t === 'f') keyFiles.push(n);
      if (n.c) walk(n.c, d+1);
    }
  }
  walk(nodes, 0);
  keyFiles.sort((a,b) => a.p.split('/').length - b.p.split('/').length || a.p.localeCompare(b.p));
  const shown = keyFiles.slice(0, 8);
  shown.forEach((f, i) => {
    html += '<div class="flow-step"><span class="num">'+(i+1)+'</span><div><span class="file" onclick="navTo(\''+esc2(f.p)+'\')">'+esc2(f.p)+'</span><div class="desc">'+(f.s ? fmt(f.s) : '')+'</div></div></div>';
  });
  if (keyFiles.length > 8) html += '<div class="flow-step"><span class="num">+</span><div class="desc">...and '+(keyFiles.length-8)+' more key files. Use search to find specific files.</div></div>';
  return html;
}

function toggleLang() {
  LANG = LANG === 'zh' ? 'en' : 'zh';
  document.getElementById('btnLang').textContent = LANG === 'zh' ? 'EN' : '中文';
  applyLang();
}
function applyLang() {
  const t = T[LANG];
  document.getElementById('guideTitle').textContent = t.guideTitle;
  document.getElementById('guideBadge').textContent = t.guideBadge;
  document.getElementById('guideHint').textContent = t.guideHint;
  document.getElementById('q').placeholder = t.searchPlaceholder;
  document.getElementById('btnExpand').textContent = t.btnExpand;
  document.getElementById('btnCollapse').textContent = t.btnCollapse;
  document.getElementById('btnReset').textContent = t.btnReset;
  document.getElementById('guideBody').innerHTML = GUIDE[LANG];
  search();
}
function toggleGuide() {
  document.getElementById('guide').classList.toggle('collapsed');
  document.getElementById('guideHdr').classList.toggle('collapsed');
}
function navTo(p) {
  const parts = p.split('/');
  for (let i=0;i<parts.length-1;i++) exp.add(parts.slice(0,i+1).join('/'));
  render();
  setTimeout(()=>{const el=els.find(e=>e.dataset.path===p);if(el)el.scrollIntoView({behavior:'smooth',block:'center',inline:'center'});},80);
}
function layout(nodes,d,sy,pcy) {
  let y=sy;const out=[];
  for(const nd of nodes) {
    if(nd.t==='f'){out.push({n:nd,d,y,pcy});y+=NH+NG;}
    else{
      const kids=nd.c||[],open=exp.has(nd.p),cy=y+NH/2;
      out.push({n:nd,d,y,pcy,hk:kids.length>0,open});
      if(open&&kids.length>0){const cs=layout(kids,d+1,y+NH+NG,cy);out.push(...cs);y=cs[cs.length-1].y+NH+NG;}
      else y+=NH+NG;
    }
  }
  return out;
}
function ml(x1,y1,x2,y2,c,w){const l=document.createElementNS('http://www.w3.org/2000/svg','line');l.setAttribute('x1',x1);l.setAttribute('y1',y1);l.setAttribute('x2',x2);l.setAttribute('y2',y2);l.setAttribute('stroke',c);l.setAttribute('stroke-width',w);return l;}
function render() {
  const ca=document.getElementById('canvas'),sv=document.getElementById('svgl');
  els.forEach(e=>e.remove());els=[];sv.innerHTML='';
  if(exp.size===0)DATA.forEach(n=>{if(n.t==='d')exp.add(n.p);});
  const flat=layout(DATA,0,0,null);
  const maxD=flat.reduce((m,n)=>Math.max(m,n.d),0);
  const lastY=flat.length?flat[flat.length-1].y+NH+40:400;
  const tw=(maxD+2)*(NW+LG)+200;
  sv.setAttribute('width',tw);sv.setAttribute('height',lastY);
  sv.setAttribute('viewBox','0 0 '+tw+' '+lastY);
  const pgrp=new Map();
  for(const f of flat){if(f.pcy!==null&&f.pcy!==undefined){const k=f.d+'|'+f.pcy;if(!pgrp.has(k))pgrp.set(k,[]);pgrp.get(k).push(f);}}
  for(const[,g]of pgrp){if(g.length<2)continue;const d=g[0].d,x=d*(NW+LG)-5;const y0=g[0].y+NH/2,y1=g[g.length-1].y+NH/2;sv.appendChild(ml(x,y0,x,y1,'#222',1));for(const gi of g)sv.appendChild(ml(x,gi.y+NH/2,x+7,gi.y+NH/2,'#222',1));}
  for(const f of flat){
    const x=f.d*(NW+LG),y=f.y;
    if(f.pcy!==null&&f.pcy!==undefined){const px=(f.d-1)*(NW+LG)+NW,py=f.pcy,cx=x,cy=y+NH/2,mx=px+(cx-px)/2;sv.appendChild(ml(px,py,mx,py,'#1a1a1a',1));sv.appendChild(ml(mx,py,mx,cy,'#1a1a1a',1));sv.appendChild(ml(mx,cy,cx,cy,'#1a1a1a',1));}
    const el=document.createElement('div');
    let cls='node '+(f.n.t==='d'?'dir':'file');
    if(f.d===0&&f.n.t==='d')cls+=' root';
    if(FLOW.has(f.n.p))cls+=' flow';
    el.className=cls;el.style.left=x+'px';el.style.top=y+'px';el.dataset.path=f.n.p;el.dataset.type=f.n.t;
    if(f.n.t==='d'){el.innerHTML='<span class="ico">'+(f.open?'📂':'📁')+'</span><span class="ni">'+esc2(f.n.n)+'</span>';if((f.n.c||[]).length>0)el.addEventListener('click',e=>{e.stopPropagation();if(exp.has(f.n.p))exp.delete(f.n.p);else exp.add(f.n.p);render();});}
    else{el.innerHTML='<span class="ico">📄</span><span class="ni">'+esc2(f.n.n)+'</span>'+(f.n.s?'<span class="sz">'+fmt(f.n.s)+'</span>':'');el.addEventListener('click',e=>{e.stopPropagation();window.open('file://'+PROOT+f.n.p,'_blank');});el.addEventListener('mouseenter',e=>showTT(e,f.n));el.addEventListener('mouseleave',hideTT);}
    ca.appendChild(el);els.push(el);
  }
  updateHL();
}
function buildIndex(nodes){const idx=[];for(const n of nodes){if(n.t==='f')idx.push({name:n.n,path:n.p,size:n.s});if(n.c)idx.push(...buildIndex(n.c));}return idx;}
const fileIndex=buildIndex(DATA);
function search(){sq=document.getElementById('q').value.toLowerCase().trim();updateHL();updateDropdown();}
function updateDropdown(){const dd=document.getElementById('srdrop'),t=T[LANG];if(!sq||sq.length<1){dd.classList.remove('show');return;}const matches=fileIndex.filter(f=>f.path.toLowerCase().includes(sq));const MAX=30;if(matches.length===0){dd.innerHTML='<div class="sr-empty">'+t.noMatch+'</div>';}else{const shown=matches.slice(0,MAX);dd.innerHTML=shown.map(f=>'<div class="sr-item" onmousedown="navTo(\''+esc2(f.path)+'\');document.getElementById(\'srdrop\').classList.remove(\'show\')"><span class="sr-name">'+esc2(f.name)+'</span><span class="sr-path">'+esc2(f.path)+'</span></div>').join('')+(matches.length>MAX?'<div class="sr-more">'+t.more+(matches.length-MAX)+t.more2+'</div>':'');}dd.classList.add('show');}
function updateHL(){if(!sq){els.forEach(e=>e.classList.remove('dim','hl'));return;}els.forEach(e=>{const p=(e.dataset.path||'').toLowerCase();if(p.includes(sq)){e.classList.remove('dim');e.classList.add('hl');}else{e.classList.add('dim');e.classList.remove('hl');}});}
function showTT(e,nd){const t=document.getElementById('tt');t.innerHTML='<div>'+esc2(nd.n)+'</div><div class="p">'+esc2(nd.p)+'</div>';t.style.display='block';t.style.left=(e.clientX+14)+'px';t.style.top=(e.clientY-8)+'px';}
function hideTT(){document.getElementById('tt').style.display='none';}
function expandAll(){function f(ns){for(const n of ns){if(n.t==='d'&&n.c&&n.c.length>0){exp.add(n.p);f(n.c);}}}f(DATA);render();}
function collapseAll(){exp.clear();DATA.forEach(n=>{if(n.t==='d')exp.add(n.p);});render();}
let px=0,py=0,pan=false,sx,sy,spx,spy;
const wr=document.getElementById('wrap'),ca=document.getElementById('canvas');
wr.addEventListener('wheel',e=>{e.preventDefault();const d=Math.min(Math.abs(e.deltaY),150)*0.00125;const ns=Math.min(3,Math.max(0.15,sc*(1+Math.sign(-e.deltaY)*d)));const r=wr.getBoundingClientRect();const mx=e.clientX-r.left,my=e.clientY-r.top;px=mx-(mx-px)*(ns/sc);py=my-(my-py)*(ns/sc);sc=ns;applyT();},{passive:false});
wr.addEventListener('mousedown',e=>{if(e.target===wr||e.target===ca||e.target.id==='svgl'){pan=true;sx=e.clientX;sy=e.clientY;spx=px;spy=py;}});
window.addEventListener('mousemove',e=>{if(!pan)return;px=spx+(e.clientX-sx)/sc;py=spy+(e.clientY-sy)/sc;applyT();});
window.addEventListener('mouseup',()=>{pan=false;});
function applyT(){ca.style.transform='translate('+px+'px,'+py+'px) scale('+sc+')';document.getElementById('zm').textContent=Math.round(sc*100)+'%';}
function resetView(){sc=1;px=0;py=0;applyT();document.getElementById('q').value='';sq='';document.getElementById('srdrop').classList.remove('show');expandAll();}
document.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key==='f'){e.preventDefault();document.getElementById('q').focus();}if(e.key==='Escape'){document.getElementById('q').value='';sq='';updateHL();document.getElementById('srdrop').classList.remove('show');}if(e.key==='0'&&(e.ctrlKey||e.metaKey)){e.preventDefault();resetView();}});
function fmt(b){if(!b)return'';const u=['B','KB','MB','GB'];let s=b,i=0;while(s>=1024&&i<u.length-1){s/=1024;i++;}return i===0?s+' B':s.toFixed(1)+' '+u[i];}
function esc2(s){const d=document.createElement('div');d.textContent=s;return d.innerHTML;}
applyLang();render();
'''

HTML_TEMPLATE = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__ — Project Structure</title>
<style>__CSS__</style>
</head>
<body>
<div class="guide-panel" id="guide">
<div class="guide-header" id="guideHdr" onclick="toggleGuide()">
  <span class="arrow">▼</span>
  <h2><span id="guideTitle"></span> <span class="badge" id="guideBadge"></span></h2>
  <span style="flex:1"></span>
  <span style="font-size:10px;color:#555" id="guideHint"></span>
</div>
<div class="guide-body" id="guideBody"></div>
</div>
<div class="topbar">
  <h1>📂 __TITLE__</h1>
  <span class="spacer"></span>
  <span class="search-wrap">
    <input type="text" id="q" placeholder="" oninput="search()" onfocus="search()" onblur="setTimeout(()=>srdrop.classList.remove('show'),200)">
    <div class="sr-drop" id="srdrop"></div>
  </span>
  <button onclick="expandAll()" id="btnExpand"></button>
  <button onclick="collapseAll()" id="btnCollapse"></button>
  <button onclick="resetView()" id="btnReset"></button>
  <button onclick="toggleLang()" class="on" id="btnLang">EN</button>
</div>
<div class="canvas-wrap" id="wrap">
  <div class="canvas" id="canvas"><svg class="lns" id="svgl"></svg></div>
  <div class="zm" id="zm">100%</div>
</div>
<div class="tt" id="tt"></div>
<script>__JS__</script>
</body>
</html>'''


def generate(scan_path, link_root, output_dir):
    project_name = os.path.basename(os.path.abspath(scan_path)) or 'project'

    print(f'Scanning: {scan_path}')
    tree = build_tree(scan_path, scan_path)
    fl = flow_set(tree)
    flow_json = json.dumps(sorted(fl), ensure_ascii=False)
    tree_json = json.dumps(tree, ensure_ascii=False)

    file_count = sum(1 for _ in _walk_files(tree))
    dir_count = sum(1 for _ in _walk_dirs(tree))
    print(f'{dir_count} dirs, {file_count} files')

    # Build JS
    js = JS.replace('__DATA__', tree_json)
    js = js.replace('__LINKROOT__', escape_json_str(link_root.rstrip('/')))
    js = js.replace('__FLOW__', flow_json)

    html = HTML_TEMPLATE.replace('__CSS__', CSS.strip())
    html = html.replace('__JS__', js.strip())
    html = html.replace('__TITLE__', html_mod.escape(project_name))

    out_path = os.path.join(output_dir, 'structure.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'Done: {out_path}')
    return out_path


def _walk_files(nodes):
    for n in nodes:
        if n['t'] == 'f':
            yield n
        if n.get('c'):
            yield from _walk_files(n['c'])


def _walk_dirs(nodes):
    for n in nodes:
        if n['t'] == 'd':
            yield n
            if n.get('c'):
                yield from _walk_dirs(n['c'])


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    generate(sys.argv[1], sys.argv[2], sys.argv[3])
```

## Notes

- The generated HTML is fully self-contained — no network requests, no external dependencies.
- `node_modules` and `.git` are excluded from scanning. `dist`, `.github`, and config files ARE included.
- The reading guide auto-detects key files: entry points (main.tsx, boot.ts), routers, middleware, schemas, and pages.
- The `file://` links work when the HTML is opened locally. VS Code's built-in preview may handle them differently than a browser — recommend opening in a browser if links don't work in VS Code.
- Zoom speed uses a proportional 0.125% per deltaY unit, tuned for both mouse wheels and trackpads.
