# Telemetry Events

## prompt_edited

Emitted when a prompt is saved through the editor.

| Field       | Type   | Description                           |
|-------------|--------|---------------------------------------|
| prompt_id   | UUID   | Identifier of the prompt edited       |
| bytes       | number | Size of the prompt body in bytes      |
| elapsed_ms  | number | Time taken to persist the prompt save |

## vault_search_performed

Emitted when a search is executed in the Vault interface.

| Field          | Type     | Description                                      |
|----------------|----------|--------------------------------------------------|
| query_length   | number   | Length of the search query in characters         |
| filters_used   | string[] | Names of filters applied to the search           |
| result_count   | number   | Number of results returned in the current page   |
| p95_bucket     | number   | Performance bucket for latency measurement       |
| query_hash     | string   | Hash of the raw query text (no PII in logs)      |
