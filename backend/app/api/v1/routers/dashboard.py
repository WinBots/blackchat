from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.auth import get_current_tenant
from app.db.session import get_db
from app.db.models import Tenant
from app.db.models.channel import Channel
from app.db.models.contact import Contact
from app.db.models.flow import Flow
from app.db.models.flow_execution import FlowExecution
from app.db.models.message import Message


router = APIRouter()


class RecentActivityItem(BaseModel):
    id: int
    name: str
    username: Optional[str] = None
    initials: str
    channel: str
    channel_type: Optional[str] = None
    event: str
    created_at: Optional[str] = None
    status: str
    direction: Optional[str] = None


class DashboardMetricsOut(BaseModel):
    contacts_total: int
    contacts_last_24h: int
    flows_active: int
    flow_executions_today: int
    channels_connected: int
    recent_activity: list[RecentActivityItem]


def _initials(name: str) -> str:
    parts = [p for p in (name or '').strip().split() if p]
    if not parts:
        return '?' 
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][:1] + parts[-1][:1]).upper()


def _safe_iso(dt) -> Optional[str]:
    if not dt:
        return None
    try:
        return dt.isoformat()
    except Exception:
        return None


@router.get("/metrics", response_model=DashboardMetricsOut)
def get_dashboard_metrics(
    limit: int = 20,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Métricas reais para a dashboard (MVP).

    - Tudo é filtrado por tenant autenticado.
    - recent_activity usa a tabela messages como fonte principal.
    """
    limit = max(1, min(int(limit or 20), 50))

    now = datetime.now(timezone.utc)
    last_24h = now - timedelta(hours=24)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

    contacts_total = (
        db.query(func.count(Contact.id))
        .filter(Contact.tenant_id == tenant.id)
        .scalar()
        or 0
    )
    contacts_last_24h = (
        db.query(func.count(Contact.id))
        .filter(Contact.tenant_id == tenant.id, Contact.created_at >= last_24h)
        .scalar()
        or 0
    )
    flows_active = (
        db.query(func.count(Flow.id))
        .filter(Flow.tenant_id == tenant.id, Flow.is_active == True)
        .scalar()
        or 0
    )
    channels_connected = (
        db.query(func.count(Channel.id))
        .filter(Channel.tenant_id == tenant.id, Channel.is_active == True)
        .scalar()
        or 0
    )
    flow_executions_today = (
        db.query(func.count(FlowExecution.id))
        .filter(FlowExecution.tenant_id == tenant.id, FlowExecution.started_at >= start_of_day)
        .scalar()
        or 0
    )

    rows = (
        db.query(Message, Contact, Channel, Flow)
        .join(Contact, Message.contact_id == Contact.id)
        .outerjoin(Channel, Message.channel_id == Channel.id)
        .outerjoin(Flow, Message.flow_id == Flow.id)
        .filter(Message.tenant_id == tenant.id)
        .order_by(Message.created_at.desc(), Message.id.desc())
        .limit(limit)
        .all()
    )

    activity: list[RecentActivityItem] = []
    for msg, contact, channel, flow in rows:
        display_name = (
            (" ".join([p for p in [contact.first_name, contact.last_name] if p]).strip())
            or (contact.username or '').strip()
            or f"Contato #{contact.id}"
        )
        username = contact.username
        channel_type = (channel.type if channel else None)
        channel_label = (
            (channel.type.title() if channel and channel.type else "Canal")
        )

        if msg.direction == "inbound":
            event = "Nova mensagem"
            status = "Recebida"
        else:
            event = "Mensagem enviada"
            status = msg.status or "Enviada"

        if flow is not None and flow.name:
            # Mantém curto, mas útil
            event = f"{event} • {flow.name}"

        activity.append(
            RecentActivityItem(
                id=msg.id,
                name=display_name,
                username=username,
                initials=_initials(display_name),
                channel=channel_label,
                channel_type=channel_type,
                event=event,
                created_at=_safe_iso(msg.created_at),
                status=status,
                direction=msg.direction,
            )
        )

    return DashboardMetricsOut(
        contacts_total=int(contacts_total),
        contacts_last_24h=int(contacts_last_24h),
        flows_active=int(flows_active),
        flow_executions_today=int(flow_executions_today),
        channels_connected=int(channels_connected),
        recent_activity=activity,
    )
