import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.flow import Flow
from app.db.models.flow_step import FlowStep
from app.db.models import User, Tenant
from app.core.auth import get_current_user, get_current_tenant
from app.services.billing_service import LimitExceededError, check_flow_limit, get_plan_for_tenant
from app.cache.service import invalidate_flow, invalidate_tenant_flows

router = APIRouter()


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


@router.get("/", response_model=List[FlowOut])
def list_flows(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """Lista flows do tenant autenticado"""
    flows = db.query(Flow).filter(Flow.tenant_id == tenant.id).order_by(Flow.id.desc()).all()
    result: list[FlowOut] = []
    for f in flows:
        result.append(
            FlowOut(
                id=f.id,
                tenant_id=f.tenant_id,
                channel_id=f.channel_id,
                name=f.name,
                description=f.description,
                trigger_type=f.trigger_type,
                trigger_config=json.loads(f.trigger_config) if f.trigger_config else None,
                config=json.loads(f.config) if f.config else None,
                is_active=f.is_active,
            )
        )
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

    print("update_flow payload", data.model_dump())

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
        print("update_flow commit error", exc)
        raise
    db.refresh(flow)
    invalidate_flow(flow_id)
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


@router.delete("/{flow_id}")
def delete_flow(flow_id: int, db: Session = Depends(get_db)):
    flow = db.query(Flow).filter(Flow.id == flow_id).first()
    if not flow:
        raise HTTPException(status_code=404, detail="Flow não encontrado")
    tenant_id = flow.tenant_id
    db.query(FlowStep).filter(FlowStep.flow_id == flow_id).delete()
    db.delete(flow)
    db.commit()
    invalidate_flow(flow_id)
    return {"ok": True}


@router.get("/{flow_id}/steps", response_model=List[FlowStepOut])
def list_steps(flow_id: int, db: Session = Depends(get_db)):
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
def create_step(flow_id: int, data: FlowStepCreate, db: Session = Depends(get_db)):
    flow = db.query(Flow).filter(Flow.id == flow_id).first()
    if not flow:
        raise HTTPException(status_code=404, detail="Flow não encontrado")
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
    return FlowStepOut(
        id=step.id,
        flow_id=step.flow_id,  # type: ignore
        type=step.type,
        order_index=step.order_index,
        config=data.config,
    )


@router.put("/{flow_id}/steps/{step_id}", response_model=FlowStepOut)
def update_step(flow_id: int, step_id: int, data: FlowStepUpdate, db: Session = Depends(get_db)):
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
        step.config = json.dumps(data.config)

    db.commit()
    db.refresh(step)
    invalidate_flow(flow_id)
    return FlowStepOut(
        id=step.id,
        flow_id=step.flow_id,  # type: ignore
        type=step.type,
        order_index=step.order_index,
        config=json.loads(step.config) if step.config else {},
    )


@router.delete("/{flow_id}/steps/{step_id}")
def delete_step(flow_id: int, step_id: int, db: Session = Depends(get_db)):
    step = (
        db.query(FlowStep)
        .filter(FlowStep.flow_id == flow_id, FlowStep.id == step_id)
        .first()
    )
    if not step:
        raise HTTPException(status_code=404, detail="Step não encontrado")
    db.delete(step)
    db.commit()
    invalidate_flow(flow_id)
    return {"ok": True}


@router.post("/{flow_id}/run-demo", response_model=DemoRunResult)
def run_demo(flow_id: int, db: Session = Depends(get_db)):
    flow = db.query(Flow).filter(Flow.id == flow_id).first()
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
