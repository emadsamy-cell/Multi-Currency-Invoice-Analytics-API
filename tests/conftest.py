"""Pytest configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models import Customer, Invoice, ExchangeRateCache

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database session override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_customer(db_session):
    """Create a sample customer for testing."""
    customer = Customer(name="Test Customer")
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer


@pytest.fixture
def sample_invoice(db_session, sample_customer):
    """Create a sample invoice for testing."""
    invoice = Invoice(
        customer_id=sample_customer.id,
        amount=1000.00,
        currency="USD",
        default_currency="USD",
        amount_in_default_currency=1000.00,
        exchange_rate=1.0
    )
    db_session.add(invoice)
    db_session.commit()
    db_session.refresh(invoice)
    return invoice


@pytest.fixture
def multiple_invoices(db_session, sample_customer):
    """Create multiple invoices for testing analytics."""
    invoices = [
        Invoice(
            customer_id=sample_customer.id,
            amount=1000.00,
            currency="USD",
            default_currency="USD",
            amount_in_default_currency=1000.00,
            exchange_rate=1.0
        ),
        Invoice(
            customer_id=sample_customer.id,
            amount=500.00,
            currency="EUR",
            default_currency="USD",
            amount_in_default_currency=550.00,
            exchange_rate=1.1
        ),
        Invoice(
            customer_id=sample_customer.id,
            amount=750.00,
            currency="GBP",
            default_currency="USD",
            amount_in_default_currency=975.00,
            exchange_rate=1.3
        )
    ]
    
    for invoice in invoices:
        db_session.add(invoice)
    
    db_session.commit()
    return invoices


@pytest.fixture
def exchange_rate_cache(db_session):
    """Create sample exchange rate cache entries."""
    cache_entries = [
        ExchangeRateCache(from_currency="EUR", to_currency="USD", rate=1.0842),
        ExchangeRateCache(from_currency="GBP", to_currency="USD", rate=1.2743),
    ]
    
    for entry in cache_entries:
        db_session.add(entry)
    
    db_session.commit()
    return cache_entries



