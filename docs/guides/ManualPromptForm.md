# Manual Prompt Form

`ManualPromptForm` renders the full set of fields required to create or update a prompt. The component now supports a `readOnly` property which disables all inputs and renders the internal `CodeEditor` instances in a non-editable state. This is useful when the form is reused for display-only scenarios such as the Prompt Detail modal.
