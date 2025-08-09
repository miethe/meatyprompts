# Search

The `/prompts` endpoint provides basic text search across prompt titles and
bodies.  Search matches are case-insensitive and combine with all supplied
filters using ``AND`` semantics.

Relevance is approximated using PostgreSQL trigram similarity on the title
and body fields with a simple weighting.  When no query is supplied, results
are ordered by the most recently updated prompts.

Pagination uses a cursor that encodes the primary sort key and prompt
identifier.  Clients should treat the cursor as an opaque string.
