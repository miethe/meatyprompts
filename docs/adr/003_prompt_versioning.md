# 3. Prompt Versioning

Date: 2025-08-05

## Status

Accepted

## Context

We need a way to store and manage prompts, including their history. This will allow us to track changes to prompts over time, and to revert to previous versions if necessary.

## Decision

We will use a two-table system to store prompts and their versions. The `prompts` table will store the header information for each prompt, including a slug and a reference to the latest version. The `prompt_versions` table will store the actual content of each prompt version.

This approach allows us to easily query for the latest version of a prompt, while still maintaining a complete history of all changes. It also provides a clean separation between the prompt's metadata and its content.

## Consequences

This decision will require us to create two new tables in our database. It will also require us to update our API and frontend to work with the new data model. However, we believe that the benefits of this approach outweigh the costs.
