# Instagram Integration - Setup Guide

## 📋 Pré-requisitos

1. **Conta Facebook Business Manager** com acesso administrativo
2. **Página do Facebook** vinculada à conta Business
3. **Conta Instagram Business** conectada à página do Facebook
4. **App Facebook Developers** criado e configurado

---

## 🔧 Configuração do App Facebook

### 1. Criar um App no Facebook Developers

1. Acesse [Facebook Developers](https://developers.facebook.com/)
2. Vá em **Meus Apps** → **Criar App**
3. Escolha o tipo: **Business**
4. Preencha:
   - **Nome do App**: WinChat Instagram Integration
   - **Email de contato**: seu email
   - **Conta Business** (opcional): selecione sua conta

### 2. Adicionar Produtos ao App

No painel do app, adicione os seguintes produtos:

#### A) **Instagram**
- Clique em **Configurar** no card do Instagram
- Isso habilita as APIs de mensagens do Instagram

#### B) **Webhooks**
- Clique em **Configurar** no card de Webhooks
- Você configurará isso mais tarde após o backend estar rodando

### 3. Configurar Permissões

No menu lateral:
1. Vá em **App Settings** → **Basic**
2. Anote:
   - **App ID** 
   - **App Secret** (clique em "Show")

3. Configure os domínios:
   - **App Domains**: adicione seu domínio (ex: `winchat.com`)
   - **Privacy Policy URL**: URL da sua política de privacidade
   - **Terms of Service URL**: URL dos termos de serviço

4. Vá em **Use Cases** → **Customize**
   - Adicione as seguintes permissões:
     - `pages_show_list`
     - `pages_messaging`
     - `instagram_basic`
     - `instagram_manage_messages`
     - `instagram_manage_insights`
     - `business_management`

---

## 🔑 Configurar Backend

### 1. Adicionar credenciais no `.env`

```bash
# Instagram / Meta Configuration
INSTAGRAM_APP_ID=seu_app_id_aqui
INSTAGRAM_APP_SECRET=seu_app_secret_aqui
INSTAGRAM_VERIFY_TOKEN=winchat_instagram_verify_token_2025

# URL pública do seu backend (use ngrok para desenvolvimento)
PUBLIC_BASE_URL=https://seu-dominio.ngrok-free.app
```

### 2. Obter URL pública com ngrok (Desenvolvimento)

```bash
# Instalar ngrok (se não tiver)
# Download: https://ngrok.com/download

# Expor porta 8061
ngrok http 8061

# Copiar a URL HTTPS (ex: https://abc123.ngrok-free.app)
# Adicionar no .env como PUBLIC_BASE_URL
```

### 3. Reiniciar o backend

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8061 --reload
```

---

## 🔗 Configurar Webhooks no Facebook

### 1. Configurar Callback URL

1. No painel do Facebook Developers, vá em **Webhooks** → **Instagram**
2. Clique em **Editar Subscription**
3. Preencha:
   - **Callback URL**: `{PUBLIC_BASE_URL}/api/v1/webhooks/instagram`
     - Exemplo: `https://abc123.ngrok-free.app/api/v1/webhooks/instagram`
   - **Verify Token**: `winchat_instagram_verify_token_2025` (mesmo do .env)

4. Clique em **Verificar e Salvar**
   - O Facebook vai fazer uma requisição GET para validar
   - Se der erro, verifique se o backend está rodando e acessível

### 2. Assinar Eventos

Após verificar o webhook, selecione os eventos:
- ✅ `messages` - Para receber DMs
- ✅ `messaging_postbacks` - Para botões e respostas rápidas
- ✅ `message_echoes` - Para ver mensagens enviadas pelo bot

Clique em **Salvar**.

---

## 🔐 Configurar OAuth Redirect URI

1. No painel do Facebook Developers
2. Vá em **Configurações** → **Básico**
3. Role até **URIs de Redirecionamento OAuth Válidos**
4. Adicione:
   - `{PUBLIC_BASE_URL}/instagram/callback`
   - Exemplo: `https://abc123.ngrok-free.app/instagram/callback`

5. Clique em **Salvar Alterações**

---

## ✅ Testar a Integração

### 1. No Frontend (WinChat)

1. Acesse **Configurações** → **Canais** → **Instagram**
2. Clique em **Conectar Instagram**
3. Você será redirecionado para o Facebook
4. Faça login e autorize as permissões
5. Selecione a **Página** e a **Conta Instagram** que deseja conectar
6. Clique em **Conectar**

### 2. Verificar Conexão

Se tudo estiver correto:
- ✅ O canal Instagram aparecerá na lista de canais conectados
- ✅ Você poderá criar fluxos para o Instagram
- ✅ O webhook estará recebendo mensagens

---

## 🚀 Modo Produção (App Review)

Para usar em produção com usuários reais:

### 1. Submeter para App Review

1. No Facebook Developers, vá em **App Review** → **Permissões e Recursos**
2. Solicite aprovação para:
   - `pages_messaging`
   - `instagram_manage_messages`
   - `pages_show_list`

3. Preencha o formulário:
   - **Finalidade**: Automação de mensagens do Instagram para chatbots
   - **Screencast**: Vídeo demonstrando o uso
   - **Instruções de teste**: Forneça credenciais de teste

### 2. Ativar o App em Produção

1. Vá em **Configurações** → **Básico**
2. Mude o status do app de **Desenvolvimento** para **Ativo**

---

## 🐛 Troubleshooting

### Erro: "Callback verification failed"

**Causa**: Webhook não conseguiu ser verificado pelo Facebook

**Solução**:
1. Verifique se o backend está rodando
2. Verifique se a URL pública está acessível
3. Verifique se o `INSTAGRAM_VERIFY_TOKEN` no .env está correto
4. Veja os logs do backend para mais detalhes

### Erro: "Invalid OAuth redirect URI"

**Causa**: A URI de callback não está registrada no Facebook

**Solução**:
1. Vá em **Configurações** → **Básico** no Facebook Developers
2. Adicione a URL completa de callback em **URIs de Redirecionamento OAuth Válidos**
3. Exemplo: `https://seu-dominio.com/instagram/callback`

### Erro: "User has no connected Instagram Business Account"

**Causa**: A conta Instagram não está configurada como Business ou não está conectada à página

**Solução**:
1. No Instagram, vá em **Configurações** → **Tipo de Conta**
2. Mude para **Conta Profissional**
3. Vincule à uma Página do Facebook
4. Tente conectar novamente

---

## 📚 Referências

- [Instagram Messaging API - Documentação Oficial](https://developers.facebook.com/docs/messenger-platform/instagram)
- [Facebook Graph API](https://developers.facebook.com/docs/graph-api)
- [Webhooks Setup](https://developers.facebook.com/docs/graph-api/webhooks)
