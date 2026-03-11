# 🧪 Como Testar Link de Referência do Telegram

## ⚡ Passo a Passo Rápido

### 1️⃣ **Criar um Fluxo com Gatilho de Link de Referência**

1. Acesse **Fluxos** no menu lateral
2. Clique em **"+ Novo Fluxo"**
3. Dê um nome (ex: "Teste Link de Ref")
4. Certifique-se que o fluxo está associado a um **bot ativo**
5. Clique em **"Editar Fluxo"**

### 2️⃣ **Configurar o Gatilho**

1. No editor de fluxo, clique em **"Adicionar Gatilho"**
2. Selecione **"Link de Referência"**
3. Um bloco de gatilho será criado automaticamente
4. Clique no bloco do gatilho para editá-lo no painel lateral

### 3️⃣ **Configurar a Chave de Referência**

No painel lateral direito, você verá:

```
┌─────────────────────────────────────────┐
│ Link de Referência do Telegram         │
├─────────────────────────────────────────┤
│                                         │
│ Bot: @seu_bot_aqui                     │  ← Confirme que o bot está correto
│                                         │
│ Chave de Referência *                   │
│ ┌─────────────────────────────────┐   │
│ │ teste_promo                     │   │  ← Digite uma chave única
│ └─────────────────────────────────┘   │
│                                         │
│ 🔗 Seu Link de Referência               │
│ ┌─────────────────────────────────┐ 📋│
│ │ https://t.me/bot?start=teste... │   │  ← Link gerado automaticamente
│ └─────────────────────────────────┘   │
│                                         │
│ 💾 Salvar em Campo (opcional)           │
│ ┌─────────────────────────────────┐   │
│ │ origem_campanha                 │   │  ← (opcional) Nome do campo
│ └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

**Campos:**
- **Chave de Referência**: Digite algo único, ex: `teste_promo`, `welcome`, `blackfriday`
- **Campo Personalizado** (opcional): Nome do campo onde salvar o parâmetro, ex: `origem`, `campanha`

### 4️⃣ **Adicionar Mensagens ao Fluxo**

1. Clique em **"Adicionar Bloco"** (botão ➕ no topo)
2. Selecione **"Mensagem de Texto"**
3. Digite uma mensagem de teste:
   ```
   🎉 Parabéns! Você clicou no link de referência!
   
   Este fluxo foi acionado pelo link: teste_promo
   ```
4. Conecte o gatilho ao bloco de mensagem:
   - Clique no **ponto de saída** do gatilho (↘)
   - Arraste até o **ponto de entrada** da mensagem (↖)

### 5️⃣ **Salvar o Fluxo**

1. Clique em **"Salvar"** no topo
2. Aguarde confirmação "Fluxo salvo com sucesso"
3. Verifique que o fluxo está **ATIVO** (badge verde no topo)

---

## 🔗 Copiar o Link Gerado

No painel de edição do gatilho, você verá o link completo:

```
https://t.me/SEU_BOT_USERNAME?start=teste_promo
```

**Para copiar:**
- Clique no botão **📋** ao lado do link
- OU clique no campo e pressione `Ctrl+C`

---

## 📱 Testar no Telegram

### **Opção 1: Testar Você Mesmo**

1. **Abra o link** copiado no navegador ou cole diretamente no Telegram
2. O Telegram vai abrir o bot automaticamente
3. Clique em **"START"** (ou **"INICIAR"**)
4. O bot deve executar o fluxo configurado

### **Opção 2: Testar com Outra Conta**

1. Envie o link para outra pessoa (WhatsApp, email, etc.)
2. Peça para clicarem no link
3. Eles serão redirecionados para o bot
4. O fluxo será executado automaticamente

---

## 🔍 Verificar se Funcionou

### **1. No Telegram:**
- O bot deve enviar a mensagem configurada
- Não deve pedir `/start` novamente (já envia automático)

### **2. No Painel WinChat:**

**Contatos:**
1. Acesse **"Contatos"** no menu
2. Procure pelo contato que clicou no link
3. Se configurou campo personalizado, verifique:
   - Clique no contato
   - Veja os campos personalizados
   - O campo `origem_campanha` deve ter o valor `teste_promo`

**Mensagens:**
1. No painel de Contatos, clique no contato
2. Veja o histórico de mensagens
3. Deve mostrar a mensagem enviada pelo fluxo

---

## 🐛 Troubleshooting

### **Problema: Link não funciona**

**Verificar:**
- ✅ O bot está **ATIVO** em Configurações?
- ✅ O fluxo está **ATIVO** (badge verde)?
- ✅ O webhook está configurado corretamente?
- ✅ O backend está rodando (porta 8061)?

**Testar manualmente:**
1. Abra o bot no Telegram
2. Digite: `/start teste_promo` (substitua pela sua chave)
3. Se funcionar assim, o problema é no link gerado

### **Problema: Bot não responde**

**Logs do Backend:**
1. Abra o terminal onde o backend está rodando
2. Procure por mensagens:
   ```
   🔗 Parâmetro de referência detectado: teste_promo
   [MATCH REF URL] Fluxo selecionado: Teste Link de Ref
   ```
3. Se não aparecer, o webhook não está recebendo mensagens

**Verificar Webhook:**
```bash
# No terminal do backend
cd backend
python check_channels.py
```

### **Problema: Campo personalizado não foi salvo**

**Verificar:**
1. O nome do campo está correto? (sem espaços ou caracteres especiais)
2. O contato foi criado antes? (pode levar alguns segundos)
3. Verifique no banco de dados:
   ```sql
   SELECT custom_fields FROM contacts WHERE telegram_user_id = 'SEU_USER_ID';
   ```

---

## 💡 Exemplos de Uso Real

### **Exemplo 1: Campanha no Instagram**

```
Fluxo: Promoção Instagram
Chave: insta_promo_jan
Campo: origem
Link: https://t.me/seu_bot?start=insta_promo_jan

Postar: "🎁 PROMOÇÃO! Clique no link da bio!"
```

### **Exemplo 2: Anúncio Facebook Ads**

```
Fluxo: Lead Magnet Facebook
Chave: fb_ads_ebook
Campo: funil
Link: https://t.me/seu_bot?start=fb_ads_ebook

Anúncio: "📚 EBOOK GRÁTIS! Clique aqui"
```

### **Exemplo 3: Email Marketing**

```
Fluxo: Newsletter Semanal
Chave: newsletter_week3
Campo: campanha
Link: https://t.me/seu_bot?start=newsletter_week3

Email: "📧 Confira as novidades desta semana!"
```

---

## 🎯 Dicas Importantes

### ✅ **Boas Práticas:**

1. **Chaves descritivas**: Use nomes que facilitem identificar a origem
   - ✅ `instagram_bio_jan25`
   - ❌ `link1`, `teste`

2. **Campos consistentes**: Use o mesmo campo para campanhas similares
   - Exemplo: sempre use `origem` para rastreamento de fonte

3. **Teste antes**: Sempre teste o link antes de compartilhar publicamente

4. **Links curtos**: Para redes sociais, considere usar encurtador de URL (bit.ly, etc.)

### ⚠️ **Evite:**

1. **Caracteres especiais** na chave (use apenas letras, números e underscore)
2. **Chaves muito longas** (Telegram tem limite de ~64 caracteres no parâmetro)
3. **Espaços** na chave (use underscore: `promo_natal` em vez de `promo natal`)

---

## 📊 Analisando Resultados

### **Ver Quantas Pessoas Clicaram:**

1. Acesse **"Contatos"**
2. Se configurou campo personalizado:
   - Clique em **"Filtrar por Tag"** (no futuro terá filtro por campo)
   - Por enquanto, veja manualmente nos detalhes de cada contato

### **Verificar Conversão:**

1. Compare número de clicks (analytics externo)
2. Com número de contatos que têm o campo `origem = teste_promo`
3. Calcule taxa de conversão

---

## 🚀 Próximos Passos

Depois que o básico funcionar, experimente:

1. **Múltiplos fluxos**: Crie links diferentes para públicos diferentes
2. **Segmentação**: Use campos personalizados para criar segmentos
3. **A/B Testing**: Crie 2 links similares e compare resultados
4. **Integração**: Combine com automações de email, SMS, etc.

---

**Tudo pronto! 🎉 Agora é só testar e compartilhar seus links!**

Se tiver algum problema, verifique a seção **Troubleshooting** acima.
