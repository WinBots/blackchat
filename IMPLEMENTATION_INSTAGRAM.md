O que você realmente precisa do Instagram?

Para imitar o Manychat no Instagram, você vai usar principalmente:

Instagram Messaging API (via Meta / Graph API) para:

Receber DMs, replies de story e mentions.

Enviar mensagens de volta.

Tudo isso passa por:

Facebook App + Instagram Business/Creator + Facebook Page ligada ao IG.

Então a conexão “Instagram” no seu sistema, na prática, é:

Guardar e renovar um Page Access Token que possua permissão de enviar/receber mensagens do IG ligado àquela página.

2. Fluxo geral de conexão Instagram no seu SaaS

No seu Manychat-like, a conexão do Instagram vai ser algo assim:

Usuário clica em “Conectar Instagram” no painel.

Você redireciona pra Meta OAuth (Login with Facebook) com as permissões certas:

pages_show_list

pages_messaging

instagram_basic

instagram_manage_messages

instagram_manage_insights

(e eventualmente outras se precisar, tipo business_management)

Depois do login, o Meta retorna um code pro seu backend.

Seu backend (FastAPI) troca esse code por:

user_access_token

lista de páginas / contas ligadas.

Você deixa o usuário escolher qual Instagram Business ele quer conectar.

Você salva no seu banco:

Page ID

IG User ID (ex: 1789xxxx)

Page Access Token (de preferência long-lived)

Data de expiração

Você registra um Webhook no Meta apontando pro seu backend:

Tipo: instagram e messages (subscrições).

Quando chegar um evento (DM, mention etc.), seu backend trata isso e joga pro sistema de flows.

3. O que precisa existir no backend (FastAPI)
3.1. Campos a mais no Channel (type = "instagram")

Você já tem Channel com:

id

tenant_id

type (telegram, instagram, etc.)

name

config (JSON em string)

Para Instagram, você vai guardar em config algo nesse formato:

{
  "fb_page_id": "1234567890",
  "ig_user_id": "1789xxxxxxxx",
  "page_access_token": "EAAG....",
  "page_access_token_expires_at": "2025-12-31T23:59:59Z",
  "app_id": "SEU_APP_ID",
  "app_secret": "SEU_APP_SECRET"
}


Isso é o que seu backend precisa pra:

Chamar a Graph API (https://graph.facebook.com/v20.0/...);

Renovar tokens;

Enviar mensagens.

3.2. Rotas necessárias no backend

Sugestão de rotas:

GET /api/v1/instagram/auth-url

Gera a URL de login do Facebook/Meta pra conectar a conta.

Exemplo de URL base:

https://www.facebook.com/v20.0/dialog/oauth?client_id={APP_ID}&redirect_uri={REDIRECT_URI}&scope=pages_show_list,pages_messaging,instagram_basic,instagram_manage_messages

O frontend chama isso, e redireciona o usuário pra essa URL.

GET /api/v1/instagram/callback
(o redirect_uri configurado na Meta Console)

Recebe code como query param.

Troca code por user_access_token:

GET https://graph.facebook.com/v20.0/oauth/access_token?...

Usa esse token pra buscar:

Páginas do usuário: /{user_id}/accounts

Para cada página, buscar IG ligado: /{page_id}?fields=connected_instagram_account

Retorna pro frontend a lista de páginas + IGs pra ele escolher.

POST /api/v1/instagram/connect

Recebe do frontend qual Page/IG o usuário escolheu.

Cria/atualiza um Channel com type="instagram" e config preenchido.

Aqui você também pode já registrar o webhook (se ainda não estiver configurado globalmente).

POST /api/v1/webhooks/instagram

Endpoint que o Meta chama quando:

Chega nova DM no IG.

Tem mention, reply de story, etc.

Você valida o hub.verify_token na verificação inicial.

Depois, processa os updates e relaciona com:

Channel (via page_id ou ig_user_id).

Contact, Flow, etc. (similar ao conceito do Telegram).

4. O que precisa existir no frontend (Vue)
4.1. Tela “Canais” (Instagram)

Na ChannelsView.vue (ou em uma tela própria de integrações), você vai:

Listar canais existentes (já vem da API).

Ter um card “Instagram” com botão “Conectar Instagram”.

Fluxo no Vue:

Botão “Conectar Instagram”:

GET /api/v1/instagram/auth-url → recebe a URL.

window.location.href = url.

Após o usuário autorizar na Meta, ele volta para o redirect_uri (que pode ser seu frontend).

Ex: /instagram/callback?code=...&state=...

Essa rota de callback no frontend:

Lê code.

Chama GET /api/v1/instagram/callback?code=....

Recebe lista de páginas/IGs disponíveis.

Mostra uma UI para o usuário escolher qual IG conectar.

Usuário seleciona um IG:

Vue faz POST /api/v1/instagram/connect com dados da página/IG selecionados.

A API cria/atualiza o canal no backend.

5. Tokens, permissões e webhooks (visão rápida)
5.1. Permissões importantes

Ao pedir login no OAuth, colocar pelo menos:

pages_show_list

pages_messaging

instagram_basic

instagram_manage_messages

(Talvez business_management dependendo da conta)

Depois você envia o app pra App Review da Meta pra liberar produção.

5.2. Webhooks Meta (Instagram)

No painel do app do Facebook/Meta:

Adicionar produto Webhooks.

Configurar:

Callback URL: https://SEU_BACKEND/api/v1/webhooks/instagram

Verify Token: string que você define e também valida no backend.

Assinar o tópico instagram e campos como messages.

Seu endpoint FastAPI precisa:

GET (para verificação inicial: responder com hub.challenge).

POST (para receber de fato os eventos).

6. Como encaixar isso no seu projeto atual (FastAPI + Vue)

Pensando direto no que você já tem:

Backend (FastAPI)

Criar um módulo/roteador:

app/api/v1/routers/instagram_connect.py
Com rotas:

/instagram/auth-url

/instagram/callback

/instagram/connect

E ajustar o já existente:

app/api/v1/routers/instagram.py

Para ser o webhook oficial de eventos de mensagem (diferente do connect).

Frontend (Vue)

Criar arquivos em src/api/instagram.js:

getInstagramAuthUrl()

finishInstagramAuth(code) (chama /instagram/callback)

connectInstagram(payload) (chama /instagram/connect)

Adicionar na UI:

Botão “Conectar Instagram”.

Tela/modal para escolher a página/conta IG retornada pelo callback.

Se você quiser, próximo passo eu posso:

Montar um .md igual o do Telegram, só que para Integração Instagram, já formatado pra você jogar no Cursor; ou

Já escrever direto o prompt estilo “chefão” pro Cursor, específico pra implementar Instagram Connect (OAuth, salvar Channel.config, webhooks base), usando exatamente a estrutura do seu projeto.