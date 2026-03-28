"""
Feature Flag Service
Manages application feature flags with deterministic percentage rollouts and whitelist overrides using Redis.
"""
import hashlib
from enum import Enum
from typing import Annotated, Optional

import redis.asyncio as aioredis  # type: ignore[import]
from fastapi import Depends

from src.infra.cache.redis import get_redis


class FeatureFlag(str, Enum):
    """
    Available feature flags. Values are used as parts of Redis keys.
    Inheriting from str makes it automatically JSON serializable.
    """
    NEW_DASHBOARD_UI = "new_dashboard_ui"
    AI_RECOMMENDATIONS = "ai_recommendations"
    DRIVE_SYNC_V2 = "drive_sync_v2"


class FeatureFlagService:
    """
    Service for checking and managing feature flags stored in Redis.
    Hash map per flag:
      enabled: "true" | "false"
      percentage: "0"-"100"
      whitelist: "comma,separated,strings"
    """

    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self._prefix = "feature_flag"

    def _key(self, flag: FeatureFlag) -> str:
        return f"{self._prefix}:{flag.value}"

    async def is_enabled(self, flag: FeatureFlag, user_id: str | None = None) -> bool:
        """
        Check if a feature is enabled for a given user.
        Logic order:
          1. Whitelist (if user_id in whitelist -> True)
          2. Global enabled check
          3. Percentage rollout check (deterministic based on user_id)
        """
        key = self._key(flag)
        data = await self.redis.hgetall(key)
        
        if not data:
            return False

        # 1. Whitelist
        if user_id:
            whitelist_str = data.get("whitelist", "")
            if whitelist_str:
                whitelist = [u.strip() for u in whitelist_str.split(",") if u.strip()]
                if user_id in whitelist:
                    return True

        # 2. Global enabled check
        if data.get("enabled") == "true":
            return True

        # 3. Percentage Rollout
        if user_id:
            try:
                percentage = int(data.get("percentage", 0))
            except ValueError:
                percentage = 0
                
            if percentage > 0:
                # Deterministic check for this (flag, user)
                hash_val = hashlib.md5(f"{flag.value}:{user_id}".encode()).hexdigest()
                score = int(hash_val, 16) % 100
                if score < percentage:
                    return True

        return False

    async def enable(self, flag: FeatureFlag, percentage: int = 0, whitelist: Optional[list[str]] = None) -> None:
        """
        Enable a feature flag. If percentage is 0 and no whitelist, only globally enabled.
        If percentage > 0 or whitelist exists, it can be globally disabled but partially rolled out.
        """
        key = self._key(flag)
        
        # If we specify partial rollout or whitelist without wanting to globally enable,
        # we can structure the API so that "enabled" is strictly global on/off.
        # But `enable` usually implies setting `enabled="true"` unless there's partial intent.
        
        mapping = {}
        # If it's a 100% rollout, just enable it globally
        if percentage >= 100:
            mapping["enabled"] = "true"
            mapping["percentage"] = "100"
        elif percentage > 0 or whitelist:
            mapping["enabled"] = "false" # partial rollout vs global
            mapping["percentage"] = str(percentage)
        else:
            mapping["enabled"] = "true"
            mapping["percentage"] = "0"
            
        if whitelist is not None:
            mapping["whitelist"] = ",".join(whitelist)
            
        await self.redis.hset(key, mapping=mapping)

    async def override_flag(self, flag: FeatureFlag, enabled: bool, percentage: int, whitelist: list[str]) -> None:
        """
        Explicitly set all parameters of a feature flag.
        """
        key = self._key(flag)
        mapping = {
            "enabled": "true" if enabled else "false",
            "percentage": str(max(0, min(100, percentage))),
            "whitelist": ",".join(whitelist) if whitelist else ""
        }
        await self.redis.hset(key, mapping=mapping)

    async def disable(self, flag: FeatureFlag) -> None:
        """
        Disable a feature flag completely, clearing partial rollouts and whitelist.
        """
        key = self._key(flag)
        mapping = {
            "enabled": "false",
            "percentage": "0",
            "whitelist": ""
        }
        await self.redis.hset(key, mapping=mapping)

    async def get_all_flags(self) -> dict[str, dict[str, str | int | list[str]]]:
        """
        Return the current state of all known feature flags.
        """
        result = {}
        for f in FeatureFlag:
            data = await self.redis.hgetall(self._key(f))
            
            w_str = data.get("whitelist", "")
            whitelist = [u.strip() for u in w_str.split(",") if u.strip()] if w_str else []
            
            try:
                percentage = int(data.get("percentage", 0))
            except ValueError:
                percentage = 0
                
            result[f.value] = {
                "enabled": data.get("enabled") == "true",
                "percentage": percentage,
                "whitelist": whitelist
            }
        return result


# Dependency to inject into FastAPI routes
async def get_feature_flag_service(
    redis: Annotated[aioredis.Redis, Depends(get_redis)]
) -> FeatureFlagService:
    return FeatureFlagService(redis)


FeatureFlagServiceDep = Annotated[FeatureFlagService, Depends(get_feature_flag_service)]
