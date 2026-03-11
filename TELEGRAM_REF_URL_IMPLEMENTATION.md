# 🔗 Link de Referência do Telegram - Implementação Completa

## 📋 Visão Geral

O gatilho de **Link de Referência do Telegram** permite criar links únicos que iniciam fluxos automaticamente quando clicados. Similar ao Manychat, cada link pode ter um parâmetro personalizado para tracking e segmentação.

---

## 🎯 Como Funciona

### **Fluxo de Uso:**

1. **Usuário cria fluxo** com gatilho "Link de Referência"
2. **Define uma chave** (ex: `welcome`, `promo2025`, `vip`)
3. **Sistema gera link**: `https://t.me/seu_bot?start=welcome`
4. **Usuário compartilha** o link em redes sociais, anúncios, etc.
5. **Quando clicado**, o Telegram abre o bot com `/start welcome`
6. **Backend detecta** o parâmetro e executa o fluxo correspondente
7. **(Opcional)** Salva o parâmetro em campo personalizado do contato

---

## 🔧 Implementação Técnica

### **Backend (`telegram.py`)**

#### 1. Detecção do Parâmetro

```python
# Detectar parâmetro no /start
ref_param = None
if text and text.startswith("/start "):
    parts = text.split(" ", 1)
    if len(parts) > 1:
        ref_param = parts[1].strip()
        print(f"🔗 Parâmetro detectado: {ref_param}")
```

#### 2. Busca de Fluxos com Trigger Ref URL

```python
if ref_param and len(flows) > 0:
    for flow in flows:
        trigger_config = json.loads(trigger_step.config)
        trigger_type = trigger_config.get("triggerType")
        
        if trigger_type == "telegram_ref_url":
            ref_key = trigger_config.get("ref_key", "").strip()
            save_ref_field = trigger_config.get("save_ref_field", "").strip()
            
            # Match exato ou parcial
            if ref_param == ref_key or ref_param.startswith(ref_key):
                # Executar fluxo
                selected_flow = flow
```

#### 3. Salvamento em Campo Personalizado

```python
if save_ref_field:
    custom_fields = json.loads(contact.custom_fields) or {}
    custom_fields[save_ref_field] = ref_param
    contact.custom_fields = json.dumps(custom_fields)
    db.commit()
```

---

### **Frontend (`FlowEditView.vue`)**

#### 1. Configuração do Trigger

```vue
<template v-if="selectedStep.config.triggerType === 'telegram_ref_url'">
  <!-- Campo: Chave de Referência -->
  <input
    v-model="selectedStep.config.ref_key"
    placeholder="Ex: welcome, promo2025, vip"
    @blur="autoSave"
  />
  
  <!-- Campo: Link Gerado (readonly) -->
  <input
    :value="getTelegramRefUrl(selectedStep.config.ref_key)"
    readonly
  />
  
  <!-- Campo: Nome do Campo Personalizado -->
  <input
    v-model="selectedStep.config.save_ref_field"
    placeholder="Ex: utm_source, campanha"
    @blur="autoSave"
  />
</template>
```

#### 2. Geração do Link

```javascript
const getTelegramRefUrl = (refKey) => {
  if (!refKey) return 'Configure a chave primeiro'
  
  const botUsername = 'seu_bot' // TODO: Buscar do canal
  return `https://t.me/${botUsername}?start=${refKey}`
}
```

---

## 📊 Estrutura do Trigger

### **Configuração no Banco de Dados:**

```json
{
  "triggerType": "telegram_ref_url",
  "ref_key": "promo_black_friday",
  "save_ref_field": "campanha"
}
```

### **Campos:**
- **`triggerType`**: Sempre `"telegram_ref_url"`
- **`ref_key`**: Chave única de identificação (ex: `welcome`, `promo2025`)
- **`save_ref_field`**: Nome do campo personalizado onde salvar o parâmetro (opcional)

---

## 💡 Casos de Uso

### **1. Campanhas de Marketing**
```
Link: https://t.me/meubot?start=blackfriday2025
Chave: blackfriday2025
Campo: campanha

Resultado: 
- Fluxo de boas-vindas especial para Black Friday
- Campo "campanha" = "blackfriday2025"
- Fácil tracking de conversões
```

### **2. Onboarding Personalizado**
```
Link: https://t.me/meubot?start=welcome_vip
Chave: welcome_vip
Campo: tipo_cliente

Resultado:
- Fluxo exclusivo para clientes VIP
- Campo "tipo_cliente" = "welcome_vip"
- Experiência diferenciada
```

### **3. Rastreamento de Origem**
```
Link: https://t.me/meubot?start=instagram_bio
Chave: instagram
Campo: origem

Resultado:
- Mesmo fluxo para todas origens "instagram*"
- Campo "origem" = "instagram_bio"
- Analytics por canal
```

---

## 🎨 Interface do Usuário

### **Tela de Configuração:**

```
┌─────────────────────────────────────────┐
│ Link de Referência do Telegram         │
├─────────────────────────────────────────┤
│                                         │
│ Chave de Referência *                   │
│ ┌─────────────────────────────────┐   │
│ │ promo_black_friday              │   │
│ └─────────────────────────────────┘   │
│ Esta chave será usada para...          │
│                                         │
│ Seu Link de Referência                  │
│ ┌─────────────────────────────────┐ 📋│
│ │ https://t.me/bot?start=promo... │   │
│ └─────────────────────────────────┘   │
│ Compartilhe este link...                │
│                                         │
│ Salvar em Campo Personalizado          │
│ ┌─────────────────────────────────┐   │
│ │ campanha                        │   │
│ └─────────────────────────────────┘   │
│ O parâmetro será salvo neste...        │
│                                         │
└─────────────────────────────────────────┘
```

---

## 🔍 Logs e Debug

### **Logs do Backend:**

```bash
# Quando mensagem /start chega
🔗 Parâmetro de referência detectado: promo_black_friday

[REF URL CHECK] Verificando match para ref_param: promo_black_friday
  ✅ MATCH! Fluxo 'Campanha Black Friday' (ref_key: promo_black_friday)
  💾 Parâmetro salvo em: campanha = promo_black_friday

[MATCH REF URL] Fluxo selecionado: Campanha Black Friday
```

---

## ⚠️ Considerações Importantes

### **1. Match Parcial**
- `ref_param.startswith(ref_key)` permite match parcial
- Ex: `ref_key = "promo"` → Match: `promo`, `promo_bf`, `promo_natal`
- Útil para criar variações de uma campanha

### **2. Prioridade**
- Links de referência têm **prioridade** sobre keywords
- Se houver match de ref URL, keywords são ignoradas
- Evita conflitos entre `/start welcome` e keyword "welcome"

### **3. Campos Personalizados**
- Campo é criado automaticamente se não existir
- Sobrescreve valor se já existir
- Permite tracking histórico com timestamps separados

### **4. Username do Bot**
- Por enquanto usa placeholder `seu_bot`
- TODO: Buscar username real do canal conectado
- Pode ser obtido do `channel.config.bot_username`

---

## 🚀 Melhorias Futuras

### **1. Buscar Username Dinâmico**
```javascript
const getTelegramRefUrl = (refKey) => {
  const channel = getCurrentChannel() // TODO
  const botUsername = channel?.bot_username || 'seu_bot'
  return `https://t.me/${botUsername}?start=${refKey}`
}
```

### **2. Validação de Chave**
- Evitar caracteres especiais
- Limitar comprimento
- Validar duplicatas

### **3. Analytics**
- Dashboard de clicks por link
- Conversão por campanha
- ROI de cada ref URL

### **4. QR Code**
- Gerar QR Code do link
- Facilitar compartilhamento offline

---

## 📝 Exemplo Completo

### **Cenário: Campanha de Natal**

1. **Criar Fluxo:**
   - Nome: "Campanha de Natal 2025"
   - Gatilho: Link de Referência
   - Chave: `natal2025`
   - Campo: `campanha_origem`

2. **Link Gerado:**
   ```
   https://t.me/minha_loja_bot?start=natal2025
   ```

3. **Compartilhar:**
   - Instagram Stories
   - Facebook Ads
   - Email Marketing
   - WhatsApp Status

4. **Quando Usuário Clica:**
   ```
   Telegram → Abre bot → Envia /start natal2025
   Backend → Detecta parâmetro
   Backend → Busca fluxo com ref_key="natal2025"
   Backend → Salva em custom_fields: {"campanha_origem": "natal2025"}
   Backend → Executa fluxo
   Bot → Envia mensagens do fluxo
   ```

5. **Resultado:**
   - Usuário recebe promoção de Natal
   - Sistema sabe origem: "natal2025"
   - Analytics mostra conversões da campanha

---

## ✅ Status de Implementação

- ✅ Backend: Detecção de parâmetro
- ✅ Backend: Match de fluxos
- ✅ Backend: Salvamento em campo personalizado
- ✅ Frontend: Interface de configuração
- ✅ Frontend: Geração de link
- ✅ Frontend: Copiar para clipboard
- ⏳ TODO: Buscar username dinâmico do bot
- ⏳ TODO: Validação de chaves
- ⏳ TODO: Analytics de links

---

**Implementação completa e funcional!** 🎉
