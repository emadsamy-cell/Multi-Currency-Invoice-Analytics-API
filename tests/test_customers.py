"""Unit tests for customer endpoints."""
import pytest
from fastapi import status


class TestCustomerEndpoints:
    def test_create_customer(self, client):
        """Test POST /customers/ returns 201 and creates customer with valid data."""
        response = client.post("/customers/", json={"name": "Test Customer"})
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Test Customer"
        assert "id" in data
    
    def test_create_customer_invalid(self, client):
        """Test POST /customers/ returns 422 when name is empty string."""
        response = client.post("/customers/", json={"name": ""})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_list_customers(self, client, sample_customer):
        """Test GET /customers/ returns 200 and list of all non-deleted customers."""
        response = client.get("/customers/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_update_customer(self, client, sample_customer):
        """Test PUT /customers/{id} returns 200 and updates customer name."""
        response = client.put(
            f"/customers/{sample_customer.id}",
            json={"name": "Updated Name"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Name"
    
    def test_update_nonexistent_customer(self, client):
        """Test PUT /customers/{id} returns 404 when customer ID doesn't exist."""
        response = client.put("/customers/99999", json={"name": "Updated"})
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_customer(self, client, sample_customer):
        """Test DELETE /customers/{id} returns 204 and soft deletes customer."""
        response = client.delete(f"/customers/{sample_customer.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify soft-deleted customer no longer appears in listing
        response = client.get("/customers/")
        customer_ids = [c["id"] for c in response.json()]
        assert sample_customer.id not in customer_ids
    
    def test_delete_nonexistent_customer(self, client):
        """Test DELETE /customers/{id} returns 404 when customer ID doesn't exist."""
        response = client.delete("/customers/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
