# Arquitetura Técnica – Plataforma de Automação (FastAPI + Vue)

## 1. Stack Tecnológica

- **Backend**: Python + FastAPI
- **Frontend**: Vue 3 + Vite (SPA)
- **Banco de Dados**: PostgreSQL ou SQL Server (modelo agnóstico, adaptável)
- **ORM**: SQLAlchemy (ou SQLModel) + Alembic para migrações
- **Fila / Worker**: Celery + Redis
- **Autenticação**: JWT (access + refresh token)
- **Proxy / Deploy**: Nginx + Uvicorn/Gunicorn
- **Outros**:
  - Docker (containers de backend, frontend, db, redis);
  - Logging estruturado (ex.: loguru ou padrão logging).

---

## 2. Organização do Backend (FastAPI)

### 2.1. Estrutura de Pastas Sugerida

```text
backend/
  app/
    main.py
    config.py
    dependencies.py

    core/
      security.py
      auth.py
      pagination.py

    db/
      base.py
      session.py
      models/
        tenant.py
        user.py
        channel.py
        contact.py
        tag.py
        attribute.py
        event.py
        flow.py
        flow_instance.py
        message_log.py

    api/
      v1/
        routers/
          auth.py
          tenants.py
          users.py
          channels.py
          contacts.py
          tags.py
          attributes.py
          flows.py
          broadcasts.py
          events.py         # eventos externos
          telegram.py       # webhook Telegram
          instagram.py      # webhook Instagram

    services/
      channels/
        base.py
        telegram_adapter.py
        instagram_adapter.py
      flows/
        engine.py
        runner.py
      contacts/
        contact_service.py
      events/
        event_service.py
      broadcasts/
        broadcast_service.py

    tasks/
      worker.py
      send_message.py
      process_event.py
      resume_flow.py
```

### 2.2. main.py (Bootstrap)

- Cria a instância FastAPI;
- Configura CORS, middlewares e includes das rotas;
- Faz o bind do app com as configurações (config.py).

Exemplo simplificado:

```python
from fastapi import FastAPI
from app.api.v1.routers import auth, tenants, channels, contacts, flows, events, telegram, instagram

app = FastAPI(title="Automation Platform API")

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(tenants.router, prefix="/api/v1/tenants", tags=["tenants"])
app.include_router(channels.router, prefix="/api/v1/channels", tags=["channels"])
app.include_router(contacts.router, prefix="/api/v1/contacts", tags=["contacts"])
app.include_router(flows.router, prefix="/api/v1/flows", tags=["flows"])
app.include_router(events.router, prefix="/api/v1/events", tags=["events"])
app.include_router(telegram.router, prefix="/api/v1/webhooks/telegram", tags=["webhooks-telegram"])
app.include_router(instagram.router, prefix="/api/v1/webhooks/instagram", tags=["webhooks-instagram"])
```

---

## 3. Modelagem de Dados (Resumo)

### 3.1. Tenants, Usuários e Relacionamentos

```text
tenants
- id
- name
- created_at

users
- id
- email
- password_hash
- full_name
- is_active
- created_at

tenant_users
- id
- tenant_id (FK tenants)
- user_id (FK users)
- role (owner, admin, editor, viewer)
```

### 3.2. Canais (Channels)

```text
channels
- id
- tenant_id (FK tenants)
- type (telegram, instagram)
- name
- config (JSON: tokens, ids, secrets)
- is_active
- created_at
```

- Telegram config (exemplo):
  - `bot_token`
  - `webhook_url`
- Instagram config (exemplo):
  - `instagram_business_id`
  - `page_id`
  - `access_token` (ou referência segura)

### 3.3. Contatos, Tags e Atributos

```text
contacts
- id
- tenant_id
- default_channel_id (FK channels, opcional)
- external_id (ID do usuário em sistema externo, opcional)
- first_name
- last_name
- username
- language
- country
- created_at
- updated_at

contact_channels
- id
- contact_id
- channel_id
- channel_user_id  # chat_id do Telegram, PSID/ID do IG, etc.
- created_at

tags
- id
- tenant_id
- name
- created_at

contact_tags
- id
- contact_id
- tag_id
- created_at

custom_attributes
- id
- tenant_id
- name
- type  # string, number, boolean, date

contact_attributes
- id
- contact_id
- custom_attribute_id
- value  # string serializada
```

### 3.4. Eventos, Fluxos e Instâncias

```text
events
- id
- tenant_id
- source (telegram, instagram, external)
- event_type (message.inbound, command.received, order.paid, etc.)
- contact_id (FK contacts, opcional)
- payload (JSON)
- processed (bool)
- created_at

flows
- id
- tenant_id
- name
- description
- is_active
- trigger_type (message_keyword, command, external_event)
- trigger_config (JSON)
- created_at
- updated_at

flow_steps
- id
- flow_id
- order_index
- type  # message, question, apply_tag, set_attribute, condition, wait, webhook_call, goto_step
- config (JSON)

flow_instances
- id
- flow_id
- contact_id
- current_step_id (FK flow_steps)
- context (JSON)
- status (running, finished, paused, error)
- created_at
- updated_at
```

### 3.5. Logs de Mensagem

```text
message_logs
- id
- tenant_id
- channel_id
- contact_id
- direction (inbound, outbound)
- message_type (text, image, button, etc.)
- content (JSON)
- created_at
```

---

## 4. Engine de Fluxos (Flow Engine)

### 4.1. Responsabilidades

- Receber um **evento** (mensagem recebida, evento externo, etc.);
- Identificar quais flows têm gatilhos compatíveis;
- Criar/continuar **instâncias de fluxo** por contato;
- Executar steps, acionar actions e decidir o próximo step.

### 4.2. Ciclo de Vida de Evento

1. Webhook ou API externa envia evento;
2. Backend salva em `events` e enfileira task `process_event`;
3. `process_event`:
   - Resolve/Cria `contact`;
   - Encontra flows compatíveis pelo `trigger_type` + `trigger_config`;
   - Cria ou retoma `flow_instance`;
   - Chama `engine.run_step(instance)`.

### 4.3. Execução de Step (Exemplo Simplificado)

```python
def run_step(instance):
    step = get_step(instance.current_step_id)

    if step.type == "message":
        text = render_template(step.config["text"], instance.context, instance.contact)
        enqueue_send_message(instance.contact, text)
        go_to_next_step(instance)

    elif step.type == "question":
        text = render_template(step.config["text"], instance.context, instance.contact)
        enqueue_send_message(instance.contact, text)
        instance.status = "paused"
        save_instance(instance)

    elif step.type == "apply_tag":
        apply_tag(instance.contact, step.config["tag"])
        go_to_next_step(instance)

    elif step.type == "set_attribute":
        set_attribute(instance.contact, step.config["attribute"], step.config["value"])
        go_to_next_step(instance)

    elif step.type == "condition":
        result = evaluate_condition(step.config["expression"], instance.contact, instance.context)
        instance.current_step_id = step.config["true_step_id"] if result else step.config["false_step_id"]
        save_instance(instance)

    elif step.type == "wait":
        schedule_resume(instance, delay=step.config["delay_seconds"])

    # ...
```

---

## 5. Adapters de Canal (Telegram & Instagram)

### 5.1. BaseChannelAdapter

```python
class BaseChannelAdapter:
    def send_message(self, channel, contact_channel, message):
        raise NotImplementedError

    def handle_webhook(self, channel, payload):
        """
        Recebe payload bruto do canal e retorna um objeto de evento interno normalizado.
        """
        raise NotImplementedError
```

### 5.2. TelegramAdapter

Responsável por:

- Interpretar payloads de webhook (messages, commands, callback_query);
- Criar eventos internos (`message.inbound`, `command.received`);
- Enviar mensagens via endpoint `sendMessage` da API de bot.

Fluxo do webhook:

- Endpoint: `POST /api/v1/webhooks/telegram/{channel_id}`
- Passos:
  1. Buscar `channel` pelo `channel_id`;
  2. Chamar `TelegramAdapter.handle_webhook(channel, payload)`;
  3. Criar `event` interno;
  4. Enfileirar `process_event`.

### 5.3. InstagramAdapter

Responsável por:

- Lidar com callbacks de verificação (`hub.challenge`);
- Interpretar eventos de mensagens (DMs) da Instagram Messaging API;
- Criar eventos internos normalizados;
- Enviar respostas de mensagem via Graph API.

Fluxo do webhook:

- Endpoint: `POST /api/v1/webhooks/instagram/{channel_id}`
- Passos similares ao Telegram, respeitando o formato do Graph API.

---

## 6. API REST – Endpoints Principais

### 6.1. Autenticação

- `POST /api/v1/auth/login` – login com e-mail/senha, retorno de JWT;
- `POST /api/v1/auth/refresh` – renovação de token;
- Opcional: `POST /api/v1/auth/register` – criação de usuários.

### 6.2. Tenants

- `GET /api/v1/tenants` – listar tenants do usuário logado;
- `POST /api/v1/tenants` – criar novo tenant/workspace;
- `GET /api/v1/tenants/{id}` – detalhes;
- `POST /api/v1/tenants/{id}/members` – adicionar/invitar usuário.

### 6.3. Canais

- `GET /api/v1/channels` – listar canais do tenant atual;
- `POST /api/v1/channels` – criar canal (telegram/instagram) com config;
- `GET /api/v1/channels/{id}` – detalhes;
- `POST /api/v1/channels/{id}/test` – testar conexão/envio simples.

### 6.4. Contatos

- `GET /api/v1/contacts` – listagem paginada com filtros (tags/atributos);
- `GET /api/v1/contacts/{id}` – detalhes, histórico de mensagens;
- `PATCH /api/v1/contacts/{id}` – atualização manual;
- `GET /api/v1/contacts/{id}/logs` – mensagens trocadas.

### 6.5. Tags & Atributos

- `GET /api/v1/tags`, `POST /api/v1/tags`;
- `POST /api/v1/contacts/{id}/tags` – aplicar/remover tag;
- CRUD de `custom_attributes`.

### 6.6. Fluxos

- `GET /api/v1/flows` – listar;
- `POST /api/v1/flows` – criar;
- `GET /api/v1/flows/{id}` – detalhes;
- `PUT /api/v1/flows/{id}` – atualizar;
- `GET /api/v1/flows/{id}/steps` – listar steps;
- `POST /api/v1/flows/{id}/steps` – adicionar step;
- `PUT /api/v1/flow-steps/{id}` – editar step.

### 6.7. Eventos Externos

- `POST /api/v1/events/external`
  - body: `{ "event_type": "...", "external_user_id": "...", "payload": {...} }`
  - backend resolve/associa contato e dispara flows.

---

## 7. Frontend – Vue 3 + Vite

### 7.1. Estrutura de Pastas (Sugestão)

```text
frontend/
  src/
    main.ts
    router/
      index.ts
    store/
      index.ts
    api/
      http.ts
      auth.ts
      tenants.ts
      channels.ts
      contacts.ts
      flows.ts
    views/
      Auth/
        LoginView.vue
      Tenants/
        TenantSelectView.vue
      Dashboard/
        DashboardView.vue
      Channels/
        ChannelListView.vue
        ChannelFormView.vue
      Contacts/
        ContactListView.vue
        ContactDetailView.vue
      Flows/
        FlowListView.vue
        FlowEditView.vue
    components/
      layout/
        AppLayout.vue
        Sidebar.vue
        Topbar.vue
      common/
        DataTable.vue
        TagBadge.vue
        ChannelBadge.vue
        JsonViewer.vue
      flows/
        StepCard.vue
        StepFormMessage.vue
        StepFormQuestion.vue
        StepFormAction.vue
        StepFormCondition.vue
```

### 7.2. Telas-Chave

1. **Login e Seleção de Workspace**
   - Login JWT;
   - Seleção de tenant (quando usuário pertence a mais de um).

2. **Dashboard**
   - Resumo de contatos, canais, fluxos ativos;
   - Eventos recentes (log básico).

3. **Canais**
   - Listagem de canais com tipo e status;
   - Formulário para cadastrar bot do Telegram ou conta de Instagram.

4. **Contatos**
   - Lista com filtros (tags, canal, atributo);
   - Tela de detalhes com histórico de mensagens.

5. **Fluxos**
   - Listagem dos fluxos;
   - Tela de edição com steps em lista (sem canvas no MVP);
   - Forms específicos por tipo de step.

---

## 8. Segurança e Multi-tenant

- JWT obrigatório para todas as rotas de aplicação (exceto webhooks);
- Cada requisição carrega:
  - `user_id` (do token);
  - `tenant_id` (selecionado e validado na sessão/contexto);
- Todas as consultas no banco devem ser filtradas por `tenant_id`:
  - Evita vazamento de dados entre workspaces;
- Perfis de acesso (role):
  - `owner`, `admin`, `editor`, `viewer` – para controle de permissões.

---

## 9. Próximos Passos Técnicos

1. Subir projeto FastAPI com base de autenticação, tenants e usuários;
2. Implementar modelos e CRUD de canais, contatos e flows;
3. Implementar webhook de Telegram + adapter;
4. Integrar engine de fluxo com eventos do Telegram;
5. Criar SPA Vue com layout base, auth e telas de gerenciamento mínimas;
6. Evoluir gradualmente para Instagram e demais features.
