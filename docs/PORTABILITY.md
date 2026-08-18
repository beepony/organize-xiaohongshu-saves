# Cross-platform portability

The reusable asset has three separate layers. Keeping them separate prevents a prompt format from being mistaken for execution permission.

## 1. Workflow contract

The portable contract defines:

- source scope and target count;
- inclusion and exclusion rules;
- requested field labels;
- evidence and confidence policy;
- one checkpoint per source post;
- completion validation and output schema.

This layer can be represented as instructions plus JSON/YAML and works with most capable language models.

## 2. Host adapter

Each AI product exposes different instruction, knowledge, script, browser, OCR, persistence, and document features.

| Host type | Installation approach | Expected limitation |
|---|---|---|
| Codex-style skills | Install the complete skill folder | Browser/document tools depend on the local environment |
| ZIP skill hosts | Upload a ZIP whose skill root contains `SKILL.md` | Script and network policies vary |
| Custom GPT / custom agent | Copy the portable instructions and upload references | Instructions alone cannot access a logged-in collection |
| Plain chat | Paste the universal prompt and upload source batches | Progress must be returned as files between sessions |

Do not describe an adapter as fully automatic until it has been tested with the target product's current permissions.

## 3. Source collector

Logged-in collection access is the non-portable part. A consumer-friendly product should eventually provide a local browser extension or desktop companion that:

1. runs only after explicit user action;
2. reads visible content from the user's existing session without exporting credentials;
3. captures text and user-approved images at a human pace;
4. writes a local, resumable source package;
5. sends only the selected content to the model chosen by the user;
6. exports Markdown, CSV, Word, or an online document.

The AI model then becomes replaceable. Users can choose Codex, Claude, Gemini, ChatGPT, Doubao, another hosted model, or a local model without changing the project schema.

## Degraded modes

- Without browser access: accept screenshots, copied text, or exports.
- Without OCR: ask for clearer images or a transcription and mark unreadable content.
- Without scripts: maintain the same checkpoint schema in downloadable JSON/CSV.
- Without persistence: process small batches and return a checkpoint after every batch.
- Without document creation: return validated Markdown and CSV.

Never imply that a model inspected content that the user did not provide and the host could not access.
