# Data Model

The Phase-1 database schema stores prompt metadata and versioned content.

## prompts
| Column | Type | Notes |
| --- | --- | --- |
| id | UUID | Primary key |
| owner_id | UUID | FK to `users.id` |
| title | text | Prompt title |
| tags | text[] | Optional labels |
| is_favorite | boolean | Default `false` |
| is_archived | boolean | Default `false` |
| block_count | integer | Reserved for future block editing |
| embedding | vector | Reserved for semantic search |
| icon_url | text | Optional icon URL |
| created_at | timestamptz | Creation timestamp |
| updated_at | timestamptz | Updated timestamp (indexed with `owner_id`) |

## prompt_versions
| Column | Type | Notes |
| --- | --- | --- |
| id | UUID | Primary key |
| prompt_id | UUID | FK to `prompts.id` |
| version | integer | Sequential version number |
| body | text | Prompt content |
| access_control | prompt_access_control | Enum `private` ∕ `unlisted` |
| use_cases | text[] | Required use cases |
| target_models | text[] | Optional target models |
| providers | text[] | Optional providers |
| integrations | text[] | Optional integrations |
| category | text | Optional category |
| complexity | text | Optional complexity |
| audience | text | Optional audience |
| status | text | Optional status |
| input_schema | jsonb | Optional input schema |
| output_format | text | Optional output format |
| llm_parameters | jsonb | Optional LLM parameters |
| success_metrics | jsonb | Optional success metrics |
| sample_input | jsonb | Optional sample input |
| sample_output | jsonb | Optional sample output |
| related_prompt_ids | uuid[] | Optional related prompt IDs |
| link | text | Optional reference link |
| created_at | timestamptz | Creation timestamp |
| updated_at | timestamptz | Last update |

## collections
| Column | Type | Notes |
| --- | --- | --- |
| id | UUID | Primary key |
| owner_id | UUID | FK to `users.id` |
| name | text | Unique per owner |
| created_at | timestamptz | Creation timestamp |
| updated_at | timestamptz | Last update (indexed with `owner_id`) |

## collection_prompts
| Column | Type | Notes |
| --- | --- | --- |
| collection_id | UUID | FK to `collections.id` (cascade delete) |
| prompt_id | UUID | FK to `prompts.id` (cascade delete) |
Primary key is `(collection_id, prompt_id)`.

## share_tokens
Unique tokens that allow read-only sharing of prompts.

Lookup tables (`models_lookup`, `tools_lookup`, `platforms_lookup`, `purposes_lookup`) store reference values for form options.
