---
name: organize-xiaohongshu-saves
description: Organize a user's authorized Xiaohongshu/REDnote likes, favorites, or named collection albums into evidence-grounded structured data and reports. Use when an AI agent must review selected or first-N saved posts, filter relevant content, extract requested fields from captions, images, video frames, and comments, checkpoint after every post, resume interrupted work, and deliver Markdown, CSV, Word, Google Docs, or Feishu-style guides without inventing missing facts.
---

# Organize Xiaohongshu Saves

Turn a logged-in user's likes, favorites, or collection album into a resumable, auditable report. Treat the source entries reviewed—not the number of retained records—as the completion target.

## Required operating rules

- Operate only in the user's authorized logged-in session. Never request, export, or expose cookies, passwords, tokens, or browser profile data.
- Do not bypass login, CAPTCHA, private-account controls, rate limits, or platform restrictions.
- Read only the source scope the user selected. Do not like, unlike, collect, uncollect, comment, follow, publish, or message unless separately requested.
- Process personal-use extraction at a human browsing pace. Summarize rather than reproduce full copyrighted posts.
- Never guess a navigation point, price, facility, rule, or other fact. Use the project's not-mentioned label when evidence is absent.
- Separate author statements, image text, commenter claims, and external cross-checks. Mark conflicts explicitly.
- After every source post, write a checkpoint and rebuild the working report before opening the next post.
- Continue until every target source position is `include` or `exclude` and validation passes. Commentary updates are not completion.

## Check capabilities before starting

Determine the strongest safe operating mode available:

1. **Full browser mode**: use an authorized browser/computer tool, inspect all requested source surfaces, and checkpoint locally.
2. **Assisted mode**: when direct browser access is unavailable, ask the user to provide an export, screenshots, or copied post content in batches; apply the same evidence and checkpoint rules.
3. **Prompt-only mode**: when neither tools nor local persistence are available, produce a structured extraction template and explain that the user must supply the source content. Never claim to have reviewed a logged-in collection.

Read [references/capability-fallbacks.md](references/capability-fallbacks.md) when the host product is not Codex or lacks browser, script, OCR, or document tools.

## Prepare the project

Resolve these inputs from the request or visible source context:

1. Source: likes, all favorites, or a named album.
2. Selection: first N, date range, keyword subset, or all visible entries.
3. Relevance rule: what to include and exclude.
4. Output fields: exact labels requested by the user.
5. Output: Markdown/CSV by default; Word, Google Docs, or Feishu when requested.

Ask only for inputs that cannot be discovered safely. If the user says “first 30” and lists fields, start without another confirmation.

When local script execution is available, create a project beside the intended deliverable:

```bash
python scripts/xhs_project.py init \
  --project /absolute/path/to/project \
  --source-type album \
  --source-name "示例周末活动" \
  --limit 30 \
  --field "导航地址" \
  --field "玩耍攻略和注意事项" \
  --field "停车攻略和费用" \
  --field "是否有厕所" \
  --field "周围饮食" \
  --include "直接玩水、溯溪、桨板或赶海" \
  --exclude "纯徒步、停车、普通公园或与主题无关" \
  --output-title "示例亲水活动攻略"
```

Read [references/project-schema.md](references/project-schema.md) before creating the first item JSON. Read [references/review-workflow.md](references/review-workflow.md) when browser/image review is required.

Generate a blank checkpoint when useful:

```bash
python scripts/xhs_project.py template \
  --project /absolute/path/to/project \
  --order 1 \
  --output /absolute/path/to/item-001.json
```

The template intentionally fails `upsert` until its title and review decision are completed.

## Enumerate before extracting

Open the selected Xiaohongshu source in the user's logged-in browser. Capture the visible source order first:

- Assign stable `order` values starting at 1.
- Record each card title and source URL when available.
- Stop enumeration at the requested limit even if exclusions appear.
- If lazy loading changes indices, use titles/order from the checkpoint rather than stale UI indices.

The limit counts source cards reviewed. Excluding a card does not pull in a later replacement unless the user explicitly asks for N retained results.

## Review one source post

For each position, perform this sequence:

1. Read title, author, date, caption, and visible structured text.
2. Inspect every relevant image or carousel page. Use screenshots or image viewing/OCR; record which media were checked.
3. Inspect video frames only when requested fields appear in video overlays or the caption is insufficient.
4. Read comments only when they add requested facts or current status. Distinguish author replies from ordinary comments.
5. Apply the relevance rule. Use `exclude` with a concrete reason when the primary scenario is outside scope.
6. For included posts, create one or more `records`. A multi-location roundup produces multiple records while still counting as one reviewed source post.
7. Populate every requested field with value, evidence, and confidence. Use the not-mentioned label rather than leaving fields empty.
8. Save the item JSON and checkpoint it immediately:

```bash
python scripts/xhs_project.py upsert \
  --project /absolute/path/to/project \
  --item-file /absolute/path/to/item-007.json
```

`upsert` atomically updates `items.json`, then rebuilds `report.md`, `included.csv`, and `excluded.csv`.

When script execution is unavailable, preserve the same object shape from [references/project-schema.md](references/project-schema.md) in the host product's workspace or downloadable files. Keep one stable source `order` per reviewed card and never store credentials.

## Evidence policy

Use these confidence values:

- `confirmed`: explicitly stated by the author or clearly readable in source media.
- `author-comment`: stated by the author in comments.
- `comment-only`: stated only by another commenter; present as unverified.
- `conflicting`: source statements disagree; show the conflict and advise rechecking.
- `not-mentioned`: checked source surfaces but found no reliable answer.
- `image-unreadable`: likely present in media but cannot be read reliably.

Keep evidence concise, for example `正文`, `图片 3`, `作者评论 2026-07-18`, or `评论区多方说法不一致`. Do not paste long post passages.

## Resume and persistence

Before browsing on a resumed run, execute:

```bash
python scripts/xhs_project.py status --project /absolute/path/to/project
```

Continue from the lowest missing or pending `order`. Never restart completed positions unless the user asks to refresh them.

If the Mac locks, a page fails, or authentication expires:

- Preserve the checkpoint and continue any safe local report work.
- Retry the authorized browser connection once using the applicable browser skill.
- If login/unlock is genuinely required, tell the user exactly what to unlock or sign in to; resume from status afterward.
- Do not silently replace inaccessible personal saves with search-engine results.

## Validate completion

Run:

```bash
python scripts/xhs_project.py validate --project /absolute/path/to/project
```

Do not deliver while validation reports missing orders, pending decisions, empty included records, or missing requested fields.

Then build the requested final artifact:

- Markdown/CSV: use the generated files directly.
- Word: use the Documents skill to transform `report.md`, render the DOCX, inspect every page, and iterate.
- Google Docs: use the Google Docs/Drive skill or import the verified DOCX when no native template constrains the document.
- Feishu: use an available Feishu connector; otherwise use the authorized browser UI. Verify the resulting document contains body text before sharing.

If the host product cannot create the requested artifact, deliver the validated Markdown and CSV source files and state the limitation clearly.

The final response must state the reviewed-source count, included-record count, excluded-source count, unresolved/conflicting count, and link the deliverable.

## Common requests

- “整理我点赞里前 50 条装修内容，提取品牌、型号、价格和避坑点。”
- “把收藏专辑里的餐厅筛出来，按地址、人均、必点菜、停车、预约整理。”
- “检查我的旅行收藏，把非亲子内容排除，输出 Word 行程攻略。”
- “从健身收藏中提取动作、目标肌群、组数、禁忌和器械，做成 CSV。”
