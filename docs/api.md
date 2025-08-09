# API Overview

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
