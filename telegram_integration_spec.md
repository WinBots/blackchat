# WinChat – Integração Telegram (Backend + Frontend)

Este documento descreve, em detalhes, a implementação da **integração com Telegram** para o projeto WinChat (FastAPI + Vue), focado em reproduzir recursos essenciais similares ao Manychat.

---

## 1. Contexto do Projeto

- **Backend**: FastAPI + SQLite  
  Pasta: `backend/`  

- **Frontend**: Vue 3 + Vite  
  Pasta: `frontend/`  

Entidades principais já existentes e relevantes para a integração:

- `Flow` e `FlowStep` – definem fluxos e passos de automação.
- `Channel` – representa um canal conectado (ex.: Telegram, Instagram).
- `Contact` – representa um contato/usuário final.

A integração com Telegram irá se apoiar nessas entidades para:

- Identificar o bot e o canal.
- Ligar mensagens recebidas a um `Contact`.
- Executar um `Flow` e enviar mensagens de volta via Telegram Bot API.

---

## 2. Objetivo da Integração Telegram

Criar uma integração Telegram **end-to-end**, incluindo:

1. Configuração do bot Telegram por canal (`Channel`).
2. Webhook para receber mensagens do Telegram.
3. Criação/atualização de contatos a partir dos updates recebidos.
4. Disparo e execução de um fluxo (Flow) padrão associado ao Telegram.
5. Envio de mensagens de volta usando a Telegram Bot API.
6. UI no frontend para configurar o bot e marcar um fluxo como “padrão para Telegram”.

---

## 3. Configuração de Bot Telegram por Canal

### 3.1. Modelo `Channel`

Já existe um modelo `Channel` com os campos:

- `id`
- `tenant_id`
- `type` (ex.: `"telegram"`, `"instagram"`)
- `name`
- `config` (string JSON)
- `is_active`
- `created_at`

Para Telegram, o campo `config` passará a armazenar um JSON com, no mínimo:

```json
{
  "bot_token": "string",
  "bot_username": "string opcional",
  "webhook_secret": "string aleatória única",
  "webhook_url": "https://SEU_DOMINIO/api/v1/webhooks/telegram/<webhook_secret>"
}
```

### 3.2. Endpoint para Configuração do Bot Telegram

Criar (ou estender) um endpoint no router de canais, por exemplo em `channels.py`:

- `PUT /api/v1/channels/{channel_id}/telegram-config`

#### Corpo da requisição

```json
{
  "bot_token": "string",
  "bot_username": "string opcional"
}
```

#### Lógica

1. Carregar o `Channel` pelo `channel_id`.
2. Validar se `channel.type == "telegram"`.
3. Se não existir `webhook_secret` ainda, gerar um novo (ex.: usando UUID).
4. Montar o JSON `config` com:
   - `bot_token`
   - `bot_username`
   - `webhook_secret`
   - `webhook_url` = `PUBLIC_BASE_URL + "/api/v1/webhooks/telegram/" + webhook_secret`
5. Salvar este JSON como string no campo `Channel.config`.

### 3.3. Variáveis de Ambiente (Backend)

No arquivo `.env` do backend, adicionar:

```env
TELEGRAM_API_BASE=https://api.telegram.org
PUBLIC_BASE_URL=https://seu-dominio.com
```

- `TELEGRAM_API_BASE` será usado para montar a URL da Telegram Bot API.
- `PUBLIC_BASE_URL` será usado para construir a `webhook_url` do canal.

---

## 4. Webhook do Telegram

O webhook é o ponto de entrada para as mensagens vindas do Telegram.

### 4.1. Endpoint no Router `telegram.py`

Em `app/api/v1/routers/telegram.py`, criar um endpoint:

```python
@router.post("/{webhook_secret}")
def telegram_webhook(
    webhook_secret: str,
    update: dict = Body(...),
    db: Session = Depends(get_db),
):
    ...
```

### 4.2. Passos da Lógica do Webhook

1. **Identificar o canal**  

   - Buscar um `Channel` cujo `type == "telegram"` e cujo `config.webhook_secret == webhook_secret`.
   - Se não encontrar, retornar `404`.

2. **Extrair dados do update do Telegram**  

   Considerando updates do tipo `message` de texto simples:

   - `chat_id = update["message"]["chat"]["id"]`
   - `user_id = update["message"]["from"]["id"]`
   - `username = update["message"]["from"].get("username")`
   - `first_name = update["message"]["from"].get("first_name")`
   - `last_name = update["message"]["from"].get("last_name")`
   - `text = update["message"]["text"]`

3. **Criar/Atualizar Contact**  

   Usar o `tenant_id` do canal (`channel.tenant_id`) para associar o contato:

   - Buscar `Contact` existente para esse tenant + alguma chave (ex.: `username` e/ou `default_channel_id`).
   - Se não existir, criar um novo:
     - `tenant_id = channel.tenant_id`
     - `first_name`, `last_name`, `username`
     - `default_channel_id = channel.id`
   - Se existir, atualizar campos básicos se necessário.

4. **Selecionar o fluxo padrão para Telegram**  

   A convenção será:

   - `Flow.trigger_config` terá um campo `"default_for": "telegram"` quando o fluxo for o fluxo padrão do Telegram para aquele tenant.
   - `Flow.is_active` deve ser `True`.

   No webhook:

   - Buscar `Flow` cujo:
     - `tenant_id == channel.tenant_id`
     - `is_active == True`
     - `trigger_config.default_for == "telegram"`

   - Se nenhum fluxo for encontrado:
     - Enviar uma mensagem padrão para o usuário, tipo: `"Bot não possui fluxo padrão configurado ainda."`
     - Retornar com `200 OK`.

5. **Executar o fluxo (MVP)**  

   - Buscar `FlowStep` do fluxo encontrado, ordenando por `order_index`.
   - Para cada `FlowStep`:

     - Se `type == "message"`:
       - Ler `config["text"]`.
       - Enviar essa mensagem usando a Telegram Bot API (ver seção 5).

     - Se `type == "wait"` (opcional no MVP):
       - Ler `config["seconds"]`.
       - **No MVP** podemos apenas registrar no log ou ignorar (não é necessário implementar delay real).

   - A resposta do webhook deve ser `200 OK` (com um JSON simples indicando que o processamento ocorreu).

---

## 5. Serviço de Envio de Mensagens via Telegram Bot API

Criar um serviço dedicado, por exemplo em `app/services/telegram_sender.py`:

### 5.1. Função principal

```python
def send_telegram_message(bot_token: str, chat_id: int | str, text: str) -> None:
    ...
```

### 5.2. Implementação

- Base URL da API: `TELEGRAM_API_BASE` (do `.env`), por exemplo `https://api.telegram.org`.
- Endpoint: `POST {TELEGRAM_API_BASE}/bot{bot_token}/sendMessage`.
- Corpo JSON:
  ```json
  {
    "chat_id": "<chat_id>",
    "text": "mensagem"
  }
  ```
- Usar `requests` ou `httpx`:

  - Adicionar no `requirements.txt` caso não exista:
    - `httpx` **ou** `requests`.

- Tratar erros:
  - Logar exceções e respostas de erro.
  - Não deixar a exceção subir para quebrar o webhook; continuar retornando `200 OK` para o Telegram sempre que possível (para evitar reenfileiramentos constantes).

### 5.3. Uso dentro do Webhook

No `telegram_webhook`:

- Carregar `Channel.config.bot_token`.
- Passar `bot_token` + `chat_id` + `text` para `send_telegram_message`.

---

## 6. Fluxo Padrão para Telegram (Trigger Config)

### 6.1. Convenção de `trigger_config`

Para marcar um fluxo como padrão Telegram:

```json
{
  "default_for": "telegram"
}
```

Esse JSON será armazenado em `Flow.trigger_config` (como string no banco e convertido para dict no Pydantic `FlowOut`).

### 6.2. Garantir exclusividade por tenant

No endpoint de atualização de fluxo (`PUT /api/v1/flows/{id}`):

- Quando receber `trigger_config` com `"default_for": "telegram"`:

  1. Buscar **outros** fluxos do mesmo `tenant_id` que tenham `"default_for": "telegram"`.
  2. Remover esse campo (ou setar para algo diferente) nos outros fluxos.
  3. Salvar alterações, garantindo que **apenas um fluxo por tenant** esteja marcado como padrão para Telegram.

---

## 7. Ajustes no Frontend – Configuração do Bot Telegram

### 7.1. API de Canais no Frontend

Criar arquivo `frontend/src/api/channels.js` com funções como:

```js
import api from './http'

export async function listChannels() {
  const res = await api.get('/api/v1/channels')
  return res.data
}

export async function updateTelegramConfig(channelId, payload) {
  const res = await api.put(`/api/v1/channels/${channelId}/telegram-config`, payload)
  return res.data
}
```

(Adaptar conforme a estrutura final do backend.)

### 7.2. Tela `ChannelsView.vue`

Alterar para:

1. Carregar a lista de canais chamando `listChannels()`.
2. Exibir os canais em tabela, separando ou identificando os de `type="telegram"`.
3. Para canais `telegram`, adicionar botão **“Configurar Telegram”** que abre um modal:

   - Campos no modal:
     - `Bot Token` (input de texto, obrigatório).
     - `Bot Username` (input opcional).
     - `Webhook URL` (campo somente leitura, exibido após salvar ou carregado da API).

4. Ao clicar em “Salvar” no modal:

   - Chamar `updateTelegramConfig(channelId, { bot_token, bot_username })`.
   - Atualizar os dados do canal em memória (recarregar a lista ou atualizar localmente).
   - Exibir o `webhook_url` retornado na UI para cópia.

### 7.3. Variáveis de Ambiente no Frontend

Adicionar em `.env.example.local`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8061
VITE_PUBLIC_WEBHOOK_BASE_URL=http://127.0.0.1:8061
```

- `VITE_API_BASE_URL` já é usada pelo `http.js` para acessar o backend.
- `VITE_PUBLIC_WEBHOOK_BASE_URL` pode ser usada (se quiser) para mostrar ao usuário a URL base do webhook, mas a `webhook_url` oficial vem do backend.

---

## 8. Ajustes no Frontend – Marcar Fluxo Padrão Telegram

### 8.1. Tela `FlowEditView.vue`

Adicionar uma seção “Configuração de gatilho Telegram” com:

- Um checkbox: **“Fluxo padrão para Telegram”**.

#### Comportamento

- Ao carregar o fluxo:
  - Verificar se `flow.trigger_config?.default_for === "telegram"`.
  - Preencher o checkbox com base nisso.

- Ao alterar o checkbox e salvar:

  - Se marcado:
    - Enviar em `updateFlow` algo como:
      ```json
      {
        "trigger_config": { "default_for": "telegram" }
      }
      ```

  - Se desmarcado:
    - Enviar `trigger_config` sem o campo `default_for` ou nulo.

O backend será responsável por:

- Garantir que apenas um fluxo por `tenant_id` tenha `"default_for": "telegram"`.
- Retornar o estado atualizado na resposta.

---

## 9. Critérios de Aceite da Integração Telegram

A integração Telegram é considerada funcional quando:

1. No **backend**:
   - Existe um endpoint para configurar `bot_token` e `webhook_secret` por canal Telegram.
   - Existe o webhook em `POST /api/v1/webhooks/telegram/{webhook_secret}` que:
     - Localiza o canal correto.
     - Cria/atualiza `Contact`.
     - Localiza o fluxo padrão para Telegram (por tenant).
     - Executa os steps `message` e envia mensagens via Telegram Bot API.

2. No **frontend**:
   - A tela de canais permite configurar um bot Telegram, exibindo o `webhook_url` resultante.
   - A tela de edição de fluxo permite marcar o fluxo como padrão para Telegram.

3. Teste mínimo (mesmo com token inválido):
   - Enviar um `update` de teste para o webhook corresponde ao `webhook_secret` do canal.
   - O backend processa o update sem erro e loga a tentativa de envio de mensagens do fluxo para o Telegram.

---

Fim do documento.
