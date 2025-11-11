from app.database import get_db


async def get_graphql_context() -> dict:
    db = next(get_db())
    try:
        yield {"db": db}
    finally:
        db.close()

