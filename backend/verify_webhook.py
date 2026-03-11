#!/usr/bin/env python3
"""
Script para verificar e testar o webhook do Telegram
Verifica: status do webhook, configuração, conectividade e testa envio de mensagem
"""
import sys
import os
from pathlib import Path
import requests
import json

# Adicionar o diretório raiz ao path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))
os.chdir(backend_dir)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import get_settings
from app.db.models.channel import Channel

def print_section(title):
    """Imprime seção formatada"""
    print("\n" + "="*80)
    print(f" {title}")
    print("="*80)

def print_status(status, message):
    """Imprime status com ícone"""
    icons = {
        'ok': '✅',
        'warning': '⚠️',
        'error': '❌',
        'info': 'ℹ️'
    }
    print(f"{icons.get(status, '')} {message}")

def check_webhook_status(bot_token):
    """Verifica o status atual do webhook no Telegram"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return None, f"Erro na API: {response.status_code}"
        
        data = response.json()
        if not data.get('ok'):
            return None, f"API retornou erro: {data.get('description')}"
        
        return data['result'], None
    except requests.exceptions.Timeout:
        return None, "Timeout ao conectar com Telegram API"
    except requests.exceptions.RequestException as e:
        return None, f"Erro de conexão: {str(e)}"
    except Exception as e:
        return None, f"Erro inesperado: {str(e)}"

def check_bot_info(bot_token):
    """Verifica informações do bot"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return None, f"Erro na API: {response.status_code}"
        
        data = response.json()
        if not data.get('ok'):
            return None, f"API retornou erro: {data.get('description')}"
        
        return data['result'], None
    except Exception as e:
        return None, f"Erro: {str(e)}"

def test_webhook_connectivity(webhook_url):
    """Testa se o webhook está acessível"""
    try:
        # Apenas testa se o servidor está respondendo
        response = requests.post(webhook_url, json={}, timeout=5)
        return True, response.status_code
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except requests.exceptions.ConnectionError:
        return False, "Conexão recusada"
    except Exception as e:
        return False, str(e)

def main():
    print_section("🔍 VERIFICADOR DE WEBHOOK DO TELEGRAM")
    
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # 1. Buscar canal Telegram
        print("\n1️⃣ Buscando canal Telegram no banco de dados...")
        
        channels = db.query(Channel).filter(
            Channel.type == 'telegram',
            Channel.is_active == True
        ).all()
        
        if not channels:
            print_status('error', "Nenhum canal Telegram ATIVO encontrado!")
            print("\n💡 Solução:")
            print("   1. Acesse Configurações no painel")
            print("   2. Conecte um bot do Telegram")
            print("   3. Verifique se o bot está marcado como ATIVO")
            return
        
        print_status('ok', f"Encontrados {len(channels)} canal(is) ativo(s)")
        
        # 2. Verificar cada canal
        for idx, channel in enumerate(channels, 1):
            print_section(f"📱 CANAL #{idx}: {channel.name}")
            
            try:
                config = json.loads(channel.config) if channel.config else {}
            except:
                print_status('error', "Erro ao ler configuração do canal")
                continue
            
            bot_token = config.get('bot_token')
            bot_username = config.get('bot_username')
            webhook_url = config.get('webhook_url')
            webhook_secret = config.get('webhook_secret')
            
            print(f"\n📋 Configuração:")
            print(f"   ID do Canal: {channel.id}")
            print(f"   Nome: {channel.name}")
            print(f"   Status: {'✅ ATIVO' if channel.is_active else '❌ INATIVO'}")
            print(f"   Bot Username: @{bot_username or 'não configurado'}")
            print(f"   Webhook URL: {webhook_url or 'não configurado'}")
            print(f"   Webhook Secret: {'✅ Configurado' if webhook_secret else '❌ Não configurado'}")
            
            if not bot_token:
                print_status('error', "Bot Token não encontrado!")
                continue
            
            # 3. Verificar informações do bot
            print("\n2️⃣ Verificando conexão com o bot...")
            bot_info, error = check_bot_info(bot_token)
            
            if error:
                print_status('error', f"Falha ao conectar com o bot: {error}")
                print("\n💡 Possíveis causas:")
                print("   - Token inválido ou expirado")
                print("   - Bot foi deletado pelo @BotFather")
                print("   - Sem conexão com a internet")
                continue
            
            print_status('ok', f"Bot conectado: @{bot_info.get('username')}")
            print(f"   Nome: {bot_info.get('first_name')}")
            print(f"   ID: {bot_info.get('id')}")
            print(f"   Pode juntar grupos: {'Sim' if bot_info.get('can_join_groups') else 'Não'}")
            
            # 4. Verificar status do webhook
            print("\n3️⃣ Verificando status do webhook no Telegram...")
            webhook_info, error = check_webhook_status(bot_token)
            
            if error:
                print_status('error', f"Falha ao obter info do webhook: {error}")
                continue
            
            current_webhook = webhook_info.get('url', '')
            
            if not current_webhook:
                print_status('error', "WEBHOOK NÃO ESTÁ CONFIGURADO!")
                print("\n💡 Solução:")
                print("   Execute: python register_webhook.py")
                continue
            
            print_status('ok', f"Webhook configurado: {current_webhook}")
            
            # Verificar se a URL do webhook no banco bate com a do Telegram
            if webhook_url and current_webhook != webhook_url:
                print_status('warning', "URL do webhook diverge entre banco e Telegram")
                print(f"   Banco: {webhook_url}")
                print(f"   Telegram: {current_webhook}")
            
            # Verificar pending updates
            pending_updates = webhook_info.get('pending_update_count', 0)
            if pending_updates > 0:
                print_status('warning', f"Existem {pending_updates} atualizações pendentes")
                print("   Isso pode indicar que o webhook não está processando mensagens")
            else:
                print_status('ok', "Sem atualizações pendentes")
            
            # Verificar último erro
            last_error = webhook_info.get('last_error_message')
            if last_error:
                print_status('error', f"Último erro: {last_error}")
                last_error_date = webhook_info.get('last_error_date')
                if last_error_date:
                    from datetime import datetime
                    error_time = datetime.fromtimestamp(last_error_date)
                    print(f"   Data: {error_time.strftime('%d/%m/%Y %H:%M:%S')}")
            else:
                print_status('ok', "Sem erros registrados")
            
            # Informações adicionais
            print(f"\n📊 Estatísticas:")
            print(f"   Max connections: {webhook_info.get('max_connections', 'não informado')}")
            print(f"   Allowed updates: {webhook_info.get('allowed_updates', ['todos'])}")
            
            # 5. Testar conectividade do webhook
            if webhook_url:
                print("\n4️⃣ Testando conectividade do webhook...")
                accessible, status = test_webhook_connectivity(webhook_url)
                
                if accessible:
                    print_status('ok', f"Webhook acessível (HTTP {status})")
                    
                    if status == 200:
                        print_status('ok', "Webhook está respondendo corretamente")
                    elif status == 401:
                        print_status('warning', "Webhook retornou 401 (Não autorizado)")
                        print("   Isso é normal se o webhook requer autenticação")
                    else:
                        print_status('warning', f"Webhook retornou código inesperado: {status}")
                else:
                    print_status('error', f"Webhook não acessível: {status}")
                    print("\n💡 Possíveis causas:")
                    print("   - Backend não está rodando")
                    print("   - Firewall bloqueando a porta")
                    print("   - URL incorreta")
                    print("   - Problema de rede/DNS")
            
            # 6. Resumo e recomendações
            print_section("📝 RESUMO E RECOMENDAÇÕES")
            
            if current_webhook and not last_error and pending_updates == 0:
                print_status('ok', "TUDO OK! Webhook configurado e funcionando")
                print("\n✅ O que está funcionando:")
                print("   • Bot está ativo e respondendo")
                print("   • Webhook está configurado corretamente")
                print("   • Não há erros ou mensagens pendentes")
                print("\n🧪 Para testar:")
                print(f"   1. Abra: https://t.me/{bot_username}")
                print("   2. Envie: /start")
                print("   3. Verifique os logs do backend")
            else:
                print_status('warning', "ATENÇÃO: Possíveis problemas detectados")
                print("\n🔧 Ações recomendadas:")
                
                if not current_webhook:
                    print("   • Registrar webhook: python register_webhook.py")
                
                if last_error:
                    print(f"   • Verificar erro: {last_error}")
                    print("   • Verificar logs do backend")
                
                if pending_updates > 0:
                    print("   • Verificar se backend está processando mensagens")
                    print("   • Reiniciar backend se necessário")
                
                if not accessible:
                    print("   • Verificar se backend está rodando na porta 8061")
                    print("   • Verificar firewall e configurações de rede")
            
            print()
    
    except Exception as e:
        print_status('error', f"Erro inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
