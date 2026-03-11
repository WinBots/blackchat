"""
Script helper para testar fluxos durante desenvolvimento
Uso:
    python test_lead.py reset windsonfaria
    python test_lead.py start windsonfaria 1
    python test_lead.py history windsonfaria
    python test_lead.py active
"""
import sys
import requests
import json

BASE_URL = "http://localhost:8061/api/v1"


def reset_lead(username):
    """Reseta todos os dados de um lead"""
    print(f"🔄 Resetando lead {username}...")
    response = requests.post(f"{BASE_URL}/dev/reset-lead/{username}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Lead resetado com sucesso!")
        print(f"   • Execuções deletadas: {data['deleted']['executions']}")
        print(f"   • Logs deletados: {data['deleted']['logs']}")
        print(f"   • Mensagens deletadas: {data['deleted']['messages']}")
    else:
        print(f"❌ Erro: {response.text}")


def start_flow(username, flow_id):
    """Inicia um fluxo para um lead"""
    print(f"🚀 Iniciando flow {flow_id} para {username}...")
    response = requests.post(
        f"{BASE_URL}/dev/start-flow",
        params={"username": username, "flow_id": flow_id}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Fluxo iniciado!")
        print(f"   • Flow: {data['flow_id']}")
        print(f"   • Execution ID: {data['execution_id']}")
    else:
        print(f"❌ Erro: {response.text}")


def show_history(username):
    """Mostra histórico completo de um lead"""
    print(f"📊 Buscando histórico de {username}...")
    response = requests.get(f"{BASE_URL}/dev/lead-history/{username}")
    
    if response.status_code == 200:
        data = response.json()
        contact = data['contact']
        
        print(f"\n👤 Lead: {contact['username']} ({contact['first_name']} {contact['last_name']})")
        print(f"   Custom Fields: {json.dumps(contact['custom_fields'], indent=2, ensure_ascii=False)}")
        
        print(f"\n📝 Execuções: {len(data['executions'])}")
        
        for i, execution in enumerate(data['executions'], 1):
            print(f"\n   [{i}] Execution #{execution['id']} - {execution['flow_name']}")
            print(f"       Status: {execution['status']}")
            print(f"       Step atual: {execution['current_step_id']}")
            print(f"       Iniciado: {execution['started_at']}")
            print(f"       Atualizado: {execution['updated_at']}")
            
            if execution['context']:
                print(f"       Contexto: {json.dumps(execution['context'], ensure_ascii=False)}")
            
            print(f"\n       📋 Logs: {len(execution['logs'])}")
            for log in execution['logs']:
                print(f"          • [{log['log_type']}] {log['description']}")
                if log['data']:
                    print(f"            Data: {json.dumps(log['data'], ensure_ascii=False)[:100]}")
            
            print(f"\n       💬 Mensagens: {len(execution['messages'])}")
            for msg in execution['messages']:
                direction_icon = "➡️" if msg['direction'] == 'outbound' else "⬅️"
                content_preview = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
                print(f"          {direction_icon} [{msg['message_type']}] {content_preview}")
        
        if data['orphan_messages']:
            print(f"\n💬 Mensagens antigas (sem execução): {len(data['orphan_messages'])}")
            for msg in data['orphan_messages'][:5]:  # Mostrar só as 5 mais recentes
                direction_icon = "➡️" if msg['direction'] == 'outbound' else "⬅️"
                content_preview = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
                print(f"   {direction_icon} {content_preview}")
    else:
        print(f"❌ Erro: {response.text}")


def show_active():
    """Mostra execuções ativas"""
    print(f"🔄 Buscando execuções ativas...")
    response = requests.get(f"{BASE_URL}/dev/executions/active")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n📊 Execuções ativas/pausadas: {data['count']}")
        
        for execution in data['executions']:
            print(f"\n   • Execution #{execution['id']}")
            print(f"     Lead: {execution['contact_username']}")
            print(f"     Flow: {execution['flow_name']}")
            print(f"     Status: {execution['status']}")
            print(f"     Step: {execution['current_step_id']}")
            if execution['context']:
                print(f"     Contexto: {json.dumps(execution['context'], ensure_ascii=False)}")
    else:
        print(f"❌ Erro: {response.text}")


def main():
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python test_lead.py reset <username>")
        print("  python test_lead.py start <username> <flow_id>")
        print("  python test_lead.py history <username>")
        print("  python test_lead.py active")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "reset":
        if len(sys.argv) < 3:
            print("Erro: Especifique o username")
            sys.exit(1)
        reset_lead(sys.argv[2])
    
    elif command == "start":
        if len(sys.argv) < 4:
            print("Erro: Especifique username e flow_id")
            sys.exit(1)
        start_flow(sys.argv[2], sys.argv[3])
    
    elif command == "history":
        if len(sys.argv) < 3:
            print("Erro: Especifique o username")
            sys.exit(1)
        show_history(sys.argv[2])
    
    elif command == "active":
        show_active()
    
    else:
        print(f"Comando desconhecido: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
