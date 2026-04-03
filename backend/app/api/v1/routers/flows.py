import json
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from app.db.session import get_db
from app.db.models.flow import Flow
from app.db.models.flow_step import FlowStep
from app.db.models import User, Tenant
from app.core.auth import get_current_user, get_current_tenant
from app.services.billing_service import LimitExceededError, check_flow_limit, get_plan_for_tenant
from app.cache.service import invalidate_flow, invalidate_tenant_flows
from app.cache.redis_client import cache_get, cache_set, cache_delete
from app.cache.keys import CacheKeys

router = APIRouter()

# Inclui sub-router de geração por IA
from app.api.v1.routers.ai_flows import router as ai_router
router.include_router(ai_router)


class FlowBase(BaseModel):
    tenant_id: int
    channel_id: int | None = None
    name: str
    description: str | None = None
    trigger_type: str = "manual"
    trigger_config: dict | None = None
    config: dict | None = None


class FlowCreate(BaseModel):
    """Schema para criar flow (tenant_id vem do usuário autenticado)"""
    channel_id: int | None = None
    name: str
    description: str | None = None
    trigger_type: str = "manual"
    trigger_config: dict | None = None
    config: dict | None = None


class FlowUpdate(BaseModel):
    channel_id: int | None = None
    name: str | None = None
    description: str | None = None
    trigger_type: str | None = None
    trigger_config: dict | None = None
    config: dict | None = None
    is_active: bool | None = None


class FlowOut(FlowBase):
    id: int
    is_active: bool

    model_config = {"from_attributes": True}


class FlowListOut(BaseModel):
    """Schema para listagem — exclui config (nodePositions/conexões) e inclui keywords."""
    id: int
    tenant_id: int
    channel_id: int | None = None
    name: str
    description: str | None = None
    trigger_type: str
    trigger_config: dict | None = None
    is_active: bool
    keywords: list[str] = []

    model_config = {"from_attributes": True}


class FlowStepBase(BaseModel):
    type: str
    order_index: int
    config: dict


class FlowStepCreate(FlowStepBase):
    pass


class FlowStepUpdate(BaseModel):
    type: str | None = None
    order_index: int | None = None
    config: dict | None = None


class FlowStepOut(FlowStepBase):
    id: int

    model_config = {"from_attributes": True}


class DemoRunResult(BaseModel):
    flow_id: int
    executed_steps: list[dict]


def _check_keyword_conflict(
    db: Session,
    current_flow: Flow,
    trigger_config: dict,
) -> None:
    """Levanta HTTP 409 se alguma keyword já está em uso por outro fluxo ativo do mesmo canal."""
    if trigger_config.get("triggerType") != "message":
        return

    new_keywords = {
        (kw if isinstance(kw, str) else kw.get("text", "")).lower().strip()
        for kw in trigger_config.get("keywords", [])
    }
    new_keywords.discard("")
    if not new_keywords:
        return

    # Outros fluxos ativos do mesmo canal (ou sem canal, para compatibilidade)
    q = db.query(Flow).filter(
        Flow.tenant_id == current_flow.tenant_id,
        Flow.is_active == True,
        Flow.id != current_flow.id,
    )
    if current_flow.channel_id:
        q = q.filter(
            or_(Flow.channel_id == current_flow.channel_id, Flow.channel_id == None)
        )

    for other_flow in q.all():
        trigger = db.query(FlowStep).filter(
            FlowStep.flow_id == other_flow.id,
            FlowStep.type == "trigger",
        ).first()
        if not trigger or not trigger.config:
            continue
        try:
            other_cfg = json.loads(trigger.config)
        except Exception:
            continue
        if other_cfg.get("triggerType") != "message":
            continue

        other_keywords = {
            (kw if isinstance(kw, str) else kw.get("text", "")).lower().strip()
            for kw in other_cfg.get("keywords", [])
        }
        other_keywords.discard("")

        conflicts = new_keywords & other_keywords
        if conflicts:
            conflict_list = ", ".join(f'"{k}"' for k in sorted(conflicts))
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Keyword(s) {conflict_list} já usada(s) no fluxo \"{other_flow.name}\". "
                    "Cada keyword deve ser única por canal."
                ),
            )


@router.get("/", response_model=List[FlowListOut])
def list_flows(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """Lista flows do tenant autenticado.

    Otimizações:
    - Cache Redis 60s (invalidado ao criar/editar/deletar)
    - Exclui o campo config (nodePositions/conexões — grande e desnecessário na lista)
    - Extrai keywords dos trigger steps server-side (evita N requisições do frontend)
    - 2 queries totais (flows + trigger steps) independente do nº de flows
    """
    cache_key = CacheKeys.tenant_flows(tenant.id)
    cached = cache_get(cache_key)
    if cached is not None:
        return [FlowListOut(**f) for f in cached]

    flows = db.query(Flow).filter(Flow.tenant_id == tenant.id).order_by(Flow.id.desc()).all()
    if not flows:
        return []

    # Buscar steps trigger de todos os flows em UMA query (evita N+1 no frontend)
    flow_ids = [f.id for f in flows]
    trigger_steps = (
        db.query(FlowStep)
        .filter(FlowStep.flow_id.in_(flow_ids), FlowStep.type == "trigger")
        .all()
    )
    trigger_by_flow: dict[int, FlowStep] = {s.flow_id: s for s in trigger_steps}

    result: list[FlowListOut] = []
    for f in flows:
        trigger = trigger_by_flow.get(f.id)
        keywords: list[str] = []
        if trigger and trigger.config:
            try:
                cfg = json.loads(trigger.config)
                raw_kws = cfg.get("keywords", [])
                keywords = [
                    (kw if isinstance(kw, str) else kw.get("text", ""))
                    for kw in raw_kws
                    if kw
                ]
                keywords = [k for k in keywords if k]
            except (json.JSONDecodeError, AttributeError):
                pass

        result.append(FlowListOut(
            id=f.id,
            tenant_id=f.tenant_id,
            channel_id=f.channel_id,
            name=f.name,
            description=f.description,
            trigger_type=f.trigger_type,
            trigger_config=json.loads(f.trigger_config) if f.trigger_config else None,
            is_active=f.is_active,
            keywords=keywords,
        ))

    cache_set(cache_key, [r.model_dump() for r in result], CacheKeys.TENANT_FLOWS_TTL)
    return result


@router.post("/", response_model=FlowOut)
def create_flow(
    data: FlowCreate,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """Cria novo flow para o tenant autenticado"""
    # Verificar limite do plano antes de criar
    try:
        plan = get_plan_for_tenant(db, tenant.id)
        if plan:
            current_flows = db.query(Flow).filter(Flow.tenant_id == tenant.id).count()
            check_flow_limit(db, tenant.id, plan, current_flows)
    except LimitExceededError as exc:
        raise HTTPException(status_code=403, detail=exc.to_dict())

    flow = Flow(
        tenant_id=tenant.id,
        channel_id=data.channel_id,
        name=data.name,
        description=data.description,
        trigger_type=data.trigger_type,
        trigger_config=json.dumps(data.trigger_config) if data.trigger_config else None,
        config=json.dumps(data.config) if data.config else None,
    )
    db.add(flow)
    db.commit()
    db.refresh(flow)
    cache_delete(CacheKeys.tenant_flows(tenant.id))
    return FlowOut(
        id=flow.id,
        tenant_id=flow.tenant_id,
        channel_id=flow.channel_id,
        name=flow.name,
        description=flow.description,
        trigger_type=flow.trigger_type,
        trigger_config=data.trigger_config,
        config=data.config,
        is_active=flow.is_active,
    )


@router.get("/{flow_id}", response_model=FlowOut)
def get_flow(
    flow_id: int,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """Busca flow do tenant autenticado"""
    flow = db.query(Flow).filter(Flow.id == flow_id, Flow.tenant_id == tenant.id).first()
    if not flow:
        raise HTTPException(status_code=404, detail="Flow não encontrado")
    return FlowOut(
        id=flow.id,
        tenant_id=flow.tenant_id,
        channel_id=flow.channel_id,
        name=flow.name,
        description=flow.description,
        trigger_type=flow.trigger_type,
        trigger_config=json.loads(flow.trigger_config) if flow.trigger_config else None,
        config=json.loads(flow.config) if flow.config else None,
        is_active=flow.is_active,
    )


@router.put("/{flow_id}", response_model=FlowOut)
def update_flow(
    flow_id: int,
    data: FlowUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """Atualiza flow do tenant autenticado"""
    flow = db.query(Flow).filter(Flow.id == flow_id, Flow.tenant_id == tenant.id).first()
    if not flow:
        raise HTTPException(status_code=404, detail="Flow não encontrado")

    logger.debug("update_flow payload: %s", data.model_dump(exclude_none=True))

    if data.channel_id is not None:
        flow.channel_id = data.channel_id
    if data.name is not None:
        flow.name = data.name
    if data.description is not None:
        flow.description = data.description
    if data.trigger_type is not None:
        flow.trigger_type = data.trigger_type
    if data.trigger_config is not None:
        # Garantir exclusividade de fluxo padrão Telegram
        if data.trigger_config.get("default_for") == "telegram":
            # Remover default_for=telegram de outros fluxos do mesmo tenant
            other_flows = db.query(Flow).filter(
                Flow.tenant_id == flow.tenant_id,
                Flow.id != flow_id
            ).all()
            
            for other_flow in other_flows:
                try:
                    other_config = json.loads(other_flow.trigger_config) if other_flow.trigger_config else {}
                    if other_config.get("default_for") == "telegram":
                        other_config.pop("default_for", None)
                        other_flow.trigger_config = json.dumps(other_config) if other_config else None
                except json.JSONDecodeError:
                    pass
        
        flow.trigger_config = json.dumps(data.trigger_config)
    if data.config is not None:
        flow.config = json.dumps(data.config)
    if data.is_active is not None:
        flow.is_active = data.is_active

    try:
        db.commit()
    except Exception as exc:
        logger.error("update_flow commit error: %s", exc)
        raise
    db.refresh(flow)
    invalidate_flow(flow_id)
    cache_delete(CacheKeys.tenant_flows(flow.tenant_id))
    return FlowOut(
        id=flow.id,
        tenant_id=flow.tenant_id,
        channel_id=flow.channel_id,
        name=flow.name,
        description=flow.description,
        trigger_type=flow.trigger_type,
        trigger_config=json.loads(flow.trigger_config) if flow.trigger_config else None,
        config=json.loads(flow.config) if flow.config else None,
        is_active=flow.is_active,
    )


@router.post("/{flow_id}/duplicate", response_model=FlowOut)
def duplicate_flow(
    flow_id: int,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Duplica um flow e todos os seus steps."""
    original = _get_flow_for_tenant(flow_id, tenant.id, db)

    # Verificar limite do plano antes de duplicar
    try:
        plan = get_plan_for_tenant(db, tenant.id)
        if plan:
            current_count = db.query(Flow).filter(Flow.tenant_id == tenant.id).count()
            check_flow_limit(db, tenant.id, plan, current_count)
    except LimitExceededError as exc:
        raise HTTPException(status_code=403, detail=exc.to_dict())

    new_flow = Flow(
        tenant_id=tenant.id,
        channel_id=original.channel_id,
        name=f"{original.name} (cópia)",
        description=original.description,
        trigger_type=original.trigger_type,
        trigger_config=original.trigger_config,
        config=None,  # posições não copiadas intencionalmente
        is_active=False,  # começa inativo para revisão
    )
    db.add(new_flow)
    db.flush()  # gera o id sem commitar

    original_steps = (
        db.query(FlowStep)
        .filter(FlowStep.flow_id == flow_id)
        .order_by(FlowStep.order_index.asc())
        .all()
    )
    for step in original_steps:
        db.add(FlowStep(
            flow_id=new_flow.id,
            type=step.type,
            order_index=step.order_index,
            config=step.config,
        ))

    db.commit()
    db.refresh(new_flow)
    cache_delete(CacheKeys.tenant_flows(tenant.id))

    return FlowOut(
        id=new_flow.id,
        tenant_id=new_flow.tenant_id,
        channel_id=new_flow.channel_id,
        name=new_flow.name,
        description=new_flow.description,
        trigger_type=new_flow.trigger_type,
        trigger_config=json.loads(new_flow.trigger_config) if new_flow.trigger_config else None,
        config=None,
        is_active=new_flow.is_active,
    )


@router.delete("/{flow_id}")
def delete_flow(
    flow_id: int,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    flow = db.query(Flow).filter(Flow.id == flow_id, Flow.tenant_id == tenant.id).first()
    if not flow:
        raise HTTPException(status_code=404, detail="Flow não encontrado")
    db.query(FlowStep).filter(FlowStep.flow_id == flow_id).delete()
    db.delete(flow)
    db.commit()
    invalidate_flow(flow_id)
    cache_delete(CacheKeys.tenant_flows(tenant.id))
    return {"ok": True}


def _get_flow_for_tenant(flow_id: int, tenant_id: int, db: Session) -> Flow:
    """Busca o flow verificando posse do tenant. Levanta 404 se não encontrado."""
    flow = db.query(Flow).filter(Flow.id == flow_id, Flow.tenant_id == tenant_id).first()
    if not flow:
        raise HTTPException(status_code=404, detail="Flow não encontrado")
    return flow


@router.get("/{flow_id}/steps", response_model=List[FlowStepOut])
def list_steps(
    flow_id: int,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    _get_flow_for_tenant(flow_id, tenant.id, db)
    steps = (
        db.query(FlowStep)
        .filter(FlowStep.flow_id == flow_id)
        .order_by(FlowStep.order_index.asc())
        .all()
    )
    return [
        FlowStepOut(
            id=s.id,
            flow_id=s.flow_id,  # type: ignore
            type=s.type,
            order_index=s.order_index,
            config=json.loads(s.config) if s.config else {},
        )
        for s in steps
    ]


@router.post("/{flow_id}/steps", response_model=FlowStepOut)
def create_step(
    flow_id: int,
    data: FlowStepCreate,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    flow = _get_flow_for_tenant(flow_id, tenant.id, db)
    if data.type == "trigger" and data.config:
        _check_keyword_conflict(db, flow, data.config)
    step = FlowStep(
        flow_id=flow_id,
        type=data.type,
        order_index=data.order_index,
        config=json.dumps(data.config),
    )
    db.add(step)
    db.commit()
    db.refresh(step)
    invalidate_flow(flow_id)
    cache_delete(CacheKeys.tenant_flows(flow.tenant_id))
    return FlowStepOut(
        id=step.id,
        flow_id=step.flow_id,  # type: ignore
        type=step.type,
        order_index=step.order_index,
        config=data.config,
    )


@router.put("/{flow_id}/steps/{step_id}", response_model=FlowStepOut)
def update_step(
    flow_id: int,
    step_id: int,
    data: FlowStepUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    flow = _get_flow_for_tenant(flow_id, tenant.id, db)
    step = (
        db.query(FlowStep)
        .filter(FlowStep.flow_id == flow_id, FlowStep.id == step_id)
        .first()
    )
    if not step:
        raise HTTPException(status_code=404, detail="Step não encontrado")

    if data.type is not None:
        step.type = data.type
    if data.order_index is not None:
        step.order_index = data.order_index
    if data.config is not None:
        effective_type = data.type or step.type
        if effective_type == "trigger":
            _check_keyword_conflict(db, flow, data.config)
        step.config = json.dumps(data.config)

    db.commit()
    db.refresh(step)
    invalidate_flow(flow_id)
    if data.type == "trigger" or (data.config is not None and step.type == "trigger"):
        cache_delete(CacheKeys.tenant_flows(flow.tenant_id))
    return FlowStepOut(
        id=step.id,
        flow_id=step.flow_id,  # type: ignore
        type=step.type,
        order_index=step.order_index,
        config=json.loads(step.config) if step.config else {},
    )


@router.delete("/{flow_id}/steps/{step_id}")
def delete_step(
    flow_id: int,
    step_id: int,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    flow = _get_flow_for_tenant(flow_id, tenant.id, db)
    step = (
        db.query(FlowStep)
        .filter(FlowStep.flow_id == flow_id, FlowStep.id == step_id)
        .first()
    )
    if not step:
        raise HTTPException(status_code=404, detail="Step não encontrado")
    is_trigger = step.type == "trigger"
    db.delete(step)
    db.commit()
    invalidate_flow(flow_id)
    if is_trigger:
        cache_delete(CacheKeys.tenant_flows(flow.tenant_id))
    return {"ok": True}


@router.post("/{flow_id}/run-demo", response_model=DemoRunResult)
def run_demo(
    flow_id: int,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    flow = db.query(Flow).filter(Flow.id == flow_id, Flow.tenant_id == tenant.id).first()
    if not flow:
        raise HTTPException(status_code=404, detail="Flow não encontrado")

    steps = (
        db.query(FlowStep)
        .filter(FlowStep.flow_id == flow_id)
        .order_by(FlowStep.order_index.asc())
        .all()
    )

    actions: list[dict] = []

    for step in steps:
        cfg = json.loads(step.config) if step.config else {}
        if step.type == "message":
            text = cfg.get("text", "")
            actions.append({"step_id": step.id, "action": "send_message", "text": text})
        elif step.type == "wait":
            seconds = cfg.get("seconds", 0)
            actions.append({"step_id": step.id, "action": "wait", "seconds": seconds})
        else:
            actions.append({"step_id": step.id, "action": "noop", "raw_config": cfg})

    return DemoRunResult(flow_id=flow_id, executed_steps=actions)
