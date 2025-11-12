"""Unit tests for analytics endpoints."""
import pytest
from fastapi import status
from unittest.mock import patch


class TestAnalyticsEndpoints:
    @patch('app.services.exchange_rate.ExchangeRateService.get_exchange_rate')
    def test_total_revenue(self, mock_exchange_rate, client, multiple_invoices):
        """Test GET /analytics/total-revenue calculates sum of all invoices."""
        mock_exchange_rate.return_value = 1.0
        
        response = client.get("/analytics/total-revenue")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_revenue" in data
        assert "currency" in data
        assert "invoice_count" in data
        assert data["invoice_count"] == 3
    
    @patch('app.services.exchange_rate.ExchangeRateService.get_exchange_rate')
    def test_total_revenue_with_currency(self, mock_exchange_rate, client, multiple_invoices):
        """Test GET /analytics/total-revenue converts to target currency when specified."""
        mock_exchange_rate.return_value = 0.85
        
        response = client.get("/analytics/total-revenue?target_currency=EUR")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["currency"] == "EUR"
    
    @patch('app.services.exchange_rate.ExchangeRateService.get_exchange_rate')
    def test_total_revenue_by_customer(self, mock_exchange_rate, client, sample_customer, sample_invoice):
        """Test GET /analytics/total-revenue filters results by customer_id parameter."""
        mock_exchange_rate.return_value = 1.0
        
        response = client.get(f"/analytics/total-revenue?customer_id={sample_customer.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["customer_id"] == sample_customer.id
        assert data["invoice_count"] >= 1
    
    def test_total_revenue_no_invoices(self, client):
        """Test GET /analytics/total-revenue returns zero when no invoices exist."""
        response = client.get("/analytics/total-revenue")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_revenue"] == 0.0
        assert data["invoice_count"] == 0
    
    @patch('app.services.exchange_rate.ExchangeRateService.get_exchange_rate')
    def test_average_invoice(self, mock_exchange_rate, client, multiple_invoices):
        """Test GET /analytics/average-invoice calculates mean of all invoice amounts."""
        mock_exchange_rate.return_value = 1.0
        
        response = client.get("/analytics/average-invoice")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "average_invoice_size" in data
        assert "currency" in data
        assert "invoice_count" in data
        assert data["invoice_count"] == 3
    
    @patch('app.services.exchange_rate.ExchangeRateService.get_exchange_rate')
    def test_average_invoice_with_currency(self, mock_exchange_rate, client, multiple_invoices):
        """Test GET /analytics/average-invoice converts amounts to target currency before averaging."""
        mock_exchange_rate.return_value = 0.85
        
        response = client.get("/analytics/average-invoice?target_currency=EUR")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["currency"] == "EUR"
    
    def test_average_invoice_no_invoices(self, client):
        """Test GET /analytics/average-invoice returns zero when no invoices exist."""
        response = client.get("/analytics/average-invoice")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["average_invoice_size"] == 0.0
        assert data["invoice_count"] == 0
