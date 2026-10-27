from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import (
    Index,

    Column,
    String,
    Integer,
    DateTime,
    Numeric,
    Enum,
    ForeignKey,
    JSON,
    UniqueConstraint,
    CheckConstraint,
    Boolean,
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Enumerations
from enum import Enum as PyEnum

class AccountStatus(PyEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    CLOSED = "CLOSED"

class QuoteStatus(PyEnum):
    DRAFT = "DRAFT"
    SENT = "SENT"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    CONVERTED = "CONVERTED"

class OrderStatus(PyEnum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    PARTIALLY_FULFILLED = "PARTIALLY_FULFILLED"
    FULFILLED = "FULFILLED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"

class ShipmentStatus(PyEnum):
    PLANNED = "PLANNED"
    PICKED = "PICKED"
    SHIPPED = "SHIPPED"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"

class InvoiceStatus(PyEnum):
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID = "PAID"
    OVERDUE = "OVERDUE"
    VOID = "VOID"
    DISPUTED = "DISPUTED"

class PaymentStatus(PyEnum):
    RECEIVED = "RECEIVED"
    CLEARED = "CLEARED"
    FAILED = "FAILED"
    REVERSED = "REVERSED"
    REFUNDED = "REFUNDED"

class DisputeStatus(PyEnum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

# Helper mixin for timestamps
class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

# Core Entities
class Account(Base, TimestampMixin):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String, unique=True, nullable=False)
    account_name = Column(String, nullable=False)
    account_type = Column(String, nullable=False)
    industry = Column(String, nullable=True)
    country = Column(String, nullable=False)
    region = Column(String, nullable=True)
    currency = Column(String(3), nullable=False)
    credit_limit = Column(Numeric(20, 4), nullable=False, default=Decimal('0'))
    payment_terms_days = Column(Integer, nullable=False, default=30)
    account_status = Column(Enum(AccountStatus), nullable=False, default=AccountStatus.ACTIVE)

    # Relationships
    quotes = relationship("Quote", back_populates="account")
    orders = relationship("SalesOrder", back_populates="account")
    invoices = relationship("Invoice", back_populates="account")
    payments = relationship("Payment", back_populates="account")
    disputes = relationship("Dispute", back_populates="account")

class Quote(Base, TimestampMixin):
    __tablename__ = "quotes"
    id = Column(Integer, primary_key=True, index=True)
    quote_id = Column(String, unique=True, nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    quote_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=False)
    currency = Column(String(3), nullable=False)
    subtotal = Column(Numeric(20, 4), nullable=False, default=Decimal('0'))
    discount_amount = Column(Numeric(20, 4), nullable=False, default=Decimal('0'))
    tax_amount = Column(Numeric(20, 4), nullable=False, default=Decimal('0'))
    total_amount = Column(Numeric(20, 4), nullable=False, default=Decimal('0'))
    status = Column(Enum(QuoteStatus), nullable=False, default=QuoteStatus.DRAFT)
    accepted_at = Column(DateTime, nullable=True)
    rejected_at = Column(DateTime, nullable=True)

    account = relationship("Account", back_populates="quotes")
    lines = relationship("QuoteLine", back_populates="quote", cascade="all, delete-orphan")
    sales_order = relationship("SalesOrder", back_populates="quote", uselist=False)

    __table_args__ = (
        CheckConstraint("credit_limit >= 0", name="ck_quote_credit_nonnegative"),
    )

class QuoteLine(Base):
    __tablename__ = "quote_lines"
    id = Column(Integer, primary_key=True, index=True)
    quote_line_id = Column(String, unique=True, nullable=False)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=False)
    line_number = Column(Integer, nullable=False)
    product_code = Column(String, nullable=False)
    product_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(20, 4), nullable=False)
    discount_amount = Column(Numeric(20, 4), nullable=False, default=Decimal('0'))
    tax_rate = Column(Numeric(5, 2), nullable=False, default=Decimal('0'))
    line_total = Column(Numeric(20, 4), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    quote = relationship("Quote", back_populates="lines")
    order_line = relationship("OrderLine", back_populates="quote_line", uselist=False)

    __table_args__ = (
        UniqueConstraint('quote_id', 'line_number', name='uq_quote_line_number'),
        CheckConstraint('quantity > 0', name='ck_quote_line_quantity_positive'),
    )

class SalesOrder(Base, TimestampMixin):
    __tablename__ = "sales_orders"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, unique=True, nullable=False)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    order_date = Column(DateTime, nullable=False)
    requested_delivery_date = Column(DateTime, nullable=False)
    currency = Column(String(3), nullable=False)
    subtotal = Column(Numeric(20, 4), nullable=False, default=Decimal('0'))
    discount_amount = Column(Numeric(20, 4), nullable=False, default=Decimal('0'))
    tax_amount = Column(Numeric(20, 4), nullable=False, default=Decimal('0'))
    total_amount = Column(Numeric(20, 4), nullable=False, default=Decimal('0'))
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.DRAFT)
    closed_at = Column(DateTime, nullable=True)

    account = relationship("Account", back_populates="orders")
    quote = relationship("Quote", back_populates="sales_order")
    lines = relationship("OrderLine", back_populates="order", cascade="all, delete-orphan")
    shipments = relationship("Shipment", back_populates="order")
    invoices = relationship("Invoice", back_populates="order")

class OrderLine(Base):
    __tablename__ = "order_lines"
    id = Column(Integer, primary_key=True, index=True)
    order_line_id = Column(String, unique=True, nullable=False)
    order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=False)
    quote_line_id = Column(Integer, ForeignKey("quote_lines.id"), nullable=False)
    line_number = Column(Integer, nullable=False)
    product_code = Column(String, nullable=False)
    quantity_ordered = Column(Integer, nullable=False)
    unit_price = Column(Numeric(20, 4), nullable=False)
    discount_amount = Column(Numeric(20, 4), nullable=False, default=Decimal('0'))
    tax_rate = Column(Numeric(5, 2), nullable=False, default=Decimal('0'))
    line_total = Column(Numeric(20, 4), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    order = relationship("SalesOrder", back_populates="lines")
    quote_line = relationship("QuoteLine", back_populates="order_line")
    shipment_lines = relationship("ShipmentLine", back_populates="order_line")
    invoice_lines = relationship("InvoiceLine", back_populates="order_line")

    __table_args__ = (
        UniqueConstraint('order_id', 'line_number', name='uq_order_line_number'),
        CheckConstraint('quantity_ordered > 0', name='ck_order_line_quantity_positive'),
    )

class Shipment(Base, TimestampMixin):
    __tablename__ = "shipments"
    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(String, unique=True, nullable=False)
    order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=False)
    shipment_date = Column(DateTime, nullable=False)
    delivery_date = Column(DateTime, nullable=True)
    carrier = Column(String, nullable=False)
    tracking_reference = Column(String, nullable=True)
    status = Column(Enum(ShipmentStatus), nullable=False, default=ShipmentStatus.PLANNED)

    order = relationship("SalesOrder", back_populates="shipments")
    lines = relationship("ShipmentLine", back_populates="shipment", cascade="all, delete-orphan")

class ShipmentLine(Base):
    __tablename__ = "shipment_lines"
    id = Column(Integer, primary_key=True, index=True)
    shipment_line_id = Column(String, unique=True, nullable=False)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False)
    order_line_id = Column(Integer, ForeignKey("order_lines.id"), nullable=False)
    quantity_shipped = Column(Integer, nullable=False)
    quantity_accepted = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    shipment = relationship("Shipment", back_populates="lines")
    order_line = relationship("OrderLine", back_populates="shipment_lines")

    __table_args__ = (
        CheckConstraint('quantity_shipped >= 0', name='ck_shipment_line_quantity_nonnegative'),
    )

class Invoice(Base, TimestampMixin):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(String, unique=True, nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=False)
    invoice_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    currency = Column(String(3), nullable=False)
    subtotal = Column(Numeric(20, 4), nullable=False, default=Decimal('0'))
    discount_amount = Column(Numeric(20, 4), nullable=False, default=Decimal('0'))
    tax_amount = Column(Numeric(20, 4), nullable=False, default=Decimal('0'))
    total_amount = Column(Numeric(20, 4), nullable=False, default=Decimal('0'))
    status = Column(Enum(InvoiceStatus), nullable=False, default=InvoiceStatus.DRAFT)

    account = relationship("Account", back_populates="invoices")
    order = relationship("SalesOrder", back_populates="invoices")
    lines = relationship("InvoiceLine", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("PaymentAllocation", back_populates="invoice")
    disputes = relationship("Dispute", back_populates="invoice")

class InvoiceLine(Base):
    __tablename__ = "invoice_lines"
    id = Column(Integer, primary_key=True, index=True)
    invoice_line_id = Column(String, unique=True, nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    order_line_id = Column(Integer, ForeignKey("order_lines.id"), nullable=False)
    product_code = Column(String, nullable=False)
    quantity_billed = Column(Integer, nullable=False)
    unit_price = Column(Numeric(20, 4), nullable=False)
    discount_amount = Column(Numeric(20, 4), nullable=False, default=Decimal('0'))
    tax_rate = Column(Numeric(5, 2), nullable=False, default=Decimal('0'))
    line_total = Column(Numeric(20, 4), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    invoice = relationship("Invoice", back_populates="lines")
    order_line = relationship("OrderLine", back_populates="invoice_lines")

    __table_args__ = (
        CheckConstraint('quantity_billed > 0', name='ck_invoice_line_quantity_positive'),
    )

class Payment(Base, TimestampMixin):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(String, unique=True, nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    payment_date = Column(DateTime, nullable=False)
    payment_method = Column(String, nullable=False)
    currency = Column(String(3), nullable=False)
    amount_received = Column(Numeric(20, 4), nullable=False)
    external_reference = Column(String, nullable=True)
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.RECEIVED)

    account = relationship("Account", back_populates="payments")
    allocations = relationship("PaymentAllocation", back_populates="payment")
    disputes = relationship("Dispute", back_populates="payment")

class PaymentAllocation(Base, TimestampMixin):
    __tablename__ = "payment_allocations"
    id = Column(Integer, primary_key=True, index=True)
    allocation_id = Column(String, unique=True, nullable=False)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    allocated_amount = Column(Numeric(20, 4), nullable=False)
    allocation_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    allocation_status = Column(String, nullable=False, default="ALLOCATED")

    payment = relationship("Payment", back_populates="allocations")
    invoice = relationship("Invoice", back_populates="payments")

class Dispute(Base, TimestampMixin):
    __tablename__ = "disputes"
    id = Column(Integer, primary_key=True, index=True)
    dispute_id = Column(String, unique=True, nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    dispute_type = Column(String, nullable=False)
    disputed_amount = Column(Numeric(20, 4), nullable=False)
    reason = Column(String, nullable=True)
    status = Column(Enum(DisputeStatus), nullable=False, default=DisputeStatus.OPEN)
    opened_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    resolution = Column(String, nullable=True)

    invoice = relationship("Invoice", back_populates="disputes")
    payment = relationship("Payment", back_populates="disputes")
    account = relationship("Account", back_populates="disputes")

class StatusEvent(Base):
    __tablename__ = "status_events"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=False)
    previous_status = Column(String, nullable=True)
    new_status = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    occurred_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    recorded_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    actor_type = Column(String, nullable=True)
    actor_id = Column(Integer, nullable=True)
    correlation_id = Column(String, nullable=True)
    source_system = Column(String, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    is_anomaly_fixture = Column(Boolean, default=False)

    __table_args__ = (
        Index('ix_status_events_entity', 'entity_type', 'entity_id'),
    )

# Additional placeholder tables (Product, Users, etc.) can be added later.
