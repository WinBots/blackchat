# ✅ Checklist de Teste - Integração Telegram

## 📋 Preparação

### Backend
- [ ] Backend rodando em `http://localhost:8061`
- [ ] Biblioteca `httpx` instalada
- [ ] Variáveis de ambiente configuradas:
  - `TELEGRAM_API_BASE=https://api.telegram.org`
  - `PUBLIC_BASE_URL=http://127.0.0.1:8061` (ou domínio público com ngrok)

### Frontend
- [ ] Frontend rodando em `http://localhost:3061`
- [ ] Sem erros no console (F12)

### Telegram
- [ ] Bot criado no @BotFather
- [ ] Token do bot copiado
- [ ] Username do bot anotado (ex: @seu_bot)

---

## 🔧 Passo 1: Conectar Bot

1. [ ] Acessar `/settings` no menu
2. [ ] Clicar em "**Telegram**" na sidebar
3. [ ] Clicar em "**Conectar**"
4. [ ] Escolher "**Conectar Bot Existente**"
5. [ ] Colar o **token** do bot
6. [ ] Clicar em "**Conectar**"
7. [ ] Verificar tela de sucesso
8. [ ] **Copiar a Webhook URL** gerada

**Resultado esperado**: 
- ✅ Mensagem de sucesso
- ✅ Webhook URL exibida

---

## 🌐 Passo 2: Configurar Webhook (Ngrok para teste local)

### Opção A: Usando Ngrok (Recomendado para teste local)

1. [ ] Instalar ngrok: https://ngrok.com/download
2. [ ] Executar: `ngrok http 8061`
3. [ ] Copiar URL gerada (ex: `https://abc123.ngrok.io`)
4. [ ] Atualizar `PUBLIC_BASE_URL` no backend para a URL do ngrok
5. [ ] **Reiniciar o backend**
6. [ ] Reconectar o bot no frontend (para gerar nova webhook URL com ngrok)
7. [ ] Copiar a nova Webhook URL
8. [ ] Configurar no Telegram:
   ```
   https://api.telegram.org/bot{SEU_TOKEN}/setWebhook?url={WEBHOOK_URL_NGROK}
   ```
9. [ ] Verificar resposta: `{"ok":true,"result":true}`

### Opção B: Servidor público (Produção)

1. [ ] Deploy do backend em servidor público
2. [ ] Atualizar `PUBLIC_BASE_URL` para domínio público
3. [ ] Configurar webhook no Telegram

**Resultado esperado**: 
- ✅ Webhook registrado no Telegram
- ✅ Backend acessível publicamente

---

## 📝 Passo 3: Criar Fluxo com Gatilho

### 3.1 Criar Fluxo para Telegram

1. [ ] Ir para `/flows`
2. [ ] Clicar em "**+ Criar Fluxo**"
3. [ ] Escolher "**Telegram**" como sistema
4. [ ] Nome: "Boas-vindas Telegram"
5. [ ] Clicar em "**Criar Fluxo**"

### 3.2 Adicionar Gatilho (OBRIGATÓRIO)

1. [ ] Na tela do fluxo, clicar em "**Adicionar Gatilho**"
2. [ ] Escolher "**Mensagem do Telegram**"
3. [ ] Clicar em "**Detectar determinadas palavras de uma mensagem**"
4. [ ] Adicionar keyword: `oi`
5. [ ] Adicionar keyword: `olá`
6. [ ] Adicionar keyword: `/start`
7. [ ] Salvar

**Ou** para testar sem keywords:
1. [ ] Escolher "**Mensagem do Telegram**"
2. [ ] Não adicionar keywords (aceita qualquer mensagem)

### 3.3 Adicionar Bloco de Mensagem

1. [ ] Clicar no **gatilho** criado
2. [ ] Clicar em "**Adicionar Bloco**" (botão superior direito)
3. [ ] Um bloco de "Mensagem" é criado
4. [ ] Clicar no bloco de **Mensagem**

### 3.4 Adicionar Sub-blocos (Conteúdo)

Na sidebar esquerda:

1. [ ] Clicar em "**Texto**"
2. [ ] Clicar no **primeiro sub-bloco de texto** criado
3. [ ] Na sidebar, editar o texto: `Olá! 👋 Bem-vindo ao nosso bot!`
4. [ ] Clicar em "**Texto**" novamente para adicionar outro
5. [ ] Clicar no **segundo sub-bloco**
6. [ ] Editar: `Como posso ajudar você hoje?`
7. [ ] (Opcional) Clicar em "**Atraso**"
8. [ ] Clicar no sub-bloco de atraso
9. [ ] Definir: `2` segundos
10. [ ] Salvar automaticamente (auto-save)

**Resultado esperado**: 
- ✅ Sub-blocos aparecendo no cartão do bloco
- ✅ Cada sub-bloco mostrando o texto correto

### 3.5 Conectar Blocos (Opcional se já estiver conectado)

1. [ ] Arrastar do **ponto de saída (↘)** do gatilho
2. [ ] Soltar no **ponto de entrada (↖)** do bloco de mensagem
3. [ ] Linha verde conecta os blocos

**Resultado esperado**: 
- ✅ Linha verde conectando gatilho → mensagem

---

## 🧪 Passo 4: Testar no Telegram

### 4.1 Iniciar conversa

1. [ ] Abrir Telegram (app ou web.telegram.org)
2. [ ] Buscar o username do seu bot (ex: `@seu_bot`)
3. [ ] Clicar em "**Start**" ou enviar mensagem
4. [ ] Enviar: `oi`

### 4.2 Verificar resposta

**Resposta esperada**:
```
Olá! 👋 Bem-vindo ao nosso bot!
Como posso ajudar você hoje?
```

**Se configurou atraso**: deve ter 2 segundos entre as mensagens

### 4.3 Verificar logs do backend

No terminal do backend, você deve ver:
```
INFO: Recebido update do Telegram para webhook_secret=...
INFO: Mensagem de user_id=..., chat_id=..., text=oi
INFO: Contato criado: ...
INFO: Executando fluxo: X - Boas-vindas Telegram
INFO: Texto enviado: Olá! 👋 Bem-vindo ao nosso bot!
INFO: Texto enviado: Como posso ajudar você hoje?
```

---

## 🐛 Troubleshooting

### ❌ Bot não responde

**Possíveis causas**:
1. Webhook não configurado
   - Verificar: `https://api.telegram.org/bot{TOKEN}/getWebhookInfo`
   - Deve mostrar a URL do webhook
2. Backend não acessível publicamente
   - Usar ngrok para teste local
3. Fluxo não marcado como padrão Telegram
   - Verificar se criou o fluxo escolhendo "Telegram" como sistema
4. Sem gatilho ou keyword não corresponde
   - Verificar se adicionou o gatilho
   - Testar com keyword exata (ex: `oi`)

### ❌ Erro 404 no webhook

- Verificar se o `webhook_secret` na URL corresponde ao do banco
- Verificar se o canal existe no banco de dados

### ❌ Erro 500 no webhook

- Verificar logs do backend
- Verificar se o `config` do canal tem `bot_token`
- Verificar se o fluxo tem steps salvos corretamente

### ❌ Mensagem enviada mas sem conteúdo

- Verificar se os sub-blocos têm texto preenchido
- Verificar no banco: `SELECT config FROM flow_steps WHERE id=X`
- O campo `config` deve conter JSON com `blocks` array

---

## 📊 Verificação no Banco de Dados

### Verificar Canal
```sql
SELECT id, name, type, config FROM channels WHERE type='telegram';
```

Deve mostrar:
- `config` com `bot_token`, `webhook_secret`, `webhook_url`

### Verificar Fluxo
```sql
SELECT id, name, trigger_config FROM flows WHERE is_active=1;
```

Deve mostrar:
- `trigger_config` com `{"default_for": "telegram"}`

### Verificar Steps
```sql
SELECT id, type, config FROM flow_steps WHERE flow_id=X ORDER BY order_index;
```

Deve mostrar:
- Step tipo `trigger` com `config` contendo `triggerType`, `keywords`
- Steps tipo `message` com `config` contendo `blocks` array

### Verificar Blocos
```sql
SELECT config FROM flow_steps WHERE type='message' AND flow_id=X;
```

O `config` deve ter estrutura:
```json
{
  "blocks": [
    {"id": "...", "type": "text", "text": "Olá! 👋"},
    {"id": "...", "type": "text", "text": "Como posso ajudar?"},
    {"id": "...", "type": "delay", "seconds": 2}
  ]
}
```

---

## ✅ Checklist Final

- [ ] Bot responde no Telegram
- [ ] Mensagens aparecem na ordem correta
- [ ] Atrasos funcionam (se configurado)
- [ ] Keywords funcionam (se configurado)
- [ ] Múltiplos blocos de texto aparecem
- [ ] Contato é criado no banco de dados
- [ ] Logs do backend mostram execução

---

## 🎉 Próximos Passos

Após confirmar que tudo funciona:

1. **Botões Inline**
   - Implementar `InlineKeyboardMarkup` do Telegram
   - Processar `callback_query` no webhook

2. **Envio de Imagens**
   - Implementar `sendPhoto` da API do Telegram
   - Upload de imagens no frontend

3. **Coleta de Dados**
   - Salvar respostas dos usuários
   - Armazenar em campos personalizados do contato

4. **Fluxos Condicionais**
   - Adicionar tipo de step "condition"
   - Múltiplos caminhos baseados em respostas

5. **Templates de Variáveis**
   - `{{first_name}}`, `{{username}}`, etc.
   - Substituir variáveis antes de enviar

---

**Boa sorte nos testes!** 🚀

