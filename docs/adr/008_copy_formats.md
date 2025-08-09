# 008: Copy Formats

Date: 2024-06-09

## Status
Accepted

## Context
Prompt users need to copy prompts in multiple formats for different tools.

## Decision
Provide three copy variants:

* Body only
* Body with YAML front-matter including title, tags, target_models, providers, link, access_control, version and updated_at
* JSON matching the `Prompt` API response

## Consequences
Ensures consistent downstream usage and prepares for future export and share features.
