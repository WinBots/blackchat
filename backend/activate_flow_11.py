#!/usr/bin/env python3
"""Script para desativar o fluxo ID: 10 e deixar apenas o ID: 11 ativo"""
import sys
sys.path.insert(0, '.')

from app.db.session import get_db
from sqlalchemy import text

def main():
    db = next(get_db())
    
    print("=" * 60)
    print("🔧 Ativando apenas o Fluxo ID: 11")
    print("=" * 60)
    
    # Desativar o fluxo ID: 10
    db.execute(text("UPDATE flows SET is_active = 0 WHERE id = 10"))
    db.commit()
    print(f"\n✅ Fluxo ID: 10 (Canal do M10) DESATIVADO!")
    
    # Verificar fluxo ID: 11
    result = db.execute(text("SELECT id, name, is_active FROM flows WHERE id = 11"))
    flow_11 = result.fetchone()
    
    if flow_11:
        print(f"\n✅ Fluxo ID: 11 (Teste Fluxo 1) está ATIVO: {bool(flow_11[2])}")
    
    # Listar fluxos ativos do Telegram
    print("\n" + "=" * 60)
    print("📊 Fluxos do Telegram Ativos Agora:")
    print("=" * 60)
    
    result = db.execute(text("""
        SELECT id, name, trigger_config 
        FROM flows 
        WHERE is_active = 1 
        AND trigger_config LIKE '%telegram%'
    """))
    flows = result.fetchall()
    
    if flows:
        for flow in flows:
            print(f"\n✅ ID: {flow[0]} | Nome: {flow[1]}")
    else:
        print("\n⚠️ Nenhum fluxo ativo do Telegram encontrado")
    
    print("\n" + "=" * 60)
    print("✅ Pronto! Agora teste novamente no Postman!")
    print("=" * 60)
    
    db.close()

if __name__ == "__main__":
    main()

