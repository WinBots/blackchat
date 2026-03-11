# 🔄 Como Funciona o Sistema de Webhook do Telegram

## 📊 Arquitetura Completa

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Telegram   │──1───▶│   ngrok     │──2───▶│   Backend   │──3───▶│   Banco de  │
│    API      │      │   (túnel)   │      │ localhost   │      │    Dados    │
└─────────────┘      └─────────────┘      └─────────────┘      └─────────────┘
     ▲                                            │
     │                                            │
     └────────────────4───────────────────────────┘
              (resposta ao usuário)
```

---

## 🔐 Onde o ngrok está configurado?

### **1. Banco de Dados (tabela `channels`)**

A URL do ngrok está armazenada no campo `config` de cada canal Telegram:

```json
{
  "bot_token": "1234567890:ABC...",
  "bot_username": "winbots_winchat_bot",
  "webhook_url": "https://97ab-2804...ngrok-free.app/api/v1/webhooks/telegram/f3fd1b17...",
  "webhook_secret": "f3fd1b17-79a2-4775-900b-3c462b3343b1"
}
```

**Localização:** `backend/data/app.db` → tabela `channels` → coluna `config`

### **2. Telegram API**

Quando você executou o script `update_webhook_url.py`, ele fez:

```python
POST https://api.telegram.org/bot{BOT_TOKEN}/setWebhook
{
  "url": "https://97ab-2804...ngrok-free.app/api/v1/webhooks/telegram/f3fd1b17..."
}
```

Isso **registra** no Telegram que todas as mensagens do bot devem ser enviadas para essa URL.

---

## 🚀 Fluxo de uma Mensagem

### **Passo 1: Usuário envia mensagem**
```
Usuário → Telegram App → Envia: "/start teste_promo"
```

### **Passo 2: Telegram processa**
```
Telegram API:
- Recebe a mensagem
- Consulta: "Qual webhook está registrado para este bot?"
- Encontra: "https://97ab-2804...ngrok-free.app/api/v1/webhooks/telegram/f3fd1b17..."
```

### **Passo 3: Telegram envia para ngrok**
```http
POST https://97ab-2804...ngrok-free.app/api/v1/webhooks/telegram/f3fd1b17...
Content-Type: application/json

{
  "update_id": 123456789,
  "message": {
    "message_id": 1,
    "from": {
      "id": 987654321,
      "first_name": "João",
      "username": "joao123"
    },
    "chat": {
      "id": 987654321,
      "first_name": "João",
      "type": "private"
    },
    "date": 1707876000,
    "text": "/start teste_promo"
  }
}
```

### **Passo 4: ngrok redireciona**
```
ngrok (túnel público):
- Recebe a requisição HTTPS na porta 443
- Redireciona para: http://localhost:8061/api/v1/webhooks/telegram/f3fd1b17...
```

### **Passo 5: Backend recebe**

**Arquivo:** `backend/app/api/v1/routers/telegram.py`

```python
@router.post("/{webhook_secret}")
def telegram_webhook(webhook_secret: str, update: dict, db: Session):
    # 1. Identifica o canal pelo webhook_secret
    channel = db.query(Channel).filter(
        Channel.config.contains(f'"webhook_secret":"{webhook_secret}"')
    ).first()
    
    # 2. Extrai dados da mensagem
    text = update.get("message", {}).get("text", "")
    chat_id = update.get("message", {}).get("chat", {}).get("id")
    
    # 3. Detecta parâmetro de referência
    ref_param = None
    if text.startswith("/start "):
        ref_param = text.split(" ", 1)[1].strip()
        # ref_param = "teste_promo"
    
    # 4. Busca fluxo com ref_key correspondente
    flows = db.query(Flow).filter(Flow.tenant_id == channel.tenant_id).all()
    
    for flow in flows:
        trigger_config = json.loads(flow.trigger_config)
        if trigger_config.get("triggerType") == "telegram_ref_url":
            ref_key = trigger_config.get("ref_key")
            if ref_param == ref_key:
                # MATCH! Executa este fluxo
                execute_flow(flow, contact, channel)
```

### **Passo 6: Backend executa o fluxo**

```python
def execute_flow(flow, contact, channel):
    # 1. Busca os steps do fluxo
    steps = db.query(FlowStep).filter(FlowStep.flow_id == flow.id).all()
    
    # 2. Executa cada step na ordem
    for step in sorted(steps, key=lambda s: s.order_index):
        if step.type == "message":
            config = json.loads(step.config)
            text = config.get("text")
            
            # 3. Envia mensagem via Telegram API
            send_telegram_message(bot_token, chat_id, text)
```

### **Passo 7: Backend envia resposta**

```python
# Chama a Telegram API
POST https://api.telegram.org/bot{BOT_TOKEN}/sendMessage
{
  "chat_id": 987654321,
  "text": "🎉 Parabéns! Você clicou no link de referência!"
}
```

### **Passo 8: Usuário recebe**
```
Telegram App → Mostra mensagem ao usuário
```

---

## 🔧 Componentes do Sistema

### **1. ngrok**
- **Função:** Criar túnel público para localhost
- **Comando:** `ngrok http 8061`
- **Resultado:** Gera URL pública HTTPS
- **Problema:** URL muda a cada reinicialização (plano gratuito)

### **2. Backend (FastAPI)**
- **Porta:** 8061
- **Rota principal:** `/api/v1/webhooks/telegram/{webhook_secret}`
- **Arquivo:** `backend/app/api/v1/routers/telegram.py`
- **Função:** Recebe webhooks e processa mensagens

### **3. Banco de Dados (SQLite)**
- **Localização:** `backend/data/app.db`
- **Tabelas importantes:**
  - `channels` - Configuração dos bots
  - `flows` - Fluxos de automação
  - `flow_steps` - Passos de cada fluxo
  - `contacts` - Usuários que interagem
  - `messages` - Histórico de mensagens

### **4. Telegram API**
- **Documentação:** https://core.telegram.org/bots/api
- **Endpoints usados:**
  - `setWebhook` - Registrar webhook
  - `getWebhookInfo` - Ver status do webhook
  - `sendMessage` - Enviar mensagem
  - `sendPhoto` - Enviar foto
  - `sendAudio` - Enviar áudio

---

## 🔒 Segurança: webhook_secret

O `webhook_secret` é um **UUID único** gerado para cada bot:

```
f3fd1b17-79a2-4775-900b-3c462b3343b1
```

**Por que usar?**
- Impede que qualquer pessoa envie requisições falsas
- Cada bot tem seu próprio secret
- Funciona como "senha" na URL

**Como funciona?**
1. Backend gera UUID ao criar canal
2. UUID é incluído na URL: `.../webhooks/telegram/{secret}`
3. Telegram só conhece essa URL
4. Requisições sem o secret correto retornam 404

---

## 📝 Scripts Importantes

### **1. update_webhook_url.py**
```bash
python update_webhook_url.py https://nova-url.ngrok-free.app
```
**O que faz:**
- Atualiza `webhook_url` no banco de dados
- Chama `setWebhook` na Telegram API
- Limpa mensagens pendentes

### **2. verify_webhook.py**
```bash
python verify_webhook.py
```
**O que faz:**
- Verifica status do webhook no Telegram
- Testa conectividade do backend
- Mostra erros e mensagens pendentes

### **3. check_channels.py**
```bash
python check_channels.py
```
**O que faz:**
- Lista todos os canais do banco
- Mostra configuração de cada um
- Exibe status (ativo/inativo)

---

## 🐛 Troubleshooting

### **Problema: Webhook não recebe mensagens**

**Verificar:**
```bash
# 1. ngrok está rodando?
# Deve ter uma janela aberta com a URL

# 2. Backend está rodando?
netstat -ano | findstr :8061

# 3. URL está atualizada?
python verify_webhook.py

# 4. Logs do backend mostram algo?
# Terminal onde rodou: uvicorn app.main:app
```

### **Problema: ngrok mudou de URL**

```bash
# 1. Copiar nova URL do ngrok
# 2. Executar:
python update_webhook_url.py https://nova-url.ngrok-free.app
```

### **Problema: Bot não responde**

**Verificar ordem:**
1. ✅ ngrok rodando
2. ✅ Backend rodando (porta 8061)
3. ✅ Webhook atualizado
4. ✅ Bot ativo no painel
5. ✅ Fluxo ativo

---

## 💡 Dicas

### **Desenvolvimento:**
- Mantenha ngrok rodando em terminal separado
- Use `--log-level debug` no uvicorn para ver detalhes
- Teste com `verify_webhook.py` após mudanças

### **Produção:**
- Use servidor com IP fixo (não precisa ngrok)
- Configure domínio próprio com HTTPS
- Use webhook_secret complexo
- Implemente rate limiting

### **Exemplo de setup produção:**
```
Domínio: api.seusite.com
Backend: VPS com IP público
HTTPS: Let's Encrypt (certbot)
Webhook: https://api.seusite.com/api/v1/webhooks/telegram/{secret}
```

---

## 📚 Fluxo Visual Completo

```
USUÁRIO ENVIA: /start teste_promo
    │
    ▼
TELEGRAM API
    │ Consulta webhook registrado
    │ Encontra: https://97ab...ngrok-free.app/api/v1/webhooks/telegram/f3fd1b17...
    ▼
ENVIA POST HTTPS
    │ URL: https://97ab...ngrok-free.app/api/v1/webhooks/telegram/f3fd1b17...
    │ Body: { "message": { "text": "/start teste_promo", ... } }
    ▼
NGROK (túnel público)
    │ Recebe HTTPS porta 443
    │ Redireciona para localhost:8061
    ▼
BACKEND (localhost:8061)
    │ Rota: /api/v1/webhooks/telegram/f3fd1b17...
    │ Arquivo: telegram.py
    │
    ├─▶ 1. Identifica canal pelo webhook_secret
    │
    ├─▶ 2. Extrai texto: "/start teste_promo"
    │
    ├─▶ 3. Detecta ref_param: "teste_promo"
    │
    ├─▶ 4. Busca fluxo com ref_key = "teste_promo"
    │
    ├─▶ 5. Encontra fluxo! Executa steps:
    │       │
    │       ├─▶ Step 1: Mensagem de texto
    │       ├─▶ Step 2: Imagem
    │       └─▶ Step 3: Áudio
    │
    └─▶ 6. Para cada step, chama Telegram API:
            POST https://api.telegram.org/bot{TOKEN}/sendMessage
            POST https://api.telegram.org/bot{TOKEN}/sendPhoto
            POST https://api.telegram.org/bot{TOKEN}/sendAudio
                │
                ▼
            TELEGRAM API
                │ Entrega mensagens ao usuário
                ▼
            USUÁRIO RECEBE MENSAGENS
```

---

**Tudo claro agora?** 🚀

O ngrok é apenas a "ponte" entre o mundo externo (Telegram) e seu computador local. Em produção, você não precisa dele!
