import pytest
from datetime import datetime, timedelta
from backend.core.inputs.health.providers import (
    apple_health, google_fit, myfitnesspal_adapter,
    oura_adapter, whoop_client
)
from backend.core.inputs.health.sync_service import HealthDataSyncService

@pytest.fixture
def date_range():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    return start_date, end_date

@pytest.fixture
def test_user_id():
    return 1  # Use a test user ID

@pytest.fixture
async def sync_service():
    service = HealthDataSyncService()
    await service.init_db()
    yield service
    await service.close_db()

@pytest.mark.asyncio
async def test_sync_all_providers(sync_service, date_range, test_user_id):
    """Test syncing data from all providers"""
    start_date, end_date = date_range
    results = await sync_service.sync_all_data(test_user_id, start_date, end_date)
    
    # Check that at least one provider succeeded
    assert any(results.values()), "No providers successfully synced"
    
    # Print individual provider results
    for provider, success in results.items():
        print(f"{provider}: {'Success' if success else 'Failed'}")

@pytest.mark.asyncio
async def test_sync_sleep_data(sync_service, date_range, test_user_id):
    """Test syncing sleep data specifically"""
    start_date, end_date = date_range
    
    for provider_name, provider in sync_service.providers.items():
        success = await sync_service._sync_sleep_data(test_user_id, provider, start_date, end_date)
        print(f"Sleep data sync for {provider_name}: {'Success' if success else 'Failed'}")

@pytest.mark.asyncio
async def test_sync_exercise_data(sync_service, date_range, test_user_id):
    """Test syncing exercise data specifically"""
    start_date, end_date = date_range
    
    for provider_name, provider in sync_service.providers.items():
        success = await sync_service._sync_exercise_data(test_user_id, provider, start_date, end_date)
        print(f"Exercise data sync for {provider_name}: {'Success' if success else 'Failed'}")

@pytest.mark.asyncio
async def test_sync_biometric_data(sync_service, date_range, test_user_id):
    """Test syncing biometric data specifically"""
    start_date, end_date = date_range
    
    for provider_name, provider in sync_service.providers.items():
        success = await sync_service._sync_biometric_data(test_user_id, provider, start_date, end_date)
        print(f"Biometric data sync for {provider_name}: {'Success' if success else 'Failed'}")

@pytest.mark.asyncio
async def test_sync_nutrition_data(sync_service, date_range, test_user_id):
    """Test syncing nutrition data specifically"""
    start_date, end_date = date_range
    
    for provider_name, provider in sync_service.providers.items():
        if hasattr(provider, 'get_nutrition_data'):
            success = await sync_service._sync_nutrition_data(test_user_id, provider, start_date, end_date)
            print(f"Nutrition data sync for {provider_name}: {'Success' if success else 'Failed'}")

@pytest.mark.asyncio
async def test_sync_mood_data(sync_service, date_range, test_user_id):
    """Test syncing mood data specifically"""
    start_date, end_date = date_range
    
    for provider_name, provider in sync_service.providers.items():
        success = await sync_service._sync_mood_data(test_user_id, provider, start_date, end_date)
        print(f"Mood data sync for {provider_name}: {'Success' if success else 'Failed'}")

@pytest.mark.asyncio
async def test_error_handling(sync_service, date_range, test_user_id):
    """Test error handling during sync"""
    start_date, end_date = date_range
    
    # Test with invalid dates
    invalid_start = datetime.now() + timedelta(days=1)
    results = await sync_service.sync_all_data(test_user_id, invalid_start, end_date)
    assert not all(results.values()), "Expected some failures with invalid dates"
    
    # Test with invalid user
    invalid_user_results = await sync_service.sync_all_data(-1, start_date, end_date)
    assert not all(invalid_user_results.values()), "Expected failures with invalid user"
