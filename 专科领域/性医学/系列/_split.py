# -*- coding: utf-8 -*-
# 性学系列 —— 按"章节归册 + 子段裁切"把 性学.tex 拆成五册
# 2026-11 定稿：老书 25 章全部保留，仅按主题归位；术语表去重（删老书 4570）
#
# ⚠️ 冻结状态（2026-11-25 起）：
#   本脚本是 2026-11-23 的"一次性切片工具"。切片完成后，五册成品 .tex
#   （A/B/C/D/E_*.tex + 各自的 X_补充.tex）已成为【正源/工作文件】，
#   后续增删改都直接编辑这些成品文件，不再经本脚本生成。
#   母本 性学.tex 已冻结为历史快照（供对照）。
#   ★ 请勿再运行本脚本：CH2BOOK 以"母本行号"为键，且 8 个新增章
#     （A性治疗/多元取向、B情趣/润滑/收纳/欲望/远程、E Kink进阶）
#     不在母本里，重跑会覆盖丢失它们。
#   如需彻底重建，须先把 8 章并入母本并改为"按章节标题"映射，再运行。
import os, io, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 性医学/
SRC = os.path.join(BASE, "性学.tex")
OUT = os.path.join(BASE, "系列")
os.makedirs(OUT, exist_ok=True)


with io.open(SRC, "r", encoding="utf-8") as f:
    lines = f.read().splitlines()
N = len(lines)

# ---- 1) 全部 \chapter 起始行 ----
CH_STARTS = []
for i, ln in enumerate(lines, start=1):
    if re.match(r"\\chapter", ln.lstrip()):
        CH_STARTS.append(i)

def end_of(start):
    nxts = [c for c in CH_STARTS if c > start]
    return min(nxts) if nxts else (N + 1)

# ---- 2) 每章归册（A通用·知 / B通用·行 / C男性 / D女性 / E BDSM）----
#   'SPLIT'=按 SUBS 子段裁切；'DROP'=去重删除
CH2BOOK = {
    75:'A',102:'A',125:'A',191:'A',297:'A',322:'A',349:'A',360:'A',
    381:'A',473:'A',571:'A',1001:'A',1558:'A',2246:'A',2460:'A',
    2726:'A',2808:'A',2937:'A',2952:'A',
    658:'B',810:'B',908:'B',1110:'B',1230:'B',1357:'B',1477:'B',
    1668:'B',1762:'B',1850:'B',1937:'B',2143:'B',2355:'B',2411:'B',
    719:'C',2533:'C',
    2594:'E',
    3012:'A',3734:'B',4570:'DROP',
    4761:'C',4888:'D',5365:'A',5602:'C',5785:'A',6204:'A',
    6554:'B',6907:'B',7161:'B',8179:'D',8750:'A',
    10478:'D',10719:'A',11065:'D',11541:'A',11651:'D',
    11874:'C',12013:'A',12162:'A',
    3944:'SPLIT',5055:'SPLIT',9300:'SPLIT',
}

# SPLIT 章子段：[(子段起始行, 目标册, 合成标题 or None=保留原\chapter行)]
SUBS = {
    3944: [   # 解决你的疑问
        (3944,'B',None),
        (4106,'E','非常性爱：非主流亲密玩法'),
        (4306,'A','避孕方法与选择（旧书整理）'),
        (4437,'A','性传播疾病的识别与防治（旧书整理）'),
        (4518,'D','生殖健康检查（旧书整理）'),
    ],
    5055: [   # 夫妻性生活卫生保健
        (5055,'B',None),
        (5114,'C','男性生理认知：阴茎·勃起·梦遗（旧书整理）'),
        (5143,'B','夫妻性差异与性卫生（旧书整理）'),
        (5246,'C','男性在性交中的意外（旧书整理）'),
        (5272,'D','女性在性交中的意外与经期/孕期（旧书整理）'),
        (5316,'B','性生活频度与有益健康（旧书整理）'),
    ],
    9300: [   # 不孕不育治疗
        (9300,'D',None),
        (9750,'C','男性不育（旧书整理）'),
        (10050,'D','女性不孕与治疗（旧书整理）'),
    ],
}

# ---- 3) 展开成有序 units ----
units = []  # (start, end_excl, book, synth_title)
for ch in sorted(CH2BOOK):
    book = CH2BOOK[ch]
    if book == 'DROP':
        continue
    if book != 'SPLIT':
        units.append((ch, end_of(ch), book, None))
    else:
        subs = SUBS[ch]
        ch_end = end_of(ch)
        for k,(s,bk,title) in enumerate(subs):
            seg_end = subs[k+1][0] if k+1 < len(subs) else ch_end
            units.append((s, seg_end, bk, title))

units.sort(key=lambda u: u[0])

# ---- 4) 清洗段内容 ----
def clean(seg):
    out = [ln for ln in seg if not re.match(r"\\part", ln.lstrip())]
    while out and out[-1].strip() == "":
        out.pop()
    if out and out[-1].strip() == r"\end{document}":
        out.pop()
        while out and out[-1].strip() == "":
            out.pop()
    return out

# ---- 5) 写各册 ----
def emit(fname, title, subtitle, book_units, extra=None, anchor=None):
    head = f"""% =================================================
% 性学系列 · {title}
% 共享基座见 common.tex
% =================================================
\\documentclass[12pt,UTF8,openany]{{ctexbook}}
\\input{{common.tex}}

\\begin{{document}}

% ===== 封面 =====
\\begin{{titlepage}}
\\centering
\\vspace*{{1.5cm}}
\\begin{{tikzpicture}}
\\draw[myblue,line width=2pt] (0,0) circle (1.2);
\\node[text=white] at (0,0) {{\\myhei\\zihao{{3}}性}};
\\end{{tikzpicture}}
\\vspace{{0.6cm}}
\\noindent\\rule{{\\textwidth}}{{0.4pt}}
\\vspace{{0.5cm}}
\\myhei\\zihao{{5}} 性学系列\\,·\\,家庭健康科普\\,·\\,全五册
\\vspace{{2.5cm}}
\\myhei\\zihao{{0}} {title}\\par
\\vspace{{1.2cm}}
\\itshape\\zihao{{3}} {subtitle}\\par
\\vspace{{5.2cm}}
\\noindent\\rule{{\\textwidth}}{{0.4pt}}
\\vspace{{0.5cm}}
\\zihao{{5}} 性学系列\\,·\\,\\today
\\end{{titlepage}}

% ===== 免责声明 =====
\\begin{{center}}\\zihao{{5}}\\itshape
本书为家庭健康科普读物，内容力求科学严谨，但\\textbf{{不替代专业医生的诊断与治疗}}。\\\\
涉及个人健康问题，请以正规医疗机构的检查与建议为准。\\\\
全书以安全、自愿、相互尊重为底色，尊重多元与个体差异。\\par\\end{{center}}
\\clearpage

% ===== 如何使用本书 =====
\\chapter*{{如何使用本书}}
\\addcontentsline{{toc}}{{chapter}}{{如何使用本书}}
\\noindent\\textbf{{性学系列共五册：}}
\\begin{{itemize}}[leftmargin=2em]
\\item \\textbf{{A 性健康基础}} —— 认知、同意、防护、STI、避孕总论（建议先读）
\\item \\textbf{{B 亲密实践与技巧}} —— 前戏、体位、高潮引导、呼吸与盆底
\\item \\textbf{{C 男性性健康}} —— 男性解剖、ED/自慰、绝育、不育
\\item \\textbf{{D 女性性健康}} —— 女性解剖、妇科、不孕、人流、避孕、孕期/更年期
\\item \\textbf{{E BDSM 与 Kink}} —— 安全框架下的亲密表达
\\end{{itemize}}
\\vspace{{0.6em}}
\\noindent\\textbf{{建议阅读路径（零基础）：}} 先通读 A 建立认知与安全底线 → 按需读 C 或 D 了解自己的身体 → 再读 B 学技巧 → 兴趣到了再读 E。每章末有“一页要点”可快读。
\\clearpage

% ===== 目录 =====
\\tableofcontents
\\clearpage
"""
    blocks = []
    inserted = False
    for (s,e,bk,stitle) in book_units:
        seg = clean(lines[s-1:e-1])
        if stitle is not None:
            seg = [f"\\chapter{{{stitle}}}"] + seg
        blocks.append("\n".join(seg))
        # 锚点插入：在该章之后插入补充专题
        if extra and anchor is not None and s == anchor and not inserted:
            blocks.append(f"\\input{{{extra}}}")
            inserted = True
    if extra and not inserted:
        blocks.append(f"\\input{{{extra}}}")
    tail = "\n\n\\end{document}\n"
    with io.open(os.path.join(OUT, fname+".tex"), "w", encoding="utf-8") as f:
        f.write(head + "\n\n".join(blocks) + tail)

TITLES = {
    "A": ("A_性健康基础", "性健康基础", "认知·同意·防护——先建立安全底线", "A_补充.tex", 297),
    "B": ("B_亲密实践与技巧", "亲密实践与技巧", "从「会做」到「做得更好」", "B_补充.tex", None),
    "C": ("C_男性性健康", "男性性健康", "男性身体的专项知识", "C_补充.tex", None),
    "D": ("D_女性性健康", "女性性健康", "女性身体的专项知识", "D_补充.tex", None),
    "E": ("E_BDSM与Kink", "BDSM 与 Kink", "安全框架下的亲密表达", None, None),
}
for bk,(fname,title,subtitle,extra,anchor) in TITLES.items():
    bu = [u for u in units if u[2]==bk]
    emit(fname, title, subtitle, bu, extra, anchor)
    loc = f"（插到第{anchor}行章后）" if anchor else (f"（册末）" if extra else "")
    print(f"{bk} -> {fname}: {len(bu)} 章" + (f" + 补充({extra}){loc}" if extra else ""))

print("DONE")
for fn in sorted(os.listdir(OUT)):
    p = os.path.join(OUT, fn)
    if fn.endswith(".tex") and os.path.isfile(p):
        print(" ", fn, os.path.getsize(p))
