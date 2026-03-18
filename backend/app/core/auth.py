"""
Utilitários de autenticação e segurança
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import User, Tenant, Subscription, TenantUser
from app.config import get_settings

# Configuração de hash de senha
# bcrypt possui limite de 72 bytes; bcrypt_sha256 faz pre-hash e suporta senhas longas.
# Mantemos "bcrypt" para compatibilidade com hashes antigos.
pwd_context = CryptContext(
    schemes=["bcrypt_sha256", "bcrypt"],
    deprecated="auto",
)

# Security scheme para JWT
security = HTTPBearer()

# Configurações
settings = get_settings()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha está correta"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Gera hash da senha"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria um token JWT"""
    to_encode = data.copy()
    if "sub" in to_encode and to_encode["sub"] is not None:
        to_encode["sub"] = str(to_encode["sub"])
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60 * 24 * 7)  # 7 dias padrão
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decodifica um token JWT"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Dependency para pegar o usuário autenticado"""
    token = credentials.credentials
    payload = decode_token(token)
    
    sub_value = payload.get("sub")
    user_id = int(sub_value) if sub_value is not None else None
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo"
        )

    # Multi-workspace: armazenar tenant_id do JWT no user object para uso interno
    jwt_tenant_id = payload.get("tid")
    if jwt_tenant_id is not None:
        user._active_tenant_id = int(jwt_tenant_id)
    else:
        # Token antigo (sem tid) — fallback para user.tenant_id original
        user._active_tenant_id = user.tenant_id
    
    return user


def get_current_tenant(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Tenant:
    """Dependency para pegar o tenant (workspace) ativo do usuário autenticado"""
    active_tid = getattr(user, "_active_tenant_id", user.tenant_id)

    # Verificar se o usuário tem acesso a esse workspace
    membership = (
        db.query(TenantUser)
        .filter(TenantUser.user_id == user.id, TenantUser.tenant_id == active_tid)
        .first()
    )

    # Fallback: se não tem registro em tenant_users (migração ainda não rodou),
    # aceitar se é o tenant_id original do user
    if membership is None and active_tid == user.tenant_id:
        # Compatibilidade — aceita acesso direto
        pass
    elif membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem acesso a esse workspace"
        )

    tenant = db.query(Tenant).filter(Tenant.id == active_tid).first()
    if tenant is None or not tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta inativa ou não encontrada"
        )

    # Armazenar role e membership no tenant para dependências de permissão
    tenant._user_role = membership.role if membership else "owner"
    tenant._user_membership = membership  # objeto TenantUser completo
    
    return tenant


def require_super_admin(
    user: User = Depends(get_current_user),
) -> User:
    """Dependency que exige is_super_admin=True. Usado em endpoints de debug/dev."""
    if not user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a super administradores.",
        )
    return user


def get_current_subscription(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
) -> Subscription:
    """Dependency para pegar a assinatura ativa do tenant"""
    subscription = (
        db.query(Subscription)
        .filter(Subscription.tenant_id == tenant.id)
        .order_by(Subscription.id.desc())
        .first()
    )
    
    if subscription is None:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Nenhuma assinatura encontrada"
        )
    
    # Verificar se a assinatura está ativa
    if subscription.status not in ["trial", "active"]:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Assinatura {subscription.status}. Por favor, atualize seu plano."
        )
    
    # Verificar se o trial expirou
    if subscription.status == "trial" and subscription.trial_ends_at:
        if datetime.utcnow() > subscription.trial_ends_at:
            subscription.status = "expired"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Período de teste expirado. Por favor, assine um plano."
            )
    
    # Verificar se o período atual expirou
    if subscription.current_period_end:
        if datetime.utcnow() > subscription.current_period_end:
            subscription.status = "expired"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Assinatura expirada. Por favor, renove seu plano."
            )
    
    return subscription


# ─── Role-based permission dependencies ──────────────────────────────────────

def require_workspace_owner(
    tenant: Tenant = Depends(get_current_tenant),
) -> Tenant:
    """Dependency que exige role='owner' no workspace ativo."""
    role = getattr(tenant, "_user_role", "owner")
    if role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o dono do workspace pode realizar esta ação.",
        )
    return tenant


def require_workspace_admin(
    tenant: Tenant = Depends(get_current_tenant),
) -> Tenant:
    """Dependency que exige role='owner' ou 'admin' no workspace ativo."""
    role = getattr(tenant, "_user_role", "owner")
    if role not in ("owner", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente para esta ação.",
        )
    return tenant


# ─── Granular permission dependencies ─────────────────────────────────────────

def require_permission(*perm_keys: str):
    """
    Factory que retorna uma FastAPI Dependency exigindo que o membro
    tenha TODAS as permissões listadas no workspace ativo.

    Uso:
        @router.get("/", dependencies=[Depends(require_permission("contacts"))])
        def list_contacts(...): ...
    """
    def _checker(tenant: Tenant = Depends(get_current_tenant)) -> Tenant:
        membership = getattr(tenant, "_user_membership", None)
        if membership is None:
            # Fallback: owner (sem membership em tenant_users)
            return tenant
        # Owner sempre tem tudo
        if membership.role == "owner":
            return tenant
        for key in perm_keys:
            if not membership.has_permission(key):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Você não tem permissão para acessar '{key}'.",
                )
        return tenant
    return _checker

