# Integração Stripe do BlackChat

## Objetivo

Ajustar a integração Stripe do sistema **BlackChat** para seguir exatamente esta arquitetura.

---

## 1. Modelo de planos

O sistema possui 3 planos:

### FREE
- Não passa pela Stripe.
- É controlado 100% pelo backend.
- Não deve gerar customer, checkout ou subscription na Stripe.

### PRO
- Plano recorrente mensal fixo.
- Valor: **R$ 99,00/mês**.
- Na Stripe ele usa **Product + Price fixo recorrente mensal**.
- O backend deve usar o **Price ID** cadastrado na Stripe para criar a assinatura.
- O Product ID do Pro pode ser salvo por organização, mas o fluxo principal usa o **Price ID**.
- A Stripe usa preços recorrentes para subscriptions e ambientes de teste e produção têm chaves e objetos separados.

### ENTERPRISE
- Plano recorrente mensal personalizado.
- O valor é definido pelo backend com base na quantidade de contatos escolhida pelo cliente.
- O volume de contatos é controlado pelo backend do BlackChat, não pela Stripe.
- Na Stripe, o Enterprise deve usar **inline/custom pricing** no momento da criação da assinatura.
- O preço inline/custom deve continuar sendo **recorrente mensal**.
- Para isso, o backend deve usar o **Product ID** do produto `BlackChat Enterprise` e criar a assinatura com preço mensal inline/custom.
- Importante: preços inline/custom não devem ser tratados como preços reutilizáveis de catálogo.

---

## 2. Regras de ambiente: teste e produção

O sistema deve suportar **Stripe Test** e **Stripe Live**.

A Stripe separa totalmente os ambientes:
- cada ambiente tem suas próprias chaves
- products e prices de teste não funcionam em produção
- objects de teste não podem ser usados no live mode

### Requisitos
Implementar suporte completo para:
- **secret key de teste**
- **publishable key de teste**
- **secret key de produção**
- **publishable key de produção**
- **webhook secret de teste**
- **webhook secret de produção**
- **price id do plano Pro em teste**
- **price id do plano Pro em produção**
- **product id do Enterprise em teste**
- **product id do Enterprise em produção**

### Regra de seleção de ambiente
- O **superadmin** deve conseguir alternar um **toggle global** entre:
  - `TEST`
  - `LIVE`
- Esse toggle deve ficar salvo no backend/banco.
- Toda chamada Stripe deve obedecer esse ambiente ativo.
- O frontend nunca deve decidir a lógica Stripe sozinho; ele apenas envia a intenção, e o backend resolve quais chaves e IDs usar.

---

## 3. Configuração persistida no banco

Todas as configurações Stripe devem ficar persistidas no banco de dados, para permitir edição sem depender de variáveis fixas no código.

### Estrutura esperada
Criar uma estrutura de configuração administrativa para Stripe contendo pelo menos:

#### Campos de configuração
- `stripe_mode_active` → `test` ou `live`
- `stripe_test_secret_key`
- `stripe_test_publishable_key`
- `stripe_test_webhook_secret`
- `stripe_test_pro_price_id`
- `stripe_test_enterprise_product_id`
- `stripe_live_secret_key`
- `stripe_live_publishable_key`
- `stripe_live_webhook_secret`
- `stripe_live_pro_price_id`
- `stripe_live_enterprise_product_id`

### Requisitos adicionais
- Os campos sensíveis devem ser protegidos no backend e nunca expostos integralmente ao frontend.
- O frontend pode exibir parcialmente as chaves mascaradas.
- O backend deve validar se a configuração necessária existe antes de permitir checkout ou criação de assinatura.
- O superadmin deve conseguir editar essas configurações por tela administrativa.

---

## 4. Painel do superadmin

Criar uma área administrativa Stripe no painel do superadmin com:

### Seção de ambiente
- toggle global:
  - `Modo de teste`
  - `Modo de produção`

### Seção de chaves
- publishable key de teste
- secret key de teste
- webhook secret de teste
- publishable key de produção
- secret key de produção
- webhook secret de produção

### Seção de IDs Stripe
- price id do Pro em teste
- price id do Pro em produção
- product id do Enterprise em teste
- product id do Enterprise em produção

### Requisitos de UX
- mostrar qual ambiente está ativo
- permitir salvar alterações
- mascarar campos sensíveis
- exibir validações claras quando faltar alguma configuração

---

## 5. Comportamento do checkout/assinatura

### Para o plano PRO
Quando o usuário escolher o plano PRO:
- o backend deve buscar o ambiente ativo
- selecionar a secret key correta
- selecionar o `price_id` correto do Pro conforme ambiente
- criar a assinatura/checkout usando esse `price_id`

### Para o plano ENTERPRISE
Quando o usuário escolher o plano Enterprise:
- o backend deve calcular o valor mensal com base na quantidade de contatos escolhida
- o backend deve buscar o `product_id` do `BlackChat Enterprise` conforme o ambiente ativo
- o backend deve criar a assinatura com **inline/custom recurring monthly price**
- o backend deve usar:
  - moeda BRL
  - recorrência mensal
  - valor calculado internamente
  - product id do Enterprise correspondente ao ambiente

### Regra importante
- O backend é a fonte da verdade do valor do Enterprise.
- O frontend nunca deve mandar o valor final “como autoridade”.
- O frontend pode mandar apenas:
  - plano escolhido
  - quantidade de contatos
  - dados do cliente
- o backend calcula o preço final e cria a assinatura.

---

## 6. Modelo de persistência de assinatura no sistema

O sistema deve gravar internamente os dados principais da assinatura Stripe.

### Campos esperados por assinatura
- usuário/empresa dono da assinatura
- plano interno (`free`, `pro`, `enterprise`)
- ambiente Stripe usado (`test` ou `live`)
- stripe customer id
- stripe subscription id
- stripe price id, quando existir
- stripe product id, quando aplicável
- status da assinatura
- valor mensal contratado
- quantidade de contatos contratada
- período atual de cobrança
- data de cancelamento, se existir
- data de expiração/acesso
- payload resumido da resposta Stripe para auditoria

### Regra específica
- no **PRO**, salvar o `price_id` utilizado
- no **ENTERPRISE**, salvar o `product_id` e o valor mensal calculado; se a Stripe retornar referência do item/preço inline criado na assinatura, persistir também para rastreabilidade

---

## 7. Webhooks obrigatórios

Implementar o endpoint de webhook Stripe com validação de assinatura usando o **webhook secret** do ambiente correspondente.

### Eventos mínimos a tratar

#### `checkout.session.completed`
Usar para confirmar conclusão do checkout quando esse fluxo estiver sendo usado.

#### `customer.subscription.created`
Usar para registrar assinatura criada e sincronizar status inicial.

#### `customer.subscription.updated`
Usar para:
- atualizar status
- refletir upgrade/downgrade
- atualizar períodos
- registrar cancelamento programado
- atualizar mudanças de cobrança

#### `customer.subscription.deleted`
Usar para:
- encerrar acesso pago
- marcar assinatura como cancelada/finalizada

#### `invoice.paid`
Usar para:
- confirmar renovação
- manter acesso ativo
- atualizar datas de vigência

#### `invoice.payment_failed`
Usar para:
- marcar pagamento pendente/falho
- iniciar regra de aviso/bloqueio
- registrar erro operacional

### Requisitos do webhook
- validar assinatura do evento com o webhook secret correto
- identificar se o evento veio do ambiente test ou live
- processar eventos com idempotência
- salvar log de eventos recebidos
- evitar reprocessamento do mesmo `event.id`

---

## 8. Idempotência e logs

Implementar robustez operacional.

### Implementar:
- tabela/log de eventos Stripe recebidos
- persistência de:
  - `event_id`
  - `event_type`
  - ambiente
  - payload bruto
  - data de recebimento
  - status de processamento
  - mensagem de erro, se houver

### Regra
- se o `event_id` já foi processado, ignorar reprocessamento
- registrar tentativas e falhas
- permitir auditoria administrativa

---

## 9. Regras de negócio internas do BlackChat

### FREE
- acesso liberado conforme regra interna
- sem Stripe

### PRO
- limite fixo definido pelo sistema
- cobrança mensal fixa
- se assinatura ativa: acesso liberado
- se falha/cancelamento: aplicar regra interna de bloqueio ou grace period

### ENTERPRISE
- quantidade de contatos controlada pelo backend
- preço calculado pelo backend
- cobrança recorrente mensal inline/custom
- mudança de quantidade de contatos deve refletir em:
  - novo valor mensal
  - eventual atualização da assinatura
  - histórico comercial

---

## 10. Atualização de plano

O sistema deve ficar preparado para:
- upgrade de Free para Pro
- upgrade de Pro para Enterprise
- downgrade de Enterprise para Pro
- cancelamento

### Requisitos
- o backend deve sempre consultar a assinatura Stripe atual antes de atualizar
- mudanças de assinatura devem considerar status atual
- quando houver troca no meio do ciclo, deixar preparado para política de proration/configuração futura da Stripe, sem acoplamento rígido
- registrar no histórico interno todas as mudanças de plano

---

## 11. Segurança

### Nunca fazer
- nunca expor secret key no frontend
- nunca deixar o frontend escolher livremente o ambiente operacional real sem mediação do backend
- nunca confiar no valor do plano Enterprise vindo do frontend
- nunca assumir que evento webhook sem validação é legítimo

### Sempre fazer
- backend resolve o ambiente ativo
- backend resolve a secret key
- backend resolve qual price id/product id usar
- backend valida webhook secret
- backend calcula o valor final do Enterprise

---

## 12. Entregáveis esperados

Ajustar o projeto já existente para entregar:

### Backend
- camada de configuração Stripe por ambiente
- serviço que resolve credenciais e IDs do ambiente ativo
- fluxo Pro com `price_id`
- fluxo Enterprise com inline/custom recurring monthly
- webhook robusto
- persistência de assinaturas
- persistência de eventos Stripe
- validações administrativas

### Frontend
- tela admin para editar configuração Stripe
- toggle global test/live
- campos de chaves e IDs
- feedback visual de ambiente ativo
- validação de preenchimento
- mascaramento de segredos

### Banco
- tabela de configuração Stripe
- tabela de assinaturas
- tabela de eventos webhook/log Stripe
- eventuais tabelas auxiliares de histórico de mudança de plano

---

## 13. Decisões finais que devem ser respeitadas

Estas decisões já estão fechadas e não devem ser alteradas:

- FREE não usa Stripe
- PRO usa `price_id` fixo recorrente mensal
- ENTERPRISE usa **inline/custom recurring monthly**
- volume de contatos do Enterprise é controlado pelo backend
- sistema deve suportar ambiente **teste** e **produção**
- superadmin alterna o ambiente por toggle
- todas as chaves e IDs ficam persistidos no banco
- webhook deve tratar criação, atualização, cancelamento, pagamento confirmado e falha de pagamento

---

## Referências oficiais Stripe

- Products e Prices: https://docs.stripe.com/products-prices/how-products-and-prices-work
- Manage prices e inline pricing: https://docs.stripe.com/products-prices/manage-prices
- Subscriptions: https://docs.stripe.com/billing/subscriptions/overview
- Build subscriptions: https://docs.stripe.com/billing/subscriptions/build-subscriptions
- Webhooks: https://docs.stripe.com/webhooks
- Subscription webhooks: https://docs.stripe.com/billing/subscriptions/webhooks
- API keys: https://docs.stripe.com/keys

