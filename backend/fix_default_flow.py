#!/usr/bin/env python3
"""Script para corrigir o fluxo padrão do Telegram"""
import sys
sys.path.insert(0, '.')

from app.db.session import get_db
from sqlalchemy import text
import json

def main():
    db = next(get_db())
    
    print("=" * 60)
    print("🔧 Corrigindo Fluxo Padrão do Telegram")
    print("=" * 60)
    
    # 1. Buscar o fluxo ID: 8
    result = db.execute(text("SELECT id, name, is_active, trigger_config FROM flows WHERE id = 8"))
    old_flow = result.fetchone()
    
    if old_flow:
        print(f"\n📋 Fluxo antigo encontrado:")
        print(f"   ID: {old_flow[0]}")
        print(f"   Nome: {old_flow[1]}")
        print(f"   Ativo: {old_flow[2]}")
        print(f"   trigger_config: {old_flow[3]}")
        
        # Desativar usando SQL direto
        db.execute(text("UPDATE flows SET is_active = 0 WHERE id = 8"))
        db.commit()
        print(f"\n✅ Fluxo ID: 8 DESATIVADO!")
    else:
        print("\n⚠️ Fluxo ID: 8 não encontrado")
    
    # 2. Listar todos os fluxos do Telegram ativos
    print("\n" + "=" * 60)
    print("📊 Fluxos do Telegram Ativos:")
    print("=" * 60)
    
    result = db.execute(text("SELECT id, name, trigger_config FROM flows WHERE is_active = 1"))
    flows = result.fetchall()
    
    telegram_flows = []
    for flow in flows:
        flow_id, flow_name, trigger_config_str = flow[0], flow[1], flow[2]
        try:
            trigger_config = json.loads(trigger_config_str) if trigger_config_str else {}
            if trigger_config.get("default_for") == "telegram":
                telegram_flows.append((flow_id, flow_name, trigger_config))
                print(f"\n✅ ID: {flow_id} | Nome: {flow_name}")
                print(f"   trigger_config: {trigger_config}")
        except:
            pass
    
    if len(telegram_flows) == 0:
        print("\n⚠️ Nenhum fluxo ativo com 'default_for': 'telegram'")
        print("\n💡 Você precisa criar um novo fluxo escolhendo 'Telegram' no modal de criação")
    elif len(telegram_flows) == 1:
        flow_id, flow_name, _ = telegram_flows[0]
        print(f"\n✅ Perfeito! Apenas 1 fluxo padrão do Telegram: {flow_name} (ID: {flow_id})")
    else:
        print(f"\n⚠️ ATENÇÃO: {len(telegram_flows)} fluxos marcados como padrão!")
        print("   O primeiro será usado. Considere desativar os outros.")
    
    print("\n" + "=" * 60)
    
    db.close()

if __name__ == "__main__":
    main()

