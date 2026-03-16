# 🆘 Guia de Socorro — BlackChat Produção

> Estes são os únicos comandos que você precisa saber se algo der errado.
> Não precisa entender o que fazem — só copiar e colar no terminal.

---

## 🔴 Sistema caiu / não responde

```bash
# Reiniciar o backend (resolve 90% dos problemas)
sudo systemctl restart blackchat-backend

# Ver se está rodando
sudo systemctl status blackchat-backend
```

---

## 🔴 Fluxos pararam de funcionar

```bash
# 1. Verificar se o backend está vivo
sudo systemctl status blackchat-backend

# 2. Verificar se o Redis está vivo
redis-cli ping
# Deve responder "PONG"

# 3. Se Redis não responde:
sudo systemctl restart redis-server

# 4. Reiniciar tudo
sudo systemctl restart redis-server
sudo systemctl restart blackchat-backend
```

---

## 🔴 Tela de erro no navegador

```bash
# Ver os últimos erros do backend
tail -50 /home/winbots/projetos/blackchat/logs/backend-error.log

# Ver atividade em tempo real (saia com Ctrl+C)
tail -f /home/winbots/projetos/blackchat/logs/backend.log
```

---

## 🔴 Memória cheia

```bash
# Ver memória do sistema
free -h

# Ver quem está consumindo mais
top -o %MEM

# Limpar cache do Redis (não perde dados, só cache)
redis-cli FLUSHDB

# Reiniciar tudo
sudo systemctl restart redis-server
sudo systemctl restart blackchat-backend
```

---

## 🟡 Atualizar o código (deploy)

```bash
# 1. Entrar na pasta do projeto
cd /home/winbots/projetos/blackchat

# 2. Baixar atualizações
git pull

# 3. Atualizar dependências do backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
deactivate

# 4. Reiniciar
sudo systemctl restart blackchat-backend

# 5. Verificar
sudo systemctl status blackchat-backend
```

---

## 🟡 Ver se o Redis está funcionando

```bash
# Ping (deve responder PONG)
redis-cli ping

# Ver memória usada
redis-cli info memory | grep used_memory_human

# Ver quantas chaves estão no cache
redis-cli dbsize

# Ver healthcheck completo
curl -s http://localhost:8061/api/health
```

---

## 🟡 Limpar cache manualmente

```bash
# Limpar TODO o cache (seguro, só fica mais lento por alguns segundos)
redis-cli FLUSHDB

# Limpar cache de um recurso específico
redis-cli DEL "plans:all"
redis-cli DEL "stripe:config"
```

---

## 📊 Monitoramento rápido

```bash
# Status geral
curl -s http://localhost:8061/api/health

# Ver logs em tempo real
tail -f /home/winbots/projetos/blackchat/logs/backend.log

# Ver uso de recursos
htop
```

---

## ⚙️ Comandos do systemd (referência)

| Ação | Comando |
|------|---------|
| Iniciar | `sudo systemctl start blackchat-backend` |
| Parar | `sudo systemctl stop blackchat-backend` |
| Reiniciar | `sudo systemctl restart blackchat-backend` |
| Status | `sudo systemctl status blackchat-backend` |
| Ver logs | `journalctl -u blackchat-backend -f` |
| Iniciar Redis | `sudo systemctl start redis-server` |
| Parar Redis | `sudo systemctl stop redis-server` |

---

## 🔥 Comando "salva tudo" (reinicia tudo de uma vez)

```bash
sudo systemctl restart redis-server && sudo systemctl restart blackchat-backend && echo "✅ Tudo reiniciado" && sleep 2 && curl -s http://localhost:8061/api/health
```

---

> **Importante:** Se nada resolver, entre em contato com o suporte técnico
> e envie o resultado deste comando:
> ```bash
> tail -100 /home/winbots/projetos/blackchat/logs/backend-error.log
> ```
