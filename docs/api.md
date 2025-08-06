# API Documentation

This document describes the API for MeatyPrompts.

## Prompts

### GET /api/v1/prompts

Returns a list of prompts. Supports filtering by `model`, `tool`, and `purpose`.

**Query Parameters:**

*   `model` (string, optional): Filter by a specific model.
*   `tool` (string, optional): Filter by a specific tool.
*   `purpose` (string, optional): Filter by a specific purpose.

**Example:** `/api/v1/prompts?model=gpt-4&tool=python`

### POST /api/v1/prompts

Creates a new prompt.

**Request Body:**

```json
{
  "title": "My New Prompt",
  "purpose": ["To do something cool"],
  "models": ["gpt-4"],
  "tools": ["python"],
  "platforms": ["web"],
  "tags": ["testing"],
  "body": "This is the prompt text.",
  "visibility": "private"
}
```

**Response:** (201 Created)

Returns the created prompt version object.

### PUT /api/v1/prompts/{prompt_id}

Updates the latest version of a prompt.

**Request Body:**

Same as the `POST` request body.

**Response:**

Returns the updated prompt version object.

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
