# Project schema

Use UTF-8 JSON. `project.json` is created by the bundled script. Create one item file per reviewed source card and pass it to `upsert`.

## Item object

```json
{
  "order": 7,
  "title": "Original post title",
  "url": "https://www.xiaohongshu.com/explore/...",
  "author": "Author name",
  "published_at": "2026-07-04",
  "decision": "include",
  "decision_reason": "Directly covers the requested scenario",
  "media_reviewed": ["caption", "image-1", "image-2", "comments"],
  "records": [
    {
      "name": "Place or subject name",
      "fields": {
        "导航地址": {
          "value": "示例游客中心",
          "evidence": "正文",
          "confidence": "confirmed"
        },
        "是否有厕所": {
          "value": "原帖未提及",
          "evidence": "已检查正文、图片和可见评论",
          "confidence": "not-mentioned"
        }
      },
      "notes": ["Recent comment says the entrance may be closed; recheck before departure."]
    }
  ],
  "source_notes": ["Photos were taken last year."],
  "reviewed_at": "2026-07-31T18:30:00+08:00"
}
```

For an excluded post, set `decision` to `exclude`, provide `decision_reason`, and use an empty `records` array.

## Required rules

- `order`: integer from 1 through the project limit.
- `decision`: `include` or `exclude`; `pending` is allowed only during drafting and fails final validation.
- `records`: non-empty for included items. A roundup may contain multiple records.
- `fields`: contain every label from `project.json.fields` for every included record.
- Field values may be strings, numbers, booleans, or lists. The report converts them to readable text.
- `confidence`: one of `confirmed`, `author-comment`, `comment-only`, `conflicting`, `not-mentioned`, or `image-unreadable`.
- `evidence`: short provenance, not a long quotation.
