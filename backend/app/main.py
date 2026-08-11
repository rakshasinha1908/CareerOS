from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.api.routes.profile import router as profile_router
from app.api.routes.preferences import router as preferences_router
from app.api.routes.company import router as company_router


app = FastAPI(
    title="CareerOS API",
    version="0.1.0",
)

app.include_router(profile_router)
app.include_router(preferences_router)
app.include_router(company_router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "careeros-api",
    }


@app.get("/api/v1/me")
def get_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return {
        "id": str(current_user.id),
        "created_at": current_user.created_at.isoformat(),
    }