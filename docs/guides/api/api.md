# API Documentation

This document describes the API for MeatyPrompts.

## Authentication

See [Authentication API](api/auth.md) for details on login, `/me`, and logout.

## Prompts

### GET /api/v1/prompts

Returns a list of prompts. Supports filtering by `model`, `provider`, and `use_case`.

**Query Parameters:**

*   `model` (string, optional): Filter by a specific model.
*   `provider` (string, optional): Filter by a specific provider.
*   `use_case` (string, optional): Filter by a specific use case.

**Example:** `/api/v1/prompts?model=gpt-4o`

### GET /api/v1/prompts/{id}

Fetch the latest version of a prompt by its identifier. Returns `404` if not found.

### POST /api/v1/prompts

Creates a new prompt.

**Request Body:**

```json
{
  "title": "My New Prompt",
  "body": "This is the prompt text.",
  "use_cases": ["testing"],
  "access_control": "private",
  "tags": ["example"]
}
```

**Response:** (201 Created)

Returns the created prompt including header fields.

### PUT /api/v1/prompts/{prompt_id}

Updates the latest version of a prompt without creating a new version.

**Response:**

Returns the updated prompt including header fields.

## Lookups

### GET /api/v1/lookups/{type}

Returns a list of available lookup values for a given type.

**Path Parameters:**

*   `type` (string): The type of lookup to fetch. Can be one of `models`, `tools`, `platforms`, `purposes`.

**Example:** `/api/v1/lookups/models`

**Response:**

```json
[
  {
    "id": "uuid-for-gpt4",
    "value": "gpt-4"
  },
  {
    "id": "uuid-for-claude",
    "value": "claude-2"
  }
]
```

### POST /api/v1/lookups/{type}

Creates a new lookup value for a given type. If the value already exists, the existing object is returned.

**Path Parameters:**

*   `type` (string): The type of lookup to create.

**Request Body:**

```json
{
  "value": "my-new-tool"
}
```

**Response:** (200 OK)

Returns the created or existing lookup object.

## Tags

### GET /api/v1/tags

Fetch the most commonly used tags, optionally filtered by a prefix.

**Query Parameters:**

* `query` (string, optional): Prefix to filter tags.
* `limit` (integer, optional): Maximum number of tags to return. Defaults to 20.

**Response:**

```json
[
  {"tag": "example", "count": 5}
]
```
