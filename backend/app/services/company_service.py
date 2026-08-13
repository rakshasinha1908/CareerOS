from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate


def _serialize_company_data(data) -> dict:
    values = data.model_dump(exclude_unset=True)

    if "career_url" in values and values["career_url"] is not None:
        values["career_url"] = str(values["career_url"])

    return values


def get_companies(
    db: Session,
) -> list[Company]:
    return list(
        db.scalars(
            select(Company).order_by(Company.name)
        ).all()
    )


def get_company(
    db: Session,
    company_id,
) -> Company | None:
    return db.scalar(
        select(Company).where(Company.id == company_id)
    )


def create_company(
    db: Session,
    data: CompanyCreate,
) -> Company:
    company = Company(
        **_serialize_company_data(data)
    )

    db.add(company)
    db.commit()
    db.refresh(company)

    return company


def update_company(
    db: Session,
    company: Company,
    data: CompanyUpdate,
) -> Company:
    updates = _serialize_company_data(data)

    for field, value in updates.items():
        setattr(company, field, value)

    db.commit()
    db.refresh(company)

    return company


def delete_company(
    db: Session,
    company: Company,
) -> None:
    db.delete(company)
    db.commit()