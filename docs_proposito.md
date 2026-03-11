# Plataforma de Automação de Conversas - WinChat
## 1. Visão Geral do Produto

Este projeto é uma plataforma SaaS de **automação de conversas** (chatbots e fluxos de mensagens), construída com **stack própria (FastAPI + Vue)** e com arquitetura aberta, extensível e multi-tenant.

O objetivo é permitir que qualquer tipo de negócio (infoprodutor, agência, e-commerce, serviços, iGaming, educação, etc.) crie experiências automatizadas de:
- Atendimento inicial (boas-vindas, dúvidas frequentes);
- Captação e qualificação de leads;
- Nutrição, engajamento e remarketing;
- Comunicação transacional e relacional (avisos, lembretes, confirmações).

Na fase inicial, o foco de canais será:
- **Telegram Bot**;
- **Instagram Direct (Instagram Messaging API)**.

Outros canais (WhatsApp, Webchat próprio, e-mail, SMS, etc.) poderão ser adicionados em fases posteriores, sem alterar o núcleo da plataforma.

---

## 2. Objetivo Principal

Criar um **hub central de automação de mensagens** que:

1. Centralize conversas de múltiplos canais;
2. Permita criar **fluxos de automação (flows)** sem programação;
3. Gerencie **contatos/subscribers**, tags e atributos personalizados;
4. Reaja a **eventos internos e externos** (mensagens, comandos, webhooks);
5. Seja comercializado como **SaaS com planos de assinatura**.

---

## 3. Objetivos Específicos

- Entregar recursos completos de automação, com foco inicial em:
  - Fluxos baseados em mensagens, perguntas, condições e ações;
  - Gestão de contatos, tags e campos personalizados;
  - Automatizações disparadas por gatilhos de mensagem ou eventos externos;
  - Envio de campanhas / broadcasts (respeitando as regras de cada canal).

- Oferecer uma experiência pronta para **agências e experts**:
  - Multi-workspace (um usuário pode gerenciar vários projetos/empresas);
  - Organização de bots/canais por workspace;
  - Isolamento de dados por tenant.

- Manter o **core 100% neutro de nicho**, permitindo criar “packs” de templates para mercados específicos sem contaminar a arquitetura:
  - Ex.: Pack iGaming, Pack Educação, Pack Clínica, etc.

---

## 4. Escopo do MVP

### 4.1. Funcionalidades Incluídas

1. **Autenticação e Multi-tenant**
   - Login com e-mail e senha;
   - Associação de usuários a um ou mais workspaces (tenants);
   - Troca de workspace dentro do painel.

2. **Canais (Channels)**
   - Cadastro e configuração de canais por workspace:
     - Telegram Bot (token, webhook);
     - Instagram Direct (dados do app Meta e IG Business).
   - Teste de conexão e status do canal (ativo/inativo).

3. **Contatos (Subscribers)**
   - Criação automática de contatos quando interagem com um canal;
   - Campos padrão: nome, username, idioma, origem, etc.;
   - **Tags** (segmentação simples);
   - **Campos personalizados** (atributos customizáveis por tenant).

4. **Fluxos (Flows)**
   - Criação de fluxos de automação com steps em lista (sem builder visual complexo no MVP);
   - Tipos de step:
     - Mensagem (texto, com variáveis);
     - Pergunta (captura de resposta);
     - Aplicar/Remover tag;
     - Definir atributo (campo customizado);
     - Condição simples (IF/ELSE baseado em tag/atributo);
     - Espera (delay em segundos/minutos);
     - Chamada de Webhook (disparar evento em API externa);
   - Gatilhos (triggers):
     - Mensagem/Comando recebido (ex.: `/start`, “menu”);
     - Evento externo (ex.: `order.paid`, `user.registered`).

5. **Eventos Externos**
   - Endpoint único de eventos (`POST /events/external`);
   - Mapeamento de `event_type` para fluxos que devem ser disparados;
   - Associação de eventos a contatos (por ID externo, telefone, dado de canal, etc.).

6. **Broadcasts (Versão Simples)**
   - Envio de uma mensagem para um segmento de contatos filtrado por tags/atributos;
   - Suporte inicial a Telegram e Instagram;
   - Controle básico de status (pendente/enviando/concluído).

7. **Histórico e Logs**
   - Visualização das mensagens enviadas/recebidas por contato;
   - Histórico de eventos e execuções de fluxo (para debug e auditoria).

### 4.2. Funcionalidades Fora do Escopo do MVP

- Builder visual em canvas com drag-and-drop (pode ser fase 2);
- Dashboard analítico avançado (gráficos, funis detalhados);
- Suporte a WhatsApp e outros canais de alto custo (fase posterior);
- White label completo (domínios customizados, branding completo).

---

## 5. Personas Alvo

1. **Expert / Infoprodutor**  
   - Vende cursos, mentorias, sinais, consultorias;
   - Quer automatizar boas-vindas, qualificação, ofertas e reminders.

2. **Agência / Social Media**  
   - Gera leads para vários clientes;
   - Necessita gerenciar múltiplos bots e fluxos em um único painel;
   - Valoriza métricas e organização multi-workspace.

3. **Pequenas e Médias Empresas**  
   - E-commerce, consultórios, serviços profissionais;
   - Querem respostas automáticas, captura de dados e nutrição básica.

---

## 6. Visão de Futuro

- Adicionar novos canais: WhatsApp, Webchat próprio, e-mail, SMS;
- Evoluir o editor de fluxos para uma experiência mais visual;
- Criar biblioteca de templates por nicho;
- Integrar billing automático com gateway (Stripe, Mercado Pago, etc.);
- Entregar relatórios de performance e engajamento mais avançados.

Essa documentação de propósito serve como base conceitual para decisões técnicas, priorização de backlog e alinhamento com times de produto/negócio.
