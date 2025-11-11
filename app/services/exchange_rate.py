import httpx
from fastapi import HTTPException, status

from app.config import settings


class ExchangeRateService:
    """Service for fetching and managing exchange rates."""
    
    def __init__(self):
        self.api_url = settings.exchange_rate_api_url
        self.api_key = settings.exchange_rate_api_key
        self.default_currency = settings.default_currency
    
    async def validate_currency(self, currency_code: str) -> bool:
        """
        Validate if a currency code is supported by the exchange rate API.
        
        Args:
            currency_code: The currency code to validate (e.g., 'USD', 'EUR')
        
        Returns:
            bool: True if currency is valid
        
        Raises:
            HTTPException: If currency is invalid or API error occurs
        """
        currency_code = currency_code.upper()
        
        # Build API URL to get supported codes
        url = f"{self.api_url}/{self.api_key}/codes"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("result") == "success":
                        supported_codes = data.get("supported_codes", [])
                        # supported_codes is a list of [code, name] pairs
                        valid_currencies = [code[0] for code in supported_codes]
                        
                        if currency_code not in valid_currencies:
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Invalid currency code: {currency_code}. Currency is not supported."
                            )
                        return True
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"API error: {data.get('error-type', 'Unknown error')}"
                        )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Exchange rate API unavailable"
                    )
                    
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Exchange rate API timeout"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to connect to exchange rate API: {str(e)}"
            )
    
    async def get_exchange_rate(
        self, 
        from_currency: str, 
        to_currency: str | None = None
    ) -> float:
        """
        Get exchange rate from given currency to target currency.
        
        Args:
            from_currency: The currency to convert from (e.g., 'EUR', 'GBP')
            to_currency: The currency to convert to (defaults to default_currency)
        
        Returns:
            float: The exchange rate
        """
        # If no target currency specified, use default
        if to_currency is None:
            to_currency = self.default_currency
        
        # If currencies are the same, return 1
        if from_currency.upper() == to_currency.upper():
            return 1.0
        
        # Validate both currencies before making the exchange rate request
        await self.validate_currency(from_currency)
        await self.validate_currency(to_currency)
        
        # Build API URL
        url = f"{self.api_url}/{self.api_key}/pair/{from_currency.upper()}/{to_currency.upper()}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("result") == "success":
                        return data.get("conversion_rate")
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid currency code or API error: {data.get('error-type', 'Unknown error')}"
                        )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid currency code or API error"
                    )
                    
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Exchange rate API timeout"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to connect to exchange rate API: {str(e)}"
            )
    
    async def get_rate_to_default(self, from_currency: str) -> float:
        return await self.get_exchange_rate(from_currency, self.default_currency)


# Singleton instance
exchange_rate_service = ExchangeRateService()


async def get_exchange_rate_to_default(currency: str) -> float:
    return await exchange_rate_service.get_rate_to_default(currency)

