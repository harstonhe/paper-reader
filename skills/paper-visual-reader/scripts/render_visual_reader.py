from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


W = 1800
MAX_H = 5200
M = 95
RED = "#b40016"
DEEP_RED = "#9f0014"
BLACK = "#161616"
GRAY = "#444444"
LIGHT_GRAY = "#f5f5f5"
LINE = "#9c2432"
DEFAULT_HIGHLIGHTS = ["#f8ead9", "#eef5e9", "#fae7e7", "#edf1fa"]


def load_font(candidates: list[str], size: int) -> ImageFont.FreeTypeFont:
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default(size=size)


F_EN_TITLE = load_font(["C:/Windows/Fonts/georgiab.ttf", "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"], 49)
F_EN_SUB = load_font(["C:/Windows/Fonts/arialbd.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"], 27)
F_EN = load_font(["C:/Windows/Fonts/arial.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf"], 30)
F_EN_SMALL = load_font(["C:/Windows/Fonts/arial.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf"], 24)
F_EN_BOLD = load_font(["C:/Windows/Fonts/arialbd.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"], 30)
F_CN_TITLE = load_font(["C:/Windows/Fonts/msyhbd.ttc", "C:/Windows/Fonts/NotoSansSC-VF.ttf"], 40)
F_CN = load_font(["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/NotoSansSC-VF.ttf"], 32)
F_CN_BOLD = load_font(["C:/Windows/Fonts/msyhbd.ttc", "C:/Windows/Fonts/NotoSansSC-VF.ttf"], 32)
F_CN_SMALL = load_font(["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/NotoSansSC-VF.ttf"], 27)
F_CN_SMALL_BOLD = load_font(["C:/Windows/Fonts/msyhbd.ttc", "C:/Windows/Fonts/NotoSansSC-VF.ttf"], 27)
F_BADGE = load_font(["C:/Windows/Fonts/arialbd.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"], 24)
F_JOURNAL = load_font(["C:/Windows/Fonts/georgiab.ttf", "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"], 62)


def text_w(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def line_h(draw: ImageDraw.ImageDraw, fnt: ImageFont.FreeTypeFont, text: str = "Hg") -> int:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[3] - box[1]


def wrap_mixed(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    tokens: list[str] = []
    buf = ""
    for ch in text:
        if ch.isascii() and (ch.isalnum() or ch in "-_./()%<>=±:;,+"):
            buf += ch
        else:
            if buf:
                tokens.append(buf)
                buf = ""
            tokens.append(" " if ch == " " else ch)
    if buf:
        tokens.append(buf)

    lines: list[str] = []
    cur = ""
    for tok in tokens:
        if tok == " " and not cur:
            continue
        test = cur + tok
        if text_w(draw, test, fnt) <= max_w or not cur:
            cur = test
        else:
            lines.append(cur.rstrip())
            cur = tok.lstrip()
    if cur:
        lines.append(cur.rstrip())
    return lines


def tokenize_with_offsets(text: str, highlights: list[dict[str, str]]) -> list[dict[str, Any]]:
    ranges: list[tuple[int, int, str]] = []
    for idx, item in enumerate(highlights):
        needle = item.get("text", "")
        if not needle:
            continue
        start = text.find(needle)
        if start >= 0:
            ranges.append((start, start + len(needle), item.get("color", DEFAULT_HIGHLIGHTS[idx % len(DEFAULT_HIGHLIGHTS)])))

    def color_for(start: int, end: int) -> str | None:
        for r_start, r_end, color in ranges:
            if start < r_end and end > r_start:
                return color
        return None

    tokens: list[dict[str, Any]] = []
    buf = ""
    buf_start = 0
    for i, ch in enumerate(text):
        if ch == "\n":
            if buf:
                tokens.append({"text": buf, "color": color_for(buf_start, i)})
                buf = ""
            tokens.append({"text": "\n", "color": None})
            continue
        if ch.isascii() and (ch.isalnum() or ch in "-_./()%<>=±:;,+"):
            if not buf:
                buf_start = i
            buf += ch
            continue
        if buf:
            tokens.append({"text": buf, "color": color_for(buf_start, i)})
            buf = ""
        tokens.append({"text": ch, "color": color_for(i, i + 1)})
    if buf:
        tokens.append({"text": buf, "color": color_for(buf_start, len(text))})
    return tokens


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.FreeTypeFont,
    max_w: int,
    fill: str = BLACK,
    leading: int = 10,
    highlights: list[dict[str, str]] | None = None,
) -> int:
    x, y = xy
    h = line_h(draw, fnt)
    if highlights:
        line: list[dict[str, Any]] = []
        width = 0

        def flush() -> None:
            nonlocal y, line, width
            while line and line[0]["text"] == " ":
                line.pop(0)
            while line and line[-1]["text"] == " ":
                line.pop()
            if not line:
                return
            cursor = x
            groups: list[tuple[int, int, str]] = []
            group_start: int | None = None
            group_color: str | None = None
            group_end = x
            for tok in line:
                tw = text_w(draw, tok["text"], fnt)
                color = tok.get("color")
                if color:
                    if group_color == color and group_start is not None:
                        group_end = cursor + tw
                    else:
                        if group_start is not None and group_color:
                            groups.append((group_start, group_end, group_color))
                        group_start = cursor
                        group_color = color
                        group_end = cursor + tw
                elif group_start is not None and group_color:
                    groups.append((group_start, group_end, group_color))
                    group_start = None
                    group_color = None
                cursor += tw
            if group_start is not None and group_color:
                groups.append((group_start, group_end, group_color))
            for gx0, gx1, color in groups:
                draw.rounded_rectangle((gx0 - 5, y - 2, gx1 + 5, y + h + 9), radius=4, fill=color)
            cursor = x
            for tok in line:
                draw.text((cursor, y), tok["text"], font=fnt, fill=fill)
                cursor += text_w(draw, tok["text"], fnt)
            y += h + leading
            line = []
            width = 0

        for tok in tokenize_with_offsets(str(text), highlights):
            if tok["text"] == "\n":
                flush()
                y += h + leading + 8
                continue
            if tok["text"] == " " and not line:
                continue
            tw = text_w(draw, tok["text"], fnt)
            if line and width + tw > max_w:
                flush()
                if tok["text"] == " ":
                    continue
            line.append(tok)
            width += tw
        flush()
        return y

    lines: list[str] = []
    for para in str(text).split("\n"):
        if para.strip():
            lines.extend(wrap_mixed(draw, para.strip(), fnt, max_w))
        lines.append("")
    if lines and lines[-1] == "":
        lines.pop()

    for ln in lines:
        if not ln:
            y += h + leading + 8
            continue
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += h + leading
    return y


def contain(img: Image.Image, box_w: int, box_h: int) -> Image.Image:
    cp = img.convert("RGB")
    cp.thumbnail((box_w, box_h), Image.Resampling.LANCZOS)
    return cp


def paste_panel(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    figure: dict[str, Any],
    box: tuple[int, int, int, int],
) -> int:
    x, y, w, h = box
    draw.rounded_rectangle((x, y, x + w, y + h), radius=6, fill="white", outline="#d9d9d9", width=2)
    draw.text((x + 18, y + 16), figure["title"], font=F_CN_SMALL_BOLD, fill=DEEP_RED)
    img = Image.open(figure["path"]).convert("RGB")
    scaled = contain(img, w - 36, h - 190)
    canvas.paste(scaled, (x + (w - scaled.width) // 2, y + 56))
    draw_wrapped(draw, (x + 22, y + h - 108), figure.get("caption", ""), F_CN_SMALL, w - 44, fill=GRAY, leading=4)
    return y + h


def render(spec: dict[str, Any]) -> tuple[Path, Path | None]:
    canvas = Image.new("RGB", (W, MAX_H), "white")
    draw = ImageDraw.Draw(canvas)

    badge = (M, 92, M + 455, 146)
    draw.rectangle(badge, fill=RED)
    draw.text((badge[0] + 18, badge[1] + 13), spec.get("badge", "RESEARCH ARTICLE SUMMARY"), font=F_BADGE, fill="white")
    draw.text((W - M - 470, 72), spec.get("journal", "Research Article"), font=F_JOURNAL, fill=DEEP_RED)

    y = 198
    draw.text((M, y), spec.get("category", "RESEARCH ARTICLE"), font=F_EN_SUB, fill=RED)
    y += 55
    title_end = draw_wrapped(draw, (M, y), spec["title_en"], F_EN_TITLE, 970, fill=BLACK, leading=8)
    draw.text((M, title_end + 20), spec.get("authors", ""), font=F_EN_SMALL, fill=BLACK)
    draw.text((M, title_end + 62), f"DOI: {spec.get('doi', '')}", font=F_EN_SMALL, fill=BLACK)

    cn_title_end = draw_wrapped(draw, (1130, 252), spec["title_cn"], F_CN_TITLE, 560, fill=DEEP_RED, leading=14)
    top_box_y = max(title_end + 135, cn_title_end + 85)

    draw.text((M, top_box_y), "Background / condensed abstract", font=F_EN_BOLD, fill=BLACK)
    en_end = draw_wrapped(
        draw,
        (M, top_box_y + 46),
        spec["english_summary"],
        F_EN,
        910,
        fill=BLACK,
        leading=9,
        highlights=spec.get("english_highlights", []),
    )
    cn_end = draw_wrapped(
        draw,
        (M + 990, top_box_y + 45),
        spec["chinese_summary"],
        F_CN,
        575,
        fill=BLACK,
        leading=12,
        highlights=spec.get("chinese_highlights", []),
    )
    top_end = max(en_end, cn_end) + 35
    draw.line((M, top_end, W - M, top_end), fill=LINE, width=3)

    table_y = top_end + 38
    draw.text((M, table_y), "Study Snapshot / 研究速览", font=F_CN_SMALL_BOLD, fill=DEEP_RED)
    snapshots = spec.get("snapshots", [])[:4]
    cell_w = (W - 2 * M - 36) // 4
    card_y = table_y + 48
    for i, item in enumerate(snapshots):
        cx = M + i * (cell_w + 12)
        draw.rounded_rectangle((cx, card_y, cx + cell_w, card_y + 150), radius=6, fill=LIGHT_GRAY, outline="#e0e0e0")
        draw.text((cx + 18, card_y + 17), item["label"], font=F_EN_BOLD, fill=DEEP_RED)
        draw_wrapped(draw, (cx + 18, card_y + 62), item["value"], F_CN_SMALL, cell_w - 36, fill=BLACK, leading=4)

    section_y = table_y + 236
    draw.rectangle((M, section_y, M + 255, section_y + 43), fill=RED)
    draw.text((M + 17, section_y + 10), "MAIN RESULTS", font=F_BADGE, fill="white")
    draw.text((M + 285, section_y + 5), "主要结果图表与解读", font=F_CN_SMALL_BOLD, fill=BLACK)

    main = spec["main_figure"]
    fig1 = Image.open(main["path"]).convert("RGB")
    fig1_scaled = contain(fig1, 950, 870)
    fig1_x = M
    fig1_y = section_y + 80
    canvas.paste(fig1_scaled, (fig1_x, fig1_y))
    interp_x = fig1_x + fig1_scaled.width + 58
    interp_y = fig1_y + 10
    draw.text((interp_x, interp_y), main.get("title", "Figure 解读"), font=F_CN_SMALL_BOLD, fill=DEEP_RED)
    bullets = "\n".join(f"{i + 1}. {b}" for i, b in enumerate(main.get("bullets", [])))
    draw_wrapped(draw, (interp_x, interp_y + 55), bullets, F_CN_SMALL, W - M - interp_x, fill=BLACK, leading=12)

    note_y = fig1_y + fig1_scaled.height + 25
    draw_wrapped(draw, (M + 30, note_y), spec.get("core_translation", ""), F_CN_BOLD, W - 2 * M - 60, fill=DEEP_RED, leading=10)

    secondary = spec.get("secondary_figures", [])
    y2 = note_y + 135
    if secondary:
        panel_gap = 36
        panel_w = (W - 2 * M - panel_gap) // 2
        panel_h = 1010
        for idx, figure in enumerate(secondary[:2]):
            px = M + (idx % 2) * (panel_w + panel_gap)
            py = y2 + (idx // 2) * (panel_h + 40)
            paste_panel(canvas, draw, figure, (px, py, panel_w, panel_h))
        bottom_y = y2 + ((len(secondary[:2]) + 1) // 2) * (panel_h + 40)
    else:
        bottom_y = y2

    draw.line((M, bottom_y, W - M, bottom_y), fill=LINE, width=2)
    y3 = draw_wrapped(draw, (M, bottom_y + 30), spec.get("take_home_en", ""), F_EN_SMALL, W - 2 * M, fill=GRAY, leading=6)
    y4 = draw_wrapped(draw, (M, y3 + 15), spec.get("take_home_cn", ""), F_CN_SMALL_BOLD, W - 2 * M, fill=BLACK, leading=8)

    used_h = min(MAX_H, y4 + 60)
    canvas = canvas.crop((0, 0, W, used_h))

    output_png = Path(spec["output_png"])
    output_png.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_png, quality=95)

    output_pdf = Path(spec["output_pdf"]) if spec.get("output_pdf") else None
    if output_pdf:
        output_pdf.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(output_pdf, "PDF", resolution=160.0)
    return output_png, output_pdf


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True, help="Path to visual reader JSON spec.")
    args = parser.parse_args()
    spec_path = Path(args.spec)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    png, pdf = render(spec)
    print(f"PNG: {png}")
    if pdf:
        print(f"PDF: {pdf}")


if __name__ == "__main__":
    main()
