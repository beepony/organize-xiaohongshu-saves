# Capability fallbacks

Use this matrix when the host AI product does not expose the same tools as Codex. Preserve the workflow and evidence policy even when the execution method changes.

## Capability matrix

| Missing capability | Safe fallback | Do not do |
|---|---|---|
| Logged-in browser access | Ask for screenshots, copied post content, or a user-created export | Claim that likes or favorites were reviewed |
| Image/OCR tools | Ask for clearer images or a text transcription; mark unreadable fields | Guess small or obscured text |
| Script execution | Maintain UTF-8 JSON/CSV files using the host workspace or downloadable artifacts | Keep progress only in chat memory for long jobs |
| Persistent files | Process small batches and return a checkpoint file after each batch | Promise unattended completion across sessions |
| Word/online-document tools | Deliver validated Markdown and CSV for later import | Report a document as created without verifying its body |
| Comment access | Mark comment-derived fields as not checked | Present assumed comments as evidence |

## Portable prompt contract

For prompt-only products, require the user to supply:

1. Source scope and target count.
2. Inclusion and exclusion rules.
3. Exact field labels.
4. Post content, screenshots, or an export.
5. Desired output format.

Return one checkpoint object per source post using the schema in `project-schema.md`. Include the source order, decision, field values, evidence location, and confidence. Count reviewed source posts rather than retained records.

## Platform packaging

- Codex and compatible skill hosts: install the complete skill folder.
- Claude custom skills: package the skill folder as a ZIP accepted by the product.
- Gemini Spark skills: keep `SKILL.md` in the uploaded skill root and include only supported text files and scripts.
- ChatGPT custom GPTs, Doubao agents, and other consumer products: place core workflow rules in the product's instruction field and upload the schema and fallback reference as knowledge when supported.

Platform support changes over time. Check the host product's current documentation before promising browser control, background execution, script support, or shared-agent installation.
