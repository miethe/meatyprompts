# 007: Markdown Editor Implementation

## Status
Accepted

## Context
A split-pane markdown editor with live preview is required for prompt editing. Two primary approaches were evaluated:

* **TipTap** – feature rich but heavy and opinionated, requiring substantial customization for markdown-first flows.
* **CodeMirror + ReactMarkdown** – lightweight, familiar, and easily extended with keyboard shortcuts.

## Decision
We chose **CodeMirror** for the editing surface and **react-markdown** with `rehype-sanitize` for the preview. This provides:

* Fast typing performance.
* Strict HTML sanitization to mitigate XSS.
* Simple toolbar/shortcut integration.

## Consequences
* Future block-based editors can replace the component while reusing the container.
* Sanitization configuration must be maintained as new markdown features are added.
