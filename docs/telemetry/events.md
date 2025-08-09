# Telemetry Events

## prompt_edited

Emitted when a prompt is saved through the editor.

| Field       | Type   | Description                           |
|-------------|--------|---------------------------------------|
| prompt_id   | UUID   | Identifier of the prompt edited       |
| bytes       | number | Size of the prompt body in bytes      |
| elapsed_ms  | number | Time taken to persist the prompt save |

## prompt_duplicated

Emitted when a new version of a prompt is created via duplication.

| Field       | Type   | Description                           |
|-------------|--------|---------------------------------------|
| prompt_id   | UUID   | Identifier of the original prompt     |
| new_version | string | Version assigned to the duplicate     |
| elapsed_ms  | number | Time taken to perform duplication     |
