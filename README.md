# Revenue Leakage Analytics Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Alembic](https://img.shields.io/badge/Alembic-1.13.2-red.svg?style=flat)](https://alembic.sqlalchemy.org/)
[![Docker Compose](https://img.shields.io/badge/Docker-Compose-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade **Revenue Leakage Analytics & Audit Platform** designed to detect, track, and remediate systemic financial discrepancies across the entire **Quote-to-Cash (Q2C) and Order-to-Cash (O2C)** lifecycle.

---

## 📌 Table of Contents

- [Overview](#-overview)
- [The Problem: Revenue Leakage](#-the-problem-revenue-leakage)
- [Key Features](#-key-features)
- [Architecture & Data Pipeline](#-architecture--data-pipeline)
- [Data Model & Entities](#-data-model--entities)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment Setup](#environment-setup)
  - [Running with Docker Compose](#running-with-docker-compose)
  - [Local Development Setup](#local-development-setup)
  - [Database Migrations (Alembic)](#database-migrations-alembic)
- [API Endpoints](#-api-endpoints)
- [Leakage Detection Vectors](#-leakage-detection-vectors)
- [Roadmap](#-roadmap)
- [License](#-license)

---

## 🔎 Overview

In high-volume B2B and SaaS operations, disconnects between sales quotes, contract fulfillment, warehouse fulfillment, invoicing, and payment reconciliation cost companies **1% to 5% of gross revenue**.

The **Revenue Leakage Analytics Platform** acts as an automated financial watchdog. By reconciling transactional flows across sales, logistics, and accounting databases, it flags anomalies such as unbilled fulfillments, under-invoicing, unauthorized discounts, duplicate credits, payment misallocations, and dormant disputes in real-time.

---

## ⚠️ The Problem: Revenue Leakage

Common failure points addressed by the platform:
1. **Unbilled Shipments:** Goods delivered or services rendered without corresponding invoices generated.
2. **Pricing & Discount Slippage:** Quotes agreed with unauthorized discount margins or discrepancies between quote line items and billed amounts.
3. **Mismatched Quantities:** Deliveries that diverge from ordered amounts without price adjustments.
4. **Payment Float & Unallocated Cash:** Payments received from customers that are never matched to open invoices, inflating days sales outstanding (DSO).
5. **Dormant Disputes & Unauthorized Write-offs:** Customer disputes lingering past SLA thresholds leading to uncollected revenue.

---

## 🚀 Key Features

- **Full Order-to-Cash Lifecycle Modeling:** Relational tracking covering Accounts, Quotes, Sales Orders, Shipments, Invoices, Payments, and Disputes.
- **Audit-Ready Status Event Ledger:** Immutable `status_events` stream capturing every entity transition, actor ID, correlation ID, and anomaly flags.
- **Robust Schema & Integrity Constraints:** Precise decimal math (`Numeric(20, 4)`) for financial amounts, strict foreign key constraints, and positive value checks to prevent negative billing errors.
- **FastAPI Core Engine:** High-performance asynchronous REST API with automatic OpenAPI (Swagger) documentation and Pydantic validation.
- **Enterprise-Grade Database Architecture:** Backed by PostgreSQL (Supabase engine compatible) with Alembic migration version control.
- **Fully Containerized:** Multi-container `docker-compose` setup for streamlined local and cloud deployments.

---

## 🏗️ Architecture & Data Pipeline

```
+--------------------------------------------------------------------------+
|                        Quote-to-Cash Lifecycle Engine                     |
+--------------------------------------------------------------------------+
  [Account] ──> [Quote & Lines] ──> [Sales Order & Lines]
                                             │
                       ┌─────────────────────┴─────────────────────┐
                       ▼                                           ▼
             [Shipment & Lines]                          [Invoice & Lines]
             (Fulfillment Track)                                   │
                       │                                           ▼
                       └───────────> [Dispute] <────────── [Payment & Allocations]
                                         │
                                         ▼
                             [Status Events & Audit Ledger]
                                         │
                                         ▼
                     [Revenue Leakage Detection & Anomaly Rules]
```

---

## 📊 Data Model & Entities

The platform models the complete financial pipeline via SQLAlchemy ORM models:

| Entity | Description | Key Relationships |
| :--- | :--- | :--- |
| `Account` | Corporate customer with credit limit, terms, and status | Quotes, Orders, Invoices, Payments, Disputes |
| `Quote` & `QuoteLine` | Negotiated commercial offers with discounts and taxes | Account, SalesOrder, Line items |
| `SalesOrder` & `OrderLine` | Executed contracts binding fulfillment and billing | Quote, Shipments, Invoices |
| `Shipment` & `ShipmentLine` | Physical or digital delivery records and accepted counts | SalesOrder, OrderLine |
| `Invoice` & `InvoiceLine` | Legally binding payment demands with status lifecycle | Account, SalesOrder, Allocations, Disputes |
| `Payment` & `PaymentAllocation` | Remittances received and allocated to outstanding invoices | Account, Invoices, Disputes |
| `Dispute` | Contested charges, deductions, and resolution tracking | Account, Invoice, Payment |
| `StatusEvent` | Immutable event log with correlation IDs and anomaly flags | Generic entity references |

---

## 📁 Project Structure

```bash
Revenue-Leakage-Analytics-Platform/
├── alembic/                      # Database migration scripts
│   ├── env.py                    # Alembic configuration environment
│   └── versions/                 # Revision scripts (e.g., initial schema)
├── backend/                      # FastAPI Application
│   ├── Dockerfile                # Backend container definition
│   ├── requirements.txt          # Python dependencies
│   └── app/
│       ├── __init__.py
│       ├── main.py               # FastAPI application entrypoint
│       ├── database.py           # DB connection & session factory
│       ├── db.py                 # Environment configuration loader
│       ├── models.py             # SQLAlchemy ORM relational models
│       └── api/
│           ├── __init__.py
│           └── v1/
│               ├── __init__.py
│               ├── router.py     # API routes (Accounts, Quotes, etc.)
│               └── schemas.py    # Pydantic validation schemas
├── .env.example                  # Template for environment configuration
├── .gitignore                    # Git ignore file for secrets and artifacts
├── alembic.ini                   # Alembic runtime settings
├── docker-compose.yml            # Multi-container orchestration
└── README.md                     # Project documentation
```

---

## 🛠️ Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) & Docker Compose
- Or locally: [Python 3.10+](https://www.python.org/) and a running [PostgreSQL 15+](https://www.postgresql.org/) instance

### Environment Setup

Create an `.env` file in the root directory (based on `.env.example`):

```bash
cp .env.example .env
```

Default local configuration:
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=revenue_leakage
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/revenue_leakage
```

---

### Running with Docker Compose

To spin up the PostgreSQL database and the FastAPI backend service together:

```bash
docker-compose up --build
```

Services will be accessible at:
- **FastAPI API & Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check:** [http://localhost:8000/health](http://localhost:8000/health)
- **PostgreSQL / Supabase DB:** `localhost:5432`

---

### Local Development Setup

If running without Docker:

1. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS / Linux:
   source .venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Run the backend development server:**
   ```bash
   cd backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

---

### Database Migrations (Alembic)

Run migrations to apply the latest database schemas:

**Using Docker:**
```bash
docker exec -it backend alembic upgrade head
```

**Locally:**
```bash
alembic upgrade head
```

To create a new auto-generated migration after editing `backend/app/models.py`:
```bash
alembic revision --autogenerate -m "describe schema change"
```

---

## 🔌 API Endpoints

The API is fully documented via interactive Swagger UI at `/docs`. Key endpoints include:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Service health status check |
| `GET` | `/api/v1/accounts` | List customer accounts with pagination |
| `POST` | `/api/v1/accounts` | Register a new customer account |
| `GET` | `/api/v1/quotes` | Retrieve commercial quotes |
| `POST` | `/api/v1/quotes` | Create a new quote with validation rules |

*(Additional endpoints for Orders, Shipments, Invoices, Payments, and Leakage Reports can be mounted under `/api/v1`)*

---

## 🎯 Leakage Detection Vectors

The platform architecture is designed to power the following analytics checks:

1. **Unbilled Shipment Detector:**
   $$\text{Quantity Shipped} > \text{Quantity Invoiced}$$
   Flags shipments where delivery occurred but invoice status remains unissued.

2. **Price Realization & Margin Variance:**
   $$\text{Invoice Unit Price} < \text{Contracted / Quoted Unit Price}$$
   Detects unauthorized post-quote discount leakage.

3. **Payment Reconciliation Deficit:**
   $$\text{Invoice Total Amount} - \sum \text{Payment Allocations} > 0 \quad (\text{past due date})$$
   Isolates overdue receivables and payment matching failures.

4. **Dispute SLA Breaches:**
   Identifies disputes open for longer than allowable credit window, preventing uncollectable debt write-offs.

---

## 🗺️ Roadmap

- [x] Initial relational database schema (Accounts, Quotes, Orders, Shipments, Invoices, Payments, Disputes)
- [x] Alembic migration pipeline setup
- [x] FastAPI base application with Pydantic validation
- [x] Docker & Docker Compose setup
- [ ] Synthetic revenue leakage dataset generation script (anomalous scenario generator)
- [ ] Automated reconciliation and leakage report endpoints
- [ ] Next.js analytics dashboard frontend with real-time discrepancy charts
- [ ] Automated email/webhook notifications for high-priority financial leaks

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
