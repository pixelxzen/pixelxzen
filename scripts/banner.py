"""
[INPUT]: fusion-pixel 10px 简中像素等宽字体（argv[1]）+ Pillow 光栅化；本文件顶部 CONTENT 是唯一文案源
[OUTPUT]: assets/banner.svg —— 左栏「紫苏子」贡献图格字 + 右栏 neofetch 自述 + CRT 扫描线
[POS]: 主页首屏横幅的唯一生成器。改文案改 CONTENT 后重跑；禁手改 SVG —— 下次重生成即被覆盖
[PROTOCOL]: 变更时更新此头部，然后同步 README.md 顶部注释块
用法: python3 scripts/banner.py [字体路径] [输出路径]
"""
import os
import sys
import random
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
    "~/Library/Fonts/fusion-pixel-10px-monospaced-zh_hans.otf")
OUT = sys.argv[2] if len(sys.argv) > 2 else "assets/banner.svg"
FONT = ImageFont.truetype(FONT_PATH, 10)
random.seed(20261018)

# ---------- CONTENT：改这里，别改下文 ----------
NAME_GRID = "紫苏子"          # 左栏贡献图里拼出的三个字（10px 字形）
PROMPT_TAIL = "cat ./来路"
TITLE = "zisuzi@pixelxzen: ~"
NEOFETCH = [
    ("Name",  "紫苏子ACG Zisuzi"),
    ("Role",  "动画导演 / 全栈开发"),
    ("Motto", "一格一阶，把想象铺成路"),
    ("Build", "Phantom-Motion"),
    ("Films", "八仙系列 · 水墨动画"),
    ("Home",  "pixelxzen.github.io"),
]
ARIA = "紫苏子ACG · 独立动画导演 / 独立全栈开发"

# ---------- 调色板：紫 / 青 / 灰 ----------
BG, PANEL, LINE = "#0a0813", "#131024", "#272040"
FG, MUTE = "#ece9f6", "#8f89ab"
LABEL = "#8b70e0"   # key 列：比名字暗一档、比底纹亮一档
PURPLES = ["#1c1633", "#3b2a68", "#6d4fc4", "#a78bfa"]   # 四档「贡献量」
EMPTY = PANEL
ACCENT = "#22d3ee"                                        # 青：只给提示符 / 光标 / 扫光
SWATCH = ["#2a2144", "#5b3fa8", "#8b5cf6", "#c4b5fd",
          "#0e7490", "#22d3ee", "#8f89ab", "#ece9f6"]

W, H = 960, 340


def bitmap(text):
    """把一行字光栅化成 1bit 点阵，返回 (rows, 实际宽度)。字模必须是 10px 原生尺寸才不糊。"""
    w = int(FONT.getlength(text)) + 2
    im = Image.new("1", (w, 12), 0)
    d = ImageDraw.Draw(im)
    d.fontmode = "1"
    d.text((0, 0), text, font=FONT, fill=1)
    return [[im.getpixel((x, y)) for x in range(w)] for y in range(1, 11)], w


def text_path(text, x, y, s, color):
    """一行像素字：同行连续像素合并成一段 run，整行一个 path（体积比逐点 rect 小一个量级）。"""
    rows, w = bitmap(text)
    d = []
    for ry, row in enumerate(rows):
        rx = 0
        while rx < w:
            if row[rx]:
                st = rx
                while rx < w and row[rx]:
                    rx += 1
                d.append(f"M{x + st * s} {y + ry * s}h{(rx - st) * s}v{s}h-{(rx - st) * s}z")
            else:
                rx += 1
    return f'<path fill="{color}" d="{"".join(d)}"/>', int(FONT.getlength(text)) * s


def line(parts, x, y, s=2):
    out = []
    for text, color in parts:
        p, w = text_path(text, x, y, s, color)
        out.append(p)
        x += w
    return "".join(out), x


svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'shape-rendering="crispEdges" role="img" aria-label="{ARIA}">',
    '<defs><pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">'
    '<rect width="4" height="2" fill="#000" opacity=".18"/></pattern></defs>',
    f'<rect width="{W}" height="{H}" fill="{BG}"/>',
    f'<rect x="2" y="2" width="{W - 4}" height="{H - 4}" fill="none" stroke="{LINE}" stroke-width="4"/>',
]

# ---------- 标题栏 ----------
svg.append(f'<rect x="4" y="4" width="{W - 8}" height="36" fill="{PANEL}"/>'
           f'<rect x="4" y="40" width="{W - 8}" height="4" fill="{LINE}"/>')
for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    svg.append(f'<rect x="{22 + i * 22}" y="16" width="12" height="12" fill="{c}"/>')
t, _ = line([(TITLE, MUTE)], (W - int(FONT.getlength(TITLE)) * 2) // 2, 13)
svg.append(t)

# ---------- 左栏：名字贡献图 ----------
L_X, L_Y = 44, 70
t, _ = line([("$ ", ACCENT), ("whoami", FG)], L_X, L_Y)
svg.append(t)

rows, gw = bitmap(NAME_GRID)
CELL, SQ, COLS, ROWS = 11, 10, 32, 12
GX, GY = L_X, L_Y + 40
cells = []
for r in range(ROWS):
    for c in range(COLS):
        # 字形取满 10 行（少一行就掉笔画）；亮格单色不随机 —— 中文字形密集，深浅一乱就读不出
        on = 1 <= r <= 10 and 1 <= c <= gw and rows[r - 1][c - 1]
        color = PURPLES[3] if on else (PURPLES[0] if random.random() < .03 else EMPTY)
        cells.append(f'<rect x="{GX + c * CELL}" y="{GY + r * CELL}" width="{SQ}" height="{SQ}" fill="{color}"/>')
svg.append(f'<g>{"".join(cells)}</g>')

# 扫描光条：静态帧名字已完整可读，动画只是叠加层，SMIL 不播也不缺内容
svg.append(f'<clipPath id="grid"><rect x="{GX}" y="{GY}" width="{COLS * CELL}" height="{ROWS * CELL}"/></clipPath>'
           f'<g clip-path="url(#grid)"><rect x="{GX - 3 * CELL}" y="{GY}" width="{3 * CELL}" height="{ROWS * CELL}" '
           f'fill="{PURPLES[3]}" opacity=".22">'
           f'<animateTransform attributeName="transform" type="translate" '
           f'values="0 0;{(COLS + 3) * CELL} 0" dur="3.2s" repeatCount="indefinite"/></rect></g>')

legend_y = GY + ROWS * CELL + 14
legend_w = int(FONT.getlength("Less ") + 5 * 7 + FONT.getlength(" More")) * 2
t, lx = line([("Less ", MUTE)], GX + COLS * CELL - legend_w, legend_y)
svg.append(t)
for i, c in enumerate([EMPTY] + PURPLES):
    svg.append(f'<rect x="{lx + i * 14}" y="{legend_y + 2}" width="10" height="10" fill="{c}"/>')
t, _ = line([(" More", MUTE)], lx + 5 * 14, legend_y)
svg.append(t)

t, cx = line([("$ ", ACCENT), (PROMPT_TAIL, FG)], L_X, legend_y + 40)
svg.append(t)
svg.append(f'<rect x="{cx + 6}" y="{legend_y + 40}" width="10" height="20" fill="{ACCENT}">'
           '<animate attributeName="opacity" values="1;0" dur="1.1s" calcMode="discrete" repeatCount="indefinite"/></rect>')

# ---------- 右栏：neofetch ----------
R_X, y, LH = 440, 70, 26
t, _ = line([("zisuzi", PURPLES[3]), ("@", FG), ("github", PURPLES[3])], R_X, y)
svg.append(t)
y += LH
t, _ = line([("-" * 14, MUTE)], R_X, y)
svg.append(t)
for k, v in NEOFETCH:
    y += LH
    t, _ = line([(f"{k:<7}", LABEL), (v, FG)], R_X, y)
    svg.append(t)

y = H - 40
for i, c in enumerate(SWATCH):
    svg.append(f'<rect x="{R_X + i * 24}" y="{y}" width="24" height="16" fill="{c}"/>')

svg.append(f'<rect x="4" y="44" width="{W - 8}" height="{H - 48}" fill="url(#scan)"/></svg>')
open(OUT, "w").write("\n".join(svg) + "\n")
print(f"wrote {OUT}  name-grid={gw}x{len(rows)}  rows-end-y={y + 16}")
