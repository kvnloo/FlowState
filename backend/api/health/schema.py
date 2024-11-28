from typing import List, Optional
import strawberry
from datetime import datetime
from .types import (
    User, SleepMetrics, NutritionMetrics, ExerciseMetrics,
    BiometricMetrics, MoodMetrics
)
from backend.core.inputs.health.providers import (
    apple_health, google_fit, myfitnesspal_adapter,
    oura_adapter, whoop_client
)
from .repository import HealthRepository

@strawberry.type
class Query:
    @strawberry.field
    async def user(self, id: int) -> Optional[User]:
        repo = HealthRepository()
        await repo.init_pool()
        user_data = await repo.get_user(id)
        await repo.close()
        return User(**user_data) if user_data else None

    @strawberry.field
    async def sleep_metrics(
        self, user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[SleepMetrics]:
        repo = HealthRepository()
        await repo.init_pool()
        metrics = await repo.get_sleep_metrics(user_id, start_date, end_date)
        await repo.close()
        return [SleepMetrics(**m) for m in metrics]

    @strawberry.field
    async def nutrition_metrics(
        self, user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[NutritionMetrics]:
        repo = HealthRepository()
        await repo.init_pool()
        metrics = await repo.get_nutrition_metrics(user_id, start_date, end_date)
        await repo.close()
        return [NutritionMetrics(**m) for m in metrics]

    @strawberry.field
    async def exercise_metrics(
        self, user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[ExerciseMetrics]:
        repo = HealthRepository()
        await repo.init_pool()
        metrics = await repo.get_exercise_metrics(user_id, start_date, end_date)
        await repo.close()
        return [ExerciseMetrics(**m) for m in metrics]

    @strawberry.field
    async def biometric_metrics(
        self, user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[BiometricMetrics]:
        repo = HealthRepository()
        await repo.init_pool()
        metrics = await repo.get_biometric_metrics(user_id, start_date, end_date)
        await repo.close()
        return [BiometricMetrics(**m) for m in metrics]

    @strawberry.field
    async def mood_metrics(
        self, user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[MoodMetrics]:
        repo = HealthRepository()
        await repo.init_pool()
        metrics = await repo.get_mood_metrics(user_id, start_date, end_date)
        await repo.close()
        return [MoodMetrics(**m) for m in metrics]

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def sync_health_data(
        self,
        user_id: int,
        providers: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> bool:
        """Sync health data from specified providers for the given date range."""
        provider_map = {
            'apple_health': apple_health.AppleHealthProvider,
            'google_fit': google_fit.GoogleFitProvider,
            'myfitnesspal': myfitnesspal_adapter.MyFitnessPalProvider,
            'oura': oura_adapter.OuraProvider,
            'whoop': whoop_client.WhoopProvider
        }
        
        repo = HealthRepository()
        await repo.init_pool()
        
        try:
            for provider_name in providers:
                if provider_name in provider_map:
                    provider = provider_map[provider_name]()
                    data = await provider.sync_data(user_id, start_date, end_date)
                    
                    # Save the data based on provider type
                    if isinstance(provider, apple_health.AppleHealthProvider):
                        await repo.save_sleep_metrics(data.get('sleep', {}))
                        await repo.save_exercise_metrics(data.get('exercise', {}))
                        await repo.save_biometric_metrics(data.get('biometrics', {}))
                    # Add similar handling for other providers...
            
            return True
        finally:
            await repo.close()

    @strawberry.mutation
    async def create_user(self, username: str, email: str) -> User:
        repo = HealthRepository()
        await repo.init_pool()
        user_data = await repo.create_user(username, email)
        await repo.close()
        return User(**user_data)

schema = strawberry.Schema(query=Query, mutation=Mutation)
