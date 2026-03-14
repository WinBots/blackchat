from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, cast, text, case
from sqlalchemy import Float, String
from typing import List, Optional, Literal
from pydantic import BaseModel
import json
import logging
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date, timedelta

from app.core.auth import get_current_tenant
from app.db.session import get_db
from app.db.models.contact import Contact
from app.db.models.channel import Channel
from app.db.models.message import Message
from app.db.models.tag import ContactTag
from app.db.models.flow import Flow
from app.db.models.flow_execution import FlowExecution
from app.db.models.flow_execution_log import FlowExecutionLog
from app.db.models.sequence import ContactSequence
from app.db.models import Tenant

logger = logging.getLogger(__name__)
router = APIRouter()


# Pydantic Models
class ContactOut(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    default_channel_id: Optional[int] = None
    channel_name: Optional[str] = None
    channel_type: Optional[str] = None
    custom_fields: Optional[dict] = {}
    tags: Optional[List[str]] = []
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class MessageOut(BaseModel):
    id: int
    direction: str  # 'inbound' ou 'outbound'
    content: Optional[str] = None
    message_type: Optional[str] = None
    status: Optional[str] = None
    external_id: Optional[str] = None
    extra_data: Optional[dict] = None
    error_message: Optional[str] = None
    flow_execution_id: Optional[int] = None
    step_id: Optional[int] = None
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class ContactListOut(BaseModel):
    items: List[ContactOut]
    total: int
    limit: int
    offset: int


class ChannelCountOut(BaseModel):
    channel_id: Optional[int] = None
    channel_name: Optional[str] = None
    channel_type: Optional[str] = None
    count: int


class TagCountOut(BaseModel):
    name: str
    count: int


class FieldPairCountOut(BaseModel):
    field: str
    value: str
    count: int


class ContactStatsOut(BaseModel):
    contacts_total: int
    by_channel: List[ChannelCountOut]
    by_tag: List[TagCountOut]


class TagIn(BaseModel):
    tag_name: str


class SendMessageIn(BaseModel):
    text: str
    parse_mode: str = "MarkdownV2"  # Telegram: MarkdownV2 para formatação (negrito, itálico, etc.)


class FieldCondition(BaseModel):
    source: Literal["system", "custom"]
    field: str
    op: Literal[
        "eq",
        "neq",
        "contains",
        "not_contains",
        "starts_with",
        "ends_with",
        "gt",
        "gte",
        "lt",
        "lte",
        "is_empty",
        "is_not_empty",
        "exists",
        "not_exists",
    ]
    value: Optional[str] = None
    value_type: Literal["string", "number", "boolean", "date"] = "string"


class BulkMessageFilters(BaseModel):
    """
    Filtros reutilizáveis para seleção em massa de contatos.
    São equivalentes aos filtros da listagem de contatos.
    """
    search: Optional[str] = None
    channel_id: Optional[int] = None
    tags: Optional[List[str]] = None

    # Novos filtros (para segmentação avançada em broadcasts)
    match_mode: Literal["all", "any"] = "all"  # all = AND, any = OR
    channel_ids: Optional[List[int]] = None
    tags_any: Optional[List[str]] = None
    tags_all: Optional[List[str]] = None
    tags_exclude: Optional[List[str]] = None
    created_after: Optional[str] = None  # ISO date/datetime
    created_before: Optional[str] = None  # ISO date/datetime
    last_inbound_days: Optional[int] = None
    field_conditions: Optional[List[FieldCondition]] = None


class BulkMessageIn(BulkMessageFilters):
    """
    Payload para envio de mensagens em massa.
    """
    text: str
    parse_mode: str = "MarkdownV2"
    dry_run: bool = False  # true = apenas simula/prevê alcance, sem enviar


class BulkFlowStartIn(BulkMessageFilters):
    """
    Payload para iniciar um fluxo em massa para um segmento de contatos.
    """
    flow_id: Optional[int] = None
    dry_run: bool = False


def _parse_iso_date_or_datetime(value: str) -> datetime:
    """Aceita 'YYYY-MM-DD' ou ISO datetime; retorna datetime."""
    raw = (value or "").strip()
    if not raw:
        raise ValueError("data vazia")
    # datetime.fromisoformat não aceita 'Z' em algumas versões
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"

    if len(raw) == 10 and raw[4] == "-" and raw[7] == "-":
        d = date.fromisoformat(raw)
        return datetime(d.year, d.month, d.day)

    return datetime.fromisoformat(raw)


def _normalize_str_list(values: Optional[List[str]]) -> List[str]:
    if not values:
        return []
    return [v.strip() for v in values if isinstance(v, str) and v.strip()]


def _normalize_int_list(values: Optional[List[int]]) -> List[int]:
    if not values:
        return []
    out: List[int] = []
    for v in values:
        try:
            iv = int(v)
        except Exception:
            continue
        if iv > 0:
            out.append(iv)
    # Dedup mantendo ordem
    seen = set()
    dedup: List[int] = []
    for iv in out:
        if iv in seen:
            continue
        seen.add(iv)
        dedup.append(iv)
    return dedup


def _mssql_json_path(key: str) -> str:
    # JSON_VALUE/JSON_QUERY usa path no formato $."key"; escapamos aspas
    safe = (key or "").replace('"', '\\"')
    return f'$."{safe}"'


def _build_field_condition_expr(cond: "FieldCondition", tenant: Tenant, db: Session):
    """Converte FieldCondition em expressão SQLAlchemy.

    Suporte exclusivo para SQL Server (JSON_VALUE/JSON_QUERY).
    """
    field = (cond.field or "").strip()
    if not field:
        raise HTTPException(status_code=400, detail="Condição de campo inválida: field vazio.")

    op = cond.op
    value_type = cond.value_type
    value = cond.value

    # Campo do sistema
    system_map = {
        "id": Contact.id,
        "first_name": Contact.first_name,
        "last_name": Contact.last_name,
        "username": Contact.username,
        "default_channel_id": Contact.default_channel_id,
        "created_at": Contact.created_at,
    }

    if cond.source == "system":
        col = system_map.get(field)
        if col is None:
            raise HTTPException(status_code=400, detail=f"Campo do sistema não suportado: {field}.")
        return _apply_op_to_expr(col, op=op, value=value, value_type=value_type)

    # Campo personalizado (JSON)
    path = _mssql_json_path(field)

    # Normaliza custom_fields para lidar com registros onde o JSON foi salvo como string (dupla serialização).
    # Ex: custom_fields = '"{\"cidade\":\"Belo Horizonte\"}"'
    # SQL Server: quando raiz é string, JSON_VALUE(cf,'$') retorna o conteúdo interno.
    dialect = None
    try:
        dialect = (db.get_bind().dialect.name or "").lower()
    except Exception:
        dialect = None
    if dialect != "mssql":
        raise HTTPException(status_code=500, detail="Somente SQL Server é suportado para filtros por campos.")

    custom_json = case(
        # JSON objeto normal
        (
            (func.ISJSON(Contact.custom_fields) == 1)
            & (func.JSON_QUERY(Contact.custom_fields, "$").isnot(None)),
            Contact.custom_fields,
        ),
        # JSON duplamente serializado (raiz string contendo JSON)
        (
            (func.ISJSON(Contact.custom_fields) == 1)
            & (func.JSON_VALUE(Contact.custom_fields, "$").isnot(None))
            & (func.ISJSON(func.JSON_VALUE(Contact.custom_fields, "$")) == 1),
            func.JSON_VALUE(Contact.custom_fields, "$"),
        ),
        else_=None,
    )

    extracted_value = func.JSON_VALUE(custom_json, path)
    extracted_query = func.JSON_QUERY(custom_json, path)
    extracted = case(
        (extracted_value.isnot(None), extracted_value),
        (extracted_query.isnot(None), extracted_query),
        else_=None,
    )

    exists_expr = or_(extracted_value.isnot(None), extracted_query.isnot(None))

    if op == "exists":
        return exists_expr
    if op == "not_exists":
        return ~exists_expr

    return _apply_op_to_expr(extracted, op=op, value=value, value_type=value_type, is_json=True)


def _apply_op_to_expr(expr, op: str, value: Optional[str], value_type: str, is_json: bool = False):
    # Operações que não dependem de value
    if op == "is_empty":
        # vazio = null ou string vazia
        return or_(expr.is_(None), cast(expr, String) == "")
    if op == "is_not_empty":
        return or_(expr.isnot(None), cast(expr, String) != "")

    if value is None:
        # para ops que exigem value
        if op in ("eq", "neq", "contains", "not_contains", "starts_with", "ends_with", "gt", "gte", "lt", "lte"):
            raise HTTPException(status_code=400, detail="Condição de campo inválida: value ausente.")

    # Comparações por tipo
    if value_type == "number":
        try:
            num = float(value)
        except Exception:
            raise HTTPException(status_code=400, detail="Condição de campo inválida: value number.")
        left = cast(expr, Float) if is_json else expr
        if op == "eq":
            return left == num
        if op == "neq":
            return left != num
        if op == "gt":
            return left > num
        if op == "gte":
            return left >= num
        if op == "lt":
            return left < num
        if op == "lte":
            return left <= num
        raise HTTPException(status_code=400, detail=f"Operador não suportado para number: {op}.")

    if value_type == "date":
        # Aceita YYYY-MM-DD
        try:
            dt = _parse_iso_date_or_datetime(value)
        except Exception:
            raise HTTPException(status_code=400, detail="Condição de campo inválida: value date.")
        # Para JSON, comparar como string ISO (armazenado como texto no JSON)
        left = cast(expr, String) if is_json else expr
        iso = dt.date().isoformat()
        if op == "eq":
            return left == iso
        if op == "neq":
            return left != iso
        if op == "gt":
            return left > iso
        if op == "gte":
            return left >= iso
        if op == "lt":
            return left < iso
        if op == "lte":
            return left <= iso
        raise HTTPException(status_code=400, detail=f"Operador não suportado para date: {op}.")

    if value_type == "boolean":
        normalized = str(value).strip().lower()
        if normalized in ("true", "1", "sim", "yes", "y"):
            b = True
        elif normalized in ("false", "0", "não", "nao", "no", "n"):
            b = False
        else:
            raise HTTPException(status_code=400, detail="Condição de campo inválida: value boolean.")
        left = cast(expr, String) if is_json else expr
        # JSON booleans normalmente aparecem como 'true'/'false' no JSON_VALUE
        if op == "eq":
            return or_(left == ("true" if b else "false"), left == ("1" if b else "0"), left == (1 if b else 0))
        if op == "neq":
            return ~or_(left == ("true" if b else "false"), left == ("1" if b else "0"), left == (1 if b else 0))
        raise HTTPException(status_code=400, detail=f"Operador não suportado para boolean: {op}.")

    # string (padrão)
    s = str(value)
    left = cast(expr, String) if is_json else expr
    if op == "eq":
        return left == s
    if op == "neq":
        return left != s
    if op == "contains":
        return left.ilike(f"%{s}%")
    if op == "not_contains":
        return ~left.ilike(f"%{s}%")
    if op == "starts_with":
        return left.ilike(f"{s}%")
    if op == "ends_with":
        return left.ilike(f"%{s}")
    raise HTTPException(status_code=400, detail=f"Operador não suportado para string: {op}.")


def _apply_segment_filters(query, body: BulkMessageFilters, tenant: Tenant, db: Session):
    """Aplica filtros avançados (AND/OR) na query de contatos.

    Mantém compatibilidade com os campos antigos: search/channel_id/tags.
    """
    # Sempre filtrar por tenant antes
    query = query.filter(Contact.tenant_id == tenant.id)

    match_mode = getattr(body, "match_mode", "all") or "all"
    match_mode = match_mode if match_mode in ("all", "any") else "all"

    conditions = []

    # Busca
    if getattr(body, "search", None):
        search_term = f"%{body.search}%"
        conditions.append(
            or_(
                Contact.first_name.ilike(search_term),
                Contact.last_name.ilike(search_term),
                Contact.username.ilike(search_term),
            )
        )

    # Canal (compat + multi)
    channel_ids = _normalize_int_list(getattr(body, "channel_ids", None))
    if channel_ids:
        conditions.append(Contact.default_channel_id.in_(channel_ids))
    elif getattr(body, "channel_id", None):
        conditions.append(Contact.default_channel_id == body.channel_id)

    # Datas de criação
    created_after = getattr(body, "created_after", None)
    if created_after:
        try:
            dt = _parse_iso_date_or_datetime(created_after)
            conditions.append(Contact.created_at >= dt)
        except Exception:
            raise HTTPException(status_code=400, detail="created_after inválido (use YYYY-MM-DD ou ISO datetime).")

    created_before = getattr(body, "created_before", None)
    if created_before:
        try:
            dt = _parse_iso_date_or_datetime(created_before)
            conditions.append(Contact.created_at <= dt)
        except Exception:
            raise HTTPException(status_code=400, detail="created_before inválido (use YYYY-MM-DD ou ISO datetime).")

    # Tags (compat: tags => any)
    tags_any = _normalize_str_list(getattr(body, "tags_any", None))
    legacy_tags = _normalize_str_list(getattr(body, "tags", None))
    if not tags_any and legacy_tags:
        tags_any = legacy_tags

    if tags_any:
        tag_contact_ids = (
            db.query(ContactTag.contact_id)
            .filter(ContactTag.tenant_id == tenant.id, ContactTag.tag_name.in_(tags_any))
            .subquery()
        )
        conditions.append(Contact.id.in_(tag_contact_ids))

    tags_all = _normalize_str_list(getattr(body, "tags_all", None))
    if tags_all:
        tags_all_subq = (
            db.query(ContactTag.contact_id)
            .filter(ContactTag.tenant_id == tenant.id, ContactTag.tag_name.in_(tags_all))
            .group_by(ContactTag.contact_id)
            .having(func.count(func.distinct(ContactTag.tag_name)) >= len(set(tags_all)))
            .subquery()
        )
        conditions.append(Contact.id.in_(tags_all_subq))

    tags_exclude = _normalize_str_list(getattr(body, "tags_exclude", None))
    if tags_exclude:
        tags_exclude_subq = (
            db.query(ContactTag.contact_id)
            .filter(ContactTag.tenant_id == tenant.id, ContactTag.tag_name.in_(tags_exclude))
            .subquery()
        )
        conditions.append(~Contact.id.in_(tags_exclude_subq))

    # Última inbound em N dias
    last_inbound_days = getattr(body, "last_inbound_days", None)
    if last_inbound_days is not None:
        try:
            days = int(last_inbound_days)
        except Exception:
            raise HTTPException(status_code=400, detail="last_inbound_days inválido (inteiro).")
        if days < 0 or days > 3650:
            raise HTTPException(status_code=400, detail="last_inbound_days fora do intervalo permitido.")

        cutoff = datetime.utcnow() - timedelta(days=days)
        inbound_contact_ids = (
            db.query(Message.contact_id)
            .filter(
                Message.tenant_id == tenant.id,
                Message.direction == "inbound",
                Message.created_at >= cutoff,
            )
            .distinct()
            .subquery()
        )
        conditions.append(Contact.id.in_(inbound_contact_ids))

    # Condições por campos (sistema/custom)
    field_conditions = getattr(body, "field_conditions", None) or []
    if field_conditions:
        for fc in field_conditions:
            try:
                conditions.append(_build_field_condition_expr(fc, tenant=tenant, db=db))
            except HTTPException:
                raise
            except Exception:
                raise HTTPException(status_code=400, detail="Condição de campo inválida.")

    if conditions:
        if match_mode == "any":
            query = query.filter(or_(*conditions))
        else:
            for cond in conditions:
                query = query.filter(cond)

    return query


@router.get("/stats", response_model=ContactStatsOut)
def get_contacts_stats(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Estatísticas para a tela de contatos (MVP).

    Retorna contagem total, por canal e por tag (para sidebar).
    """
    contacts_total = int(
        (db.query(func.count(Contact.id)).filter(Contact.tenant_id == tenant.id).scalar() or 0)
    )

    by_channel_rows = (
        db.query(
            Contact.default_channel_id.label('channel_id'),
            Channel.name.label('channel_name'),
            Channel.type.label('channel_type'),
            func.count(Contact.id).label('count'),
        )
        .outerjoin(Channel, Contact.default_channel_id == Channel.id)
        .filter(Contact.tenant_id == tenant.id)
        .group_by(Contact.default_channel_id, Channel.name, Channel.type)
        .order_by(func.count(Contact.id).desc())
        .all()
    )

    by_channel = [
        ChannelCountOut(
            channel_id=row.channel_id,
            channel_name=row.channel_name,
            channel_type=row.channel_type,
            count=int(row.count or 0),
        )
        for row in by_channel_rows
    ]

    by_tag_rows = (
        db.query(
            ContactTag.tag_name.label('name'),
            func.count(ContactTag.contact_id).label('count'),
        )
        .filter(ContactTag.tenant_id == tenant.id)
        .group_by(ContactTag.tag_name)
        .order_by(func.count(ContactTag.contact_id).desc())
        .all()
    )

    by_tag = [TagCountOut(name=row.name, count=int(row.count or 0)) for row in by_tag_rows]

    return ContactStatsOut(contacts_total=contacts_total, by_channel=by_channel, by_tag=by_tag)


@router.get("/field-stats", response_model=List[FieldPairCountOut])
def get_contacts_field_stats(
    limit: int = 60,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Retorna agregação simples de campos personalizados (key:value) para a sidebar (SQL Server)."""
    limit = max(1, min(int(limit or 60), 200))

    dialect = None
    try:
        dialect = (db.get_bind().dialect.name or "").lower()
    except Exception:
        dialect = None

    if not dialect:
        logger.warning("field-stats: não foi possível determinar o dialeto do banco; retornando vazio")
        return []

        if dialect != "mssql":
                logger.warning("field-stats: dialeto não suportado (somente mssql); retornando vazio")
                return []

        # SQL Server: usar JSON nativo. Também lida com custom_fields duplamente serializado,
        # ex: '"{\"cidade\":\"BH\"}"' — nesse caso JSON_VALUE(custom_fields,'$') retorna o JSON interno.
        sql = text(
            """
            WITH cf AS (
              SELECT
                CASE
                  WHEN ISJSON(c.custom_fields) = 1 AND JSON_QUERY(c.custom_fields, '$') IS NOT NULL
                    THEN c.custom_fields
                  WHEN ISJSON(c.custom_fields) = 1
                       AND JSON_VALUE(c.custom_fields, '$') IS NOT NULL
                       AND ISJSON(JSON_VALUE(c.custom_fields, '$')) = 1
                    THEN JSON_VALUE(c.custom_fields, '$')
                  ELSE NULL
                END AS cf_json
              FROM contacts c
              WHERE c.tenant_id = :tenant_id
                AND c.custom_fields IS NOT NULL
                AND LTRIM(RTRIM(c.custom_fields)) != ''
                AND ISJSON(c.custom_fields) = 1
            ), kv AS (
              SELECT
                je.[key] AS field,
                CASE
                  WHEN je.[type] = 1 THEN je.[value]
                  WHEN je.[type] IN (2, 5) THEN CAST(je.[value] AS NVARCHAR(4000))
                  WHEN je.[type] = 3 THEN 'true'
                  WHEN je.[type] = 4 THEN 'false'
                  ELSE NULL
                END AS value
              FROM cf
              CROSS APPLY OPENJSON(cf.cf_json) AS je
              WHERE cf.cf_json IS NOT NULL
                AND je.[key] IS NOT NULL
            )
            SELECT
              kv.field AS field,
              kv.value AS value,
              COUNT(*) AS count
            FROM kv
            WHERE kv.value IS NOT NULL AND kv.value != ''
            GROUP BY kv.field, kv.value
            ORDER BY COUNT(*) DESC
            OFFSET 0 ROWS FETCH NEXT :limit ROWS ONLY;
            """
        )

        try:
                rows = db.execute(sql, {"tenant_id": tenant.id, "limit": limit}).fetchall()
        except Exception as e:
                logger.warning(
                        f"field-stats: falha ao executar JSON no SQL Server, retornando vazio: {e}"
                )
                rows = []

        out: List[FieldPairCountOut] = []
        for row in rows:
                try:
                        out.append(
                                FieldPairCountOut(
                                        field=str(row.field),
                                        value=str(row.value),
                                        count=int(row.count or 0),
                                )
                        )
                except Exception:
                        continue
        return out


@router.get("/", response_model=ContactListOut)
def list_contacts(
    search: Optional[str] = None,
    channel_id: Optional[int] = None,
    tags: Optional[List[str]] = None,
    match_mode: Literal["all", "any"] = "all",
    field_conditions: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Lista todos os contatos
    
    Query params:
    - search: Busca por nome ou username
    - channel_id: Filtrar por canal
    - limit: Limite de resultados (padrão: 100)
    - offset: Offset para paginação
    """
    limit = max(1, min(int(limit or 100), 500))
    offset = max(0, int(offset or 0))

    query = db.query(
        Contact,
        Channel.name.label('channel_name'),
        Channel.type.label('channel_type')
    ).outerjoin(
        Channel, Contact.default_channel_id == Channel.id
    )

    # Parse field_conditions (JSON string)
    parsed_field_conditions: Optional[List[FieldCondition]] = None
    if field_conditions:
        try:
            raw = json.loads(field_conditions)
            if isinstance(raw, dict) and "field_conditions" in raw:
                raw = raw.get("field_conditions")
            if not isinstance(raw, list):
                raise ValueError("field_conditions must be a list")
            parsed_field_conditions = [FieldCondition.model_validate(item) for item in raw]
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=400, detail="field_conditions inválido (JSON).")

    # Reaproveita a lógica de segmentação avançada (inclui field_conditions)
    body = BulkMessageFilters(
        search=search,
        channel_id=channel_id,
        tags=tags,
        match_mode=match_mode or "all",
        field_conditions=parsed_field_conditions,
    )

    query = _apply_segment_filters(query, body=body, tenant=tenant, db=db)
    
    # Total (para paginação) com os mesmos filtros
    count_q = db.query(func.count(Contact.id))
    count_q = _apply_segment_filters(count_q, body=body, tenant=tenant, db=db)
    total = int(count_q.scalar() or 0)

    # Ordenar por mais recente
    query = query.order_by(Contact.id.desc())

    # Paginação
    results = query.limit(limit).offset(offset).all()
    
    # Formatar resultado
    contacts = []
    for contact, channel_name, channel_type in results:
        # Carregar tags do contato
        contact_tags = db.query(ContactTag.tag_name).filter(
            ContactTag.contact_id == contact.id
        ).all()
        tags_list = [tag[0] for tag in contact_tags]
        
        # Parse custom_fields se for string
        custom_fields_data = contact.custom_fields
        if isinstance(custom_fields_data, str):
            try:
                custom_fields_data = json.loads(custom_fields_data)
            except:
                custom_fields_data = {}
        elif not custom_fields_data:
            custom_fields_data = {}
        
        contact_dict = {
            'id': contact.id,
            'first_name': contact.first_name,
            'last_name': contact.last_name,
            'username': contact.username,
            'default_channel_id': contact.default_channel_id,
            'channel_name': channel_name,
            'channel_type': channel_type,
            'custom_fields': custom_fields_data,
            'tags': tags_list,
            'created_at': contact.created_at.isoformat() if contact.created_at else None
        }
        contacts.append(ContactOut(**contact_dict))
    
    return ContactListOut(items=contacts, total=total, limit=limit, offset=offset)


@router.delete("/{contact_id:int}")
def delete_contact(
    contact_id: int,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Exclui um contato e remove rastros principais (MVP).

    Remove:
    - mensagens
    - execuções de fluxo + logs
    - tags do contato
    - inscrições em sequências
    - o próprio contato
    """
    contact = (
        db.query(Contact)
        .filter(Contact.id == contact_id, Contact.tenant_id == tenant.id)
        .first()
    )
    if not contact:
        raise HTTPException(status_code=404, detail="Contato não encontrado")

    # 1) Tags e sequências (independentes)
    db.query(ContactTag).filter(
        ContactTag.tenant_id == tenant.id,
        ContactTag.contact_id == contact_id,
    ).delete(synchronize_session=False)

    db.query(ContactSequence).filter(
        ContactSequence.tenant_id == tenant.id,
        ContactSequence.contact_id == contact_id,
    ).delete(synchronize_session=False)

    # 2) Mensagens (referenciam flow_executions)
    db.query(Message).filter(
        Message.tenant_id == tenant.id,
        Message.contact_id == contact_id,
    ).delete(synchronize_session=False)

    # 3) Logs de execução e execuções
    execution_ids = [
        row[0]
        for row in (
            db.query(FlowExecution.id)
            .filter(FlowExecution.tenant_id == tenant.id, FlowExecution.contact_id == contact_id)
            .all()
        )
    ]

    if execution_ids:
        db.query(FlowExecutionLog).filter(
            FlowExecutionLog.flow_execution_id.in_(execution_ids)
        ).delete(synchronize_session=False)

    db.query(FlowExecution).filter(
        FlowExecution.tenant_id == tenant.id,
        FlowExecution.contact_id == contact_id,
    ).delete(synchronize_session=False)

    # 4) Contato
    db.delete(contact)
    db.commit()

    return {"deleted": True, "contact_id": contact_id}


@router.get("/{contact_id:int}", response_model=ContactOut)
def get_contact(
    contact_id: int,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """
    Obtém detalhes de um contato específico
    """
    result = db.query(
        Contact,
        Channel.name.label('channel_name'),
        Channel.type.label('channel_type')
    ).outerjoin(
        Channel, Contact.default_channel_id == Channel.id
    ).filter(Contact.id == contact_id, Contact.tenant_id == tenant.id).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Contato não encontrado")
    
    contact, channel_name, channel_type = result
    
    # Carregar tags do contato
    contact_tags = db.query(ContactTag.tag_name).filter(
        ContactTag.contact_id == contact.id
    ).all()
    tags_list = [tag[0] for tag in contact_tags]
    
    # Parse custom_fields se for string
    custom_fields_data = contact.custom_fields
    if isinstance(custom_fields_data, str):
        try:
            custom_fields_data = json.loads(custom_fields_data)
        except:
            custom_fields_data = {}
    elif not custom_fields_data:
        custom_fields_data = {}
    
    contact_dict = {
        'id': contact.id,
        'first_name': contact.first_name,
        'last_name': contact.last_name,
        'username': contact.username,
        'default_channel_id': contact.default_channel_id,
        'custom_fields': custom_fields_data,
        'tags': tags_list,
        'channel_name': channel_name,
        'channel_type': channel_type,
        'created_at': contact.created_at.isoformat() if contact.created_at else None
    }
    
    return ContactOut(**contact_dict)


@router.get("/{contact_id:int}/messages", response_model=List[MessageOut])
def list_contact_messages(
    contact_id: int,
    limit: int = 100,
    offset: int = 0,
    order: str = "desc",
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Lista todas as mensagens de um contato
    
    Retorna as mensagens em ordem cronológica (mais antigas primeiro)
    """
    # Verificar se o contato existe
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.tenant_id == tenant.id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contato não encontrado")
    
    limit = max(1, min(int(limit or 100), 500))
    offset = max(0, int(offset or 0))
    order = (order or "desc").lower().strip()
    if order not in ("asc", "desc"):
        order = "desc"

    q = db.query(Message).filter(
        Message.contact_id == contact_id,
        Message.tenant_id == tenant.id,
    )
    if order == "asc":
        q = q.order_by(Message.created_at.asc(), Message.id.asc())
    else:
        q = q.order_by(Message.created_at.desc(), Message.id.desc())

    messages = q.limit(limit).offset(offset).all()
    
    # Formatar resultado
    result = []
    for msg in messages:
        extra = None
        if msg.extra_data:
            try:
                extra = json.loads(msg.extra_data) if isinstance(msg.extra_data, str) else msg.extra_data
            except Exception:
                extra = None
        result.append(MessageOut(
            id=msg.id,
            direction=msg.direction,
            content=msg.content,
            message_type=msg.message_type,
            status=msg.status,
            external_id=msg.external_id,
            extra_data=extra,
            error_message=msg.error_message,
            flow_execution_id=msg.flow_execution_id,
            step_id=msg.step_id,
            created_at=msg.created_at.isoformat() if msg.created_at else None
        ))
    
    return result


@router.post("/{contact_id:int}/send-message")
def send_message_to_contact(
    contact_id: int,
    body: SendMessageIn,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """Envia uma mensagem de texto diretamente a um contato via Telegram."""
    from app.services.telegram_sender import send_telegram_message

    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.tenant_id == tenant.id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contato não encontrado")

    channel = db.query(Channel).filter(Channel.id == contact.default_channel_id).first()
    if not channel:
        raise HTTPException(status_code=400, detail="Contato não possui canal configurado")

    # Recuperar chat_id da última mensagem inbound
    last_inbound = db.query(Message).filter(
        Message.contact_id == contact_id,
        Message.direction == 'inbound'
    ).order_by(Message.id.desc()).first()

    if not last_inbound or not last_inbound.extra_data:
        raise HTTPException(status_code=400, detail="Contato ainda não interagiu com o bot.")

    try:
        extra = json.loads(last_inbound.extra_data) if isinstance(last_inbound.extra_data, str) else last_inbound.extra_data
        chat_id = extra.get('chat_id')
    except Exception:
        chat_id = None

    if not chat_id:
        raise HTTPException(status_code=400, detail="Não foi possível determinar o chat_id do contato.")

    try:
        cfg = json.loads(channel.config) if isinstance(channel.config, str) else (channel.config or {})
        bot_token = cfg.get('bot_token')
    except Exception:
        bot_token = None

    if not bot_token:
        raise HTTPException(status_code=500, detail="Token do bot não configurado no canal.")

    result = send_telegram_message(bot_token, chat_id, body.text, parse_mode=body.parse_mode)
    if result is None:
        raise HTTPException(status_code=502, detail="Falha ao enviar mensagem pelo Telegram.")

    # Salvar no BD
    msg = Message(
        tenant_id=tenant.id,
        contact_id=contact.id,
        channel_id=channel.id,
        direction='outbound',
        content=body.text,
        message_type='text',
        status='sent',
        extra_data=json.dumps({'chat_id': chat_id})
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    return MessageOut(
        id=msg.id,
        direction=msg.direction,
        content=msg.content,
        message_type=msg.message_type,
        status=msg.status,
        extra_data={'chat_id': chat_id},
        created_at=msg.created_at.isoformat() if msg.created_at else None
    )


@router.post("/bulk-send")
def send_bulk_message(
    body: BulkMessageIn,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """
    Envia uma mensagem de texto para um conjunto de contatos filtrados.

    - Reutiliza os mesmos filtros da listagem de contatos (search, channel_id, tags)
    - Quando dry_run=True, apenas retorna a quantidade de contatos impactados
    """
    from app.services.telegram_sender import send_telegram_message

    # Construir query base (reaproveitando filtros avançados)
    query = _apply_segment_filters(db.query(Contact), body=body, tenant=tenant, db=db)

    contacts: List[Contact] = query.all()
    total = len(contacts)

    # Apenas previsão de alcance
    if body.dry_run:
        sample = [
            {
                "id": c.id,
                "username": c.username,
                "first_name": c.first_name,
                "last_name": c.last_name,
            }
            for c in contacts[:20]
        ]
        return {"total": total, "sample": sample}

    if total == 0:
        return {"total": 0, "sent": 0, "failed": 0, "errors": []}

    # Limite de segurança para evitar estouro em um único request HTTP
    MAX_BULK_SEND = 2000
    if total > MAX_BULK_SEND:
        raise HTTPException(
            status_code=400,
            detail=f"Segmento muito grande ({total} contatos). Refine os filtros ou reduza o público (limite {MAX_BULK_SEND}).",
        )

    sent = 0
    failed = 0
    errors: List[dict] = []

    for contact in contacts:
        try:
            channel = db.query(Channel).filter(Channel.id == contact.default_channel_id).first()
            if not channel:
                failed += 1
                errors.append({"contact_id": contact.id, "reason": "Canal não configurado"})
                continue

            last_inbound = (
                db.query(Message)
                .filter(
                    Message.contact_id == contact.id,
                    Message.direction == "inbound",
                )
                .order_by(Message.id.desc())
                .first()
            )
            if not last_inbound or not last_inbound.extra_data:
                failed += 1
                errors.append({"contact_id": contact.id, "reason": "Contato ainda não interagiu com o bot"})
                continue

            try:
                extra = (
                    json.loads(last_inbound.extra_data)
                    if isinstance(last_inbound.extra_data, str)
                    else last_inbound.extra_data
                )
                chat_id = extra.get("chat_id")
            except Exception:
                chat_id = None

            if not chat_id:
                failed += 1
                errors.append({"contact_id": contact.id, "reason": "chat_id não encontrado"})
                continue

            try:
                cfg = json.loads(channel.config) if isinstance(channel.config, str) else (channel.config or {})
                bot_token = cfg.get("bot_token")
            except Exception:
                bot_token = None

            if not bot_token:
                failed += 1
                errors.append({"contact_id": contact.id, "reason": "Token do bot não configurado no canal"})
                continue

            result = send_telegram_message(bot_token, chat_id, body.text, parse_mode=body.parse_mode)
            if result is None:
                failed += 1
                errors.append({"contact_id": contact.id, "reason": "Falha ao enviar pelo Telegram"})
                continue

            msg = Message(
                tenant_id=tenant.id,
                contact_id=contact.id,
                channel_id=channel.id,
                direction="outbound",
                content=body.text,
                message_type="text",
                status="sent",
                extra_data=json.dumps({"chat_id": chat_id}),
            )
            db.add(msg)
            sent += 1

        except Exception as e:
            failed += 1
            errors.append({"contact_id": contact.id, "reason": str(e)})

    db.commit()

    return {
        "total": total,
        "sent": sent,
        "failed": failed,
        "errors": errors,
    }


@router.post("/bulk-start-flow")
def bulk_start_flow(
    body: BulkFlowStartIn,
    background_tasks: BackgroundTasks,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """
    Inicia um fluxo para um conjunto de contatos filtrados.

    Usa os mesmos filtros da listagem de contatos (search, channel_id, tags).
    Quando dry_run=True, apenas retorna a quantidade de contatos impactados.
    """
    # Reaproveitar lógica de filtros (avançada)
    query = _apply_segment_filters(db.query(Contact), body=body, tenant=tenant, db=db)

    contacts: List[Contact] = query.all()
    total = len(contacts)

    if body.dry_run:
        sample = [
            {
                "id": c.id,
                "username": c.username,
                "first_name": c.first_name,
                "last_name": c.last_name,
            }
            for c in contacts[:20]
        ]
        return {"total": total, "sample": sample}

    if not body.flow_id:
        raise HTTPException(status_code=400, detail="flow_id é obrigatório para disparar (dry_run=false).")

    if total == 0:
        return {"total": 0, "started": 0, "failed": 0, "errors": []}

    MAX_BULK_START = 2000
    if total > MAX_BULK_START:
        raise HTTPException(
            status_code=400,
            detail=f"Segmento muito grande ({total} contatos). Refine os filtros ou reduza o público (limite {MAX_BULK_START}).",
        )

    started = 0
    failed = 0
    errors: List[dict] = []

    for contact in contacts:
        try:
            # Reutilizar a função existente de start_flow_for_contact para manter a lógica centralizada
            _ = start_flow_for_contact(
                contact_id=contact.id,
                flow_id=body.flow_id,
                background_tasks=background_tasks,
                tenant=tenant,
                db=db,
            )
            started += 1
        except HTTPException as e:
            failed += 1
            errors.append({"contact_id": contact.id, "reason": e.detail})
        except Exception as e:
            failed += 1
            errors.append({"contact_id": contact.id, "reason": str(e)})

    return {
        "total": total,
        "started": started,
        "failed": failed,
        "errors": errors,
    }

@router.post("/{contact_id:int}/send-media")
async def send_media_to_contact(
    contact_id: int,
    file: UploadFile = File(...),
    media_type: str = Form("auto"),
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """Envia uma mídia (foto, vídeo, áudio, vídeo-nota circular) diretamente a um contato via Telegram."""
    import os
    import uuid
    import shutil
    from app.services.telegram_sender import (
        send_telegram_photo, send_telegram_video,
        send_telegram_audio, send_telegram_video_note
    )

    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.tenant_id == tenant.id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contato não encontrado")

    channel = db.query(Channel).filter(Channel.id == contact.default_channel_id).first()
    if not channel:
        raise HTTPException(status_code=400, detail="Contato não possui canal configurado")

    last_inbound = db.query(Message).filter(
        Message.contact_id == contact_id,
        Message.direction == 'inbound'
    ).order_by(Message.id.desc()).first()

    if not last_inbound or not last_inbound.extra_data:
        raise HTTPException(status_code=400, detail="Contato ainda não interagiu com o bot.")

    try:
        extra = json.loads(last_inbound.extra_data) if isinstance(last_inbound.extra_data, str) else last_inbound.extra_data
        chat_id = extra.get('chat_id')
    except Exception:
        chat_id = None

    if not chat_id:
        raise HTTPException(status_code=400, detail="Não foi possível determinar o chat_id do contato.")

    try:
        cfg = json.loads(channel.config) if isinstance(channel.config, str) else (channel.config or {})
        bot_token = cfg.get('bot_token')
    except Exception:
        bot_token = None

    if not bot_token:
        raise HTTPException(status_code=500, detail="Token do bot não configurado no canal.")

    # Detectar tipo pelo Content-Type se 'auto'
    content_type = file.content_type or ''
    if media_type == 'auto':
        if content_type.startswith('image/'):
            media_type = 'photo'
        elif content_type.startswith('video/'):
            media_type = 'video'
        elif content_type.startswith('audio/'):
            media_type = 'audio'
        else:
            raise HTTPException(status_code=400, detail=f"Tipo de mídia não suportado: {content_type}")

    upload_dirs = {
        'photo': 'uploads/images',
        'video': 'uploads/video',
        'video_note': 'uploads/video',
        'audio': 'uploads/audio',
    }
    upload_dir = upload_dirs.get(media_type)
    if not upload_dir:
        raise HTTPException(status_code=400, detail=f"Tipo de mídia inválido: {media_type}")

    original_ext = os.path.splitext(file.filename or 'file')[1] or ''
    unique_name = f"{uuid.uuid4().hex}{original_ext}"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = f"{upload_dir}/{unique_name}"

    try:
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo: {e}")

    media_url_map = {
        'photo': f"/api/v1/media/images/{unique_name}",
        'video': f"/api/v1/media/video/{unique_name}",
        'video_note': f"/api/v1/media/video/{unique_name}",
        'audio': f"/api/v1/media/audio/{unique_name}",
    }
    local_url = media_url_map[media_type]

    result = None
    try:
        if media_type == 'photo':
            result = send_telegram_photo(bot_token, chat_id, local_url)
        elif media_type == 'video':
            result = send_telegram_video(bot_token, chat_id, local_url)
        elif media_type == 'video_note':
            result = send_telegram_video_note(bot_token, chat_id, local_url)
        elif media_type == 'audio':
            result = send_telegram_audio(bot_token, chat_id, local_url)
    except Exception as e:
        logger.error(f"❌ Erro ao enviar mídia Telegram: {e}")

    if result is None:
        try:
            os.remove(file_path)
        except Exception:
            pass
        raise HTTPException(status_code=502, detail="Falha ao enviar mídia pelo Telegram.")

    msg = Message(
        tenant_id=tenant.id,
        contact_id=contact.id,
        channel_id=channel.id,
        direction='outbound',
        content=file.filename or unique_name,
        message_type=media_type,
        status='sent',
        extra_data=json.dumps({
            'chat_id': chat_id,
            'file_name': unique_name,
            'media_url': local_url
        })
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    return MessageOut(
        id=msg.id,
        direction=msg.direction,
        content=msg.content,
        message_type=msg.message_type,
        status=msg.status,
        extra_data={'chat_id': chat_id, 'file_name': unique_name, 'media_url': local_url},
        created_at=msg.created_at.isoformat() if msg.created_at else None
    )


@router.post("/{contact_id:int}/start-flow/{flow_id:int}")
def start_flow_for_contact(
    contact_id: int,
    flow_id: int,
    background_tasks: BackgroundTasks,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Inicia um fluxo manualmente para um contato específico
    """
    logger.info(f"🚀 Iniciando fluxo manual: contact_id={contact_id}, flow_id={flow_id}")
    
    # Buscar contato
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.tenant_id == tenant.id).first()
    if not contact:
        logger.error(f"❌ Contato {contact_id} não encontrado")
        raise HTTPException(status_code=404, detail="Contato não encontrado")
    
    logger.info(f"✓ Contato encontrado: {contact.first_name} (ID: {contact.id})")
    
    # Buscar fluxo
    flow = db.query(Flow).filter(Flow.id == flow_id).first()
    if not flow:
        logger.error(f"❌ Fluxo {flow_id} não encontrado")
        raise HTTPException(status_code=404, detail="Fluxo não encontrado")
    
    logger.info(f"✓ Fluxo encontrado: {flow.name} (ID: {flow.id})")
    
    if not flow.is_active:
        logger.error(f"❌ Fluxo {flow.name} não está ativo")
        raise HTTPException(status_code=400, detail="Fluxo não está ativo")
    
    logger.info(f"✓ Fluxo está ativo")
    
    # Buscar canal do contato
    channel = db.query(Channel).filter(Channel.id == contact.default_channel_id).first()
    if not channel:
        logger.error(f"❌ Contato não possui canal configurado (default_channel_id: {contact.default_channel_id})")
        raise HTTPException(status_code=400, detail="Contato não possui canal configurado")
    
    logger.info(f"✓ Canal encontrado: {channel.name} (ID: {channel.id})")
    
    # Buscar chat_id da última mensagem INBOUND (recebida do usuário)
    logger.info(f"🔍 Buscando última mensagem INBOUND para contact_id={contact_id}")
    
    last_message = db.query(Message).filter(
        Message.contact_id == contact_id,
        Message.direction == 'inbound'  # 🔥 CRÍTICO: Apenas mensagens recebidas!
    ).order_by(Message.id.desc()).first()
    
    if not last_message:
        logger.error(f"❌ Nenhuma mensagem INBOUND encontrada para contact_id={contact_id}")
        raise HTTPException(
            status_code=400, 
            detail="Este contato ainda não interagiu com o bot. É necessário que o contato envie pelo menos uma mensagem antes de iniciar um fluxo manualmente."
        )
    
    logger.info(f"✓ Última mensagem INBOUND encontrada: ID={last_message.id}")
    logger.info(f"  extra_data: {last_message.extra_data}")
    
    # Extrair chat_id do extra_data da mensagem
    chat_id = None
    if last_message.extra_data:
        try:
            extra_data = json.loads(last_message.extra_data) if isinstance(last_message.extra_data, str) else last_message.extra_data
            chat_id = extra_data.get('chat_id')
            logger.info(f"✓ chat_id extraído do extra_data: {chat_id}")
        except Exception as e:
            logger.error(f"❌ Erro ao extrair chat_id do extra_data: {e}")
    else:
        logger.warning(f"⚠️  extra_data está vazio na mensagem INBOUND ID={last_message.id}")
        logger.info(f"💡 Isso significa que a mensagem foi criada antes da implementação do chat_id")
    
    if not chat_id:
        logger.error(f"❌ chat_id não encontrado. extra_data={last_message.extra_data}")
        raise HTTPException(
            status_code=400,
            detail="Não foi possível determinar o chat_id do contato. Por favor, peça ao contato para enviar uma nova mensagem ao bot para atualizar o registro."
        )
    
    # Extrair bot_token do config do canal
    try:
        channel_config = json.loads(channel.config) if isinstance(channel.config, str) else channel.config
        bot_token = channel_config.get("bot_token")
        
        if not bot_token:
            logger.error(f"❌ bot_token não encontrado no config do canal ID={channel.id}")
            raise HTTPException(status_code=500, detail="Configuração do canal está incompleta (bot_token não encontrado)")
        
        logger.info(f"✓ bot_token encontrado")
    except Exception as e:
        logger.error(f"❌ Erro ao extrair bot_token do config: {e}")
        raise HTTPException(status_code=500, detail="Erro ao processar configuração do canal")
    
    # Registrar execução do fluxo
    flow_execution = FlowExecution(
        tenant_id=tenant.id,
        contact_id=contact.id,
        flow_id=flow.id,
        trigger_type='manual',
        status='active'
    )
    db.add(flow_execution)
    db.commit()
    db.refresh(flow_execution)
    
    logger.info(f"✓ Execução registrada: FlowExecution ID={flow_execution.id}")
    
    # Importar função de execução de fluxo
    from app.api.v1.routers.telegram import run_flow_background
    
    # Executar fluxo em background
    background_tasks.add_task(
        run_flow_background,
        channel.id,
        contact.id,
        flow.id,
        chat_id,
        bot_token,
        flow_execution.id,  # Passar execution_id
        None  # start_from_step_id (None = começar do início)
    )
    
    logger.info(f"Fluxo '{flow.name}' (ID: {flow.id}) iniciado manualmente para contato '{contact.first_name}' (ID: {contact.id}), chat_id={chat_id}")
    
    return {
        "message": "Fluxo iniciado com sucesso",
        "contact_id": contact_id,
        "flow_id": flow_id,
        "flow_name": flow.name,
        "contact_name": f"{contact.first_name} {contact.last_name or ''}".strip(),
        "execution_id": flow_execution.id
    }


@router.get("/{contact_id:int}/flow-history")
def get_contact_flow_history(
    contact_id: int,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Retorna o histórico de fluxos executados para um contato
    """
    # Verificar contato pertence ao tenant
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.tenant_id == tenant.id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contato não encontrado")

    executions = db.query(
        FlowExecution.flow_id,
        Flow.name.label('flow_name'),
        func.count(FlowExecution.id).label('execution_count'),
        func.max(FlowExecution.started_at).label('last_execution')
    ).join(
        Flow, FlowExecution.flow_id == Flow.id
    ).filter(
        FlowExecution.contact_id == contact_id,
        FlowExecution.tenant_id == tenant.id,
    ).group_by(
        FlowExecution.flow_id,
        Flow.name
    ).all()
    
    result = []
    for execution in executions:
        result.append({
            "flow_id": execution.flow_id,
            "flow_name": execution.flow_name,
            "execution_count": execution.execution_count,
            "last_execution": execution.last_execution.isoformat() if execution.last_execution else None
        })
    
    return result


@router.post("/{contact_id:int}/tags", response_model=ContactOut)
def add_contact_tag(
    contact_id: int,
    payload: TagIn,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    tag_name = (payload.tag_name or '').strip()
    if not tag_name:
        raise HTTPException(status_code=400, detail="tag_name é obrigatório")

    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.tenant_id == tenant.id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contato não encontrado")

    db.add(ContactTag(tenant_id=tenant.id, contact_id=contact.id, tag_name=tag_name))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # tag já existe: ok
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar tag: {e}")

    return get_contact(contact_id=contact_id, tenant=tenant, db=db)


@router.delete("/{contact_id:int}/tags/{tag_name}", response_model=ContactOut)
def remove_contact_tag(
    contact_id: int,
    tag_name: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    tag_name = (tag_name or '').strip()
    if not tag_name:
        raise HTTPException(status_code=400, detail="tag_name é obrigatório")

    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.tenant_id == tenant.id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contato não encontrado")

    db.query(ContactTag).filter(
        ContactTag.tenant_id == tenant.id,
        ContactTag.contact_id == contact.id,
        ContactTag.tag_name == tag_name,
    ).delete(synchronize_session=False)
    db.commit()

    return get_contact(contact_id=contact_id, tenant=tenant, db=db)


@router.get("/ping")
def ping():
    return {"service": "contacts", "status": "ok"}
