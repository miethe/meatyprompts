# API Documentation

This document describes the API for MeatyPrompts.

## Prompts

### GET /api/v1/prompts

Returns a list of prompts.

### POST /api/v1/prompts

Creates a new prompt.

**Request Body:**

```json
{
  "title": "My New Prompt",
  "purpose": "To do something cool",
  "models": ["gpt-3.5-turbo"],
  "tools": ["python"],
  "tags": ["testing"],
  "body": "This is the prompt text.",
  "visibility": "private"
}
```

**Response:**

```json
{
  "id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "title": "My New Prompt",
  "purpose": "To do something cool",
  "models": ["gpt-3.5-turbo"],
  "tools": ["python"],
  "tags": ["testing"],
  "body": "This is the prompt text.",
  "visibility": "private",
  "version": 1,
  "createdAt": "2025-08-05T14:54:42.964981Z",
  "prompt_id": "p1q2r3s4-t5u6-v7w8-x9y0-z1a2b3c4d5e6"
}
```
