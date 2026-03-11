"""
Router de autenticação
"""
import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.session import get_db
from app.db.models import User, Tenant, Subscription, Plan
from app.db.models.password_reset_token import PasswordResetToken
from app.core.auth import (
    create_access_token,
    verify_password,
    get_password_hash,
    get_current_user,
    get_current_tenant
)
from app.services.email_sender import (
    send_welcome_email_background,
    send_password_reset_email_background,
)

router = APIRouter()


# Schemas
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    company_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
    tenant: dict


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    is_admin: bool
    is_super_admin: bool | None = None
    tenant_id: int


class TenantOut(BaseModel):
    id: int
    name: str
    email: str


@router.post("/register", response_model=TokenResponse)
def register(
    data: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Registro de novo usuário e tenant
    Cria automaticamente uma assinatura trial
    """
    email = data.email.strip().lower()

    # Verificar se o email já existe (case-insensitive)
    existing_user = db.query(User).filter(func.lower(User.email) == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail já cadastrado"
        )
    
    # Verificar se o email do tenant já existe
    existing_tenant = db.query(Tenant).filter(func.lower(Tenant.email) == email).first()
    if existing_tenant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empresa já cadastrada com este email"
        )
    
    # Criar tenant
    tenant = Tenant(
        name=data.company_name,
        email=email,
        is_active=True
    )
    db.add(tenant)
    db.flush()  # Para pegar o ID
    
    # Criar usuário
    try:
        password_hash = get_password_hash(data.password)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha inválida. Use uma senha menor ou sem caracteres especiais muito longos.",
        )

    user = User(
        tenant_id=tenant.id,
        email=email,
        password_hash=password_hash,
        full_name=data.full_name,
        is_active=True,
        is_admin=True  # Primeiro usuário é admin
    )
    db.add(user)
    db.flush()
    
    # Criar assinatura trial (14 dias)
    free_plan = db.query(Plan).filter(Plan.name == "free").first()
    if not free_plan:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Plano gratuito não encontrado. Execute o script de seed."
        )
    
    subscription = Subscription(
        tenant_id=tenant.id,
        plan_id=free_plan.id,
        status="trial",
        started_at=datetime.utcnow(),
        trial_ends_at=datetime.utcnow() + timedelta(days=14),
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow() + timedelta(days=14)
    )
    db.add(subscription)
    
    db.commit()
    db.refresh(user)
    db.refresh(tenant)

    # Email de boas-vindas (não bloqueia o registro)
    background_tasks.add_task(
        send_welcome_email_background,
        to_email=user.email,
        full_name=user.full_name,
        company_name=tenant.name,
    )
    
    # Criar token
    access_token = create_access_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_admin": user.is_admin,
            "is_super_admin": bool(getattr(user, "is_super_admin", False)),
            "tenant_id": user.tenant_id
        },
        "tenant": {
            "id": tenant.id,
            "name": tenant.name,
            "email": tenant.email
        }
    }


# ─── Schemas para recuperação de senha ───────────────────────────────────────

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


# ─── Recuperação de senha ─────────────────────────────────────────────────────

@router.post("/forgot-password")
def forgot_password(
    data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Envia e-mail de recuperação de senha.
    Sempre retorna 200 para não expor se o e-mail está cadastrado.
    """
    email = data.email.strip().lower()
    user = db.query(User).filter(func.lower(User.email) == email).first()

    if user:
        # Invalida tokens anteriores não usados
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used == False,  # noqa: E712
        ).update({"used": True})

        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        prt = PasswordResetToken(user_id=user.id, token=token, expires_at=expires_at)
        db.add(prt)
        db.commit()

        settings = get_settings()
        reset_url = f"{settings.PUBLIC_BASE_URL}/#/reset-password?token={token}"
        background_tasks.add_task(
            send_password_reset_email_background,
            to_email=user.email,
            full_name=user.full_name,
            reset_url=reset_url,
        )

    return {"message": "Se o e-mail estiver cadastrado, você receberá as instruções em breve."}


@router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    """Redefine a senha usando o token enviado por e-mail."""
    if len(data.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A senha deve ter no mínimo 6 caracteres.",
        )

    prt = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == data.token,
        PasswordResetToken.used == False,  # noqa: E712
    ).first()

    if not prt or prt.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido ou expirado. Solicite um novo link.",
        )

    user = db.query(User).filter(User.id == prt.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    user.password_hash = get_password_hash(data.new_password)
    prt.used = True
    db.commit()

    return {"message": "Senha redefinida com sucesso."}


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Login de usuário existente"""
    # Buscar usuário
    email = data.email.strip().lower()
    user = db.query(User).filter(func.lower(User.email) == email).first()
    
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    
    # Buscar tenant
    tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
    
    if not tenant or not tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta inativa"
        )
    
    # Atualizar último login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Criar token
    access_token = create_access_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_admin": user.is_admin,
            "is_super_admin": bool(getattr(user, "is_super_admin", False)),
            "tenant_id": user.tenant_id
        },
        "tenant": {
            "id": tenant.id,
            "name": tenant.name,
            "email": tenant.email
        }
    }


@router.get("/me", response_model=dict)
def get_me(
    user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """Retorna informações do usuário logado"""
    # Buscar assinatura
    subscription = (
        db.query(Subscription)
        .join(Plan)
        .filter(Subscription.tenant_id == tenant.id)
        .order_by(Subscription.id.desc())
        .first()
    )
    
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_admin": user.is_admin,
            "is_super_admin": bool(getattr(user, "is_super_admin", False)),
            "tenant_id": user.tenant_id
        },
        "tenant": {
            "id": tenant.id,
            "name": tenant.name,
            "email": tenant.email
        },
        "subscription": {
            "id": subscription.id if subscription else None,
            "plan_name": subscription.plan.display_name if subscription else None,
            "status": subscription.status if subscription else None,
            "trial_ends_at": subscription.trial_ends_at.isoformat() if subscription and subscription.trial_ends_at else None,
            "current_period_end": subscription.current_period_end.isoformat() if subscription and subscription.current_period_end else None
        } if subscription else None
    }
