# Collections

Collections group related prompts for faster retrieval.

## Creating Collections

Use the “New Collection” control in the sidebar or send a `POST /collections`
request with a name. Names are unique per user and may include letters,
numbers, spaces and `-_.&/` characters.

## Adding Prompts

Open a prompt and choose “Add to collection” to select one or more
collections. Membership updates save immediately.

## Filtering the Vault

Select a collection in the sidebar or pass `collection_id` to
`GET /prompts` to show only prompts in that collection. Clearing the
filter returns to the full list.
