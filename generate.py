#!/usr/bin/env python3
"""
generate.py — Project Structure Viewer Generator
==================================================
Scans a project directory and produces a self-contained interactive HTML file
that renders the complete file tree as a left-to-right horizontal diagram.

Usage: python3 generate.py <scanPath> <linkRoot> <outputDir>

Arguments:
  scanPath   — path to scan the filesystem
  linkRoot   — host path used for file:// links in the generated HTML
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
            if nd["t"] == "f" and "/" not in p:
                if name in ("package.json", "tsconfig.json", "Dockerfile",
                            "Makefile", "Cargo.toml", "go.mod", "pyproject.toml",
                            "Gemfile", "build.gradle", "pom.xml",
                            "pnpm-workspace.yaml", "lerna.json",
                            "AGENTS.md", "CLAUDE.md", "README.md", "PROJECT_GUIDE.md"):
                    files.add(p)
            if name in ("main.tsx", "main.ts", "index.tsx", "index.ts",
                        "App.tsx", "App.ts", "boot.ts", "boot.js",
                        "server.ts", "server.js", "app.ts", "app.js",
                        "index.html", "_app.tsx", "_app.ts",
                        "layout.tsx", "layout.ts"):
                files.add(p)
            if name in ("router.ts", "router.tsx", "routes.ts", "routes.tsx",
                        "middleware.ts", "middleware.tsx",
                        "context.ts", "context.tsx"):
                files.add(p)
            if name in ("schema.ts", "schema.prisma", "types.ts", "types.d.ts"):
                files.add(p)
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

// File role descriptions (keyed by pattern)
function descFile(p, n, lang) {
  const nm = n.toLowerCase(); const pp = p.toLowerCase();
  const zh = {
    'package.json':'项目清单 — 依赖、脚本、元信息',
    'tsconfig.json':'TypeScript 编译配置',
    'dockerfile':'容器镜像 — 定义生产运行环境',
    '.env.example':'环境变量模板 — 列出所有需配置的密钥和地址',
    'pnpm-workspace.yaml':'Monorepo 工作区定义 — 声明子包位置',
    '.gitignore':'Git 忽略规则',
    'eslint.config.js':'ESLint 代码规范配置',
    'vite.config.ts':'Vite 构建配置 — 插件、代理、路径别名',
    'tailwind.config.js':'Tailwind CSS 主题和设计令牌配置',
  };
  if (zh[nm]) return zh[nm];
  if (zh[pp]) return zh[pp];
  // Pattern-based
  if (/(^|\/)main\.(tsx?|jsx?)$/.test(p)) return 'React 应用入口 — 挂载根组件，初始化 Provider 和路由';
  if (/(^|\/)index\.html$/.test(p)) return 'SPA 入口 HTML — 浏览器首先加载此页面';
  if (/(^|\/)App\.(tsx?|jsx?)$/.test(p)) return '根组件 — 定义路由表和全局布局';
  if (/(^|\/)boot\.(ts|js)$/.test(p)||/(^|\/)server\.(ts|js)$/.test(p)||/(^|\/)app\.(ts|js)$/.test(p)) return '服务端入口 — 启动 HTTP 服务，注册中间件和路由';
  if (/router/i.test(nm)) return '路由定义 — 将 URL 路径映射到处理函数，组织 API 端点';
  if (/middleware/i.test(nm)) return '请求中间件 — 身份认证、权限校验、日志记录';
  if (/schema/i.test(nm)&&!/json/i.test(nm)) return '数据库模型 — 定义表结构、字段类型和关联关系';
  if (/context/i.test(nm)) return '请求上下文 — 从请求头解析用户身份和会话信息';
  if (/auth/i.test(nm)) return '认证模块 — 处理用户登录、token 签发与验证';
  if (/(pages|views|screens)\//.test(p)) return '页面组件 — 对应一个前端路由的完整视图';
  if (/(components|ui)\//.test(p)&&!/node_modules/.test(p)) return 'UI 组件 — 可复用的界面元素';
  if (/hooks\//.test(p)) return '自定义 Hook — 封装可复用的状态逻辑';
  if (/lib\//.test(p)||/utils\//.test(p)) return '工具函数 — 通用辅助逻辑';
  if (/providers?\//.test(p)) return 'Context Provider — 为子树注入全局状态或服务';
  if (/queries?\//.test(p)) return '数据查询 — 封装数据库读写操作';
  if (/contracts?\//.test(p)||/\/types\.(ts|d\.ts)$/.test(p)) return '类型定义 — 共享接口、枚举和类型契约';
  if (/i18n\//.test(p)||/locales?\//.test(p)) return '国际化 — 多语言翻译文本';
  if (/\.(test|spec)\.(tsx?|jsx?)$/.test(p)) return '测试文件 — 单元测试或集成测试';
  if (/deploy/i.test(p)) return '部署脚本 — 自动化发布和上线流程';
  if (/docker/i.test(p)||/nginx/i.test(p)) return '运维配置 — 容器编排或反向代理规则';
  if (/\.md$/i.test(p)) return '项目文档';
  return '';
}

function descFileEn(p, n) {
  const nm = n.toLowerCase(); const pp = p.toLowerCase();
  const en = {
    'package.json':'Project manifest — dependencies, scripts, metadata',
    'tsconfig.json':'TypeScript compiler configuration',
    'dockerfile':'Container image — defines production runtime',
    '.env.example':'Environment template — lists all required secrets and URLs',
    'pnpm-workspace.yaml':'Monorepo workspace — declares sub-package locations',
    '.gitignore':'Git ignore rules',
    'eslint.config.js':'ESLint code style configuration',
    'vite.config.ts':'Vite build config — plugins, proxy, path aliases',
    'tailwind.config.js':'Tailwind CSS theme and design tokens',
  };
  if (en[nm]) return en[nm];
  if (en[pp]) return en[pp];
  if (/(^|\/)main\.(tsx?|jsx?)$/.test(p)) return 'React entry point — mounts root, initializes providers and router';
  if (/(^|\/)index\.html$/.test(p)) return 'SPA entry HTML — the first page the browser loads';
  if (/(^|\/)App\.(tsx?|jsx?)$/.test(p)) return 'Root component — defines route table and global layout';
  if (/(^|\/)boot\.(ts|js)$/.test(p)||/(^|\/)server\.(ts|js)$/.test(p)||/(^|\/)app\.(ts|js)$/.test(p)) return 'Server entry — starts HTTP server, registers middleware and routes';
  if (/router/i.test(nm)) return 'Route definitions — maps URL paths to handlers, organizes API endpoints';
  if (/middleware/i.test(nm)) return 'Request middleware — authentication, authorization, logging';
  if (/schema/i.test(nm)&&!/json/i.test(nm)) return 'Database schema — defines table structure, column types, and relations';
  if (/context/i.test(nm)) return 'Request context — resolves user identity and session from headers';
  if (/auth/i.test(nm)) return 'Auth module — handles login, token issuance and verification';
  if (/(pages|views|screens)\//.test(p)) return 'Page component — complete view for a frontend route';
  if (/(components|ui)\//.test(p)&&!/node_modules/.test(p)) return 'UI component — reusable interface element';
  if (/hooks\//.test(p)) return 'Custom hook — encapsulates reusable state logic';
  if (/lib\//.test(p)||/utils\//.test(p)) return 'Utility — shared helper functions';
  if (/providers?\//.test(p)) return 'Context provider — injects global state or service into subtree';
  if (/queries?\//.test(p)) return 'Data query — encapsulates database read/write operations';
  if (/contracts?\//.test(p)||/\/types\.(ts|d\.ts)$/.test(p)) return 'Type definitions — shared interfaces, enums, and type contracts';
  if (/i18n\//.test(p)||/locales?\//.test(p)) return 'Internationalization — multi-language translation texts';
  if (/\.(test|spec)\.(tsx?|jsx?)$/.test(p)) return 'Test file — unit or integration test';
  if (/deploy/i.test(p)) return 'Deployment script — automates release and rollout';
  if (/docker/i.test(p)||/nginx/i.test(p)) return 'Ops config — container orchestration or reverse proxy rules';
  if (/\.md$/i.test(p)) return 'Documentation';
  return '';
}

const GUIDE = {
  zh: '<div class="flow-col"><h3>📋 关键文件一览</h3>'+buildGuide(DATA,'zh')+'</div><div class="flow-col"><h3>💡 使用提示</h3><div class="flow-note">上方列出了项目中自动识别出的<b>关键文件</b>及其作用。灰框节点在树状图中同样有标记。<br><br>使用 <b>搜索框</b> 可按文件名快速过滤，下拉列表中点击即可跳转。<br><br><b>Ctrl+F</b> 聚焦搜索 · <b>Esc</b> 清除 · <b>Ctrl+0</b> 重置视图。<br><br>点击任意文件节点可在编辑器中直接打开。</div></div>',
  en: '<div class="flow-col"><h3>📋 Key Files Overview</h3>'+buildGuide(DATA,'en')+'</div><div class="flow-col"><h3>💡 Tips</h3><div class="flow-note">Above are auto-detected <b>key files</b> with their roles. Gray-bordered nodes in the tree are also marked.<br><br>Use the <b>search box</b> to filter by filename — click results in the dropdown to navigate.<br><br><b>Ctrl+F</b> focus search · <b>Esc</b> clear · <b>Ctrl+0</b> reset view.<br><br>Click any file node to open it directly in your editor.</div></div>'
};

function buildGuide(nodes, lang) {
  const keyFiles = [];
  function walk(ns) { for (const n of ns) { if (FLOW.has(n.p) && n.t === 'f') keyFiles.push(n); if (n.c) walk(n.c); } }
  walk(nodes);
  keyFiles.sort((a,b) => a.p.split('/').length - b.p.split('/').length || a.p.localeCompare(b.p));
  const shown = keyFiles.slice(0, 10);
  let html = '';
  shown.forEach((f, i) => {
    const desc = lang==='zh' ? descFile(f.p, f.n, 'zh') : descFileEn(f.p, f.n);
    const sz = f.s ? fmt(f.s) : '';
    html += '<div class="flow-step"><span class="num">'+(i+1)+'</span><div><span class="file" onclick="navTo(\''+esc2(f.p)+'\')">'+esc2(f.p)+'</span>'+(desc?'<div class="desc">'+esc2(desc)+'</div>':'')+(sz?'<div class="desc" style="color:#444">'+sz+'</div>':'')+'</div></div>';
  });
  if (keyFiles.length > 10) {
    const more = lang==='zh' ? '...还有 '+(keyFiles.length-10)+' 个关键文件，使用搜索框查找' : '...and '+(keyFiles.length-10)+' more key files. Use search to find them';
    html += '<div class="flow-step"><span class="num">+</span><div class="desc">'+more+'</div></div>';
  }
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

    js = JS.replace('__DATA__', tree_json)
    js = js.replace('__LINKROOT__', escape_json_str(link_root.rstrip('/')))
    js = js.replace('__FLOW__', flow_json)

    html = HTML_TEMPLATE.replace('__CSS__', CSS.strip())
    html = html.replace('__JS__', js.strip())
    html = html.replace('__TITLE__', html_mod.escape(project_name))

    os.makedirs(output_dir, exist_ok=True)
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
