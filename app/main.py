from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from app.database import engine, get_db
from app import models
from app.config import settings
from app.routers import customers, invoices, analytics
from app.graphql.schema import schema
from app.graphql.context import get_graphql_context

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register routers
app.include_router(customers.router)
app.include_router(invoices.router)
app.include_router(analytics.router)

# Add GraphQL Router
graphql_app = GraphQLRouter(
    schema,
    context_getter=get_graphql_context
)
app.include_router(graphql_app, prefix="/graphql", tags=["GraphQL"])

@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "docs": "/docs",
        "graphql": "/graphql",
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "database": "healthy",
        "service": settings.app_name
    }

