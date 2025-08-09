# Telemetry Events

## prompt_edited

Emitted when a prompt is saved through the editor.

| Field       | Type   | Description                           |
|-------------|--------|---------------------------------------|
| prompt_id   | UUID   | Identifier of the prompt edited       |
| bytes       | number | Size of the prompt body in bytes      |
| elapsed_ms  | number | Time taken to persist the prompt save |
