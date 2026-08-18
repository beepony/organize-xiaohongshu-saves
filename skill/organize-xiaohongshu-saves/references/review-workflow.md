# Browser and media review workflow

## Source surfaces

Prefer the user's explicitly named browser. Otherwise use an applicable browser connector/skill before Computer Use. Keep the authenticated session inside the chosen browser; do not inspect or export its credentials.

Review these surfaces in order:

1. Collection/likes card order.
2. Post caption and visible metadata.
3. Every image in the post carousel.
4. Relevant video frames or overlay text.
5. Author replies and recent comments when needed for current status.

## Image handling

- Capture the original-resolution image or the clearest available screenshot.
- Inspect maps, receipts, menus, parking signs, product labels, itineraries, and warning text.
- Record media provenance as `图片 N` or `视频 00:14`.
- If text is too small or obstructed, mark `image-unreadable`; do not infer characters from context.
- When a map provides a landmark but not a full address, preserve the landmark and label it as a navigation keyword.

## Comment handling

- Treat an author reply as `author-comment`.
- Treat other comments as `comment-only` unless corroborated.
- Use `conflicting` when comments contradict the caption or each other.
- Prefer recent operational information for closures and fees, but state its date and uncertainty.

## UI reliability

- Refresh the accessibility/DOM state after every navigation before reusing an element reference.
- Save the item checkpoint before navigating away.
- If a detail modal overlays the collection, close/back to the collection before selecting the next stable order.
- Avoid final responses used only as progress updates. Continue within the active run until validation passes or a user action is genuinely required.
