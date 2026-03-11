"""
Utilitários de autenticação e segurança
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import User, Tenant, Subscription
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
    
    return user


def get_current_tenant(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Tenant:
    """Dependency para pegar o tenant do usuário autenticado"""
    tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
    if tenant is None or not tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta inativa ou não encontrada"
        )
    
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

