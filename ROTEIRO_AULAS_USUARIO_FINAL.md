# Roteiro de Gravação — Curso Blackchat Pro (Usuário Final)

Público: pessoas que vão usar o sistema no dia a dia (sem termos de programação).

Formato sugerido: aulas curtas (3–7 min), com foco em “o que é / para que serve / como usar”.

---

## Módulo 0 — Boas-vindas e visão geral do sistema

### Aula 0.1 — O que você vai conseguir fazer aqui
- Objetivo: mostrar o “antes e depois” (manual vs. automatizado).
- Mostre rapidamente o menu: **Dashboard**, **Contatos**, **Automações**, **Mensagens em massa**, **Configurações**.
- Frase pronta: “Hoje você vai aprender a conectar seu Telegram, criar automações e disparar campanhas para segmentos de contatos.”

### Aula 0.2 — Onde fica cada coisa (tour de 60 segundos)
- Abra o menu lateral.
- Explique em 1 frase cada item:
  - **Dashboard**: visão geral e atividade recente.
  - **Contatos**: sua base (filtros, tags, campos, exportação).
  - **Automações**: seus fluxos (criar, ativar, duplicar, organizar).
  - **Mensagens em massa**: selecionar público e disparar um fluxo.
  - **Configurações**: conta, planos/cobrança e Telegram.

---

## Módulo 1 — Configurando o ambiente (começo do zero)

### Aula 1.1 — Criando sua conta
- Caminho: página inicial → **Começar Grátis**.
- Preencha: **Nome completo**, **E-mail**, **Empresa**, **Senha**.
- Dica de fala: “Use um e-mail que você realmente acessa, porque é ele que identifica sua conta.”

### Aula 1.2 — Entrando no sistema
- Caminho: **Entrar**.
- Mostre: e-mail + senha.
- Boas práticas: “Se é um computador compartilhado, não marque ‘Lembrar de mim’.”

### Aula 1.3 — Esqueci minha senha (recuperação)
- Caminho: tela de login → **Esqueceu a senha?**
- Explique o fluxo: solicitar → receber instruções → redefinir.

### Aula 1.4 — Configurações: o que é cada coisa (aba Geral)
- Caminho: menu → **Configurações** → **Geral**.
- Explique campos:
  - **Nome da conta**: nome que aparece para sua equipe.
  - **Email (somente leitura)**: seu login.
  - **Fuso horário**: deixa datas/horários corretos nos relatórios e atividades.
  - **Salvar**: aplica mudanças.
  - **Sair**: encerra a sessão.

---

## Módulo 2 — Conectando o Telegram (primeiro canal)

### Aula 2.1 — O que significa “conectar um bot do Telegram”
- Fala simples: “Você cria um bot no Telegram e conecta aqui para que o sistema possa responder automaticamente.”
- Resultado esperado: o bot aparece como **ativo** em Configurações.

### Aula 2.2 — Criando seu bot no Telegram (BotFather) — passo a passo
- No Telegram, procure por **@BotFather**.
- Envie: `/newbot`.
- Siga o passo a passo:
  - Defina um **nome** (ex.: “Atendimento Minha Empresa”).
  - Defina um **username** (precisa terminar com `bot`, ex.: `minhaempresa_atendimento_bot`).
  - Copie o **código do bot** que o BotFather entrega (o sistema chama isso de “token”).
- Dica: guarde esse código em local seguro.

### Aula 2.3 — Conectando o bot no Blackchat Pro
- Caminho: **Configurações** → **Telegram**.
- Mostre a tela “Bots do Telegram Conectados”.
- Clique para adicionar/conectar.
- Cole o **código do bot** (token) e conclua.
- Final: o bot deve aparecer na lista, com status **ativo**.

### Aula 2.4 — Gerenciando bots conectados (editar, ativar e desativar)
- Ainda em **Configurações → Telegram**, mostre a lista de bots.
- Mostre ações comuns:
  - **Renomear** o bot (nome interno para sua equipe).
  - **Ativar/Desativar** um bot (quando você quer pausar atendimentos).
  - **Atualizar o código do bot** (se você recriar o bot no BotFather).
- Alerta de fala: “Se um bot estiver inativo, seus fluxos podem aparecer com aviso e não vão responder mensagens.”

### Aula 2.5 — Boas práticas do Telegram antes do primeiro teste
- Defina uma foto e descrição do bot no BotFather (deixa mais profissional).
- Evite usar o bot pessoal como atendimento (crie um dedicado por marca/produto).

### Aula 2.6 — Teste rápido: mandando a primeira mensagem para o bot
- Abra o bot no Telegram.
- Envie um “oi”.
- Explique: “Se ainda não existem automações ativas, ele pode ficar em silêncio — isso é normal.”

---

## Módulo 3 — Primeira automação do zero (do jeito certo)

### Aula 3.1 — O que é uma automação (fluxo)
- Fala simples: “Um fluxo é um caminho de conversa: quando alguém manda X, o bot faz Y.”
- Onde fica: menu → **Automações**.

### Aula 3.2 — Criando seu primeiro fluxo
- Caminho: **Automações** → **Criar Fluxo**.
- Preencha nome e descrição com objetivo claro (ex.: “Menu Principal”).
- Dica: nomeie pensando na equipe (ex.: “Vendas — Qualificação”, “Suporte — Triagem”).

### Aula 3.3 — Entendendo a lista de fluxos
- Mostre a tabela:
  - **Gatilho**: como inicia.
  - **Keywords**: palavras que disparam.
  - **Status**: ativo/inativo.
- Mostre ações rápidas:
  - **Editar**
  - **Duplicar**
  - **Excluir**
  - Chave liga/desliga (ativar/desativar)

### Aula 3.4 — Editor do fluxo: como se movimentar
- Abra um fluxo → **Editar**.
- Ensine o básico:
  - Arrastar blocos.
  - Conectar saídas (↘) nas entradas (↖).
  - Zoom e “Reset Zoom”.
  - Botão **Salvar**.

### Aula 3.5 — Avisos importantes: bot inativo e limites do seu plano
- Volte na lista de **Automações** e mostre:
  - Aviso **“Bot inativo”**: significa que o canal/bot do fluxo está desativado.
  - Contador de **quantidade de fluxos** do seu plano e o link **Upgrade** quando estiver no limite.
- Fala simples: “Se você travar no limite, primeiro revise e apague/una fluxos repetidos; se precisar de mais, faça upgrade.”

---

## Módulo 4 — Gatilhos: como o fluxo começa

### Aula 4.1 — Gatilho por mensagem (keywords)
- No editor: **Adicionar Gatilho**.
- Explique “Se a mensagem contém…”
- Exemplos de keywords:
  - `preço`, `orcamento`, `comprar`
  - `suporte`, `ajuda`, `problema`
- Dica essencial: use palavras específicas (evite `oi`, `ola`).

### Aula 4.2 — Como evitar conflito de keywords (duplicadas)
- Fala simples: “Se dois fluxos tiverem a mesma keyword, pode ficar confuso qual vai disparar.”
- Solução prática:
  - padronize um “dicionário” de keywords por área.
  - separe por intenção (vendas vs suporte).
  - desative fluxos que não estão em uso.

### Aula 4.3 — Gatilho por link (Link de Referência do Telegram)
- Quando usar: anúncios, bio do Instagram, e-mail, QR code.
- No gatilho, configure a **chave de referência**.
- Mostre o campo “Seu Link de Referência pronto para usar” e o botão **Copiar**.
- Opcional: “Salvar parâmetro em Campo Personalizado” para registrar a campanha/origem.

---

## Módulo 5 — Blocos de Conteúdo (mensagens do bot)

### Aula 5.0 — Iniciar Automação (o “começo” do fluxo)
- Explique a diferença:
  - **Gatilho**: define *como* o fluxo começa.
  - **Iniciar Automação**: a primeira etapa do caminho (normalmente uma mensagem de boas-vindas).
- Mostre um padrão simples: **Gatilho** → **Iniciar Automação** → **Mensagem Telegram**.

### Aula 5.1 — Mensagem Telegram: texto
- Adicione o bloco **Mensagem Telegram**.
- Mostre como escrever uma mensagem curta e clara.
- Dica: uma pergunta por vez.

### Aula 5.2 — Mensagem Telegram: mídias (imagem, vídeo, áudio)
- Mostre que o mesmo bloco envia mídias.
- Boas práticas:
  - imagem: use para cardápio, tabela simples, banner.
  - vídeo: curto, com legenda.
  - áudio: use com moderação (muita gente prefere texto).

### Aula 5.3 — Variáveis (personalização) sem complicação
- Mostre o botão de **Variáveis** nos campos.
- Explique com exemplo:
  - “Olá {primeiro_nome}, tudo bem?”
- Diga o benefício: “Mensagem parece 1:1, mesmo sendo automática.”

---

## Módulo 6 — Bloco “Ações”: organizando e qualificando contatos

### Aula 6.1 — Para que servem as Ações
- Fala simples: “Ações atualizam o contato: guardam respostas, colocam tags e organizam a base.”

### Aula 6.2 — Definir Campo Personalizado (guardar informação)
- Exemplo prático: salvar **cidade**, **interesse**, **orçamento**, **telefone**.
- Mostre:
  - **Nome do Campo** (ex.: `cidade`)
  - **Valor** (ex.: `{ultima_mensagem}` para guardar o que a pessoa respondeu)

### Aula 6.3 — Tags: marcar contatos por interesse/etapa
- Ação: **Adicionar Tag** e **Remover Tag**.
- Exemplos de tags:
  - `lead_quente`, `cliente_vip`, `aguardando_pagamento`, `precisa_suporte`
- Dica: padronize tags (sem espaços, tudo minúsculo).

### Aula 6.4 — Sequências: iniciar/parar uma sequência automática
- Mostre as ações:
  - **Iniciar Sequência**
  - **Parar Sequência**
- Explicação simples: “Uma sequência é uma série de mensagens em dias/horas diferentes.”
- Observação de gravação: se sua conta não usa sequências ainda, grave como ‘conceito’ e use exemplos.

### Aula 6.5 — Ir para Fluxo (trocar de conversa)
- Use quando: “menu → vendas”, “menu → suporte”, “voltar ao início”.
- Mostre o seletor de fluxo.

### Aula 6.6 — Ir para Passo (atalhos dentro do mesmo fluxo)
- Use quando: pular etapas, voltar para menu, criar caminho rápido.
- Mostre o seletor de passos.

### Aula 6.7 — Atraso (esperar antes de seguir)
- Mostre a ação **Atraso Inteligente** (na lista de ações).
- Exemplo: “esperar 1 hora e depois enviar lembrete.”

### Aula 6.8 — Notificar Admin / Inbox (avisar a equipe)
- Use quando: lead “quente”, pedido urgente, solicitação de humano.
- Configure:
  - **Mensagem de notificação** (com variáveis)
  - **Tag adicional** (opcional)

### Aula 6.9 — Integrações externas (no sistema: “Requisição Externa / Webhook”)
- Explicação sem termos técnicos: “Serve para enviar dados do contato para outra ferramenta (ex.: planilhas, Zapier, Make).”
- O que você preenche:
  - um **link** (URL)
  - o tipo de envio (GET/POST/PUT)
  - “Headers” só se a ferramenta pedir (normalmente você copia/cola de um tutorial).
- Dica: se você não usa integrações, pode ignorar por enquanto.

---

## Módulo 7 — Blocos de Lógica (quando você quer automações mais inteligentes)

### Aula 7.1 — Condição (IF/ELSE): caminhos diferentes
- Use quando: “se tem tag X, então manda oferta; se não tem, manda conteúdo.”
- Configure:
  - Tipo: **Campo**, **Tag** ou **Variável**
  - Operador (igual, contém, existe…)
- Feche com dica: “Comece simples: 1 condição por vez.”

### Aula 7.2 — Randomizador (A/B): testar duas mensagens
- Use quando: comparar abordagem A vs B.
- Configure percentuais até somar **100%**.
- Dica: rode por um tempo e compare resultados.

### Aula 7.3 — Atraso Inteligente (bloco)
- Use quando: você quer espaçar mensagens e evitar “spam”.
- Tipos:
  - **Fixo**
  - **Aleatório**
  - **Inteligente** (horário comercial)

---

## Módulo 8 — Blocos de Fluxos e organização

### Aula 8.1 — Ir para outro Fluxo (bloco dedicado)
- Use quando: você quer “encaminhar” o contato para um fluxo completo.
- Mostre o bloco **Ir para outro Fluxo** e como escolher o destino.

### Aula 8.2 — Comentário: documentação dentro do fluxo
- Use para anotar regras do time, lembrar decisões e explicar por que algo existe.
- Mostre o seletor de cor.

### Aula 8.3 — Salvando e revisando antes de ativar
- Checklist:
  - fluxo tem gatilho?
  - mensagens têm variáveis corretas?
  - tags/campos estão padronizados?
  - existem keywords repetidas?
  - testou no Telegram?

---

## Módulo 9 — Configuração de “quando não há match”

### Aula 9.1 — O que acontece quando ninguém acerta uma keyword
- Caminho: **Automações** (no topo da página).
- Card: **Resposta Quando Não Há Match**.
- Explique as opções visíveis:
  - **Ignorar** (bot fica em silêncio)
  - outras opções podem aparecer como **Em breve**.
- Mostre salvar a configuração.

---

## Módulo 10 — Contatos: sua base, filtros e segmentação

### Aula 10.1 — Entendendo a tela de Contatos
- Caminho: menu → **Contatos**.
- Mostre:
  - busca por nome/username
  - total de contatos
  - botão **Exportar**

### Aula 10.2 — Filtrar por canal
- Use quando: quer ver só os contatos de um bot/canal.
- Mostre a lista de canais na coluna esquerda.

### Aula 10.3 — Tags: ver, filtrar e combinar
- Mostre como clicar em tags para filtrar.
- Explique que tags viram “etapas” do funil.

### Aula 10.4 — Campos: filtrar por informações do contato
- Mostre como escolher um campo e um valor.
- Exemplos:
  - `cidade = São Paulo`
  - `interesse_produto = Plano Pro`

### Aula 10.5 — Segmentos: salvar filtros para usar depois
- Monte um filtro.
- Clique em **Salvar filtros como segmento**.
- Depois aplique o segmento com 1 clique.

### Aula 10.6 — Exportar contatos
- Clique em **Exportar**.
- Explique casos de uso: relatório, auditoria, CRM.

### Aula 10.7 — Abrindo um contato (painel de detalhes)
- Clique em um contato da lista.
- Mostre o painel da direita:
  - nome, username e canal
  - campos personalizados (quando existirem)
  - tags do contato

### Aula 10.8 — Gerenciar tags direto no contato
- Ainda no painel do contato, mostre as tags.
- Remova uma tag (quando existir) e explique o impacto: “tags mudam o segmento e podem mudar o caminho do fluxo.”

### Aula 10.9 — Aba Chat: vendo as conversas
- No contato, clique na aba **Chat**.
- Mostre a lista de conversas e as mensagens.
- Fala simples: “Aqui você entende o contexto antes de responder ou ajustar a automação.”

### Aula 10.10 — Enviar um fluxo para um contato (1:1)
- Na linha do contato (na lista), mostre o botão de ação **Enviar fluxo**.
- Use caso real: “mandar um fluxo de boas-vindas”, “reenviar instruções”, “retomar atendimento”.

### Aula 10.11 — Seleção em massa (operações rápidas)
- Selecione 2–3 contatos usando o checkbox.
- Mostre a barra de ações em massa (quando aparecer).
- Explique o objetivo: “aplicar uma ação em vários contatos sem abrir um por um.”

### Aula 10.12 — Mesclar duplicados (quando o mesmo contato aparece mais de uma vez)
- Dentro do contato, mostre a opção de **mesclar duplicados** (se disponível).
- Explique sem termos técnicos: “Ele une registros repetidos para você não ter contagem/segmentação errada.”
- Boas práticas: faça isso quando perceber contatos repetidos por canal ou importação.

---

## Módulo 11 — Mensagens em massa (campanhas e disparos)

### Aula 11.1 — Conceito: não é “enviar texto”, é “disparar um fluxo”
- Caminho: **Mensagens em massa**.
- Explicação simples: “Você escolhe o público e dispara uma automação.”

### Aula 11.2 — Combinar condições: Todas (E) vs Qualquer (OU)
- Mostre o toggle.
- Exemplos:
  - **Todas (E)**: “Tag = cliente_vip” E “cidade = SP”.
  - **Qualquer (OU)**: “Tag = cliente_vip” OU “Tag = lead_quente”.

### Aula 11.3 — Condições mais usadas (público)
- Mostre as opções:
  - busca por nome/username
  - canal
  - tags
  - campos (do sistema e personalizados)
  - última interação (dias)
  - criado após / criado antes

### Aula 11.4 — Alcance estimado e limites
- Mostre “Alcance estimado”.
- Diga: “Se aparecer ‘Acima do limite’, reduza o público ou divida em campanhas.”

### Aula 11.5 — Disparando o fluxo certo
- Selecione um fluxo pensado para campanhas (ex.: “Campanha Março”).
- Explique boas práticas:
  - mensagem curta
  - CTA claro
  - opção de parar/voltar ao menu

### Aula 11.6 — Conferindo a prévia do público antes de disparar
- Mostre que o sistema calcula o **Alcance estimado**.
- Abra a visualização/preview do público (quando disponível na tela).
- Dica: “Antes de disparar, confira se as regras não estão amplas demais.”

---

## Módulo 12 — Dashboard: leitura rápida do dia

### Aula 12.1 — O que olhar no Dashboard em 1 minuto
- Mostre os cards:
  - **Total de Contatos**
  - **Fluxos Ativos**
  - **Canais Conectados**
- Explique “Atividade Recente” (quem fez o quê recentemente).
- Clique em **Atualizar**.

---

## Módulo 13 — Planos e Cobrança (quando chegar a hora de escalar)

### Aula 13.1 — Onde ver seu plano atual
- Caminho: **Configurações** → **Cobrança**.
- Mostre:
  - Plano atual
  - Período
  - Botão **Gerenciar cobrança**

### Aula 13.2 — Onde comparar e assinar um plano
- Caminho: **Configurações** → **Planos**.
- Mostre os cards.
- Explique:
  - plano grátis
  - plano Pro
  - Enterprise (personalizado)

### Aula 13.3 — Estimativa do ciclo (quando aparecer)
- Explique a “Estimativa do ciclo atual” de forma simples:
  - quantos contatos ativos (últimos 30 dias)
  - estimativa de valor
- Dica: acompanhe isso para evitar surpresas.

### Aula 13.4 — Após assinar: confirmando que está tudo certo
- Mostre a tela de confirmação (Obrigado por assinar).
- Clique em **Ver meu plano**.
- Confirme em **Configurações → Cobrança** se o plano atual mudou.

---

## Módulo 14 — Rotina de operação (checklist do usuário final)

### Aula 14.1 — Checklist diário (5 min)
- Dashboard → olhar atividade.
- Contatos → ver novos leads e aplicar tags.
- Automações → garantir que fluxos importantes estão ativos.

### Aula 14.2 — Checklist semanal (15 min)
- Revisar keywords (evitar duplicadas).
- Revisar segmentos.
- Ajustar mensagens e CTAs.
- Exportar contatos (se necessário).

---

## Módulo 15 — (Opcional) Super Admin (somente para quem tiver acesso)

### Aula 15.1 — O que é a área “Super Admin”
- Explique: “É uma área administrativa avançada. Se você não vê no menu, ignore.”
- Mostre como entrar e para que serve (visão de gestão da operação).

---

## Apêndice — Roteiros rápidos de exemplos prontos (para gravar como bônus)

### Bônus A — “Menu principal” em 7 minutos
- Gatilho: keyword `menu`.
- Mensagem: “Escolha: 1 Vendas | 2 Suporte”.
- Ação: tag `no_menu`.
- Caminhos: ir para fluxo de vendas / fluxo de suporte.

### Bônus B — “Qualificação de lead” em 10 minutos
- Perguntas em mensagens curtas.
- Guardar respostas em campos (cidade, interesse, orçamento).
- Tag final: `lead_qualificado`.
- Notificar equipe quando orçamento alto.

### Bônus C — “Campanha para clientes VIP” em 8 minutos
- Segmento: tag `cliente_vip`.
- Mensagens em massa: disparar um fluxo de oferta.
- Atraso: espaçar 1 hora entre etapas.

