#!/usr/bin/env python3
"""Script para debugar configuração do webhook do Telegram"""

from app.db.database import get_db
from app.db.models.channel import Channel
from app.db.models.flow import Flow, FlowStep
import json

def main():
    db = next(get_db())
    
    print("=" * 60)
    print("🔍 DEBUG: Configuração do Webhook Telegram")
    print("=" * 60)
    
    # 1. Verificar canal Telegram
    channel = db.query(Channel).filter(Channel.type == 'telegram').first()
    
    if not channel:
        print("❌ ERRO: Nenhum canal Telegram encontrado!")
        return
    
    print(f"\n✅ Canal encontrado:")
    print(f"   ID: {channel.id}")
    print(f"   Nome: {channel.name}")
    print(f"   Tipo: {channel.type}")
    print(f"   Ativo: {channel.is_active}")
    
    # Config do canal
    try:
        config = json.loads(channel.config) if channel.config else {}
        print(f"\n📋 Configuração do Canal:")
        print(f"   Bot Token: {'*' * 20}{config.get('bot_token', '')[-10:] if config.get('bot_token') else 'Não configurado'}")
        print(f"   Bot Username: @{config.get('bot_username', 'Não configurado')}")
        print(f"   Webhook Secret: {config.get('webhook_secret', 'Não configurado')}")
        print(f"   Webhook URL: {config.get('webhook_url', 'Não configurado')}")
    except Exception as e:
        print(f"❌ Erro ao parsear config: {e}")
        return
    
    # 2. Verificar fluxos para Telegram
    flows = db.query(Flow).filter(
        Flow.tenant_id == channel.tenant_id,
        Flow.is_active == True
    ).all()
    
    print(f"\n📊 Fluxos Ativos: {len(flows)}")
    
    default_flow = None
    for flow in flows:
        try:
            trigger_config = json.loads(flow.trigger_config) if flow.trigger_config else {}
            is_default = trigger_config.get("default_for") == "telegram"
            print(f"\n   {'✅' if is_default else '  '} Flow ID {flow.id}: {flow.name}")
            print(f"      trigger_config: {trigger_config}")
            
            if is_default:
                default_flow = flow
        except:
            print(f"\n   ⚠️ Flow ID {flow.id}: {flow.name} (trigger_config inválido)")
    
    if not default_flow:
        print("\n❌ PROBLEMA: Nenhum fluxo está marcado como padrão para Telegram!")
        print("   Solução: Crie um novo fluxo escolhendo 'Telegram' como sistema.")
        return
    
    # 3. Verificar steps do fluxo
    print(f"\n🔄 Analisando fluxo padrão: {default_flow.name} (ID: {default_flow.id})")
    
    trigger_steps = db.query(FlowStep).filter(
        FlowStep.flow_id == default_flow.id,
        FlowStep.type == "trigger"
    ).all()
    
    print(f"\n🎯 Trigger Steps: {len(trigger_steps)}")
    for step in trigger_steps:
        try:
            step_config = json.loads(step.config) if step.config else {}
            print(f"\n   Step ID {step.id}:")
            print(f"      triggerType: {step_config.get('triggerType')}")
            print(f"      keywords: {step_config.get('keywords', [])}")
        except Exception as e:
            print(f"   ⚠️ Erro ao parsear config: {e}")
    
    message_steps = db.query(FlowStep).filter(
        FlowStep.flow_id == default_flow.id,
        FlowStep.type == "message"
    ).order_by(FlowStep.order_index).all()
    
    print(f"\n📨 Message Steps: {len(message_steps)}")
    for step in message_steps:
        try:
            step_config = json.loads(step.config) if step.config else {}
            blocks = step_config.get('blocks', [])
            print(f"\n   Step ID {step.id} (ordem: {step.order_index}):")
            print(f"      Blocos: {len(blocks)}")
            for i, block in enumerate(blocks):
                print(f"         [{i+1}] {block.get('type')}: {block.get('text', block.get('seconds', ''))}")
        except Exception as e:
            print(f"   ⚠️ Erro ao parsear config: {e}")
    
    # 4. URL de teste
    webhook_url = config.get('webhook_url', '')
    print("\n" + "=" * 60)
    print("📬 TESTE NO POSTMAN:")
    print("=" * 60)
    print(f"\nMétodo: POST")
    print(f"URL: {webhook_url}")
    print(f"\nBody (raw JSON):")
    print("""{
  "message": {
    "message_id": 1,
    "from": {
      "id": 123456789,
      "first_name": "Teste",
      "username": "teste"
    },
    "chat": {
      "id": 123456789,
      "type": "private"
    },
    "text": "Wind"
  }
}""")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()

