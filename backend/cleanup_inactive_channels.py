#!/usr/bin/env python3
"""Script para limpar canais inativos"""
from app.db.session import get_db
from app.db.models import Channel

def cleanup():
    db = next(get_db())
    
    # Buscar canais inativos
    inactive = db.query(Channel).filter(Channel.is_active == False).all()
    
    print(f"Encontrados {len(inactive)} canais inativos")
    
    for channel in inactive:
        print(f"   Canal #{channel.id} - {channel.name} - {channel.type}")
        db.delete(channel)
    
    db.commit()
    print(f"OK - {len(inactive)} canais removidos do banco")

if __name__ == "__main__":
    cleanup()

