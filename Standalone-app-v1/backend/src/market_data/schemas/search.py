from pydantic import BaseModel

class FinnhubSymbolResult(BaseModel):
    symbol: str
    description: str
    type: str
    mic_code: str | None = None

class SymbolValidationResult(BaseModel):
    valid: bool
    current_price: float | None = None
    currency: str | None = None
    exchange: str | None = None
    symbol: str

class SymbolSearchResult(FinnhubSymbolResult):
    current_price: float | None = None