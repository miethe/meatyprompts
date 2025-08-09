# 009 Export Format Guarantee

## Status
Accepted

## Context

Users require a stable format when exporting their prompt library so that data
can be moved between systems without breakage. The existing `Prompt` API model
already describes the canonical shape of a prompt.

## Decision

The JSON export feature emits an array of objects that exactly match the
`Prompt` response model used by the API. Any future changes to the `Prompt`
model must remain backward compatible or be versioned separately.

## Consequences

* Downstream tools can rely on the export format matching the API response.
* Snapshot tests can detect unintentional changes to the export payload.
