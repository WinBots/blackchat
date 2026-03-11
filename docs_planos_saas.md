# Planos de Assinatura – Proposta Inicial

## 1. Premissas de Precificação

Antes de definir os planos, consideramos:

- **Canais do MVP**: Telegram e Instagram (ambos com custo de API praticamente zero; o principal custo é infraestrutura);
- Público-alvo principal:
  - Experts/infoprodutores;
  - Agências pequenas/médias;
  - Pequenas empresas;
- Estrutura de custos do SaaS:
  - Servidores (backend, banco, redis);
  - Domínio, SSL, monitoramento;
  - Trabalho de suporte e manutenção.

A estratégia é começar com **3 planos simples**, fáceis de entender, priorizando:

- Limite por número de **contatos ativos**;
- Limite de **canais conectados** (bots e IGs);
- Recursos liberados por plano;
- Valores que permitam margem para crescer e cobrir custos fixos.

Os valores são sugestões iniciais em **R$ (BRL)** e podem ser ajustados depois com base na aceitação do mercado e nos custos reais de operação.

---

## 2. Resumo dos Planos

- **Plano START** – Para iniciantes e pequenos projetos
- **Plano PRO** – Para experts e pequenas empresas com base ativa
- **Plano AGENCY** – Para agências e operações multi-projetos

---

## 3. Detalhamento dos Planos

### 3.1. Plano START

**Objetivo**: permitir que um usuário teste seriamente a plataforma em um projeto pequeno, com baixo risco financeiro.

- **Preço sugerido**: **R$ 97,00 / mês**
- **Características**:
  - Até **1 workspace** (1 projeto/empresa);
  - Até **1 canal Telegram** conectado;
  - Até **1 canal Instagram** conectado;
  - Até **2.000 contatos ativos**;
  - Fluxos ilimitados dentro do limite de contatos;
  - Broadcasts limitados (ex.: até 5 campanhas/mês);
  - Registro de eventos externos (webhooks) limitado (ex.: até 2.000 eventos/mês);
  - Suporte por e-mail.

**Indicado para**:
- Experts/infoprodutores em início de operação;
- Pequenos negócios testando automação pela primeira vez;
- Projetos que ainda não têm grande volume de leads.

---

### 3.2. Plano PRO

**Objetivo**: atender a operação principal de um expert ou pequeno/médio negócio com base relevante de leads.

- **Preço sugerido**: **R$ 197,00 / mês**
- **Características**:
  - Até **3 workspaces** (ex.: negócios/projetos diferentes);
  - Até **3 canais Telegram** conectados;
  - Até **3 canais Instagram** conectados;
  - Até **10.000 contatos ativos**;
  - Fluxos ilimitados;
  - Broadcasts ilimitados (com limites saudáveis de rate interno);
  - Registro de eventos externos mais amplo (ex.: até 20.000 eventos/mês);
  - Segmentação avançada por tags e atributos personalizados;
  - Suporte por e-mail + canal prioritário (ex.: WhatsApp/Telegram de suporte).

**Indicado para**:
- Experts com mais de um produto/projeto;
- Pequenas e médias empresas com listas maiores;
- Operações que já fazem lançamentos, campanhas recorrentes e remarketing.

---

### 3.3. Plano AGENCY

**Objetivo**: atender agências e operações que cuidam de múltiplos clientes/projetos, com necessidade de escala e organização.

- **Preço sugerido**: **R$ 497,00 / mês**
- **Características**:
  - Até **10 workspaces** (clientes/projetos);
  - Até **10 canais Telegram** conectados;
  - Até **10 canais Instagram** conectados;
  - Até **50.000 contatos ativos** no total (somando todos os workspaces);
  - Fluxos ilimitados em todos os workspaces;
  - Broadcasts ilimitados (com controle de rate e filas);
  - Registro de eventos externos ampliado (ex.: até 100.000 eventos/mês);
  - Permissões avançadas por usuário/tenant (owner/admin/editor/viewer);
  - Acesso prioritário a novas features e templates;
  - Suporte prioritário (SLA melhor, canal direto).

**Indicado para**:
- Agências que gerenciam automações para múltiplos clientes;
- Operações de nicho com várias marcas ou subprojetos;
- Quem precisa de organização multi-conta e mais volume.

---

## 4. Possíveis Add-ons e Upsells Futuros

Mesmo com 3 planos principais, você pode criar **add-ons** para aumentar faturamento por cliente:

- **Add-on de Contatos Extras**:
  - Ex.: pacotes adicionais de 5.000 contatos por R$ XX/mês;
- **Add-on de Eventos Externos Extras**:
  - Ex.: pacotes de eventos para integrações intensivas;
- **Add-on de Canais Extras**:
  - Cliente PRO que quer mais canais Telegram/Instagram;
- **White Label (sobre o AGENCY)**:
  - Customização de domínio, logo, cores (R$ adicional fixo/mês).

---

## 5. Regras Gerais de Uso por Plano (Sugestões)

- Considerar **contatos ativos** aqueles que tiveram alguma interação nos últimos X meses (ex.: 12 meses);
- Bloquear novos envios/broadcasts quando o plano estiver:
  - Com contatos acima do limite;
  - Com número de eventos externos muito acima do contratado;
- Exibir sempre no painel:
  - Uso atual (contatos, canais, eventos) vs limite do plano;
  - Botão claro de upgrade de plano.

---

## 6. Roadmap de Billing

1. **Fase 1 – Manual / Semi-automatizado**
   - Controle de planos e limites no banco (campos na tabela `tenants`);
   - Upgrades/downgrades ajustados manualmente;
   - Cobrança feita manualmente ou por outro sistema (ex.: checkout externo).

2. **Fase 2 – Integração com Gateway de Pagamento**
   - Integração com Stripe / Mercado Pago / Asaas etc.;
   - Planos cadastrados no gateway;
   - Webhooks de cobrança para:
     - Ativar/desativar tenants;
     - Atualizar plano automaticamente.

3. **Fase 3 – Billing mais avançado**
   - Cálculo de uso real (contatos/eventos) e cobrança variável;
   - Métricas de MRR, churn, LTV etc. no painel admin.

---

## 7. Ajustes Futuros de Preço

Os valores sugeridos (R$ 97 / 197 / 497) são um ponto de partida. É esperado que:

- Sejam ajustados após:
  - Validação do mercado;
  - Análise de concorrentes diretos;
  - Entendimento do custo real de infraestrutura;
- Sejam complementados com planos anuais com desconto (ex.: 2 meses grátis).

Essa documentação de planos serve como base para:

- Criar a página de preços no site;
- Implementar validação de limites no backend;
- Guiar o desenho da tabela de `tenants` e campos relacionados a plano/limites.
