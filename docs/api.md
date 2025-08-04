# API Documentation

This document outlines the API endpoints for the MeatyPrompts application.

## Prompts

### `GET /api/v1/prompts`

- **Purpose:** Retrieves a list of all prompts.
- **Status:** Stubbed
- **Response:**
  ```json
  [
    {
      "id": "string",
      "title": "string",
      "content": "string",
      "model": "string",
      "createdAt": "string",
      "updatedAt": "string"
    }
  ]
  ```

### `POST /api/v1/prompts`

- **Purpose:** Creates a new prompt.
- **Status:** Stubbed
- **Request Body:**
  ```json
  {
    "title": "string",
    "content": "string",
    "model": "string"
  }
  ```
- **Response:**
  ```json
  {
    "id": "string",
    "title": "string",
    "content": "string",
    "model": "string",
    "createdAt": "string",
    "updatedAt": "string"
  }
  ```
