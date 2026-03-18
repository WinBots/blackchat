"""
Router de Workspaces – Multi-workspace support
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import User, Tenant, TenantUser, Subscription, Plan
from app.db.models.tenant_user import AVAILABLE_PERMISSIONS, PERMISSION_LABELS
from app.core.auth import (
    create_access_token,
    get_current_user,
    get_current_tenant,
    require_workspace_owner,
)

router = APIRouter()


# ─── Schemas ──────────────────────────────────────────────────────────────────

class WorkspaceCreate(BaseModel):
    name: str

class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None

class InviteMember(BaseModel):
    email: EmailStr
    role: str = "member"   # admin | member
    permissions: Optional[List[str]] = None  # ex: ["dashboard","contacts","flows"]

class UpdateMemberRole(BaseModel):
    role: str  # admin | member

class UpdateMemberPermissions(BaseModel):
    permissions: List[str]  # ex: ["dashboard","contacts","flows"]


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _build_workspace_response(tenant: Tenant, role: str, is_default: bool, subscription=None, membership=None):
    """Monta dict padrão de workspace."""
    plan_name = None
    sub_info = None
    if subscription:
        plan_name = subscription.plan.display_name if subscription.plan else None
        sub_info = {
            "plan_name": plan_name,
            "status": subscription.status,
        }
    # Permissões: owner sempre tem tudo; se membership fornecido, usar get_permissions()
    if membership:
        perms = membership.get_permissions()
    else:
        perms = list(AVAILABLE_PERMISSIONS)
    return {
        "id": tenant.id,
        "name": tenant.name,
        "role": role,
        "is_default": is_default,
        "plan_name": plan_name,
        "permissions": perms,
        "subscription": sub_info,
    }


# ─── CRUD Workspaces ─────────────────────────────────────────────────────────

@router.get("/")
def list_workspaces(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista todos os workspaces do usuário."""
    memberships = (
        db.query(TenantUser)
        .filter(TenantUser.user_id == user.id)
        .all()
    )

    if not memberships:
        # Fallback pré-migração
        tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
        if tenant:
            sub = db.query(Subscription).filter(
                Subscription.tenant_id == tenant.id
            ).order_by(Subscription.id.desc()).first()
            return [_build_workspace_response(tenant, "owner", True, sub)]
        return []

    tenant_ids = [m.tenant_id for m in memberships]
    tenants = db.query(Tenant).filter(Tenant.id.in_(tenant_ids), Tenant.is_active == True).all()
    tenant_map = {t.id: t for t in tenants}

    # Buscar subscriptions
    subs = db.query(Subscription).filter(
        Subscription.tenant_id.in_(tenant_ids)
    ).order_by(Subscription.id.desc()).all()
    # Manter apenas a mais recente de cada tenant
    sub_map = {}
    for s in subs:
        if s.tenant_id not in sub_map:
            sub_map[s.tenant_id] = s

    result = []
    for m in memberships:
        t = tenant_map.get(m.tenant_id)
        if t:
            result.append(_build_workspace_response(t, m.role, m.is_default, sub_map.get(t.id), membership=m))
    return result


@router.get("/permissions/available")
def get_available_permissions(
    user: User = Depends(get_current_user),
):
    """Retorna a lista de permissões disponíveis no sistema."""
    return [
        {"key": key, "label": PERMISSION_LABELS.get(key, key)}
        for key in AVAILABLE_PERMISSIONS
    ]


@router.post("/", status_code=201)
def create_workspace(
    data: WorkspaceCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Cria um novo workspace para o usuário.
    Regra: só pode criar FREE se não tiver nenhum workspace FREE ativo.
    """
    # Verificar regra: máximo 1 workspace FREE por usuário
    memberships = db.query(TenantUser).filter(TenantUser.user_id == user.id).all()
    my_tenant_ids = [m.tenant_id for m in memberships]

    if my_tenant_ids:
        free_plan = db.query(Plan).filter(Plan.name == "free").first()
        if free_plan:
            existing_free = (
                db.query(Subscription)
                .filter(
                    Subscription.tenant_id.in_(my_tenant_ids),
                    Subscription.plan_id == free_plan.id,
                    Subscription.status.in_(["trial", "active"]),
                )
                .first()
            )
            if existing_free:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Você já possui um workspace no plano gratuito. "
                           "Faça upgrade do plano gratuito existente antes de criar um novo workspace.",
                )

    # Criar novo tenant (workspace)
    new_tenant = Tenant(
        name=data.name.strip(),
        email=user.email,
        is_active=True,
    )
    db.add(new_tenant)
    db.flush()

    # Criar vínculo como owner
    tu = TenantUser(
        tenant_id=new_tenant.id,
        user_id=user.id,
        role="owner",
        is_default=False,
    )
    db.add(tu)

    # Criar subscription FREE (trial 14 dias)
    free_plan = db.query(Plan).filter(Plan.name == "free").first()
    if not free_plan:
        raise HTTPException(status_code=500, detail="Plano gratuito não encontrado.")

    sub = Subscription(
        tenant_id=new_tenant.id,
        plan_id=free_plan.id,
        status="trial",
        started_at=datetime.utcnow(),
        trial_ends_at=datetime.utcnow() + timedelta(days=14),
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow() + timedelta(days=14),
    )
    db.add(sub)

    db.commit()
    db.refresh(new_tenant)

    # Gerar novo token apontando para o workspace recém-criado
    access_token = create_access_token(data={"sub": user.id, "tid": new_tenant.id})

    return {
        "workspace": _build_workspace_response(new_tenant, "owner", False, sub, membership=tu),
        "access_token": access_token,
    }


@router.put("/{workspace_id}")
def update_workspace(
    workspace_id: int,
    data: WorkspaceUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Atualiza info do workspace. Apenas owner pode editar."""
    membership = (
        db.query(TenantUser)
        .filter(TenantUser.user_id == user.id, TenantUser.tenant_id == workspace_id)
        .first()
    )
    if not membership or membership.role != "owner":
        raise HTTPException(status_code=403, detail="Apenas o dono pode editar o workspace.")

    tenant = db.query(Tenant).filter(Tenant.id == workspace_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Workspace não encontrado.")

    if data.name is not None:
        tenant.name = data.name.strip()

    db.commit()
    db.refresh(tenant)
    return {"id": tenant.id, "name": tenant.name}


@router.post("/{workspace_id}/switch")
def switch_workspace(
    workspace_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Troca o workspace ativo. Gera novo JWT com o tenant_id do workspace."""
    membership = (
        db.query(TenantUser)
        .filter(TenantUser.user_id == user.id, TenantUser.tenant_id == workspace_id)
        .first()
    )
    if not membership:
        raise HTTPException(status_code=403, detail="Você não tem acesso a esse workspace.")

    tenant = db.query(Tenant).filter(Tenant.id == workspace_id, Tenant.is_active == True).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Workspace não encontrado ou inativo.")

    # Atualizar is_default: tirar de todos, marcar este
    db.query(TenantUser).filter(TenantUser.user_id == user.id).update({"is_default": False})
    membership.is_default = True
    db.commit()

    # Gerar novo token com o workspace selecionado
    access_token = create_access_token(data={"sub": user.id, "tid": tenant.id})

    return {
        "access_token": access_token,
        "tenant": {
            "id": tenant.id,
            "name": tenant.name,
            "email": tenant.email,
        },
        "role": membership.role,
    }


# ─── Membros do Workspace ────────────────────────────────────────────────────

@router.get("/{workspace_id}/members")
def list_members(
    workspace_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista membros do workspace."""
    # Verificar se o usuário faz parte do workspace
    my_membership = (
        db.query(TenantUser)
        .filter(TenantUser.user_id == user.id, TenantUser.tenant_id == workspace_id)
        .first()
    )
    if not my_membership:
        raise HTTPException(status_code=403, detail="Sem acesso a esse workspace.")

    members = (
        db.query(TenantUser, User)
        .join(User, User.id == TenantUser.user_id)
        .filter(TenantUser.tenant_id == workspace_id)
        .all()
    )
    return [
        {
            "user_id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "role": tu.role,
            "permissions": tu.get_permissions(),
            "joined_at": tu.created_at.strftime("%Y-%m-%d %H:%M:%S") if tu.created_at else None,
        }
        for tu, u in members
    ]


@router.post("/{workspace_id}/members")
def invite_member(
    workspace_id: int,
    data: InviteMember,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Convida um usuário existente para o workspace.
    Apenas o owner pode convidar.
    """
    # Verificar que eu sou owner desse workspace
    my_membership = (
        db.query(TenantUser)
        .filter(TenantUser.user_id == user.id, TenantUser.tenant_id == workspace_id)
        .first()
    )
    if not my_membership or my_membership.role != "owner":
        raise HTTPException(status_code=403, detail="Apenas o dono do workspace pode convidar membros.")

    # Validar role
    if data.role not in ("admin", "member"):
        raise HTTPException(status_code=400, detail="Role deve ser 'admin' ou 'member'.")

    # Buscar o usuário pelo email
    email = data.email.strip().lower()
    target_user = db.query(User).filter(func.lower(User.email) == email).first()
    if not target_user:
        raise HTTPException(
            status_code=404,
            detail="Nenhum usuário encontrado com esse email. O usuário precisa ter uma conta no sistema.",
        )

    if target_user.id == user.id:
        raise HTTPException(status_code=400, detail="Você já é membro desse workspace.")

    # Verificar se já é membro
    existing = (
        db.query(TenantUser)
        .filter(TenantUser.user_id == target_user.id, TenantUser.tenant_id == workspace_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Este usuário já é membro do workspace.")

    # Criar vínculo
    new_member = TenantUser(
        tenant_id=workspace_id,
        user_id=target_user.id,
        role=data.role,
        is_default=False,
    )
    # Definir permissões (se fornecidas, senão null = ALL)
    if data.permissions is not None:
        new_member.set_permissions(data.permissions)
    db.add(new_member)
    db.commit()

    return {
        "message": f"{target_user.full_name} foi adicionado ao workspace.",
        "member": {
            "user_id": target_user.id,
            "email": target_user.email,
            "full_name": target_user.full_name,
            "role": data.role,
            "permissions": new_member.get_permissions(),
        }
    }


@router.put("/{workspace_id}/members/{member_user_id}")
def update_member_role(
    workspace_id: int,
    member_user_id: int,
    data: UpdateMemberRole,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Altera o role de um membro. Apenas owner pode."""
    my_membership = (
        db.query(TenantUser)
        .filter(TenantUser.user_id == user.id, TenantUser.tenant_id == workspace_id)
        .first()
    )
    if not my_membership or my_membership.role != "owner":
        raise HTTPException(status_code=403, detail="Apenas o dono pode alterar permissões.")

    if member_user_id == user.id:
        raise HTTPException(status_code=400, detail="Você não pode alterar seu próprio role.")

    if data.role not in ("admin", "member"):
        raise HTTPException(status_code=400, detail="Role deve ser 'admin' ou 'member'.")

    membership = (
        db.query(TenantUser)
        .filter(TenantUser.user_id == member_user_id, TenantUser.tenant_id == workspace_id)
        .first()
    )
    if not membership:
        raise HTTPException(status_code=404, detail="Membro não encontrado.")

    membership.role = data.role
    db.commit()
    return {"message": "Role atualizado.", "role": data.role}


@router.put("/{workspace_id}/members/{member_user_id}/permissions")
def update_member_permissions(
    workspace_id: int,
    member_user_id: int,
    data: UpdateMemberPermissions,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Atualiza as permissões de um membro. Apenas owner pode."""
    my_membership = (
        db.query(TenantUser)
        .filter(TenantUser.user_id == user.id, TenantUser.tenant_id == workspace_id)
        .first()
    )
    if not my_membership or my_membership.role != "owner":
        raise HTTPException(status_code=403, detail="Apenas o dono pode alterar permissões.")

    if member_user_id == user.id:
        raise HTTPException(status_code=400, detail="Você não pode alterar suas próprias permissões.")

    membership = (
        db.query(TenantUser)
        .filter(TenantUser.user_id == member_user_id, TenantUser.tenant_id == workspace_id)
        .first()
    )
    if not membership:
        raise HTTPException(status_code=404, detail="Membro não encontrado.")

    if membership.role == "owner":
        raise HTTPException(status_code=400, detail="Não é possível alterar permissões do dono.")

    # Validar que todas as permissões são válidas
    invalid = [p for p in data.permissions if p not in AVAILABLE_PERMISSIONS]
    if invalid:
        raise HTTPException(
            status_code=400,
            detail=f"Permissões inválidas: {', '.join(invalid)}",
        )

    membership.set_permissions(data.permissions)
    db.commit()
    return {
        "message": "Permissões atualizadas.",
        "permissions": membership.get_permissions(),
    }


@router.delete("/{workspace_id}/members/{member_user_id}")
def remove_member(
    workspace_id: int,
    member_user_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Remove um membro do workspace.
    Owner pode remover qualquer um. Membro pode sair (remover a si mesmo).
    """
    my_membership = (
        db.query(TenantUser)
        .filter(TenantUser.user_id == user.id, TenantUser.tenant_id == workspace_id)
        .first()
    )
    if not my_membership:
        raise HTTPException(status_code=403, detail="Sem acesso a esse workspace.")

    is_self = member_user_id == user.id

    # Apenas owner pode remover outros
    if not is_self and my_membership.role != "owner":
        raise HTTPException(status_code=403, detail="Apenas o dono pode remover membros.")

    # Owner não pode se remover
    target = (
        db.query(TenantUser)
        .filter(TenantUser.user_id == member_user_id, TenantUser.tenant_id == workspace_id)
        .first()
    )
    if not target:
        raise HTTPException(status_code=404, detail="Membro não encontrado.")

    if target.role == "owner":
        raise HTTPException(status_code=400, detail="O dono do workspace não pode ser removido.")

    db.delete(target)
    db.commit()
    return {"message": "Membro removido do workspace."}
