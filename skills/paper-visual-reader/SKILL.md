---
name: paper-visual-reader
description: Generate Chinese-English visual literature reading summaries and Xiaohongshu-ready literature sharing posts from academic paper PDFs. Use when the user asks to make a 精读PDF, 文献精读图, research article summary, bilingual paper explainer, 小红书文献分享文案, or a layout matching a provided reference image. For a paper PDF, Codex should first extract key background, methods, findings, limitations, and original figures, produce a polished long-form image/PDF with the paper figures inserted exactly from the source, then write a concise Xiaohongshu post for nursing graduate students unless the user asks to skip the post.
---

# Paper Visual Reader

Create two linked outputs from one academic paper PDF:

1. A polished Chinese-English literature reading artifact, usually a vertical research-summary long image plus a PDF version.
2. A Xiaohongshu-ready Chinese literature sharing post for nursing graduate students.

Default order: make the visual reading image/PDF first, then write the Xiaohongshu post based on the same extracted paper logic.

## Visual Reader Workflow

1. Read the input PDF.
   - Use PyMuPDF (`fitz`) to extract title, authors, journal, DOI, abstract, methods, results, discussion, conclusion, figure captions, and page count.
   - Render likely figure pages to PNG and visually inspect them before cropping.
   - If the user provides a style/reference image, match its hierarchy, red accents, two-column intro, highlighted key sentences, and figure-focused lower section.

2. Select figures.
   - Prefer the main results figures from the paper, not supplementary figures, unless the user asks otherwise.
   - Insert figures by cropping/rendering from the PDF itself. Do not redraw, recreate, translate, or simplify the paper's figures when the user requests original figures.
   - Save cropped figures under an output folder next to the final artifact.

3. Write the bilingual reading content.
   - Top section: concise English background or abstract-style summary.
   - Highlight by complete key-finding sentences, not isolated keywords or whole accidental lines. Use the full sentence from its beginning to the ending period.
   - Chinese background: highlight the conclusion sentence(s), also from sentence beginning to sentence-ending punctuation.
   - Snapshot cards: design, sample/data, scale/measure, analysis/model.
   - Main results section: show the most important figure largest and place Chinese interpretation beside it.
   - Secondary results: place remaining original figures in smaller panels with short captions.
   - End with a one-sentence take-home message in English and a stronger Chinese "一句话精读".

4. Build a JSON spec for the renderer.
   - Use `scripts/render_visual_reader.py`.
   - Include absolute paths for cropped figure images.
   - Keep Chinese text concise enough for a single vertical page; shorten before lowering font size.

5. Render and verify.
   - Run the renderer to create PNG and PDF.
   - Open the PNG for visual inspection.
   - Check for overlapping text, clipped final lines, broken Chinese fonts, fuzzy figures, or captions outside panels.
   - Iterate until clean.

## Output Convention

Write outputs to:

```text
output/<paper-stem>_visual_reader/
```

Use stable names:

```text
figure1_original.png
figure2_original.png
visual_reader.png
visual_reader.pdf
visual_reader_spec.json
xhs_post.md
```

## Renderer Usage

Create a spec JSON, then run:

```bash
python <skill-dir>/scripts/render_visual_reader.py --spec output/<paper-stem>_visual_reader/visual_reader_spec.json
```

Minimum spec shape:

```json
{
  "output_png": "E:/project/Paper-reader/output/example_visual_reader/visual_reader.png",
  "output_pdf": "E:/project/Paper-reader/output/example_visual_reader/visual_reader.pdf",
  "journal": "Cancer Medicine",
  "badge": "RESEARCH ARTICLE SUMMARY",
  "category": "SYMPTOM NETWORK ANALYSIS",
  "title_en": "Paper title",
  "title_cn": "中文精读标题",
  "authors": "Author A, Author B",
  "doi": "10.xxxx/xxxxx",
  "english_summary": "Concise background and findings...",
  "english_highlights": [
    {"text": "Key finding: complete sentence.", "color": "#fae7e7"}
  ],
  "chinese_summary": "中文浓缩解读...",
  "chinese_highlights": [
    {"text": "最重要的结论句。", "color": "#fae7e7"}
  ],
  "snapshots": [
    {"label": "Design", "value": "Cross-sectional study / 横断面研究"}
  ],
  "main_figure": {
    "path": "E:/.../figure1_original.png",
    "title": "Figure 1 解读",
    "bullets": ["第一条解读", "第二条解读"]
  },
  "core_translation": "核心转译：...",
  "secondary_figures": [
    {"path": "E:/.../figure2_original.png", "title": "Figure 2 原文图", "caption": "简短说明"}
  ],
  "take_home_en": "Take-home message...",
  "take_home_cn": "一句话精读：..."
}
```

## PDF Figure Extraction Pattern

Use PyMuPDF for high-resolution crops:

```python
import fitz
doc = fitz.open(pdf_path)
page = doc[page_index]
rect = fitz.Rect(x0, y0, x1, y1)
pix = page.get_pixmap(matrix=fitz.Matrix(3.2, 3.2), clip=rect, alpha=False)
pix.save(output_path)
```

Render a full page first, inspect the PNG, then tune `rect`. Keep the crop close enough to remove surrounding article text, but include panel labels, axes, legends, and figure-internal titles.

## Xiaohongshu Post Workflow

After the visual reader is complete, write a Xiaohongshu post for nursing graduate students unless the user only wants the figure/PDF.

Use the user's preferred logic:

1. Start with paper identity, not a long opening.
   - 论文题目
   - 期刊
   - DOI

2. Explain what the paper focuses on in plain nursing-language.
   - Use a short setup like: "这篇文章关注的是..."
   - Compare the paper's framing with common clinical/research habits, for example "以往我们经常会问哪个症状发生率最高、哪个症状最严重".

3. Give the central reminder as a standalone sentence.
   - Format as a short punchline.
   - Example pattern: "最严重的症状，不一定是症状网络中最核心的症状。"

4. Summarize design and methods in one compact paragraph.
   - Include sample size, population, key scale/tool, variables/symptoms, and analysis method.
   - Avoid methods-heavy jargon unless it is central for nursing research learning.

5. Present the most interesting finding.
   - Use "最有意思的发现是：" before the finding.
   - If listing core symptoms or concepts, put each on its own short line.
   - Preserve English terms next to key Chinese terms when useful, such as "情绪痛苦 distress".

6. Translate findings into nursing research/practice implications.
   - Use the user's tone: "也就是说，从护理干预角度看..."
   - Emphasize how the paper changes symptom assessment, intervention target selection, or research design thinking.

7. Add a paragraph for nursing graduate students.
   - Say why the method is useful for symptom management, chronic disease management, cancer rehabilitation, patient-reported outcomes, or nursing research methods.
   - If relevant, note that symptom groups do not have to be studied only by traditional clustering; network analysis can show connection strength, core nodes, and possible intervention paths.

8. Add a limitations/caution paragraph.
   - For cross-sectional studies, explicitly say network relationships cannot be interpreted as causality.
   - Suggest longitudinal data when appropriate.

9. End without an over-polished marketing tone.
   - Do not force a "一句话总结" if the body already ends cleanly.
   - Keep the post suitable for Xiaohongshu: readable, lightly academic, not too formal.

10. Add targeted tags.
   - Default tags: `#护理研究生 #护理科研 #护理人懂护理人 #护理考研 #症状网络分析 #护理研究方法`
   - Add topic-specific tags only when natural, for example `#肿瘤护理`, `#慢病管理`, `#患者报告结局`.

## Xiaohongshu Post Template

Use this structure as the default:

```text
论文题目：
<English title>

期刊：<journal>
DOI：<doi>

这篇文章关注的是<研究对象/问题>。以往我们做<领域>时，经常会问：<常见判断标准1>？<常见判断标准2>？然后优先处理这些问题。

但这篇文章提供了一个很重要的提醒：

<核心提醒句。>

研究纳入了 <N> 名<对象>，使用 <scale/tool> 评估 <symptoms/variables>。作者采用 <method>，探索<关系/机制>，并计算<关键指标>。

最有意思的发现是：

<主要发现。真正关键/核心的是：>

<术语1 English term>
<术语2 English term>
<术语3 English term>

也就是说，从护理干预角度看，我们不能只盯着<传统重点>，还要思考：<研究启发问题1>？<研究启发问题2>？

<进一步解释临床/护理情境中的意义。>

对护理研究生来说，这类方法很适合用于<适用研究方向>。护理研究中的<传统概念>不一定只能用<传统方法>来做。<新方法>可以让我们看到<连接强度/核心节点/潜在干预路径>，非常适合用来拓展<研究主题>的思路。

不过也要注意，这是一项<研究设计>，<不能推断什么>。未来如果能结合<更好的数据/设计>，就可以进一步<未来方向>，也更接近真实的护理干预逻辑。

#护理研究生 #护理科研 #护理人懂护理人 #护理考研 #症状网络分析 #护理研究方法
```

## Content Rules

- Preserve the paper's claims; do not overstate causality for cross-sectional or correlational designs.
- Explain network/statistical terms in plain Chinese when useful, for example centrality, density, predictability, bootstrap stability.
- Prefer "核心转译" for the visual reader's practical interpretation and "一句话精读" for the visual reader's final bottom line.
- Use exact numeric findings from the paper when they are central to the argument.
- If original figures are unreadable after fitting, enlarge the figure area or reduce the number of figures rather than replacing them.
- For Xiaohongshu posts, prioritize clarity and nursing-research relevance over exhaustive detail.
