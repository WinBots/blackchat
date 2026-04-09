# WinChat / Blackchat Pro

Plataforma SaaS de automação de conversas via Telegram com CRM integrado, fluxos visuais, sequências e multi-tenancy.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | FastAPI + SQLAlchemy (Python 3.11) |
| Banco de dados | SQL Server (remoto: 185.237.253.115:1533) |
| Cache / Filas | Redis (Memurai em dev, Redis nativo em prod Ubuntu) |
| Worker de filas | ARQ (async Redis queue) |
| Frontend | Vue 3 + Vite (porta 3061) |
| Mensageria | Telegram Bot API (webhooks) |
| Email | SMTP Titan/HostGator |
| Pagamentos | Stripe |
| IA | Claude API (Anthropic) |

---

## Como rodar em desenvolvimento

Pré-requisitos: Python 3.11, Node.js, Memurai (Redis para Windows), ngrok (para webhooks Telegram).

```bash
# Terminal 1 — Backend
cd backend
set PYTHONPATH=%CD%
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8061
# ou: run_local.bat

# Terminal 2 — Worker ARQ (opcional — sem ele, tudo cai em fallback síncrono)
cd backend
set PYTHONPATH=%CD%
arq worker.WorkerSettings

# Terminal 3 — Frontend
cd frontend
npm run dev
```

**Variáveis de ambiente críticas** (`backend/.env`):
```
REDIS_URL=redis://127.0.0.1:6379/0   # Memurai local
DATABASE_URL=mssql+pyodbc://...       # SQL Server remoto
PUBLIC_BASE_URL=https://...ngrok...   # URL pública para webhooks
```

---

## Estrutura do projeto

```
backend/
  app/
    api/v1/routers/     # Endpoints FastAPI
      telegram.py       # Webhook handler + execução de fluxos (arquivo principal, ~2500 linhas)
      flows.py          # CRUD de fluxos e steps
      contacts.py       # CRM, bulk send
      auth.py           # Login, registro, reset de senha
      channels.py       # Gestão de canais Telegram
    db/
      models/           # SQLAlchemy models
      auto_migrate.py   # Migrações incrementais automáticas (roda no startup)
      session.py        # Pool de conexões SQL Server
    workers/
      arq_pool.py       # Pool ARQ singleton com fallback gracioso
      worker_settings.py # Jobs e WorkerSettings para ARQ
    cache/
      redis_client.py   # Cache Redis com fallback gracioso
    services/
      telegram_sender.py
      email_sender.py
      billing_service.py
  worker.py             # Entry point para arq CLI

frontend/
  src/
    views/              # Páginas Vue (LoginView, RegisterView, etc.)
    api/http.js         # Axios com interceptors de auth
    composables/        # useAuth, useToast
```

---

## Arquitetura de filas (ARQ)

Implementado em 5 fases. **Todos os pontos têm fallback síncrono** — se Redis estiver offline, o sistema continua funcionando como antes.

| Worker | Responsabilidade |
|---|---|
| `WebhookWorkerSettings` | Processa updates Telegram de forma assíncrona |
| `FlowWorkerSettings` | Executa fluxos via ARQ (usa run_in_executor) |
| `BulkWorkerSettings` | Bulk send em background com tracking de progresso |
| `SequenceWorkerSettings` | Sequências agendadas (cron a cada minuto) + emails |

Em desenvolvimento, use `arq worker.WorkerSettings` (processa todas as filas).

---

## Problema de performance em aberto — CRÍTICO

### Causa raiz identificada
O banco SQL Server está em servidor remoto com **207ms de latência** (ping confirmado). Cada query custa 207ms de round-trip de rede. O webhook handler faz ~5 queries antes de disparar o primeiro passo do fluxo → **~1 segundo de overhead só de latência de rede**, antes de qualquer mensagem ser enviada.

### O que já foi otimizado (sessão anterior)
Para reduzir o número de queries ao mínimo possível:

1. **N+1 eliminado no keyword matching** — de N+1 queries (1 por fluxo) para 2 queries fixas + lookup O(1) em dict. Função `_load_trigger_map()` em `telegram.py`.
2. **Cache em memória 30s do trigger_map** — rajadas de webhooks do mesmo tenant não vão ao banco.
3. **Busca de canal por webhook_secret** — coluna `channels.webhook_secret` desnormalizada e indexada. Query direta em vez de loop.
4. **Busca de contato por telegram_user_id** — coluna `contacts.telegram_user_id` indexada. Query direta em vez de LIKE em JSON.
5. **Commits agrupados** — `save_outbound_message` usa `db.flush()` em vez de `db.commit()` por mensagem.
6. **Novos índices compostos** — `flow_steps(flow_id, type)`, `flow_executions(contact_id, status)`, `contacts(tenant_id, telegram_user_id)`, `channels(webhook_secret)`.
7. **Backfill automático** — `auto_migrate.py` popula as novas colunas com dados existentes no startup.

### Solução definitiva pendente
**Mover o banco de dados para o mesmo servidor do backend (Ubuntu).**

Opções em ordem de impacto:
1. Instalar PostgreSQL no Ubuntu de produção e migrar os dados → latência < 1ms
2. Instalar SQL Server Express no Ubuntu e migrar → mantém mesmo engine
3. Mover o backend para o mesmo datacenter do banco → sem mudança de banco

Trocar apenas o engine (ex: SQL Server → PostgreSQL) **não resolve** se o banco continuar remoto. O problema é a localização, não o engine.

---

## Multi-tenancy

- Cada tenant tem seus próprios canais, fluxos, contatos e assinatura
- Usuário pode pertencer a múltiplos workspaces (`tenant_users` com `role` e `permissions`)
- Planos: `free`, `pro`, etc. com limites de contatos ativos, fluxos e sequências
- Billing via Stripe (webhook em `/api/v1/billing/stripe-webhook`)

---

## Modelos principais

| Model | Tabela | Descrição |
|---|---|---|
| `Contact` | `contacts` | Contato do Telegram. Tem `telegram_user_id` (indexado) e `custom_fields` (JSON) |
| `Channel` | `channels` | Bot Telegram. Tem `webhook_secret` (indexado, desnormalizado de `config`) |
| `Flow` | `flows` | Fluxo de automação |
| `FlowStep` | `flow_steps` | Step de um fluxo (trigger, message, action, wait, condition) |
| `FlowExecution` | `flow_executions` | Instância de execução de um fluxo para um contato |
| `Sequence` | `sequences` | Sequência de mensagens agendadas |
| `ContactSequence` | `contact_sequences` | Contato inscrito em uma sequência |

---

## Padrões importantes

- **Fallback gracioso**: todo uso de Redis/ARQ tem try/except que cai em comportamento síncrono
- **auto_migrate**: migrações incrementais no startup — nunca precisar rodar script manual
- **`_trigger_cache`**: dict em memória em `telegram.py` com TTL 30s — invalidado ao salvar fluxos
- **`invalidate_trigger_cache(tenant_id)`**: chamar sempre que fluxos ou steps forem alterados
- **`save_outbound_message(auto_commit=True)`**: usa `db.flush()` internamente — commit real acontece no final do step ou na pausa do fluxo
- Sempre responder ao usuário em **português-BR**
