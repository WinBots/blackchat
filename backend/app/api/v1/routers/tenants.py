from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.auth import get_current_tenant
from app.db.session import get_db
from app.db.models.tenant import Tenant

router = APIRouter()


class TenantOut(BaseModel):
    id: int
    name: str
    email: str | None = None
    timezone: str | None = None

    model_config = {"from_attributes": True}


class TenantCreate(BaseModel):
    name: str


class TenantMeUpdate(BaseModel):
    name: str | None = None
    timezone: str | None = None


@router.get("/", response_model=list[TenantOut])
def list_tenants(db: Session = Depends(get_db)):
    tenants = db.query(Tenant).all()
    return tenants


@router.post("/", response_model=TenantOut)
def create_tenant(data: TenantCreate, db: Session = Depends(get_db)):
    tenant = Tenant(name=data.name)
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


@router.get("/me", response_model=TenantOut)
def get_tenant_me(
    tenant: Tenant = Depends(get_current_tenant),
):
    return tenant


@router.put("/me", response_model=TenantOut)
def update_tenant_me(
    body: TenantMeUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    updated = False
    if body.name is not None:
        name = body.name.strip()
        if not name:
            raise HTTPException(status_code=400, detail="Nome inválido")
        tenant.name = name
        updated = True

    if body.timezone is not None:
        tz = body.timezone.strip()
        tenant.timezone = tz or None
        updated = True

    if updated:
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
    return tenant
