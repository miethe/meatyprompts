# Prompt Versioning

Prompts are versioned to preserve history. Each save as a new version creates a
separate record with an incremented version number.

## Duplication

Using the **Duplicate** action creates a new version of the current prompt. The
new version number is one greater than the latest and the prompt title is
updated with a `(vX)` suffix where `X` is the new version. Previous versions are
retained.

Tags remain associated with the prompt header while version-specific fields like
providers and models are copied to the new version.

## UI cues

The prompt cards and detail views display the version using a `vX` badge. After
duplicating, the badge reflects the new version and the title shows the
corresponding suffix.
