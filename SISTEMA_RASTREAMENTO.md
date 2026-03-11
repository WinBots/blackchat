# 📊 Sistema de Rastreamento Completo de Leads

## ✅ Implementado

### 1. Banco de Dados

#### Nova Tabela: `flow_execution_logs`
Registra cada passo da execução de um fluxo:
- `id`: ID do log
- `flow_execution_id`: Vínculo com a execução
- `step_id`: ID do step executado
- `log_type`: Tipo de evento (step_start, step_complete, message_sent, action_executed, condition_evaluated, flow_paused, flow_resumed, error, info)
- `description`: Descrição legível do evento
- `data`: Dados em JSON (configuração do step, resultado, etc)
- `error_message`: Mensagem de erro (se houver)
- `created_at`: Timestamp do evento

#### Campos Adicionados em `messages`
- `flow_execution_id`: Vincula mensagem à execução do fluxo
- `step_id`: Vincula mensagem ao step específico que a enviou

### 2. Logging Automático

O sistema agora registra automaticamente:
- ✅ Início de cada step
- ✅ Conclusão de cada step
- ✅ Mensagens enviadas (texto, imagem, áudio, vídeo, botões)
- ✅ Ações executadas (set_field, add_tag, etc)
- ✅ Condições avaliadas (resultado true/false)
- ✅ Pausa do fluxo (quando aguarda resposta)
- ✅ Retomada do fluxo (após resposta)
- ✅ Erros durante execução

### 3. Endpoints de Debug/Rastreamento

#### 📊 GET `/api/v1/debug/contacts/{contact_id}/history`
**Retorna histórico COMPLETO de um lead**

Resposta inclui:
```json
{
  "contact": {
    "id": 1,
    "username": "windsonfaria",
    "first_name": "Windson",
    "custom_fields": {...}
  },
  "total_messages": 45,
  "total_executions": 3,
  "executions": [
    {
      "id": 1,
      "flow": {
        "id": 1,
        "name": "Fluxo de Boas Vindas"
      },
      "status": "completed",
      "trigger_type": "telegram_ref_url",
      "started_at": "2026-02-15T10:30:00",
      "completed_at": "2026-02-15T10:32:00",
      "current_step_id": 5,
      "context": {...},
      "logs": [
        {
          "id": 1,
          "step_id": 2,
          "log_type": "step_start",
          "description": "Iniciando step tipo: message",
          "data": {...},
          "created_at": "2026-02-15T10:30:01"
        },
        {
          "id": 2,
          "step_id": 2,
          "log_type": "message_sent",
          "description": "Mensagem enviada",
          "data": {
            "message_id": 10,
            "content": "Olá! Seja bem-vindo..."
          },
          "created_at": "2026-02-15T10:30:02"
        }
      ],
      "messages": [
        {
          "id": 10,
          "step_id": 2,
          "direction": "outbound",
          "content": "Olá! Seja bem-vindo...",
          "message_type": "text",
          "created_at": "2026-02-15T10:30:02"
        }
      ]
    }
  ]
}
```

**Casos de uso:**
- Ver TODOS os fluxos que o lead passou
- Ver TODOS os logs de cada execução
- Ver TODAS as mensagens enviadas/recebidas
- Rastrear exatamente onde ocorreram erros
- Analisar comportamento do lead

---

#### 📍 GET `/api/v1/debug/contacts/{contact_id}/current-position`
**Retorna posição atual do lead nos fluxos ativos**

Resposta:
```json
{
  "contact_id": 1,
  "username": "windsonfaria",
  "active_flows": 2,
  "positions": [
    {
      "execution_id": 5,
      "flow_name": "Fluxo de Vendas",
      "flow_id": 2,
      "status": "waiting_response",
      "current_step": {
        "id": 15,
        "type": "action",
        "order_index": 3
      },
      "total_steps": 10,
      "context": {
        "waiting_for_field": "nome",
        "next_step_index": 4
      },
      "last_activity": "2026-02-15T11:45:00",
      "updated_at": "2026-02-15T11:45:00"
    }
  ]
}
```

**Casos de uso:**
- Ver onde o lead está AGORA
- Verificar se está aguardando resposta
- Ver progresso em cada fluxo (step 3 de 10)
- Identificar fluxos travados

---

#### 🧹 DELETE `/api/v1/debug/contacts/{contact_id}/clear-test-data`
**Limpa TODOS os dados de teste de um lead**

⚠️ **ATENÇÃO: Ação IRREVERSÍVEL!**

Remove:
- ✅ Todas as execuções de fluxos
- ✅ Todos os logs
- ✅ Todas as mensagens
- ✅ Todos os custom_fields

Resposta:
```json
{
  "message": "Dados de teste limpos com sucesso",
  "contact_id": 1,
  "username": "windsonfaria",
  "deleted": {
    "executions": 3,
    "logs": 45,
    "messages": 67
  }
}
```

**Casos de uso em desenvolvimento:**
- Limpar tudo antes de testar um fluxo do zero
- Remover dados de testes anteriores
- Resetar lead para novo ciclo de testes

---

#### 📈 GET `/api/v1/debug/flows/{flow_id}/execution-summary`
**Retorna resumo de todas as execuções de um fluxo**

Resposta:
```json
{
  "flow": {
    "id": 1,
    "name": "Fluxo de Boas Vindas"
  },
  "total_executions": 150,
  "by_status": {
    "completed": 120,
    "waiting_response": 15,
    "active": 10,
    "failed": 5
  },
  "recent_executions": [
    {
      "id": 150,
      "contact": {
        "id": 1,
        "username": "windsonfaria"
      },
      "status": "waiting_response",
      "current_step_id": 5,
      "log_count": 12,
      "started_at": "2026-02-15T11:00:00",
      "updated_at": "2026-02-15T11:05:00"
    }
  ]
}
```

**Casos de uso:**
- Ver quantas pessoas passaram pelo fluxo
- Identificar fluxos com muitas falhas
- Analisar taxa de conclusão
- Ver quem está travado no fluxo

---

## 🎯 Fluxo de Trabalho em Desenvolvimento

### 1️⃣ Antes de Testar
```bash
# Limpar dados anteriores
curl -X DELETE http://localhost:8061/api/v1/debug/contacts/1/clear-test-data
```

### 2️⃣ Durante o Teste
```bash
# Ver onde o lead está
curl http://localhost:8061/api/v1/debug/contacts/1/current-position
```

### 3️⃣ Após o Teste
```bash
# Ver histórico completo
curl http://localhost:8061/api/v1/debug/contacts/1/history
```

### 4️⃣ Analisar Fluxo
```bash
# Ver resumo geral do fluxo
curl http://localhost:8061/api/v1/debug/flows/1/execution-summary
```

---

## 📝 Script de Teste

Use o arquivo `test_tracking.py` para testar todos os endpoints:

```bash
cd backend
python test_tracking.py
```

---

## 🔍 O Que Você Consegue Rastrear Agora

### Por Lead (Contato)
✅ Histórico completo de todos os fluxos que passou  
✅ Todos os logs detalhados de cada execução  
✅ Todas as mensagens enviadas e recebidas  
✅ Posição atual em fluxos ativos  
✅ Custom fields preenchidos  
✅ Status atual (aguardando resposta, ativo, completo, falha)  

### Por Fluxo
✅ Quantas pessoas executaram  
✅ Taxa de conclusão  
✅ Quantidade por status  
✅ Últimas execuções  
✅ Quais leads estão travados  

### Por Execução
✅ Cada step executado  
✅ Quando foi executado  
✅ Configuração do step  
✅ Resultado de cada ação  
✅ Condições avaliadas (true/false)  
✅ Mensagens enviadas em cada step  
✅ Erros ocorridos  
✅ Quando pausou e quando retomou  

---

## 🛠️ Integração com Frontend

Você pode criar uma página de debug no frontend que:

1. **Lista todos os contatos**
2. **Para cada contato, mostra:**
   - Fluxos ativos e posição atual
   - Botão "Ver Histórico Completo"
   - Botão "Limpar Dados de Teste"

3. **Visualização de Histórico:**
   - Timeline de execuções
   - Logs detalhados
   - Mensagens em formato de chat

Exemplo de chamada no frontend:
```javascript
// Ver histórico
const response = await fetch(`/api/v1/debug/contacts/${contactId}/history`);
const history = await response.json();

// Ver posição atual
const position = await fetch(`/api/v1/debug/contacts/${contactId}/current-position`);
const current = await position.json();

// Limpar dados de teste
await fetch(`/api/v1/debug/contacts/${contactId}/clear-test-data`, {
  method: 'DELETE'
});
```

---

## 🎉 Benefícios

### Em Desenvolvimento
- ✅ Rastreamento completo do que acontece
- ✅ Fácil limpar dados de teste
- ✅ Ver exatamente onde fluxo está travado
- ✅ Identificar rapidamente erros

### Em Produção
- ✅ Suporte ao cliente mais eficiente
- ✅ Debugar problemas relatados por usuários
- ✅ Análise de comportamento
- ✅ Métricas detalhadas de conversão

---

## 📚 Tipos de Logs Registrados

| Tipo | Descrição | Quando é registrado |
|------|-----------|---------------------|
| `step_start` | Início do step | Ao começar a processar qualquer step |
| `step_complete` | Step concluído | Ao terminar de processar o step |
| `message_sent` | Mensagem enviada | Toda vez que envia texto, imagem, vídeo, etc |
| `action_executed` | Ação executada | Ao executar set_field, add_tag, etc |
| `condition_evaluated` | Condição avaliada | Ao avaliar um bloco condition |
| `flow_paused` | Fluxo pausado | Quando encontra {ultima_mensagem} |
| `flow_resumed` | Fluxo retomado | Quando usuário responde e fluxo continua |
| `error` | Erro | Quando ocorre qualquer erro |
| `info` | Informação | Eventos gerais do sistema |
