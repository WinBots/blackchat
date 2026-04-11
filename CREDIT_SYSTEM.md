# Modelo de Créditos SaaS - Blackchat

## Visão Geral

Sistema de créditos baseado em dois tipos de moedas:
- **Créditos do Plano**: Renovam mensalmente, não acumulam, uso prioritário
- **Créditos Comprados**: Permanentes, acumulam indefinidamente, fallback

---

## 1. Estrutura de Precificação

### Planos e Alocação de Créditos

| Plano | Créditos/mês | Tipo | Expiração | Preço/mês |
|-------|--------------|------|-----------|-----------|
| **Free** | 1 | Plano | 30 dias | Grátis |
| **Pro** | 10 | Plano | 30 dias | R$ 99,00 |
| **Enterprise** | 25 | Plano | 30 dias | R$ 999,00 |
| **Extras** | 10-100+ | Comprado | Indefinido | R$ 12,50-125,00 |

### Custo Real vs Preço Comercial

**Claude 3.5 Sonnet em BRL:**
- Input: R$ 0,000015 por token
- Output: R$ 0,000075 por token
- **Resposta média (2.000 input + 1.000 output)**: R$ 0,105

**Valor de 1 Crédito (Comprado):**
- Custo real: R$ 0,105 (token API Claude)
- Preço comercial: R$ 1,25 (1.090% markup)
- **Estratégia**: Créditos são operações, não apenas tokens puros. Inclui plataforma + suporte.

---

## 2. Lógica de Consumo

### Ordem de Dedução (CRÍTICO)

Quando um usuário consome 1 crédito:

```
1. Verifica plan_balance > 0?
   ✅ SIM → Deduz 1 do PLANO (prioritário)
   ❌ NÃO → Próximo passo

2. Verifica purchased_balance > 0?
   ✅ SIM → Deduz 1 do COMPRADO (fallback)
   ❌ NÃO → Próximo passo

3. Nenhum saldo disponível?
   🚫 BLOQUEIA operação → Erro 402 "Out of Credits"
```

### Exemplo de Ciclo (Pro)

```
MÊS 1 (1º-31º de Abril):
├─ Dia 1: +10 créditos do PLANO
│         Saldo: 10 (plano) + 0 (comprados)
│
├─ Dia 10: -7 créditos do PLANO
│          Saldo: 3 (plano) + 0 (comprados)
│
├─ Dia 20: +10 créditos COMPRADOS (pagou R$ 12,50)
│          Saldo: 3 (plano) + 10 (comprados)
│
├─ Dia 29: -8 créditos (consome 3 PLANO + 5 COMPRADOS)
│          Saldo: 0 (plano) + 0 (comprados)
│
└─ Dia 31: Reset automático
           ❌ 3 créditos do PLANO não usados = PERDIDOS
           ✅ Créditos COMPRADOS = esgotados (como esperado)

MÊS 2 (1º-30º de Maio):
├─ Dia 1: +10 créditos NOVOS do PLANO
│         Saldo: 10 (plano) + 0 (comprados)
│
└─ (continua...)
```

---

## 3. Ciclo de Vida do Usuário

### Free Trial

```
Dia 1: Signup
  ├─ Recebe 1 crédito
  ├─ Dashboard: "1 crédito disponível"
  └─ Alerta: "Seu crédito expira em 30 dias"

Dia 2: Usa 1 crédito
  ├─ Consome do PLANO
  ├─ Saldo: 0
  └─ Bloqueio automático

Dia 3: Sem créditos
  ├─ CTA 1: "Upgrade para Pro (R$ 99/mês)"
  ├─ CTA 2: "Comprar 5 créditos (R$ 25)"
  └─ CTA 3: "Esperar reset (próximo mês)"
```

### Conversão para Pro

```
Semana 1: Compra 10 créditos extras (R$ 12,50)
  ├─ Saldo: 0 (plano) + 10 (comprados)
  └─ Usa os 10 créditos durante semana

Semana 2: Email marketing
  ├─ "Você testou Blackchat"
  ├─ "Assine Pro e ganhe 10 créditos/mês"
  └─ Proposta: "Economize vs compras avulsas (R$ 12,50 por 10 créditos)"

Semana 3: Conversão
  ├─ Clica: "Upgrade para Pro (R$ 99/mês)"
  ├─ Stripe processa pagamento
  ├─ Recebe 10 créditos do PLANO imediatamente
  └─ Saldo: 10 (plano) + 0 (comprados)
```

### Usuário Pro Recorrente

```
Dia 1 do Mês: Reset automático
  ├─ +10 créditos do PLANO
  ├─ Créditos COMPRADOS preservados
  └─ Email: "Seus novos 10 créditos chegaram!"

Dia 15: Aviso de consumo
  ├─ Consumiu 6 do PLANO
  ├─ Saldo: 4 (plano) + 0 (comprados)
  └─ Email: "Você tem 4 créditos, reseta em 16 dias"

Dia 20: Compra extra
  ├─ Compra 20 créditos (R$ 25,00)
  ├─ Saldo: 4 (plano) + 20 (comprados)
  └─ Continua usando sem bloqueio

Dia 28: Consumo contínuo
  ├─ Usa os 4 do PLANO
  ├─ Depois os 16 dos COMPRADOS (de 20)
  └─ Saldo: 0 (plano) + 4 (comprados)

Dia 1 (Próx. Mês): Reset
  ├─ +10 do PLANO novo
  ├─ 4 créditos COMPRADOS preservados
  └─ Saldo: 10 (plano) + 4 (comprados) = 14 total
  
Observação: Se tivesse comprado 20 e consumido 16, restaria 4 para mês seguinte.
```

---

## 4. Dashboard do Usuário

### Widget de Créditos (Header)

```
┌────────────────────────────────┐
│ 💳 CRÉDITOS                    │
├────────────────────────────────┤
│                                 │
│ 📊 Plano (uso prioritário)      │
│    ████░░░░░░ 4 / 10           │
│                                 │
│ 💳 Comprados (backup)           │
│    ██████░░░░ 6 / 15           │
│                                 │
│ ─────────────────────────────  │
│ ✅ Total: 10 créditos           │
│ ⏰ Reseta em: 18 dias           │
│                                 │
│ [Comprar mais] [Fazer upgrade]  │
└────────────────────────────────┘
```

### Página Detalhada de Créditos

**Seção: Saldo Atual**
```
Créditos do Plano: 4 / 10
  └─ Reseta todo 1º do mês
  └─ Última renovação: 2026-04-01
  └─ Próxima renovação: 2026-05-01

Créditos Comprados: 6 / 15
  └─ Sem expiração
  └─ Comprado em 2026-04-20 (10 créditos por R$ 12,50)
  └─ Comprado em 2026-03-15 (20 créditos por R$ 25,00)
```

**Seção: Histórico de Transações**
```
| Data | Operação | Consumo | Fonte | Saldo Plano | Saldo Comprado |
|------|----------|---------|-------|-------------|----------------|
| 11/04 10:30 | Resposta IA | -1 | Plano | 4 → 3 | 6 |
| 11/04 09:15 | Resposta IA | -1 | Plano | 5 → 4 | 6 |
| 10/04 14:20 | Compra | +10 | — | 5 | 1 → 11 |
| 01/04 00:00 | Reset plano | +10 | — | 0 → 10 | 6 |
```

**Seção: Próximas Ações**
```
⚠️ Você tem 4 créditos do plano
   Reseta em 18 dias
   
💡 Sugestão: Compre créditos extras agora (mínimo 10 por R$ 12,50)
   Continuará usando sem bloqueio
   
🎁 Oferta: Upgrade para Pro e ganhe 10/mês
```

---

## 5. Alertas e Notificações

### Alertas Automáticos

| Evento | Trigger | Ação |
|--------|---------|------|
| **Saldo baixo** | 50% consumido do plano | Email + push notification |
| **Sem créditos** | balance == 0 | Bloqueio de operação + modal |
| **Próxima expiração** | 7 dias antes de reset | Email: "Seus X créditos expiram" |
| **3 dias antes** | 3 dias antes de reset | Reminder email |
| **1 dia antes** | 1 dia antes de reset | Last call email |
| **Reset realizado** | Dia 1º do mês | Confirmação: "10 novos créditos!" |

### Email de Saldo Baixo (Exemplo)

```
Assunto: Seus créditos do Blackchat estão acabando 🚨

Oi João,

Você tem apenas 2 créditos do seu plano Pro.

📊 Seu saldo:
  • 2 créditos do plano (reseta em 16 dias)
  • 0 créditos comprados

Opções:
1️⃣ Compre agora - 10 créditos por R$ 12,50
2️⃣ Upgrade para plano superior
3️⃣ Espere o reset (próximo 1º de maio)

[Comprar créditos] [Ver planos]
```

---

## 6. Regras de Negócio

### Créditos do Plano

- ✅ Renascencem no 1º de cada mês (calendário UTC)
- ❌ Não acumulam (créditos não usados expiram)
- ✅ Uso prioritário (deduzido ANTES de comprados)
- ✅ Inclusos na assinatura (sem custo adicional)

### Créditos Comprados

- ✅ Permanecem indefinidamente
- ✅ Acumulam com novas compras
- ✅ Sem expiração
- ✅ Uso como fallback (deduzido APÓS plano)
- ✅ Preço: R$ 1,25 por crédito
- ✅ Mínimo de compra: 10 créditos (R$ 12,50)

### Operações Bloqueadas

```
Se balance == 0:
  └─ Bloqueia: Resposta IA, processamento de arquivo, etc.
  └─ Mensagem: "Você não tem créditos disponíveis"
  └─ CTA: Upgrade ou comprar créditos
```

### Transações

```
Tipos permitidos:
├─ plan_allocation   (reset mensal automático)
├─ purchased         (compra via Stripe)
├─ consumed          (uso de operação)
├─ refunded          (reembolso por erro)
└─ admin_adjustment  (suporte técnico)

Cada transação registra:
├─ Quantidade
├─ Tipo (allocation/purchased/consumed/refunded/adjustment)
├─ Fonte (plan ou purchased) — para consumo
├─ Saldo antes e depois
└─ Timestamp
```

---

## 7. Integração Stripe

### Fluxo de Compra de Créditos Extras

```
1. Usuário clica "Comprar 5 créditos (R$ 25)"
   ├─ Frontend abre checkout Stripe
   └─ SKU: "credit_5_brl" / Preço: R$ 25

2. Stripe processa pagamento
   ├─ Cartão aprovado
   └─ Webhook: POST /webhooks/stripe

3. Webhook Blackchat
   ├─ Verifica assinatura Stripe
   ├─ Extrai user_id e amount
   ├─ UPDATE user_credits.purchased_balance += 5
   ├─ INSERT credit_transactions (type='purchased', ...)
   └─ Retorna 200 OK

4. Frontend atualiza
   ├─ Refresh balance
   ├─ Mostra modal sucesso
   └─ Email: "5 créditos adicionados!"
```

### Fluxo de Assinatura (Pro/Enterprise)

```
1. Usuário clica "Assinar Pro"
   ├─ Abre checkout Stripe
   └─ SKU: "plan_pro_monthly" / Preço: R$ 99

2. Stripe processa assinatura
   ├─ Cria subscription
   ├─ Webhook: POST /webhooks/stripe (event: invoice.payment_succeeded)
   └─ Cobrança recorrente configurada

3. Webhook Blackchat
   ├─ Verifica assinatura Stripe
   ├─ UPDATE users.subscription_plan = 'pro'
   ├─ UPDATE user_credits.plan_monthly_allocation = 10
   ├─ UPDATE user_credits.plan_balance = 10
   ├─ INSERT credit_transactions (type='plan_allocation', ...)
   └─ Retorna 200 OK

4. Cronjob (diário 00:00 UTC)
   ├─ Encontra usuários com reset_date == hoje
   ├─ plan_balance = plan_monthly_allocation
   ├─ reset_date = próximo 1º
   └─ Registra transaction type='plan_allocation'
```

---

## 8. Banco de Dados

### Tabela: user_credits

```sql
CREATE TABLE user_credits (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
  
  -- Créditos do plano (não acumulam)
  plan_balance INTEGER DEFAULT 0,
  plan_monthly_allocation INTEGER DEFAULT 0,
  plan_reset_date DATE,
  
  -- Créditos comprados (acumulam)
  purchased_balance INTEGER DEFAULT 0,
  
  -- Metadata
  subscription_plan VARCHAR(50) DEFAULT 'free', -- 'free', 'pro', 'enterprise'
  subscription_started_at TIMESTAMP,
  last_reset_at TIMESTAMP,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_credits_user_id ON user_credits(user_id);
CREATE INDEX idx_user_credits_plan_reset_date ON user_credits(plan_reset_date);
```

### Tabela: credit_transactions

```sql
CREATE TABLE credit_transactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  
  -- Tipo de transação
  type VARCHAR(50), -- 'plan_allocation', 'purchased', 'consumed', 'refunded', 'admin_adjustment'
  source VARCHAR(50), -- 'plan' ou 'purchased' (para consumed)
  
  -- Quantidades
  amount INTEGER NOT NULL,
  reason TEXT,
  
  -- Saldos antes e depois
  plan_balance_before INTEGER,
  plan_balance_after INTEGER,
  purchased_balance_before INTEGER,
  purchased_balance_after INTEGER,
  
  -- Auditoria
  created_by VARCHAR(255), -- 'system', 'admin', 'stripe', etc
  stripe_event_id VARCHAR(255), -- para rastreabilidade Stripe
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_credit_transactions_user_id ON credit_transactions(user_id);
CREATE INDEX idx_credit_transactions_created_at ON credit_transactions(created_at);
CREATE INDEX idx_credit_transactions_type ON credit_transactions(type);
```

---

## 9. APIs

### POST /api/v1/credits/consume

Deduz 1 crédito de um usuário (com prioridade).

**Request:**
```json
{
  "operation": "ai_response" // tipo de operação (para logging)
}
```

**Response (Sucesso):**
```json
{
  "success": true,
  "consumed": 1,
  "source": "plan", // "plan" ou "purchased"
  "balance": {
    "plan": 3,
    "purchased": 5,
    "total": 8
  }
}
```

**Response (Erro - Sem créditos):**
```json
{
  "success": false,
  "error": "out_of_credits",
  "message": "Você não tem créditos disponíveis",
  "status": 402,
  "balance": {
    "plan": 0,
    "purchased": 0,
    "total": 0
  }
}
```

---

### GET /api/v1/credits/balance

Retorna saldo atual do usuário.

**Response:**
```json
{
  "plan_balance": 3,
  "plan_monthly_allocation": 10,
  "plan_reset_date": "2026-05-01",
  
  "purchased_balance": 5,
  
  "total": 8,
  "subscription_plan": "pro",
  "subscription_started_at": "2026-04-01T10:30:00Z"
}
```

---

### POST /api/v1/credits/purchase

Compra créditos extras via Stripe.

**Request:**
```json
{
  "amount": 5, // quantidade de créditos (5, 10, 20)
  "price_in_cents": 2500 // R$ 25.00
}
```

**Response:**
```json
{
  "success": true,
  "stripe_session_id": "cs_test_...",
  "checkout_url": "https://checkout.stripe.com/...",
  "purchased_balance": 10
}
```

---

### GET /api/v1/credits/history

Retorna histórico de transações.

**Query Parameters:**
```
?limit=20&offset=0&type=consumed
```

**Response:**
```json
{
  "total": 142,
  "transactions": [
    {
      "id": "uuid",
      "type": "consumed",
      "source": "plan",
      "amount": 1,
      "plan_balance_before": 5,
      "plan_balance_after": 4,
      "purchased_balance_before": 2,
      "purchased_balance_after": 2,
      "reason": "ai_response",
      "created_at": "2026-04-11T10:30:00Z"
    },
    {
      "id": "uuid",
      "type": "purchased",
      "amount": 5,
      "plan_balance_before": 4,
      "plan_balance_after": 4,
      "purchased_balance_before": 2,
      "purchased_balance_after": 7,
      "stripe_event_id": "evt_...",
      "created_at": "2026-04-10T15:20:00Z"
    }
  ]
}
```

---

### POST /api/v1/admin/credits/adjust

Adiciona/remove créditos manualmente (apenas admin).

**Request:**
```json
{
  "user_id": "uuid",
  "amount": 5, // positivo para adicionar, negativo para remover
  "reason": "promotion_easter_2026",
  "type": "admin_adjustment"
}
```

**Response:**
```json
{
  "success": true,
  "new_balance": {
    "plan": 10,
    "purchased": 8,
    "total": 18
  }
}
```

---

## 10. Cronjobs

### Reset Automático de Créditos (Diário 00:00 UTC)

```python
# Executa todo dia à meia-noite UTC
@app.scheduled_task('0 0 * * *')
def reset_monthly_credits():
    """
    Renova créditos do plano para usuários cujo reset_date == hoje
    """
    today = date.today()
    
    # Encontra usuários que precisam de reset
    users_to_reset = db.query(UserCredits).filter(
        UserCredits.plan_reset_date == today,
        UserCredits.subscription_plan.in_(['pro', 'enterprise'])
    ).all()
    
    for user_credit in users_to_reset:
        old_balance = user_credit.plan_balance
        user_credit.plan_balance = user_credit.plan_monthly_allocation
        user_credit.plan_reset_date = date.today().replace(day=1) + relativedelta(months=1)
        user_credit.last_reset_at = datetime.now()
        
        # Log na tabela de transações
        transaction = CreditTransaction(
            user_id=user_credit.user_id,
            type='plan_allocation',
            amount=user_credit.plan_monthly_allocation,
            plan_balance_before=old_balance,
            plan_balance_after=user_credit.plan_balance,
            purchased_balance_before=user_credit.purchased_balance,
            purchased_balance_after=user_credit.purchased_balance,
            reason=f'Monthly reset for {user_credit.subscription_plan} plan',
            created_by='system'
        )
        db.add(transaction)
        
        # Email de confirmação
        send_email(
            user_credit.user.email,
            "Seus créditos foram renovados!",
            f"Você recebeu {user_credit.plan_monthly_allocation} créditos novos."
        )
    
    db.commit()
    logger.info(f"Reset completed for {len(users_to_reset)} users")
```

### Alertas de Expiração (Diário)

```python
@app.scheduled_task('8 9 * * *')  # 09:08 UTC (evita :00/:30)
def send_expiration_alerts():
    """
    Envia alertas de expiração de créditos em 7, 3, 1 dias
    """
    today = date.today()
    
    # 7 dias antes de reset
    in_7_days = today + timedelta(days=7)
    users_7d = db.query(UserCredits).filter(
        UserCredits.plan_reset_date == in_7_days,
        UserCredits.plan_balance > 0
    ).all()
    
    for user_credit in users_7d:
        send_email(
            user_credit.user.email,
            "Atenção: Seus créditos expiram em 7 dias",
            f"Você tem {user_credit.plan_balance} créditos que expiram em {user_credit.plan_reset_date}"
        )
    
    # Similar para 3 dias e 1 dia
    # ...
```

---

## 11. Roadmap de Implementação

### Fase 1: Estrutura Base (Semana 1-2)

- [ ] Tabelas `user_credits` e `credit_transactions`
- [ ] Endpoint `POST /api/v1/credits/consume` com lógica de prioridade
- [ ] Endpoint `GET /api/v1/credits/balance`
- [ ] Cronjob de reset automático
- [ ] Integração básica com Stripe webhooks

### Fase 2: Frontend + UX (Semana 3-4)

- [ ] Widget de créditos no header
- [ ] Página detalhada de créditos
- [ ] Modal "Sem créditos" com CTAs
- [ ] Histórico de transações
- [ ] Alertas visuais (50%, 80%, 100% consumido)

### Fase 3: Automação + Relatórios (Semana 5-6)

- [ ] Webhooks Stripe completos (purchase + subscription)
- [ ] Alertas automáticos por email (7, 3, 1 dias)
- [ ] Admin dashboard de receita
- [ ] Endpoint admin para ajuste manual
- [ ] Analytics: taxa de conversão, churn, top-ups

---

## 12. Testes

### Casos de Teste Críticos

```gherkin
Scenario: Usuário Free tenta usar sem créditos
  Given um usuário Free com 0 créditos
  When tenta consumir 1 crédito
  Then retorna erro 402 "out_of_credits"
  And bloqueia a operação

Scenario: Pro com créditos do plano se esgota, usa comprados
  Given um usuário Pro com 2 (plano) + 5 (comprados)
  When consome 8 créditos
  Then deduz 2 do PLANO primeiro
  And deduz 6 do COMPRADOS depois
  And saldo final: 0 (plano) + -1 (comprados) ❌ ERRO!
  
  # Corrigir: bloqueia ao atingir 0

Scenario: Reset mensal não acumula plano
  Given um usuário Pro com 2 créditos no dia 31
  When dia 1º chega
  Then PERDE os 2 do plano
  And recebe 10 NOVOS do plano

Scenario: Créditos comprados persistem entre resets
  Given um usuário Pro com 0 (plano) + 3 (comprados) no dia 31
  When dia 1º chega
  Then recebe 10 do PLANO novo
  And mantém 3 do COMPRADOS
  And saldo total: 13

Scenario: Compra de créditos via Stripe
  Given um usuário Pro com 5 créditos totais
  When compra 5 créditos por R$ 25
  And Stripe webhook retorna sucesso
  Then purchased_balance += 5
  And novo saldo total: 10
  And email: "5 créditos adicionados!"
```

---

## 13. Segurança e Validações

### Validações de Entrada

```python
def consume_credit(user_id: UUID, operation: str) -> dict:
    # Valida user_id
    if not user_id or not isinstance(user_id, UUID):
        raise ValidationError("Invalid user_id")
    
    # Valida operation
    if operation not in ALLOWED_OPERATIONS:
        raise ValidationError(f"Operation '{operation}' not allowed")
    
    # Fetch user_credits com lock pessimista (evita race condition)
    user_credit = db.query(UserCredits).with_for_update().filter(
        UserCredits.user_id == user_id
    ).first()
    
    if not user_credit:
        raise NotFoundError("User credits not found")
    
    # Verifica saldo
    total_balance = user_credit.plan_balance + user_credit.purchased_balance
    if total_balance <= 0:
        raise OutOfCreditsError("No credits available")
    
    # ... rest of logic
```

### Rate Limiting

```
POST /api/v1/credits/consume:
  └─ 100 requests / minute per user
  └─ 10000 requests / hour per IP
```

### Auditoria

Todas as transações de crédito devem ser logadas:
- Quem (user_id)
- O quê (type, amount)
- Quando (timestamp)
- Por quê (reason)
- De onde (source IP, created_by)

---

## 14. Troubleshooting

### Usuário perdeu créditos inesperadamente

```sql
-- Auditar transações do usuário
SELECT * FROM credit_transactions 
WHERE user_id = 'user_id_aqui' 
ORDER BY created_at DESC 
LIMIT 50;

-- Recalcular saldo atual
SELECT 
  user_id,
  plan_balance,
  purchased_balance,
  (plan_balance + purchased_balance) as total
FROM user_credits 
WHERE user_id = 'user_id_aqui';
```

### Cronjob não executou

```
Verificar logs:
  1. systemd: journalctl -u blackchat-cron
  2. Application: grep "reset_monthly_credits" app.log
  3. Database: SELECT last_reset_at FROM user_credits WHERE plan_reset_date < NOW()

Se reset não executou:
  1. Verificar se cronjob está ativo
  2. Rodar manualmente: python manage.py reset_credits --force
```

### Webhook Stripe não processou

```
Verificar:
  1. Stripe event log em dashboard.stripe.com
  2. Logs da aplicação: grep "webhook" app.log
  3. Tabela payment_events (se existe)

Se falhou:
  1. Reprocessar webhook manualmente
  2. Ou adicionar créditos manualmente via admin
```

---

## 15. Exemplos de Preço

### Créditos Comprados

| Quantidade | Preço | Preço/Crédito |
|-----------|-------|---------------|
| 10 | R$ 12,50 | R$ 1,25 |
| 20 | R$ 25,00 | R$ 1,25 |
| 50 | R$ 62,50 | R$ 1,25 |
| 100 | R$ 125,00 | R$ 1,25 |

**Nota:** Mínimo de compra = 10 créditos. Múltiplos de 10 recomendados.

### Comparação com Planos

| Cenário | Custo | Créditos | Preço/Crédito |
|---------|-------|----------|---------------|
| Free (limite) | R$ 0 | 1 | N/A (grátis) |
| Compra mínima (10 créditos) | R$ 12,50 | 10 | R$ 1,25 |
| Compra 20 créditos | R$ 25,00 | 20 | R$ 1,25 |
| Pro (10 créditos/mês) | R$ 99/mês | 10 | R$ 9,90 |
| Enterprise (25 créditos/mês) | R$ 999/mês | 25 | R$ 39,96 |

**Insight**: Pro é mais caro por crédito, mas ideal para uso recorrente (comprometimento mensal).

---

## 16. FAQ

**P: Por que créditos do plano não acumulam?**
R: Cria urgência de uso mensal e força engagement contínuo com a plataforma.

**P: Posso transferir créditos entre usuários?**
R: Não. Créditos são pessoais e intransferíveis.

**P: Posso pedir reembolso de créditos comprados?**
R: Política de reembolso será definida separadamente. Por padrão: não reembolsável.

**P: Qual é o limite máximo de créditos comprados?**
R: Não há limite. Usuário pode comprar quantos quiser.

**P: O que acontece se minha assinatura cancelar?**
R: Créditos do plano expiram imediatamente. Créditos comprados permanecem válidos.

---

## 17. Referências

- Documentação Stripe: https://stripe.com/docs
- Claude API Pricing: https://www.anthropic.com/pricing
- SaaS Credit Systems: https://www.saasvalue.com

