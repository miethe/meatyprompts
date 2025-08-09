# API Overview

Copying prompts as JSON produces the same structure returned by `GET /prompts`.
No additional API endpoints were added for this feature.

## GET /prompts

Returns a paginated list of prompts for the authenticated user.

### Query Parameters

| Name | Type | Description |
|------|------|-------------|
| `q` | string | Optional text to search in title and body |
| `tags` | string[] | Tags that must all be present on the prompt |
| `favorite` | bool | When `true`, only favorite prompts are returned |
| `archived` | bool | When `true`, only archived prompts are returned |
| `target_models` | string[] | Filter by target model identifiers |
| `providers` | string[] | Filter by model providers |
| `purposes` | string[] | Filter by use cases (alias `use_cases`) |
| `collection_id` | UUID | Limit results to a collection |
| `sort` | enum | `updated_desc` (default), `created_desc`, `title_asc`, `relevance_desc` |
| `limit` | int | Maximum number of items to return (≤50) |
| `after` | string | Cursor from a previous response for pagination |

### Response

```json
{
  "items": [ { /* Prompt */ } ],
  "next_cursor": "opaque-string-or-null",
  "count": 37,
  "total_estimate": null
}
```

The `next_cursor` value should be sent in the `after` query parameter to
retrieve the next page.  The cursor format is opaque and may change over
time.

## GET /_int/tenancy/ping

Internal endpoint that returns the current tenant identifier from the session
context. It is intended for development and testing of tenancy features.

## Collections

### GET /collections

List all collections for the authenticated user.

Optional query parameter `include=count` adds a `count` field with the
number of prompts in each collection.

### POST /collections

Create a collection by providing a JSON body `{ "name": "Project" }`.
Returns the created collection. Duplicate names for the same user result
in `409`.

### PATCH /collections/{collection_id}

Rename a collection. Body matches the create request. Returns the updated
collection.

### DELETE /collections/{collection_id}

Remove a collection and its prompt memberships. Responds with `204` on
success.

### POST /collections/{collection_id}/prompts

Add a prompt to a collection with body `{ "prompt_id": "uuid" }`.
Operation is idempotent and returns `{ "ok": true }`.

### DELETE /collections/{collection_id}/prompts/{prompt_id}

Remove a prompt from a collection. Responds with `204` even if the
membership does not exist.
