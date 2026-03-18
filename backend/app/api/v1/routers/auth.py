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
from app.db.models import User, Tenant, Subscription, Plan, TenantUser
from app.db.models.tenant_user import AVAILABLE_PERMISSIONS
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

    # Criar vínculo workspace (multi-workspace)
    tenant_user = TenantUser(
        tenant_id=tenant.id,
        user_id=user.id,
        role="owner",
        is_default=True,
    )
    db.add(tenant_user)
    
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
    
    # Criar token (com tenant_id para multi-workspace)
    access_token = create_access_token(data={"sub": user.id, "tid": tenant.id})
    
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
        },
        "workspaces": [
            {"id": tenant.id, "name": tenant.name, "role": "owner", "is_default": True, "permissions": list(AVAILABLE_PERMISSIONS)}
        ]
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

    # Buscar workspaces do usuário
    memberships = (
        db.query(TenantUser)
        .filter(TenantUser.user_id == user.id)
        .all()
    )

    # Se o usuário não tem registros em tenant_users (dados pré-migração),
    # usa o tenant_id original como fallback
    if not memberships:
        active_tenant_id = user.tenant_id
        workspaces_list = []
    else:
        # Pegar o workspace default, ou o primeiro
        default_ws = next((m for m in memberships if m.is_default), memberships[0])
        active_tenant_id = default_ws.tenant_id
        workspaces_list = memberships

    # Buscar tenant ativo
    tenant = db.query(Tenant).filter(Tenant.id == active_tenant_id).first()
    
    if not tenant or not tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta inativa"
        )
    
    # Atualizar último login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Criar token (com tenant_id para multi-workspace)
    access_token = create_access_token(data={"sub": user.id, "tid": tenant.id})

    # Montar lista de workspaces para o frontend
    ws_data = []
    if workspaces_list:
        tenant_ids = [m.tenant_id for m in workspaces_list]
        tenants = db.query(Tenant).filter(Tenant.id.in_(tenant_ids), Tenant.is_active == True).all()
        tenant_map = {t.id: t for t in tenants}
        # Buscar subscriptions para incluir plano
        subs = db.query(Subscription).filter(
            Subscription.tenant_id.in_(tenant_ids)
        ).order_by(Subscription.id.desc()).all()
        sub_map = {}
        for s in subs:
            if s.tenant_id not in sub_map:
                sub_map[s.tenant_id] = s
        for m in workspaces_list:
            t = tenant_map.get(m.tenant_id)
            if t:
                sub = sub_map.get(t.id)
                ws_data.append({
                    "id": t.id,
                    "name": t.name,
                    "role": m.role,
                    "is_default": m.is_default,
                    "plan_name": sub.plan.display_name if sub and sub.plan else None,
                    "permissions": m.get_permissions(),
                })
    else:
        ws_data.append({
            "id": tenant.id,
            "name": tenant.name,
            "role": "owner",
            "is_default": True,
            "plan_name": None,
            "permissions": list(AVAILABLE_PERMISSIONS),
        })
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_admin": user.is_admin,
            "is_super_admin": bool(getattr(user, "is_super_admin", False)),
            "tenant_id": active_tenant_id
        },
        "tenant": {
            "id": tenant.id,
            "name": tenant.name,
            "email": tenant.email
        },
        "workspaces": ws_data
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

    # Buscar workspaces do usuário
    memberships = db.query(TenantUser).filter(TenantUser.user_id == user.id).all()
    ws_data = []
    if memberships:
        tenant_ids = [m.tenant_id for m in memberships]
        tenants = db.query(Tenant).filter(Tenant.id.in_(tenant_ids), Tenant.is_active == True).all()
        tenant_map = {t.id: t for t in tenants}
        # Buscar subscriptions para incluir plano
        subs = db.query(Subscription).filter(
            Subscription.tenant_id.in_(tenant_ids)
        ).order_by(Subscription.id.desc()).all()
        sub_map = {}
        for s in subs:
            if s.tenant_id not in sub_map:
                sub_map[s.tenant_id] = s
        for m in memberships:
            t = tenant_map.get(m.tenant_id)
            if t:
                sub = sub_map.get(t.id)
                ws_data.append({
                    "id": t.id,
                    "name": t.name,
                    "role": m.role,
                    "is_default": m.is_default,
                    "plan_name": sub.plan.display_name if sub and sub.plan else None,
                    "permissions": m.get_permissions(),
                })
    else:
        ws_data.append({
            "id": tenant.id,
            "name": tenant.name,
            "role": "owner",
            "is_default": True,
            "plan_name": None,
            "permissions": list(AVAILABLE_PERMISSIONS),
        })
    
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_admin": user.is_admin,
            "is_super_admin": bool(getattr(user, "is_super_admin", False)),
            "tenant_id": getattr(user, "_active_tenant_id", user.tenant_id)
        },
        "tenant": {
            "id": tenant.id,
            "name": tenant.name,
            "email": tenant.email
        },
        "workspaces": ws_data,
        "subscription": {
            "id": subscription.id if subscription else None,
            "plan_name": subscription.plan.display_name if subscription else None,
            "status": subscription.status if subscription else None,
            "trial_ends_at": subscription.trial_ends_at.strftime("%Y-%m-%d %H:%M:%S") if subscription and subscription.trial_ends_at else None,
            "current_period_end": subscription.current_period_end.strftime("%Y-%m-%d %H:%M:%S") if subscription and subscription.current_period_end else None
        } if subscription else None
    }
