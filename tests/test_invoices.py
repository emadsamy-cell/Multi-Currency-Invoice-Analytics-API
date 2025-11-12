"""Unit tests for invoice endpoints."""
import pytest
from fastapi import status
from unittest.mock import patch, AsyncMock


class TestInvoiceEndpoints:
    @patch('app.services.exchange_rate.ExchangeRateService.get_exchange_rate')
    def test_create_invoice(self, mock_exchange_rate, client, sample_customer):
        """Test POST /invoices/ returns 201 and creates invoice with exchange rate conversion."""
        mock_exchange_rate.return_value = 1.0842
        
        response = client.post(
            "/invoices/",
            json={
                "customer_id": sample_customer.id,
                "amount": 1000.00,
                "currency": "EUR"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["customer_id"] == sample_customer.id
        assert data["amount"] == 1000.00
        assert data["currency"] == "EUR"
        assert "exchange_rate" in data
        assert "amount_in_default_currency" in data
    
    def test_create_invoice_invalid_customer(self, client):
        """Test POST /invoices/ returns 404 when customer_id doesn't exist."""
        response = client.post(
            "/invoices/",
            json={
                "customer_id": 99999,
                "amount": 1000.00,
                "currency": "USD"
            }
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_create_invoice_negative_amount(self, client, sample_customer):
        """Test POST /invoices/ returns 422 when amount is negative."""
        response = client.post(
            "/invoices/",
            json={
                "customer_id": sample_customer.id,
                "amount": -100.00,
                "currency": "USD"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_invoice_invalid_currency(self, client, sample_customer):
        """Test POST /invoices/ returns 422 when currency code is invalid."""
        response = client.post(
            "/invoices/",
            json={
                "customer_id": sample_customer.id,
                "amount": 1000.00,
                "currency": "INVALID"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_list_invoices(self, client, sample_invoice):
        """Test GET /invoices/ returns 200 and list of all non-deleted invoices."""
        response = client.get("/invoices/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_list_invoices_by_customer(self, client, sample_invoice, sample_customer):
        """Test GET /invoices/ filters results by customer_id query parameter."""
        response = client.get(f"/invoices/?customer_id={sample_customer.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(inv["customer_id"] == sample_customer.id for inv in data)
    
    def test_list_invoices_pagination(self, client, db_session, sample_customer):
        """Test GET /invoices/ respects skip and limit pagination parameters."""
        from app.models import Invoice
        
        # Create multiple invoices
        for i in range(15):
            invoice = Invoice(
                customer_id=sample_customer.id,
                amount=100.00 * (i + 1),
                currency="USD",
                default_currency="USD",
                amount_in_default_currency=100.00 * (i + 1),
                exchange_rate=1.0
            )
            db_session.add(invoice)
        db_session.commit()
        
        # Test pagination
        response = client.get("/invoices/?skip=0&limit=10")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 10
        
        response = client.get("/invoices/?skip=10&limit=10")
        assert len(response.json()) == 5
    
    def test_get_invoice(self, client, sample_invoice):
        """Test GET /invoices/{id} returns 200 and invoice details."""
        response = client.get(f"/invoices/{sample_invoice.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_invoice.id
        assert data["amount"] == sample_invoice.amount
    
    def test_get_nonexistent_invoice(self, client):
        """Test GET /invoices/{id} returns 404 when invoice ID doesn't exist."""
        response = client.get("/invoices/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @patch('app.services.exchange_rate.ExchangeRateService.get_exchange_rate')
    def test_update_invoice(self, mock_exchange_rate, client, sample_invoice):
        """Test PUT /invoices/{id} returns 200 and updates amount and currency."""
        mock_exchange_rate.return_value = 1.2
        
        response = client.put(
            f"/invoices/{sample_invoice.id}",
            json={
                "amount": 1500.00,
                "currency": "EUR"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["amount"] == 1500.00
        assert data["currency"] == "EUR"
    
    def test_update_nonexistent_invoice(self, client):
        """Test PUT /invoices/{id} returns 404 when invoice ID doesn't exist."""
        response = client.put(
            "/invoices/99999",
            json={"amount": 1000.00}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_invoice(self, client, sample_invoice):
        """Test DELETE /invoices/{id} returns 204 and soft deletes invoice."""
        response = client.delete(f"/invoices/{sample_invoice.id}")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify soft-deleted invoice no longer appears in listing
        response = client.get("/invoices/")
        invoices = response.json()
        invoice_ids = [inv["id"] for inv in invoices]
        assert sample_invoice.id not in invoice_ids
    
    def test_delete_invoice_twice(self, client, sample_invoice):
        """Test DELETE /invoices/{id} returns 400 when attempting to delete already deleted invoice."""
        # First delete
        response = client.delete(f"/invoices/{sample_invoice.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Second delete should fail
        response = client.delete(f"/invoices/{sample_invoice.id}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST



