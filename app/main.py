from fastapi import FastAPI
from .services.weather_service import WeatherService
from .utils.middleware import auth_backend
from .services.prediction_service import PredictionService
from fastapi_users import FastAPIUsers
from .manager.usermanager import get_user_manager
from .routers import app_routes
from .schemas.users import UserCreate, UserRead, UserUpdate
from .models.database import User
from .utils.database import init_db

app = FastAPI(title="Network Outage Forecaster")
weather_service = WeatherService()
prediction_service = PredictionService()


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(app_routes)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/auth_users",
    tags=["users"],
)


@app.on_event("startup")
async def startup_event():
    init_db()
