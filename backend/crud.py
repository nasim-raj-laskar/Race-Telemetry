from sqlalchemy import text
from sqlalchemy.orm import Session

def fetch_rows_after_id(
    db: Session,
    last_id: int,
    limit: int = 1
):
    query = text("""
        SELECT *
        FROM my_table
        WHERE id > :last_id
        ORDER BY id ASC
        LIMIT :limit
    """)

    result = db.execute(
        query,
        {"last_id": last_id, "limit": limit}
    )

    columns = result.keys()
    rows = result.fetchall()

    return [dict(zip(columns, row)) for row in rows]
