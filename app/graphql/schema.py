import strawberry
from app.graphql.queries import Query

# Read-only schema
schema = strawberry.Schema(query=Query)

