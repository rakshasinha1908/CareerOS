from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def get_or_create_single_user(db: Session) -> User:
    user = db.scalar(
        select(User)
        .order_by(User.created_at)
        .limit(1)
    )

    if user:
        return user

    user = User()
    db.add(user)
    db.commit()
    db.refresh(user)

    return user