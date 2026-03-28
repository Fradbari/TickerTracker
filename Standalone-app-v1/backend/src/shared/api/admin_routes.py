from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel

from src.infra.feature_flags.service import FeatureFlag, FeatureFlagServiceDep
from src.shared.infra.config import settings

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


@router.get("/feature-flags", dependencies=[Depends(verify_admin_token)])
async def list_feature_flags(
    feature_flag_svc: FeatureFlagServiceDep
) -> dict[str, Any]:
    """List all feature flags and their current state."""
    flags = await feature_flag_svc.get_all_flags()
    return {"flags": flags}


@router.post("/feature-flags/{flag_name}", dependencies=[Depends(verify_admin_token)])
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

