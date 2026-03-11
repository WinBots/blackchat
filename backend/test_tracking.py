"""
Script de exemplo para testar os novos endpoints de rastreamento
"""
import httpx
import json

BASE_URL = "http://localhost:8061/api/v1"

# Substitua pelo ID do seu contato de teste
CONTACT_ID = 1  # windsonfaria

def test_contact_history():
    """Ver histórico completo de um lead"""
    print("=" * 80)
    print("📊 HISTÓRICO COMPLETO DO LEAD")
    print("=" * 80)
    
    response = httpx.get(f"{BASE_URL}/debug/contacts/{CONTACT_ID}/history")
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\n👤 Contato: {data['contact']['username']}")
        print(f"📧 Total de mensagens: {data['total_messages']}")
        print(f"🔄 Total de execuções: {data['total_executions']}")
        
        for execution in data['executions']:
            print(f"\n{'─' * 80}")
            print(f"🔄 Execução #{execution['id']} - {execution['flow']['name']}")
            print(f"   Status: {execution['status']}")
            print(f"   Iniciado: {execution['started_at']}")
            print(f"   Atualizado: {execution['updated_at']}")
            
            if execution['logs']:
                print(f"\n   📝 Logs ({len(execution['logs'])} eventos):")
                for log in execution['logs'][-5:]:  # Últimos 5 logs
                    print(f"      [{log['log_type']}] {log['description']}")
            
            if execution['messages']:
                print(f"\n   💬 Mensagens ({len(execution['messages'])}):")
                for msg in execution['messages'][-3:]:  # Últimas 3 mensagens
                    emoji = "📤" if msg['direction'] == 'outbound' else "📥"
                    content = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
                    print(f"      {emoji} {content}")
    else:
        print(f"❌ Erro: {response.status_code}")
        print(response.text)


def test_current_position():
    """Ver posição atual do lead nos fluxos ativos"""
    print("\n" + "=" * 80)
    print("📍 POSIÇÃO ATUAL DO LEAD NOS FLUXOS")
    print("=" * 80)
    
    response = httpx.get(f"{BASE_URL}/debug/contacts/{CONTACT_ID}/current-position")
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\n👤 Contato: {data['username']}")
        print(f"🔄 Fluxos ativos: {data['active_flows']}")
        
        for position in data['positions']:
            print(f"\n{'─' * 80}")
            print(f"📊 {position['flow_name']} (ID: {position['flow_id']})")
            print(f"   Status: {position['status']}")
            
            if position['current_step']:
                print(f"   Step atual: #{position['current_step']['order_index']} (ID: {position['current_step']['id']})")
                print(f"   Tipo: {position['current_step']['type']}")
            
            print(f"   Progresso: {position['current_step']['order_index'] if position['current_step'] else 0}/{position['total_steps']} steps")
            print(f"   Última atividade: {position['last_activity']}")
            
            if position['context']:
                print(f"   Contexto: {position['context']}")
    else:
        print(f"❌ Erro: {response.status_code}")
        print(response.text)


def test_clear_data():
    """Limpar todos os dados de teste de um lead"""
    print("\n" + "=" * 80)
    print("🧹 LIMPAR DADOS DE TESTE")
    print("=" * 80)
    
    confirm = input(f"\n⚠️ Tem certeza que deseja limpar TODOS os dados do contato {CONTACT_ID}? (sim/não): ")
    
    if confirm.lower() != 'sim':
        print("❌ Operação cancelada")
        return
    
    response = httpx.delete(f"{BASE_URL}/debug/contacts/{CONTACT_ID}/clear-test-data")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ {data['message']}")
        print(f"\n📊 Removidos:")
        print(f"   • {data['deleted']['executions']} execuções")
        print(f"   • {data['deleted']['logs']} logs")
        print(f"   • {data['deleted']['messages']} mensagens")
    else:
        print(f"❌ Erro: {response.status_code}")
        print(response.text)


def test_flow_summary():
    """Ver resumo de execuções de um fluxo"""
    FLOW_ID = 1  # ID do seu fluxo de teste
    
    print("\n" + "=" * 80)
    print(f"📈 RESUMO DE EXECUÇÕES DO FLUXO #{FLOW_ID}")
    print("=" * 80)
    
    response = httpx.get(f"{BASE_URL}/debug/flows/{FLOW_ID}/execution-summary")
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\n📊 Fluxo: {data['flow']['name']}")
        print(f"🔄 Total de execuções: {data['total_executions']}")
        
        print(f"\n📊 Por status:")
        for status, count in data['by_status'].items():
            print(f"   • {status}: {count}")
        
        if data['recent_executions']:
            print(f"\n📝 Últimas execuções:")
            for execution in data['recent_executions'][:5]:
                print(f"   • Execução #{execution['id']} - @{execution['contact']['username']}")
                print(f"     Status: {execution['status']} | Logs: {execution['log_count']} | Iniciado: {execution['started_at']}")
    else:
        print(f"❌ Erro: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    print("\n🔍 SISTEMA DE RASTREAMENTO DE LEADS - TESTES\n")
    
    try:
        # 1. Ver histórico completo
        test_contact_history()
        
        # 2. Ver posição atual
        test_current_position()
        
        # 3. Ver resumo do fluxo
        test_flow_summary()
        
        # 4. Limpar dados (comentado por segurança)
        # test_clear_data()
        
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
