# Multi-Currency Invoice Analytics API

A powerful FastAPI-based REST and GraphQL API for managing customers, invoices, and analytics across multiple currencies with real-time exchange rate conversion and intelligent caching.

[![technologies](https://skillicons.dev/icons?i=python,fastapi,postgresql,docker,graphql)](https://github.com)

## Table of Contents

- [Multi-Currency Invoice Analytics API](#multi-currency-invoice-analytics-api)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Database Schema](#database-schema)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [Running the Application with Docker](#running-the-application-with-docker)
  - [API Documentation](#api-documentation)
    - [REST API Endpoints](#rest-api-endpoints)
    - [GraphQL Playground](#graphql-playground)
  - [Exchange Rate Caching](#exchange-rate-caching)
  - [Running Tests](#running-tests)
  - [API Usage Examples](#api-usage-examples)
  - [Troubleshooting](#troubleshooting)

## Features

- **Customer Management** - Create, read, update, and delete customer records
- **Invoice Management** - Handle invoices in multiple currencies with automatic conversion
- **Analytics** - Calculate total revenue and average invoice size across currencies
- **Multi-Currency Support** - Automatic exchange rate conversion to a default currency
- **Exchange Rate Caching** - Database-level caching for improved performance (1-hour cache)
- **Dual API Support** - Both REST and GraphQL endpoints available
- **Soft Delete** - Non-destructive deletion of records
- **Comprehensive Testing** - Full test suite with 27 unit tests

## Database Schema

The database schema includes three main tables optimized for performance:

**Tables:**

- **customers** - Customer information with soft delete support
- **invoices** - Invoice records with multi-currency support and exchange rates
- **exchange_rate_cache** - Cached exchange rates (1-hour TTL) for performance optimization

### Schema Details

**customers**

- `id` (Primary Key), `name`, `created_at`, `updated_at`, `deleted_at`

**invoices**

- `id` (Primary Key), `customer_id` (Foreign Key), `amount`, `currency`, `default_currency`
- `amount_in_default_currency`, `exchange_rate`, `created_at`, `updated_at`, `deleted_at`

**exchange_rate_cache**

- `id` (Primary Key), `from_currency`, `to_currency`, `rate`, `created_at`
- Indexed on `(from_currency, to_currency)` for fast lookups

## Getting Started

### Prerequisites

Before running the application, ensure you have the following installed:

- [Docker](https://docs.docker.com/get-docker/) (v20.10 or higher)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.0 or higher)
- Exchange Rate API Key (free at [ExchangeRate-API](https://www.exchangerate-api.com/))

### Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd Multi-Currency-Invoice
   ```

2. **Configure environment variables:**

   ```bash
   cp env.example .env
   ```

   Edit the `.env` file and add your configuration:

   ```env
   # Exchange Rate Configuration
   EXCHANGE_RATE_API_KEY=your_actual_api_key_here
   EXCHANGE_RATE_API_URL=https://v6.exchangerate-api.com/v6

   # Database Configuration
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=fastapi_db
   POSTGRES_HOST=db
   POSTGRES_PORT=5432

   # Application Configuration
   DEFAULT_CURRENCY=USD
   APP_NAME="Multi-Currency Invoice Analytics API"
   APP_VERSION="1.0.0"
   ```

3. **Build and start the application:**
   ```bash
   docker-compose up --build
   ```

## Running the Application with Docker

To run the entire system using Docker, ensure you have Docker and Docker Compose installed, then execute:

```bash
# Start all services
docker-compose up --build

# Run in detached mode (background)
docker-compose up -d --build

# Stop the application
docker-compose down

# Stop and remove volumes (reset database)
docker-compose down -v
```

The application will be available at:

- **API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **GraphQL Playground:** http://localhost:8000/graphql

## API Documentation

### REST API Endpoints

The REST API is fully documented with interactive Swagger UI.

**🔗 Live Documentation:** http://ec2-18-227-79-172.us-east-2.compute.amazonaws.com:8000/docs

**Available Endpoints:**

**Customers**

- `POST /customers/` - Create a new customer
- `GET /customers/` - List all customers (supports pagination)
- `PUT /customers/{customer_id}` - Update customer details
- `DELETE /customers/{customer_id}` - Soft delete a customer

**Invoices**

- `POST /invoices/` - Create a new invoice with automatic currency conversion
- `GET /invoices/` - List all invoices (supports filtering and pagination)
- `GET /invoices/{invoice_id}` - Get specific invoice details
- `PUT /invoices/{invoice_id}` - Update invoice details
- `DELETE /invoices/{invoice_id}` - Soft delete an invoice

**Analytics**

- `GET /analytics/total-revenue` - Calculate total revenue across all invoices
  - Query params: `target_currency`, `customer_id`, `start_date`, `end_date`
- `GET /analytics/average-invoice` - Calculate average invoice size
  - Query params: `target_currency`, `customer_id`, `start_date`, `end_date`

**Utility**

- `GET /` - API welcome message with links
- `GET /health` - Health check endpoint

### GraphQL Playground

The GraphQL API provides flexible querying and mutations.

**🔗 Live Playground:** http://ec2-18-227-79-172.us-east-2.compute.amazonaws.com:8000/graphql

**Example Queries:**

```graphql
# Get all customers
customers {
  id
  name
  createdAt
}

# Get all invoices with customer details
invoices {
  id
  amount
  currency
  customer {
    name
  }
}
```

**Example Mutations:**

```graphql
# Create customer
createCustomer(name: "Customer Name") {
  id
  name
}

# Create invoice
createInvoice(customerId: 1, amount: 1000.00, currency: "USD") {
  id
  amount
  exchangeRate
}
```

## Exchange Rate Caching

The application implements an intelligent database-level caching system for exchange rates to improve performance and reduce external API calls.

### How It Works

1. **First Request:** When an exchange rate is requested (e.g., EUR to USD):

   - System checks the `exchange_rate_cache` table
   - If not found or expired, fetches from ExchangeRate-API
   - Stores the rate in the database with a timestamp

2. **Subsequent Requests:**

   - Returns cached rate if still valid (within 1 hour)
   - No external API call needed

3. **Inverse Rate Optimization:**
   - If EUR→USD is cached, USD→EUR is calculated as 1/rate
   - Reduces API calls by 50% for bidirectional conversions

### Performance Benefits

- **Faster Response Times** - Cached rates return in <10ms vs 200-500ms for API calls
- **Reduced API Costs** - Fewer external API requests
- **Better Reliability** - Works even if external API is temporarily unavailable
- **Scalability** - Handles high request volumes efficiently

**Configuration:**

- Cache Duration: 1 hour (configurable in `app/services/exchange_rate.py`)
- Storage: PostgreSQL `exchange_rate_cache` table
- Automatic Updates: Expired rates are automatically refreshed

## Running Tests

The project includes a comprehensive test suite covering all main endpoints.

```bash
# Run all tests
docker-compose run --rm api pytest tests/ -v

# Run specific test files
docker-compose run --rm api pytest tests/test_customers.py -v
docker-compose run --rm api pytest tests/test_invoices.py -v
docker-compose run --rm api pytest tests/test_analytics.py -v
```

**Test Coverage:**

- 27 tests total
- Customer endpoints (7 tests)
- Invoice endpoints (13 tests)
- Analytics endpoints (7 tests)

All tests use an in-memory SQLite database, so no external database setup is required.

## API Usage Examples

### Create a Customer

```bash
curl -X POST "http://localhost:8000/customers/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Acme Corporation"}'
```

### Create an Invoice

```bash
curl -X POST "http://localhost:8000/invoices/" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "amount": 1000.00,
    "currency": "EUR"
  }'
```

### Get Total Revenue

```bash
# Total revenue in USD
curl "http://localhost:8000/analytics/total-revenue"

# Total revenue in EUR for specific customer
curl "http://localhost:8000/analytics/total-revenue?target_currency=EUR&customer_id=1"

# Total revenue for date range
curl "http://localhost:8000/analytics/total-revenue?start_date=2024-01-01&end_date=2024-12-31"
```

## Troubleshooting

### Database Connection Issues

```bash
# Check if database is running
docker-compose ps

# View database logs
docker-compose logs db

# Restart services
docker-compose restart
```

### API Not Responding

```bash
# Check API logs
docker-compose logs api

# Rebuild containers
docker-compose down
docker-compose up --build
```

### Exchange Rate API Errors

- Verify your API key is valid in `.env`
- Check API quota at https://www.exchangerate-api.com/
- Review logs for specific error messages

---

**Built with:** FastAPI, PostgreSQL, Docker, Strawberry GraphQL, SQLAlchemy

**Exchange rates provided by:** [ExchangeRate-API](https://www.exchangerate-api.com/)
