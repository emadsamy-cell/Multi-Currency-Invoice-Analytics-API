import httpx
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.config import settings
from app.models import ExchangeRateCache
from app.database import get_db


class ExchangeRateService:
    """Service for fetching and managing exchange rates with caching."""
    
    CACHE_DURATION_HOURS = 1  # Cache exchange rates for 1 hour
    
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
    
    def _get_cached_rate(self, from_currency: str, to_currency: str) -> float | None:
        """
        Args:
            from_currency: Source currency
            to_currency: Target currency
        
        Returns:
            float | None: Cached rate if found and fresh, None otherwise
        """
        db = next(get_db())
        try:
            from_currency = from_currency.upper()
            to_currency = to_currency.upper()
            
            # Calculate cutoff time (1 hour ago)
            cutoff_time = datetime.now() - timedelta(hours=self.CACHE_DURATION_HOURS)
            
            # Check direct rate (from -> to)
            cached = db.query(ExchangeRateCache).filter(
                ExchangeRateCache.from_currency == from_currency,
                ExchangeRateCache.to_currency == to_currency,
                ExchangeRateCache.created_at >= cutoff_time
            ).order_by(ExchangeRateCache.created_at.desc()).first()
            
            if cached:
                return cached.rate
            
            # Check inverse rate (to -> from) and invert it
            cached_inverse = db.query(ExchangeRateCache).filter(
                ExchangeRateCache.from_currency == to_currency,
                ExchangeRateCache.to_currency == from_currency,
                ExchangeRateCache.created_at >= cutoff_time
            ).order_by(ExchangeRateCache.created_at.desc()).first()
            
            if cached_inverse:
                return 1 / cached_inverse.rate
            
            return None
        finally:
            db.close()
    
    def _cache_rate(self, from_currency: str, to_currency: str, rate: float):
        """
        Store or update exchange rate in cache.
        Updates existing rate if found, otherwise creates new entry.
        
        Args:
            from_currency: Source currency
            to_currency: Target currency
            rate: Exchange rate to cache
        """
        db = next(get_db())
        try:
            from_currency = from_currency.upper()
            to_currency = to_currency.upper()
            
            # Check if rate already exists
            existing = db.query(ExchangeRateCache).filter(
                ExchangeRateCache.from_currency == from_currency,
                ExchangeRateCache.to_currency == to_currency
            ).first()
            
            if existing:
                # Update existing rate
                existing.rate = rate
                existing.created_at = datetime.now()
            else:
                # Create new cache entry
                cache_entry = ExchangeRateCache(
                    from_currency=from_currency,
                    to_currency=to_currency,
                    rate=rate
                )
                db.add(cache_entry)
            
            db.commit()
        finally:
            db.close()
    
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
        
        # Check cache first
        cached_rate = self._get_cached_rate(from_currency, to_currency)
        if cached_rate is not None:
            return cached_rate
        
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
                        rate = data.get("conversion_rate")
                        
                        # Cache the rate
                        self._cache_rate(from_currency, to_currency, rate)
                        
                        return rate
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


async def get_exchange_rate_to_default(currency: str) -> float:
    """
    Get exchange rate to default currency with caching support.
    
    Args:
        currency: Currency to convert from
    
    Returns:
        float: Exchange rate
    """
    service = ExchangeRateService()
    return await service.get_rate_to_default(currency)

