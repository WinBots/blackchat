#!/bin/bash
# ═══════════════════════════════════════════════════
#  BlackChat — Script de setup para produção
#  VPS: 16GB RAM / 6 cores
# ═══════════════════════════════════════════════════

set -e

echo "═══════════════════════════════════════"
echo " BlackChat — Setup Produção"
echo "═══════════════════════════════════════"

# ── 1. Instalar Redis ──
echo ""
echo "📦 Instalando Redis..."
sudo apt update
sudo apt install -y redis-server

# Configurar Redis para produção (512MB max, política LRU)
sudo mkdir -p /etc/redis/redis.conf.d

sudo tee /etc/redis/redis.conf.d/blackchat.conf > /dev/null <<EOF
# BlackChat Redis Config
maxmemory 512mb
maxmemory-policy allkeys-lru
save ""
appendonly no
EOF

# Adicionar include no redis.conf (se ainda não existir)
if ! grep -q "blackchat.conf" /etc/redis/redis.conf 2>/dev/null; then
    echo "include /etc/redis/redis.conf.d/blackchat.conf" | sudo tee -a /etc/redis/redis.conf
fi

sudo systemctl enable redis-server
sudo systemctl restart redis-server

echo "✅ Redis instalado e configurado (max 512MB, LRU)"

# ── 2. Instalar dependência Python ──
echo ""
echo "📦 Instalando redis para Python..."
cd /home/winbots/projetos/blackchat/backend
source venv/bin/activate
pip install redis>=5.0.0
deactivate

echo "✅ Dependência Python instalada"

# ── 3. Criar diretório de logs ──
echo ""
echo "📁 Criando diretório de logs..."
mkdir -p /home/winbots/projetos/blackchat/logs
touch /home/winbots/projetos/blackchat/logs/backend.log
touch /home/winbots/projetos/blackchat/logs/backend-error.log

echo "✅ Diretório de logs criado"

# ── 4. Adicionar REDIS_URL ao .env (se não existir) ──
ENV_FILE="/home/winbots/projetos/blackchat/backend/.env"
if [ -f "$ENV_FILE" ]; then
    if ! grep -q "REDIS_URL" "$ENV_FILE"; then
        echo "" >> "$ENV_FILE"
        echo "# Redis (cache)" >> "$ENV_FILE"
        echo "REDIS_URL=redis://localhost:6379/0" >> "$ENV_FILE"
        echo "✅ REDIS_URL adicionado ao .env"
    else
        echo "ℹ️  REDIS_URL já existe no .env"
    fi
fi

# ── 5. Parar processo uvicorn manual (se existir) ──
echo ""
echo "🔄 Parando processos uvicorn manuais..."
pkill -f "uvicorn app.main:app" 2>/dev/null || true
sleep 2

# ── 6. Instalar service do systemd ──
echo ""
echo "🔧 Configurando systemd..."
sudo cp /home/winbots/projetos/blackchat/deploy/blackchat-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable blackchat-backend
sudo systemctl start blackchat-backend

echo "✅ Service instalado e iniciado (4 workers)"

# ── 7. Verificar status ──
echo ""
echo "═══════════════════════════════════════"
echo " Status Final"
echo "═══════════════════════════════════════"
echo ""
echo "🔴 Redis:"
redis-cli ping
echo ""
echo "🟢 Backend:"
sudo systemctl status blackchat-backend --no-pager -l
echo ""
echo "🏥 Healthcheck:"
sleep 3
curl -s http://localhost:8061/api/health | python3 -m json.tool 2>/dev/null || echo "(aguardando startup...)"
echo ""
echo "═══════════════════════════════════════"
echo " ✅ Setup completo!"
echo ""
echo " Comandos úteis:"
echo "   sudo systemctl status blackchat-backend"
echo "   sudo systemctl restart blackchat-backend"
echo "   redis-cli ping"
echo "   curl http://localhost:8061/api/health"
echo "═══════════════════════════════════════"
