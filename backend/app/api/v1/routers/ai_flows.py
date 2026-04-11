"""
Endpoint de geração de fluxos via IA (Claude).
POST /api/v1/flows/ai-generate
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import json
import logging

from sqlalchemy.orm import Session

from app.core.auth import get_current_tenant
from app.config import get_settings
from app.db.models import Tenant
from app.db.session import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


# ──────────────────────────────────────────────────────────────────────────────
# System prompt — descreve toda a estrutura de fluxos para o Claude
# ──────────────────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """Você é um especialista em criar fluxos de automação para chatbots no Telegram.
Sua tarefa é receber uma descrição em linguagem natural e gerar um JSON completo e válido de um fluxo.

## ESTRUTURA DO FLUXO

O fluxo é composto por dois campos principais:
1. `steps` — array de passos
2. `connections` — array de conexões entre passos

---

## TIPOS DE STEPS

### 1. trigger (SEMPRE o primeiro step, obrigatório)
```json
{
  "id": 1,
  "type": "trigger",
  "order_index": 1,
  "config": {
    "triggerType": "message",
    "keywords": ["oi", "olá", "inicio"]
  }
}
```
- `triggerType`: "message" (padrão) ou "telegram_ref_url"
- `keywords`: array de palavras-chave que ativam o fluxo (vazio = qualquer mensagem)

---

### 2. message (envia mensagens ao usuário)
```json
{
  "id": 2,
  "type": "message",
  "order_index": 2,
  "config": {
    "text": "Descrição interna do step",
    "blocks": [
      { "id": "b1", "type": "text", "text": "Olá! Como posso ajudar?" },
      {
        "id": "b2",
        "type": "button",
        "text": "Escolha uma opção:",
        "buttons": [
          { "text": "Opção A", "action": "flow", "targetStepId": 3 },
          { "text": "Saiba mais", "action": "url", "url": "https://exemplo.com" }
        ]
      }
    ]
  }
}
```

**Tipos de blocks dentro de message:**
- `text`: `{ "id": "bX", "type": "text", "text": "conteúdo" }`
- `button`: `{ "id": "bX", "type": "button", "text": "texto acima", "buttons": [{ "text": "label", "action": "flow", "targetStepId": N }] }`
- `image`: `{ "id": "bX", "type": "image", "url": "https://...", "caption": "legenda" }`
- `delay`: `{ "id": "bX", "type": "delay", "seconds": 2 }` (simula digitação)
- `data`: **USE ESTE para coletar dados do usuário** — envia o prompt e pausa o fluxo aguardando a resposta, salvando-a no campo especificado.
  ```json
  { "id": "bX", "type": "data", "field": "nome_do_campo", "prompt": "Qual é o seu nome?" }
  ```
  - `field`: nome do campo personalizado onde a resposta será salva (ex: `"horario"`, `"data_agendamento"`, `"nome"`, `"email"`)
  - `prompt`: mensagem enviada ao usuário pedindo a informação

**REGRA IMPORTANTE — quando coletar dados do usuário:**
- Use **sempre** o bloco `data` dentro de um step `message` quando precisar pedir e salvar uma informação digitada pelo usuário.
- **NÃO** use `action set_field com field_value: "{ultima_mensagem}"` para coletar dados — use o bloco `data`.
- O bloco `data` automaticamente pausa o fluxo, aguarda a resposta e salva no campo. O próximo step só executa após o usuário responder.
- Exemplo correto para coletar horário:
  ```json
  {
    "id": "b1", "type": "text", "text": "Perfeito! Agora me informe o horário desejado."
  },
  {
    "id": "b2", "type": "data", "field": "horario_agendamento", "prompt": "Digite o horário no formato HH:MM (ex: 14:30)"
  }
  ```

Para botões de navegação interna: `"action": "flow"` com `"targetStepId": id_do_step_destino`
Para links externos: `"action": "url"` com `"url": "https://..."`

---

### 3. action (executa ações no sistema)
```json
{
  "id": 3,
  "type": "action",
  "order_index": 3,
  "config": {
    "actions": [
      { "type": "set_field", "field_name": "plano", "field_value": "pro" },
      { "type": "add_tag", "tag_name": "cliente-pro" },
      { "type": "remove_tag", "tag_name": "lead" },
      { "type": "smart_delay", "delay_value": 1, "delay_unit": "minutes" },
      { "type": "webhook", "webhook_url": "https://...", "method": "POST" },
      { "type": "notify_admin", "notification_message": "Novo lead!", "notify_tag": "vendas" }
    ]
  }
}
```

**Tipos de actions:**
- `set_field`: salva valor em campo do contato
  - **Campos do sistema** (atualizam o perfil nativo): `first_name`, `last_name`, `username`
    - Exemplo: `{ "type": "set_field", "field_name": "first_name", "field_value": "{ultima_mensagem}" }`
  - **Campos personalizados** (qualquer outro nome): armazenados como atributos extras do contato
    - Exemplo: `{ "type": "set_field", "field_name": "plano", "field_value": "pro" }`
  - Para capturar a resposta do usuário, prefira o bloco `data` dentro de um step `message` em vez de `set_field` com `{ultima_mensagem}`
- `add_tag`: adiciona tag ao contato
- `remove_tag`: remove tag do contato
- `smart_delay`: pausa a execução — use SEMPRE `delay_value` (número) e `delay_unit` ("seconds"|"minutes"|"hours"|"days")
  - Exemplo: `{ "type": "smart_delay", "delay_value": 2, "delay_unit": "minutes" }`
- `webhook`: chama URL externa
- `notify_admin`: notifica equipe interna

---

### 4. condition (bifurca o fluxo em verdadeiro/falso)
```json
{
  "id": 4,
  "type": "condition",
  "order_index": 4,
  "config": {
    "conditionType": "field",
    "field": "plano",
    "operator": "equals",
    "value": "pro"
  }
}
```

**Tipos de condition:**
- `conditionType: "field"`: compara campo personalizado
  - `operator`: "equals" | "not_equals" | "contains" | "not_contains" | "exists" | "not_exists" | "greater_than" | "less_than"
- `conditionType: "tag"`: verifica se contato tem tag
  - `tag`: nome da tag

**Connections para condition:** usa `outputId: "true"` e `outputId: "false"`

---

### 5. wait (aguarda resposta ou tempo)
```json
{
  "id": 5,
  "type": "wait",
  "order_index": 5,
  "config": {
    "delayType": "fixed",
    "value": 24,
    "unit": "hours"
  }
}
```

**IMPORTANTE — nomes exatos dos campos do config de `wait`:**
- `delayType` (camelCase): `"fixed"` | `"random"` | `"smart"` — NUNCA use `delay_type`
- `value` (não `delay_value`): número inteiro
- `unit` (não `delay_unit`): `"seconds"` | `"minutes"` | `"hours"` | `"days"`

---

### 6. randomizer (distribui tráfego - A/B test)
```json
{
  "id": 6,
  "type": "randomizer",
  "order_index": 6,
  "config": {
    "paths": [
      { "id": "path-a", "name": "Versão A", "percentage": 50 },
      { "id": "path-b", "name": "Versão B", "percentage": 50 }
    ]
  }
}
```
**Connections para randomizer:** usa `outputId: "path-a"`, `outputId: "path-b"` etc.

---

## CONNECTIONS

```json
{
  "id": "1-default-2",
  "from": 1,
  "to": 2,
  "outputId": "default"
}
```

**Regras de outputId:**
- Steps normais (message, action, wait, trigger): `"outputId": "default"`
- Condition true: `"outputId": "true"`
- Condition false: `"outputId": "false"`
- Botão específico: `"outputId": "btn-{block_id}-{button_index}"` — use quando um botão deve redirecionar para step diferente do fluxo principal
- Randomizer: `"outputId": "{path_id}"` (ex: "path-a", "path-b")

**IMPORTANTE:** Quando um button block tem `"action": "flow"` com `"targetStepId"`, a conexão entre o step do botão e o destino deve ter `outputId: "btn-{block_id}-{button_index}"`.

---

## POSICIONAMENTO (nodePositions)

Distribua os steps em um grid lógico:
- Trigger: x=80, y=120
- Cada step seguinte: incremente x em +320 (fluxo horizontal) ou y em +200 (ramificações)
- Branches (condition true/false): use y diferente para cada caminho

---

## FORMATO DE RESPOSTA

Responda APENAS com um JSON válido, sem markdown, sem explicações:

```json
{
  "name": "Nome sugestivo do fluxo",
  "description": "Descrição breve do que o fluxo faz",
  "trigger_type": "keyword",
  "steps": [...],
  "connections": [...],
  "nodePositions": {
    "1": { "x": 80, "y": 120 },
    "2": { "x": 400, "y": 120 }
  }
}
```

## REGRAS IMPORTANTES

1. IDs de steps são inteiros sequenciais começando em 1
2. O step com `type: "trigger"` DEVE ser o primeiro (id=1, order_index=1)
3. Cada step deve ter um ID único
4. Connections devem referenciar apenas IDs existentes
5. IDs de blocks dentro de message devem ser únicos (use "b1", "b2", etc.)
6. Para fluxos com coleta de dados (nome, email), use steps message com text block perguntando, seguidos de steps action com set_field após a resposta
7. Sempre crie um fluxo completo — não deixe steps sem conexão (exceto o último step de cada caminho)
8. Se o usuário pedir coleta de campo (nome, email, etc.), use a sequência: message perguntando → (implícito: bot aguarda resposta → set_field automaticamente)
9. Mantenha o fluxo focado e prático — máximo de 12 steps para fluxos simples
"""


# ──────────────────────────────────────────────────────────────────────────────
# Schemas
# ──────────────────────────────────────────────────────────────────────────────

class AIFlowGenerateIn(BaseModel):
    prompt: str
    flow_id: Optional[int] = None  # se fornecido, sobrescreve fluxo existente


class AIFlowGenerateOut(BaseModel):
    name: str
    description: str
    trigger_type: str
    steps: list
    connections: list
    node_positions: dict


# ──────────────────────────────────────────────────────────────────────────────
# Endpoint
# ──────────────────────────────────────────────────────────────────────────────

@router.post("/ai-generate", response_model=AIFlowGenerateOut)
def generate_flow_with_ai(
    body: AIFlowGenerateIn,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """
    Gera um fluxo completo a partir de um prompt em linguagem natural usando Claude.
    """
    # Salva o que precisamos e libera a conexão DB *antes* da chamada ao Claude.
    # Sem isso, a sessão fica aberta durante os ~30s da API externa e o SQL Server
    # mata a conexão TCP ociosa, causando erros 10060 nos requests seguintes.
    tenant_id = tenant.id
    db.close()

    settings = get_settings()
    api_key = settings.ANTHROPIC_API_KEY
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="ANTHROPIC_API_KEY não configurada. Adicione ao arquivo .env do backend."
        )

    try:
        import anthropic
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="Pacote 'anthropic' não instalado. Execute: pip install anthropic"
        )

    prompt_text = (body.prompt or "").strip()
    if not prompt_text:
        raise HTTPException(status_code=400, detail="Prompt não pode estar vazio.")
    if len(prompt_text) > 2000:
        raise HTTPException(status_code=400, detail="Prompt muito longo (máx 2000 caracteres).")

    logger.info("ai_generate: tenant=%s prompt=%r", tenant_id, prompt_text[:80])

    client = anthropic.Anthropic(api_key=api_key)

    try:
        message = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=8000,
            system=_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Crie um fluxo de chatbot para o seguinte objetivo:\n\n{prompt_text}\n\n"
                        "Responda APENAS com o JSON válido, sem markdown nem explicações."
                    )
                }
            ]
        )
    except Exception as e:
        logger.error("ai_generate: erro na API Anthropic: %s", e)
        raise HTTPException(status_code=502, detail=f"Erro ao chamar a API de IA: {e}")

    raw = message.content[0].text.strip()

    # Remove possíveis markdown code fences se o modelo insistir
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:])
        if raw.endswith("```"):
            raw = raw[:-3].strip()

    try:
        data = json.loads(raw)
    except Exception:
        logger.error("ai_generate: JSON inválido retornado: %r", raw[:300])
        raise HTTPException(
            status_code=502,
            detail="A IA retornou um JSON inválido. Tente reformular o prompt."
        )

    # Validação mínima
    steps = data.get("steps")
    connections = data.get("connections")
    if not isinstance(steps, list) or not steps:
        raise HTTPException(status_code=502, detail="A IA não gerou steps válidos. Tente novamente.")
    if not isinstance(connections, list):
        connections = []

    # Garante que step IDs sejam inteiros e order_index esteja preenchido
    for idx, step in enumerate(steps, start=1):
        if "id" not in step:
            step["id"] = idx
        else:
            try:
                step["id"] = int(step["id"])
            except Exception:
                step["id"] = idx
        if "order_index" not in step:
            step["order_index"] = idx
        if "config" not in step:
            step["config"] = {}

        # ── Normalizar config do step "wait" ─────────────────────────────────
        # A IA pode gerar snake_case (delay_type, delay_value, delay_unit)
        # mas o frontend espera camelCase (delayType, value, unit)
        if step["type"] == "wait":
            cfg = step["config"]
            if "delay_type" in cfg and "delayType" not in cfg:
                cfg["delayType"] = cfg.pop("delay_type")
            if "delay_value" in cfg and "value" not in cfg:
                cfg["value"] = cfg.pop("delay_value")
            if "delay_unit" in cfg and "unit" not in cfg:
                cfg["unit"] = cfg.pop("delay_unit")
            # Garantir defaults obrigatórios
            cfg.setdefault("delayType", "fixed")
            cfg.setdefault("value", 5)
            cfg.setdefault("unit", "minutes")

        # ── Normalizar ações smart_delay dentro de steps "action" ─────────────
        # A IA pode gerar "value"/"unit" em vez de "delay_value"/"delay_unit"
        if step["type"] == "action":
            for act in step["config"].get("actions", []):
                if act.get("type") == "smart_delay":
                    if "value" in act and "delay_value" not in act:
                        act["delay_value"] = act.pop("value")
                    if "unit" in act and "delay_unit" not in act:
                        act["delay_unit"] = act.pop("unit")
                    act.setdefault("delay_value", 1)
                    act.setdefault("delay_unit", "minutes")

    # Garante connection IDs
    for conn in connections:
        if "id" not in conn:
            conn["id"] = f"{conn.get('from')}-{conn.get('outputId','default')}-{conn.get('to')}"
        try:
            conn["from"] = int(conn["from"])
            conn["to"] = int(conn["to"])
        except Exception:
            pass

    node_positions = data.get("nodePositions", data.get("node_positions", {}))
    # Converte chaves para string (compatibilidade com frontend)
    node_positions = {str(k): v for k, v in node_positions.items()}

    # Gera posições padrão para steps sem posição
    existing_ids = set(node_positions.keys())
    x, y = 80, 120
    for step in steps:
        sid = str(step["id"])
        if sid not in existing_ids:
            node_positions[sid] = {"x": x, "y": y}
            x += 320

    logger.info(
        "ai_generate: fluxo gerado '%s' com %d steps e %d connections",
        data.get("name", "?"), len(steps), len(connections)
    )

    return AIFlowGenerateOut(
        name=data.get("name", "Fluxo Gerado por IA"),
        description=data.get("description", ""),
        trigger_type=data.get("trigger_type", "keyword"),
        steps=steps,
        connections=connections,
        node_positions=node_positions,
    )
