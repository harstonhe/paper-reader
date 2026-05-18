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

After the visual reader is complete, write a Xiaohongshu post for nursing graduate students unless the user only wants the figure/PDF. Keep the post body within 1000 Chinese characters so it can be pasted into Xiaohongshu. Also output a short Xiaohongshu title before the body.

Use the user's preferred logic:

1. Write a Xiaohongshu title.
   - Use the pattern: `护理科研 | 文献精读 02 LCA+网络分析`.
   - Format: `护理科研 | 文献精读 <two-digit number> <method/topic>`.
   - If the user provides a series number, use it. If there is clear prior numbering in the thread/output, continue it. Otherwise use `01`.
   - Keep the method/topic short, for example `症状网络分析`, `LCA+网络分析`, `潜在剖面分析`, `护士职业倦怠`, or `癌症症状管理`.

2. Start the body with paper identity, not a long opening.
   - 论文题目
   - 期刊
   - DOI

3. Explain what the paper focuses on in plain nursing-language.
   - Use a short setup like: "这篇文章关注的是..."
   - Compare the paper's framing with common clinical/research habits, for example "以往我们经常会问哪个症状发生率最高、哪个症状最严重", "抑郁水平高不高", or "职业倦怠总分高不高".
   - Move from the usual score/prevalence framing to the paper's added value: not only "how severe/common", but "which symptoms connect problems together".

4. Give the central reminder as a standalone sentence.
   - Format as a short punchline.
   - Example pattern: "最严重的症状，不一定是症状网络中最核心的症状。"

5. Summarize design and methods in one compact paragraph.
   - Include sample size, population, key scale/tool, variables/symptoms, and analysis method.
   - Avoid methods-heavy jargon unless it is central for nursing research learning.

6. Present the most interesting finding.
   - Use "最有意思的发现是：" before the finding.
   - If listing core symptoms or concepts, put each on its own short line.
   - Preserve English terms next to key Chinese terms when useful, such as "情绪痛苦 distress".
   - For latent class/profile + network papers, first name the identified profiles/classes with percentages if reported, then explain how the network differs across classes.
   - When bridge symptoms are central, frame them as "连接点/桥接症状", not as proven causes.

7. Translate findings into nursing research/practice implications.
   - Use the user's tone: "也就是说，从护理干预角度看..."
   - Emphasize how the paper changes symptom assessment, intervention target selection, or research design thinking.
   - For LCA/profile + network papers, explicitly translate the combined method:
     - LCA can answer "人群中有哪些不同类型的人".
     - Network analysis can answer "每一类人群中，哪些症状最关键、最值得干预".

8. Add a paragraph for nursing graduate students.
   - Say why the method is useful for symptom management, chronic disease management, cancer rehabilitation, patient-reported outcomes, or nursing research methods.
   - If relevant, note that symptom groups do not have to be studied only by traditional clustering; network analysis can show connection strength, core nodes, and possible intervention paths.

9. Add a limitations/caution paragraph.
   - For cross-sectional studies, explicitly say network relationships cannot be interpreted as causality.
   - Suggest longitudinal data when appropriate.
   - In method-learning posts, add a writing caution when relevant: avoid causal verbs such as "导致", "强化", "改善", "enhance", or "improve" for cross-sectional/correlational network findings; prefer cautious wording such as "相关", "连接更强", "可能提示", "可能是干预入口", "may be associated with", or "may serve as a potential target".

10. End without an over-polished marketing tone.
   - Do not force a "一句话总结" if the body already ends cleanly.
   - Keep the post suitable for Xiaohongshu: readable, lightly academic, not too formal.

11. Add targeted tags.
   - Default tags: `#护理研究生 #护理科研 #护理人懂护理人 #护理考研 #症状网络分析 #护理研究方法`
   - Add topic-specific tags only when natural, for example `#肿瘤护理`, `#慢病管理`, `#患者报告结局`.
   - Count tags inside the 1000-character body limit; use 6-8 tags.

## Xiaohongshu Post Template

Use this structure as the default:

```text
标题：
护理科研 | 文献精读 <two-digit number> <method/topic>

正文（1000字以内）：
论文题目：
<English title>

期刊：<journal>
DOI：<doi>

这篇文章关注的是<研究对象/问题>。以往我们做<领域>时，经常会问：<常见判断标准1>？<常见判断标准2>？然后优先处理这些问题。

但这篇文章提供了一个很重要的提醒：

<核心提醒句。>

研究纳入了 <N> 名<对象>，使用 <scale/tool> 评估 <symptoms/variables>。作者采用 <method>，探索<关系/机制>。

最有意思的发现是：

<主要发现。真正关键/核心的是：>

<术语1 English term>
<术语2 English term>

也就是说，从护理干预角度看，我们不能只盯着<传统重点>，还要思考：<研究启发问题1>？<研究启发问题2>？

如果论文结合了 LCA/潜在剖面/潜在类别分析和网络分析，加入这一段：

对护理科研来说，这篇文章很值得学习的地方在于，它把 <LCA/潜在剖面/潜在类别分析> 和网络分析结合起来了。<LCA/潜在类别分析> 回答“人群中有哪些不同类型的人”；网络分析回答“每一类人群中，哪些症状最关键、最值得干预”。

对护理研究生来说，这类方法很适合用于<适用研究方向>。它提醒我们，分组不一定只按总分高低，干预靶点也不一定只看平均分最高的变量。

不过也要注意，如果是横断面/相关性研究，不能直接推断因果。写论文时也要避免把结果写成“强化/改善/导致（enhance/improve）”，尽量用“可能提示”“相关”“连接更强”“潜在干预入口”等更谨慎的表达。

#护理研究生 #护理科研 #护理人懂护理人 #护理考研 #症状网络分析 #护理研究方法
```

## Content Rules

- Preserve the paper's claims; do not overstate causality for cross-sectional or correlational designs.
- For network-analysis posts, describe edges/centrality/bridge symptoms as associations or potential targets unless the paper has longitudinal/experimental evidence.
- For LCA/profile + network papers, make the method logic explicit: profiles/classes identify "which kinds of people"; networks identify "which symptoms connect or bridge problems within each group".
- Explain network/statistical terms in plain Chinese when useful, for example centrality, density, predictability, bootstrap stability.
- Prefer "核心转译" for the visual reader's practical interpretation and "一句话精读" for the visual reader's final bottom line.
- Use exact numeric findings from the paper when they are central to the argument.
- If original figures are unreadable after fitting, enlarge the figure area or reduce the number of figures rather than replacing them.
- For Xiaohongshu posts, prioritize clarity and nursing-research relevance over exhaustive detail.
- For Xiaohongshu posts, keep the body under 1000 Chinese characters, including hashtags. If the first draft is longer, cut background first, then methods detail, then secondary findings; preserve the title, DOI, central reminder, key findings, nursing implication, and causality caution.
- Always output a Xiaohongshu title separately from the body using `护理科研 | 文献精读 <two-digit number> <method/topic>`.
