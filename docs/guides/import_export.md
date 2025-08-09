# Import and Export

This guide describes how to transfer prompt data using the API.

## Import

Send a `POST /api/v1/import` request with a CSV or JSON file and a mapping of
columns to prompt fields. The mapping values correspond to the column names or
JSON keys in the uploaded file. Array fields such as `tags` and
`target_models` should be comma separated strings which are automatically
split and normalised.

A dry run can be performed by setting `dry_run=true` (default). The response
includes validation results for the first 20 rows. To persist the data, submit
the same request with `dry_run=false`.

## Export

Use `GET /api/v1/export` to download all prompts owned by the current user as a
JSON array. Pass `collection_id` to restrict the export to a single
collection.

The export format matches the `Prompt` model returned by the API and is stable
for future versions.
