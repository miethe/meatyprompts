"""Service layer for tag suggestions."""
from __future__ import annotations

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.tag import TagCount


def top_tags(db: Session, limit: int = 20, query: Optional[str] = None) -> List[TagCount]:
    """Return the most frequently used tags.

    Parameters
    ----------
    db: Session
        Database session used to execute the query.
    limit: int, default 20
        Maximum number of tags to return.
    query: Optional[str]
        Optional prefix to filter tag suggestions. Matching is case-insensitive.

    Returns
    -------
    List[TagCount]
        A list of tag/count pairs sorted by frequency descending.
    """
    base_sql = (
        "SELECT tag, COUNT(*) AS count FROM (SELECT UNNEST(tags) AS tag FROM prompts) t"
    )
    params: dict[str, object] = {"limit": limit}
    if query:
        base_sql += " WHERE tag LIKE :q"
        params["q"] = f"{query.lower()}%"
    base_sql += " GROUP BY tag ORDER BY count DESC LIMIT :limit"
    result = db.execute(text(base_sql), params)
    rows = result.fetchall()
    return [TagCount(tag=row["tag"], count=row["count"]) for row in rows]
