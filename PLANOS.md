# Documentação Consolidada — Planos, Billing (VPM), Excedentes e Stripe (Telegram SaaS)

## 1) Objetivo

Esta documentação define:

* os **planos comerciais** (Free, Pro, Enterprise)
* o modelo de cobrança por **VPM (valor por 1.000 contatos ativos)**
* as regras de **excedente de limite do plano**
* a modelagem e fluxo de **Stripe Billing**
* as regras mínimas para implementação no sistema (backend + billing + produto)

---

## 2) Escopo atual do produto (estado real)

### Canal suportado

* **Telegram** (único canal por enquanto)

### Recursos que **não existem ainda** (não prometer como disponíveis)

* Controle de colaboradores/usuários (multiusuário)
* Webhooks do produto
* API pública
* Templates prontos

> Esses itens podem aparecer como **“em breve”** internamente, mas não devem ser vendidos como ativos.

---

## 3) Modelo de Precificação (VPM)

## 3.1 Conceito

**VPM = Valor por Mil contatos ativos/mês**

### Fórmula base

* `preco_mensal = blocos_de_1000 * VPM`
* `blocos_de_1000 = ceil(contatos_ativos / 1000)`

### Regra de mínimo mensal

Cada plano pago possui **valor mínimo mensal**:

* Pro: mínimo R$ 99
* Enterprise: mínimo R$ 999

### Fórmula final (com mínimo)

* `valor_calculado = ceil(contatos_ativos / 1000) * VPM`
* `valor_final = max(valor_calculado, minimo_mensal)`

---
### ⚠️ Estado atual da implementação Stripe (realidade do código)

> **Importante para IA/dev:** O que está documentado acima é o modelo de precificação IDEAL.
> O código atual implementa de forma simplificada:

* **Stripe cobra preço fixo** por assinatura (Price estático, `quantity=1`).
* **VPM é calculado no backend** (`/api/v1/billing/vpm-estimate`) e exibido no painel — mas **não é enviado para a Stripe como uso medido**.
* Portanto, **excedente de VPM não é cobrado automaticamente** na fatura da Stripe hoje.
* Para escalar para cobrança real por volume, será necessário migrar para **metered billing** (Opção C) ou lançar invoice items manualmente.
* O limite do Free usa **`count_active_contacts`** (contatos que interagiram nos últimos 30 dias) — consistente com a definição de VPM.

---
## 3.2 Definição de “contato ativo” (billing)

**Contato ativo** = contato que:

* interagiu com o bot nos últimos **30 dias**
  **ou**
* recebeu/enviou mensagem no mês

### Regras obrigatórias de apuração (para evitar disputa)

Definir no sistema:

* **momento de apuração** (ex.: fechamento mensal)
* **timezone oficial de billing** (recomendado: `America/Sao_Paulo` ou UTC, mas fixar uma)
* **arredondamento**: bloco de 1.000 com `ceil`
* **reprocessamento** de dados atrasados (se houver)

---

## 4) Planos

## 4.1 Free (mínimo possível)

**Preço:** R$ 0/mês

### Objetivo

Plano para **teste** da ferramenta, não para operação real.

### Limites

* Até **100 contatos ativos**
* **1 fluxo**
* **1 gatilho**
* **1 sequência**
* **1 tag**
* **1 usuário** (sem controle de colaboradores)

### Recursos

* Chat ao vivo Telegram: ✅ *(se já existir)*
* Teste A/B: ❌
* Webhooks: ❌
* API: ❌
* Templates prontos: ❌

---

## 4.2 Pro (plano principal)

**Preço:** **R$ 49 / 1.000 contatos ativos**
**Mínimo mensal:** **R$ 99/mês**

### Limites

* **3 bots** no Telegram
* **1.000 contatos ativos**
* **10 fluxos** de automação
* **5 gatilhos** de entrada
* **10 sequências** de mensagens
* Tags: **Ilimitadas**
* **3 colaboradores**

### Recursos

* Chat ao vivo Telegram: ✅
* Teste A/B: ✅ *(somente se existir; se não existir, usar ❌ ou “em breve”)*
* Webhooks: ❌
* API: ❌
* Templates prontos: ❌

### Posicionamento

Para operações em crescimento que precisam de automação no Telegram com cobrança por volume.

---

## 4.3 Enterprise (escala)

**Preço:** **R$ 29 / 1.000 contatos ativos**
**Mínimo mensal:** **R$ 999/mês**

### Inclui

* Tudo do Pro
* **5 bots** no Telegram
* Contatos ativos: **Ilimitados (VPM)**
* Fluxos/Gatilhos/Sequências: **Ilimitados**
* Tags: **Ilimitadas**
* **5 usuários administradores**
* Suporte prioritário 24/7 ✅

### Recursos ainda indisponíveis (hoje)

* Webhooks: ❌ *(em breve)*
* API: ❌ *(em breve)*
* Templates prontos: ❌

### Posicionamento

Para operações com maior volume e necessidade de prioridade no atendimento.

---

## 4.4 Resumo rápido (pricing)

### Free

* **R$ 0/mês**
* Até **100 contatos ativos**
* Recursos mínimos

### Pro

* **R$ 49 por 1.000 contatos ativos**
* **Mínimo R$ 99/mês**

### Enterprise

* **R$ 29 por 1.000 contatos ativos**
* **Mínimo R$ 999/mês**

---

## 4.5 Exemplos de cálculo (VPM)

### Pro (R$ 49 / 1.000)

* 1.000 contatos = R$ 49 → **cobra R$ 99 (mínimo)**

### Enterprise (R$ 29 / 1.000, mínimo R$ 999)

* 20.000 contatos = R$ 580 → **cobra R$ 999 (mínimo)**
* 50.000 contatos = **R$ 1.450**
* 100.000 contatos = **R$ 2.900**

---

# 5) Regras de Excedente do Plano (IMPORTANTE)

## 5.1 Visão geral

Toda regra de excedente deve seguir este princípio:

> **Não quebrar a operação inteira por causa de um excedente específico.**
> Bloquear apenas a funcionalidade excedida, com aviso e tolerância quando possível.

---

## 5.2 Excedente de limite de usuários (colaboradores) — **JÁ DOCUMENTADO**

### Contexto atual

Hoje o sistema **ainda não tem controle de colaboradores/usuários**.

### Consequência

* **Não há aplicação automática ainda**
* Mas a regra já fica definida para implementação futura

### Regra recomendada (futura)

#### 1) Soft limit (aviso)

Ao atingir 100% do limite:

* alerta no painel
* aviso por e-mail/Telegram
* orientação de upgrade ou add-on

#### 2) Grace period (tolerância)

Ao ultrapassar:

* permitir por **3 a 7 dias**
* exibir aviso de upgrade

#### 3) Hard limit parcial (bloqueio parcial)

Após tolerância:

* **bloquear apenas novos convites**
* manter usuários existentes ativos
* **não pausar automações**
* **não desconectar Telegram**

### O que NÃO fazer

* bloquear conta inteira
* pausar fluxos
* remover usuários sem aviso

### Exemplo futuro

Se Pro permitir 3 usuários:

* 3/3 = normal
* tentativa de adicionar 4º = aviso de limite
* com tolerância: permite por 7 dias
* após prazo: bloqueia novos convites até regularizar

### Monetização futura recomendada

* **Add-on por usuário extra** (ex.: R$ 29/mês por usuário extra)
* alternativa: upgrade obrigatório

---

## 5.3 Excedente de contatos ativos (VPM) — regra de cobrança (ESSENCIAL)

Este é o excedente **mais importante hoje**, porque já impacta billing.

> **⚠️ Realidade atual (código):** A Stripe está configurada com **preço fixo** (não metered). O VPM é calculado e exibido no painel, mas o excedente de volume **não é cobrado automaticamente** pela Stripe. Qualquer ajuste de cobrança por volume hoje é manual. A migração para metered billing é a Fase 3 do roadmap.

### Regra recomendada

Quando o cliente ultrapassar o volume implícito do preço atual:

* **não bloquear automações imediatamente**
* recalcular valor no próximo ciclo (ou via ajuste conforme estratégia)
* avisar no painel que o volume aumentou e haverá ajuste de cobrança

### Opções de tratamento

#### Opção A — Reajuste no próximo ciclo (recomendado para começar)

* mede contatos ativos no fechamento
* recalcula preço
* atualiza assinatura para o próximo mês

#### Opção B — Cobrança de excedente na fatura

* cobra mínimo/base
* lança excedente como item adicional

#### Opção C — Usage-based (metered)

* envia uso para Stripe
* Stripe calcula automaticamente ao final do período

### O que evitar

* travar bot ao ultrapassar contatos
* bloquear envio/automações sem aviso
* mudar preço sem regra clara e sem comunicação

---

## 5.4 Excedente no Free (limite de 100 contatos)

### Regra sugerida (simples e clara)

Quando Free atingir 100 contatos:

* mostrar aviso de limite no painel
* impedir crescimento adicional da base **ou** impedir novas automações/novas entradas (escolher uma regra clara)
* incentivar upgrade para Pro

### Recomendação prática

**Bloquear novas entradas acima de 100** (mais claro), mas:

* manter operação existente funcionando de forma limitada
* não apagar contatos
* não quebrar bot de forma abrupta

---

# 6) Política operacional de limites (resumo de produto)

## 6.1 Princípios

* Transparência no painel
* Avisos antes de bloqueio
* Grace period quando possível
* Bloqueio parcial da funcionalidade excedida
* Não interromper automações sem necessidade

## 6.2 Ordem padrão de tratamento

1. Detecta limite atingido
2. Registra evento interno
3. Mostra aviso no painel
4. Envia notificação (e-mail/Telegram)
5. Aplica tolerância (se existir)
6. Aplica bloqueio parcial
7. Remove bloqueio após upgrade/regularização

---

# 7) Stripe Billing — Modelo para este SaaS

## 7.1 Conceito da Stripe (atual)

A Stripe usa:

* **Product** = o que você vende
* **Price** = preço + recorrência
* **Subscription** = assinatura do cliente

> Não é necessário usar “Plan” (modelo antigo).
> Para assinatura recorrente, você precisa de um **Price recorrente**.

---

## 7.2 Dá para trabalhar recorrência sem “plano cadastrado”?

### Sim

Você pode trabalhar recorrência sem “plano” no sentido antigo.

### Mas precisa de:

* **`Price` recorrente** para criar `Subscription`

Esse Price pode ser:

* pré-cadastrado no dashboard
* criado dinamicamente via API

---

## 7.3 Estratégias de implementação na Stripe

### Opção A — Prices fixos por faixa (simples)

Criar vários preços por faixas de contatos.

**Prós**

* simples
* fácil de usar com Checkout

**Contras**

* engessado
* manutenção de várias faixas

---

### Opção B — Price dinâmico por cliente/ciclo (**recomendado agora**)

Criar preço recorrente via API conforme cálculo do VPM.

**Prós**

* flexível
* bom para pricing em evolução
* combina com vendas consultivas

**Contras**

* mais objetos no catálogo da Stripe

---

### Opção C — Usage-based / metered (futuro)

Cobrança por uso medido real.

**Prós**

* ideal para VPM variável
* escalável

**Contras**

* mais complexo de implementar

---

## 7.4 Recomendação por estágio

### Agora (fase atual)

Usar **Opção B (Price dinâmico)**

### Depois (escala)

Migrar para **usage-based/metered**

---

## 7.5 ⚠️ Implementação real atual (estado do código)

> O código atual usa **Opção A — Prices fixos** (simplificado).

* Checkout Session cria `Subscription` com `price_id` fixo do banco + `quantity=1`
* Não há cálculo dinâmico de valor no momento da contratação
* VPM é calculado **depois**, no endpoint `/api/v1/billing/vpm-estimate`, apenas para exibição no painel
* Para cobrar o valor real de VPM, seria necessário ou:
  * **Opção B**: recalcular e recriar o Price antes do checkout, **ou**
  * **Opção C**: usar meter events na Stripe (metered billing)

**Recomendação de caminho de migração:**
1. Curto prazo: criar Price dinâmico antes do checkout (Opção B)
2. Médio prazo: migrar para meter events (Opção C)

---

# 8) Fluxo de cobrança com Stripe (implementação)

## 8.1 Fluxo de contratação (Pro/Enterprise)

### 1. Criar/recuperar Customer

Associar customer da Stripe à conta/workspace do sistema.

### 2. Calcular valor

Com base em:

* plano (Pro / Enterprise)
* contatos ativos
* VPM
* mínimo mensal

### 3. Criar Product/Price (se preço dinâmico)

Criar `Price` recorrente mensal em BRL com valor final.

### 4. Criar Subscription

Criar assinatura da conta com aquele `Price`.

### 5. Aguardar confirmação via webhook

**Não liberar acesso apenas pelo frontend.**

### 6. Provisionar acesso no sistema

Liberar plano após evento de pagamento/assinatura ativa.

---

## 8.2 Fluxo com Stripe Checkout (recomendado para começar)

### Passos

1. Backend cria Checkout Session (`mode=subscription`)
2. Informa `line_items` com `Price` recorrente
3. Cliente paga na página da Stripe
4. Stripe redireciona para `success_url` / `cancel_url`
5. Sistema confirma por webhook e ativa plano

---

## 8.3 Webhooks da Stripe (obrigatório)

## Por que obrigatório?

Para sincronizar corretamente:

* assinatura ativa
* pagamento aprovado
* falha de cobrança
* cancelamento

## Regras técnicas mínimas

* validar assinatura do webhook
* salvar evento recebido
* processar com **idempotência**
* atualizar estado local da assinatura
* registrar logs de erro e reprocessamento

## Eventos relevantes (conceito)

* checkout concluído (se usar Checkout)
* invoice paga
* invoice com falha
* subscription criada/atualizada/cancelada

> Implementar com mapeamento exato dos eventos usados no fluxo escolhido.

---

# 9) Estados de assinatura no sistema (interno)

## 9.1 Estados sugeridos

* `free`
* `trialing`
* `active`
* `past_due`
* `unpaid`
* `canceled`

## 9.2 Comportamento sugerido

* `active`: acesso normal
* `past_due`: acesso mantido + avisos
* `unpaid`: restringir ações sensíveis / upgrades
* `canceled`: downgrade para Free ao fim do ciclo (ou imediato, conforme política)

> Evitar bloqueio abrupto de automações na primeira falha.

---

# 10) Regras de upgrade, downgrade e cobrança

## 10.1 Upgrade (Pro ↔ Enterprise)

### Recomendação

* recalcular valor com novo VPM e mínimo
* definir se aplica:

  * **imediato com prorrata**
  * **no próximo ciclo** (mais simples)

## 10.2 Downgrade

### Recomendação

* aplicar no próximo ciclo
* comunicar data efetiva ao cliente

## 10.3 Falha de pagamento

### Política recomendada

1. falha → `past_due`
2. avisar cliente (e-mail/Telegram)
3. tentar nova cobrança
4. se persistir → restringir ações sensíveis
5. cancelar/downgrade após prazo

### Evitar

* desligar bot imediatamente
* apagar dados
* desconectar Telegram

---

# 11) Estrutura de dados mínima (backend)

## 11.1 `accounts` / `workspaces`

* `id`
* `plan_name` (`free`, `pro`, `unlimited`) *("unlimited" = Enterprise)*
* `billing_status`
* `current_contacts_active`
* `timezone_billing`
* `billing_cycle_anchor`
* `limits_snapshot` (json opcional)

## 11.2 `stripe_customers`

* `account_id`
* `stripe_customer_id`

## 11.3 `stripe_subscriptions`

* `account_id`
* `stripe_subscription_id`
* `stripe_price_id`
* `status`
* `current_period_start`
* `current_period_end`

## 11.4 `billing_snapshots`

* `account_id`
* `period_start`
* `period_end`
* `active_contacts_count`
* `thousand_blocks`
* `vpm_value`
* `minimum_applied`
* `final_amount`
* `plan_name`

## 11.5 `stripe_webhook_events`

* `stripe_event_id`
* `type`
* `received_at`
* `processed_at`
* `status`
* `payload_json`
* `idempotency_key`

## 11.6 `limit_events` (recomendado)

* `account_id`
* `limit_type` (`contacts`, `users`, `flows`, etc.)
* `limit_value`
* `current_value`
* `detected_at`
* `status` (`warning`, `grace_period`, `blocked_partial`, `resolved`)
* `resolved_at`

---

# 12) Regras de aplicação no sistema (backend/produto)

## 12.1 Middleware/serviço de checagem de limites

Criar um serviço central para validar limites por conta antes de ações críticas.

### Exemplo de ações que precisam validação

* criar fluxo
* criar gatilho
* criar sequência
* criar tag
* adicionar usuário (futuro)
* processar novas entradas no Free > 100 contatos

## 12.2 Resposta padrão de limite excedido

Retornar estrutura padronizada (exemplo conceitual):

* `code`: `PLAN_LIMIT_EXCEEDED`
* `limit_type`: `contacts`
* `current`: 101
* `limit`: 100
* `action_blocked`: `new_contact_entry`
* `upgrade_required`: true
* `suggested_plan`: `pro`

---

# 13) Checklist de implementação (prioridade)

## Fase 1 — MVP comercial cobrando

* [ ] Definir timezone de billing
* [ ] Implementar apuração de contatos ativos
* [ ] Implementar cálculo VPM + mínimo
* [ ] Criar planos no backend (`free`, `pro`, `unlimited`) *("unlimited" = Enterprise)*
* [ ] Aplicar limites do Free (100 contatos, 1 fluxo, 1 gatilho, 1 sequência, 1 tag)
* [ ] Integrar Stripe Customer + Subscription
* [ ] Criar Price dinâmico mensal
* [ ] Criar Checkout (opcional, recomendado)
* [ ] Implementar webhooks Stripe
* [ ] Sincronizar status de assinatura
* [ ] Ativar/desativar plano via estado de billing

## Fase 2 — Robustez

* [ ] Idempotência de webhooks
* [ ] Logs e reprocessamento de eventos
* [ ] Snapshots de billing por ciclo
* [ ] Notificações de limite e cobrança
* [ ] Tela de billing no painel
* [ ] Política de upgrade/downgrade clara

## Fase 3 — Escala

* [ ] Usage-based / metered billing
* [ ] Add-on de usuários extras (quando houver colaboradores)
* [ ] Customer portal
* [ ] Prorrata automatizada
* [ ] Relatórios de reconciliação Stripe x sistema

---

# 14) Texto de política (pronto para uso no produto/termos)

## 14.1 Política de limite de usuários (futuro)

Quando o cliente atingir o limite de usuários do plano, ele receberá um aviso no painel. Caso tente adicionar novos usuários acima do limite, o sistema bloqueará apenas novos convites, sem interromper automações já ativas. Dependendo do plano, poderá ser feito upgrade ou contratação de usuários extras.

## 14.2 Política de cobrança por volume (VPM)

Os planos pagos são cobrados com base na quantidade de contatos ativos no período de faturamento, em blocos de 1.000 contatos, conforme o VPM do plano contratado, respeitado o valor mínimo mensal aplicável. A definição de contato ativo e a regra de apuração são informadas na documentação comercial e nos termos de uso.

---

# 15) Pontos de atenção (evitar erro de implementação)

* Não liberar plano pago só com retorno do frontend (usar webhook)
* Não mudar preço sem snapshot da apuração
* Não bloquear automações por excedente de forma abrupta
* Não prometer recursos que ainda não existem
* Não deixar indefinido:

  * timezone de billing
  * data de apuração
  * arredondamento por mil
  * comportamento em falha de pagamento

---

# 16) Conclusão prática (recomendação final)

## Implementar agora

* Planos definidos (Free / Pro / Enterprise)
* VPM com mínimo mensal
* Stripe com **Price recorrente dinâmico**
* Webhooks para ativação e status
* Regras de limite no Free
* Política documentada de excedente (incluindo usuários, para quando lançar)

## Implementar depois

* Multiusuário/colaboradores
* Add-on de usuário extra
* Webhooks/API do produto
* Usage-based metered billing completo

---

## Confirmação importante

✅ **Esta documentação já contempla a regra de “exceder limite do plano”**, incluindo:

* excedente de **usuários** (futuro, com soft limit + tolerância + bloqueio parcial)
* excedente de **contatos** (VPM / cobrança)
* excedente do **Free (100 contatos)**
---

# 17) FAQ para IA — Perguntas frequentes sobre o billing

> Esta seção existe para que IAs (Copilot, ChatGPT, etc.) que analisem este projeto entendam o estado real da implementação antes de sugerir código.

---

## Q: O excedente de VPM é cobrado automaticamente?

**Não.** O Stripe está configurado com **preço fixo**. O VPM é calculado e exibido no painel, mas o cliente só paga o valor base da assinatura. Para cobrar automaticamente por volume, é necessário migrar para metered billing (Fase 3).

---

## Q: O que é "contato ativo" no sistema?

Contato que **interagiu com o bot nos últimos 30 dias** (enviou ou recebeu mensagem). A contagem usa a função `count_active_contacts(db, tenant_id)` no `billing_service.py`, que verifica a tabela `messages` com janela de 30 dias.

---

## Q: O Free limita 100 contatos totais ou ativos?

**Ativos** (janela de 30 dias). A função `check_contact_limit` chama `count_active_contacts`, não `count_total_contacts`.

---

## Q: Como funciona o mínimo mensal?

Se o valor calculado (blocos × VPM) for menor que o mínimo do plano, cobra-se o mínimo. Exemplo: Pro com 500 contatos ativos = 1 bloco × R$49 = R$49 → cobra R$99 (mínimo). O endpoint `/api/v1/billing/vpm-estimate` retorna `minimum_applied: true` nesse caso.

---

## Q: O VPM é enviado para a Stripe?

**Não.** O VPM é calculado localmente e exibido no painel frontend (widget "Estimativa de Cobrança" na aba Cobrança). A Stripe só recebe o `price_id` do plano contratado.

---

## Q: O que o webhook da Stripe processa?

Eventos: `checkout.session.completed`, `customer.subscription.created`, `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.payment_succeeded`, `invoice.payment_failed`. Todos com idempotência por `stripe_event_id`.

---

## Q: Qual o range de estados de billing possíveis?

`trial` → `active` → `past_due` (1–2 falhas) → `unpaid` (3+ falhas) → `canceled`. Mapeados do status da Stripe subscription para estado interno em `billing_service.py`.