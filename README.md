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
  - [Troubleshooting](#troubleshooting)

## Features

- **Customer Management** - Create, read, update, and delete customer records
- **Invoice Management** - Handle invoices in multiple currencies with automatic conversion
- **Analytics** - Calculate total revenue and average invoice size across currencies
- **Multi-Currency Support** - Automatic exchange rate conversion to a default currency
- **Dual API Support** - Both REST and GraphQL endpoints available


## Database Schema
<img width="1562" height="1156" alt="db-schema" src="https://github.com/user-attachments/assets/4c30ae21-6635-4013-8c45-bd18159042cf" />


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
## Running the Application with Docker

To run the entire system using Docker, ensure you have Docker and Docker Compose installed, then execute:

```bash
# Start all services
docker-compose up
```

The application will be available at:

- **API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **GraphQL Playground:** http://localhost:8000/graphql

## API Documentation

### REST API Endpoints

The REST API is fully documented with an interactive Swagger UI.

**🔗 Live Documentation:** http://ec2-18-227-79-172.us-east-2.compute.amazonaws.com:8000/docs

### GraphQL Playground

The GraphQL API provides flexible querying.

**🔗 Live Playground:** http://ec2-18-227-79-172.us-east-2.compute.amazonaws.com:8000/graphql

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

### Exchange Rate API Errors

- Verify your API key is valid in `.env`
- Check API quota at https://www.exchangerate-api.com/
- Review logs for specific error messages

---

**Built with:** FastAPI, PostgreSQL, Docker, Strawberry GraphQL, SQLAlchemy

**Exchange rates provided by:** [ExchangeRate-API](https://www.exchangerate-api.com/)
