# ADR 004: Strategy for Managing Dynamic, User-Extensible Metadata

## Status

Accepted

## Context

The platform needs to associate prompts with various metadata, such as AI models, tools, and platforms. Some of these metadata categories are predefined but should be extensible by users in the future (e.g., a user might want to add a new AI model that is not yet in our system). We need a flexible and scalable way to store and manage this data.

## Decision

We will use separate **lookup tables** for each category of extensible metadata (e.g., `models_lookup`, `tools_lookup`, `platforms_lookup`). Each lookup table will have a simple structure, typically a `UUID` primary key and a unique `TEXT` value.

The `prompt_versions` table will store arrays of these values (e.g., `models TEXT[]`) rather than foreign keys to the lookup tables.

## Consequences

### Advantages

*   **Extensibility**: New options can be added to the lookup tables at runtime via API endpoints without requiring a schema change or a new deployment. This is the primary driver for this decision.
*   **Decoupling**: The prompt service is not hardcoded with enum values. It can query the lookup tables to get the available options.
*   **Performance**: For filtering, querying for the existence of a value in a `TEXT[]` array using a GIN index is very performant in PostgreSQL. It avoids complex joins that would be required if we used a many-to-many relationship table.
*   **Simplicity**: The schema is straightforward and easy to understand. The API for managing lookup values is simple and consistent across different types.

### Disadvantages

*   **Data Integrity**: There is no foreign key constraint between the `prompt_versions` table and the lookup tables. This means it's technically possible to have a value in `prompt_versions.models` that does not exist in `models_lookup`. This is a trade-off we accept for the flexibility of this approach. The application layer will be responsible for ensuring data consistency.
*   **Potential for Duplication**: If not handled carefully at the application layer, it's possible to create duplicate-meaning entries (e.g., "GPT-4" and "gpt-4"). The API will handle this by enforcing uniqueness on the `value` column and using consistent casing.
