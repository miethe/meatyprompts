# Copy Variants

Users can copy prompt content in different formats from prompt cards or the detail modal.

## Options

* **Copy body** – copies only the prompt body text.
* **Copy body + front-matter** – copies YAML front-matter followed by the body.
* **Copy JSON** – copies a JSON object mirroring the `/prompts` API response.

Each action shows a confirmation toast and records telemetry for `prompt_copied`.
