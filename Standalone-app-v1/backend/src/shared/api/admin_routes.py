from typing import Annotated, Any
import json
import httpx
from sqlalchemy import select
from sqlalchemy.future import select
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel

from src.infra.feature_flags.service import FeatureFlag, FeatureFlagServiceDep
from src.shared.infra.config import settings
from src.shared.infra.database import get_db, AsyncSessionLocal
from src.shared.domain.app_config import AppConfig

router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
)

def verify_admin_token(x_admin_token: Annotated[str, Header()]) -> None:
    """Dependency to verify the admin token for protected routes."""
    if x_admin_token != settings.ADMIN_TOKEN.get_secret_value():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid administrative token",
        )

# Require admin token for all routes in this router
AdminAuthDep = Annotated[None, Depends(verify_admin_token)]

class FeatureFlagUpdateRequest(BaseModel):
    enabled: bool
    percentage: int
    whitelist: list[str]
    model_config = {
        "json_schema_extra": {
            "example": {
                "enabled": True,
                "percentage": 100,
                "whitelist": ["user_123", "user_456"]
            }
        }
    }


@router.get(
    "/feature-flags",
    dependencies=[Depends(verify_admin_token)],
    summary="List all feature flags",
    description="Returns all active feature flags and their current state (percentage, whitelist, etc.).",
    response_description="A dictionary of feature flags",
    responses={
        200: {
            "description": "Success",
            "content": {"application/json": {"example": {"flags": {"FF_NEW_UI": {"enabled": True, "percentage": 50, "whitelist": []}}}}}
        },
        401: {
            "description": "Unauthorized - Missing or invalid admin token",
            "content": {"application/json": {"example": {"detail": "Invalid administrative token"}}}
        }
    }
)
async def list_feature_flags(
    feature_flag_svc: FeatureFlagServiceDep
) -> dict[str, Any]:
    """List all feature flags and their current state."""
    flags = await feature_flag_svc.get_all_flags()
    return {"flags": flags}


@router.post(
    "/feature-flags/{flag_name}",
    dependencies=[Depends(verify_admin_token)],
    summary="Update a feature flag",
    description="Updates a specific feature flag (e.g., changes its percentage or adds users to a whitelist). Needs valid admin token.",
    response_description="The updated feature flag mapping",
    responses={
        200: {
            "description": "Successfully updated",
            "content": {"application/json": {"example": {"status": "success", "flag": {"enabled": True, "percentage": 100, "whitelist": ["user_abc"]}}}}
        },
        401: {
            "description": "Unauthorized - Missing or invalid admin token",
            "content": {"application/json": {"example": {"detail": "Invalid administrative token"}}}
        },
        422: {
            "description": "Validation Error - Invalid flag name or body",
            "content": {"application/json": {"example": {"detail": [{"msg": "Input should be a valid boolean"}]}}}
        }
    }
)
async def update_feature_flag(
    flag_name: FeatureFlag,
    request: FeatureFlagUpdateRequest,
    feature_flag_svc: FeatureFlagServiceDep
) -> dict[str, Any]:
    """Create or update a feature flag's settings."""
    await feature_flag_svc.override_flag(
        flag=flag_name,
        enabled=request.enabled,
        percentage=request.percentage,
        whitelist=request.whitelist
    )
    # Return the updated state
    flags = await feature_flag_svc.get_all_flags()
    return {"status": "success", "flag": flags.get(flag_name.value)}


class FinnhubKeyRequest(BaseModel):
    api_key: str

@router.get("/config/finnhub-key", dependencies=[Depends(verify_admin_token)], summary="Ottieni info chiave Finnhub")
async def get_finnhub_key(db = Depends(get_db)):
    result = await db.execute(select(AppConfig).where(AppConfig.key == "FINNHUB_API_KEY"))
    config = result.scalar_one_or_none()
    if config:
        try:
            data = json.loads(config.value)
            return {"valid": True, "updated_at": config.updated_at, "quota_remaining": data.get("quota_remaining")}
        except:
            return {"valid": True, "updated_at": config.updated_at, "quota_remaining": None}
    return {"valid": False, "updated_at": None, "quota_remaining": None}

@router.post("/config/finnhub-key", dependencies=[Depends(verify_admin_token)], summary="Verifica e Salva chiave API Finnhub")
async def save_finnhub_key(request: FinnhubKeyRequest, db = Depends(get_db)):
    url = f"https://finnhub.io/api/v1/search?q=AAPL&token={request.api_key}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Chiave API Finnhub non valida o quota esaurita")
        
        quota = response.headers.get("X-Ratelimit-Limit", "Unknown")
        val = json.dumps({"api_key": request.api_key, "quota_remaining": quota})
        
        result = await db.execute(select(AppConfig).where(AppConfig.key == "FINNHUB_API_KEY"))
        config = result.scalar_one_or_none()
        
        if config:
            config.value = val
        else:
            config = AppConfig(key="FINNHUB_API_KEY", value=val)
            db.add(config)
            
        await db.commit()
        return {"valid": True, "quota_remaining": quota}
