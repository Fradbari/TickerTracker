import pytest
from src.infra.feature_flags.service import FeatureFlagService, FeatureFlag

@pytest.fixture
async def redis_client():
    from fakeredis import aioredis
    client = aioredis.FakeRedis(decode_responses=True)
    yield client
    await client.close()

@pytest.fixture
def ff_service(redis_client) -> FeatureFlagService:
    return FeatureFlagService(redis_client)

@pytest.mark.asyncio
async def test_whitelist_override_global_off(ff_service: FeatureFlagService):
    # Global off, percentage 0, but user in whitelist
    await ff_service.override_flag(
        FeatureFlag.NEW_DASHBOARD_UI, 
        enabled=False, 
        percentage=0, 
        whitelist=["user1", "user2"]
    )
    
    flag_states = await ff_service.get_all_flags()
    assert flag_states[FeatureFlag.NEW_DASHBOARD_UI.value]["enabled"] is False

    # user1 should be enabled
    assert await ff_service.is_enabled(FeatureFlag.NEW_DASHBOARD_UI, "user1") is True
    # user3 is not in whitelist, so disabled
    assert await ff_service.is_enabled(FeatureFlag.NEW_DASHBOARD_UI, "user3") is False

@pytest.mark.asyncio
async def test_percentage_rollout_deterministic(ff_service: FeatureFlagService):
    # Enable percentage rollout at 50%
    await ff_service.override_flag(
        FeatureFlag.AI_RECOMMENDATIONS,
        enabled=False,
        percentage=50,
        whitelist=[]
    )
    
    user_results = {}
    for i in range(100):
        uid = f"user_{i}"
        user_results[uid] = await ff_service.is_enabled(FeatureFlag.AI_RECOMMENDATIONS, uid)
        
    # Check deterministic behavior
    for uid, result in user_results.items():
        assert await ff_service.is_enabled(FeatureFlag.AI_RECOMMENDATIONS, uid) == result

    enabled_count = sum(user_results.values())
    # Given enough users, the count should be around 50. 
    # MD5 hash behavior should give us something roughly in [30, 70] for 100 users.
    assert 20 <= enabled_count <= 80

@pytest.mark.asyncio
async def test_disable_clears_settings(ff_service: FeatureFlagService):
    await ff_service.override_flag(
        FeatureFlag.DRIVE_SYNC_V2,
        enabled=True,
        percentage=100,
        whitelist=["test_user"]
    )
    assert await ff_service.is_enabled(FeatureFlag.DRIVE_SYNC_V2, "test_user") is True
    
    # Run disable
    await ff_service.disable(FeatureFlag.DRIVE_SYNC_V2)
    
    # Ensure it's off and cleared
    flags = await ff_service.get_all_flags()
    state = flags[FeatureFlag.DRIVE_SYNC_V2.value]
    
    assert state["enabled"] is False
    assert state["percentage"] == 0
    assert state["whitelist"] == []
    
    assert await ff_service.is_enabled(FeatureFlag.DRIVE_SYNC_V2, "test_user") is False
