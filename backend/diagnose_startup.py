"""Script para diagnosticar problemas de inicialização do backend"""
import sys
import time

print("=== DIAGNÓSTICO DE INICIALIZAÇÃO ===\n")

# 1. Testar imports básicos
print("1. Testando imports básicos...")
try:
    import fastapi
    print("   ✓ FastAPI importado")
except Exception as e:
    print(f"   ✗ Erro ao importar FastAPI: {e}")
    sys.exit(1)

try:
    import uvicorn
    print("   ✓ Uvicorn importado")
except Exception as e:
    print(f"   ✗ Erro ao importar Uvicorn: {e}")
    sys.exit(1)

try:
    import sqlalchemy
    print("   ✓ SQLAlchemy importado")
except Exception as e:
    print(f"   ✗ Erro ao importar SQLAlchemy: {e}")
    sys.exit(1)

# 2. Testar config
print("\n2. Testando configuração...")
try:
    from app.config import get_settings
    settings = get_settings()
    print(f"   ✓ Configuração carregada")
    print(f"   - DATABASE_URL: {settings.DATABASE_URL}")
    print(f"   - APP_PORT: {settings.APP_PORT}")
except Exception as e:
    print(f"   ✗ Erro ao carregar configuração: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. Testar sessão do banco
print("\n3. Testando conexão com banco de dados...")
try:
    from app.db.session import engine, Base
    print("   ✓ Engine criado")
except Exception as e:
    print(f"   ✗ Erro ao criar engine: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 4. Testar imports dos modelos
print("\n4. Testando imports dos modelos...")
try:
    from app.db import models
    print("   ✓ Modelos importados")
except Exception as e:
    print(f"   ✗ Erro ao importar modelos: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 5. Testar criação das tabelas
print("\n5. Testando criação das tabelas...")
try:
    start = time.time()
    Base.metadata.create_all(bind=engine)
    elapsed = time.time() - start
    print(f"   ✓ Tabelas criadas em {elapsed:.2f}s")
except Exception as e:
    print(f"   ✗ Erro ao criar tabelas: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 6. Testar imports dos routers
print("\n6. Testando imports dos routers...")
routers = [
    "auth", "tenants", "channels", "flows", "contacts", "events",
    "telegram", "instagram", "instagram_connect", "media", "admin", "public"
]
for router_name in routers:
    try:
        module = __import__(f"app.api.v1.routers.{router_name}", fromlist=[router_name])
        print(f"   ✓ Router '{router_name}' importado")
    except Exception as e:
        print(f"   ✗ Erro ao importar router '{router_name}': {e}")
        import traceback
        traceback.print_exc()

# 7. Testar criação da aplicação FastAPI
print("\n7. Testando criação da aplicação FastAPI...")
try:
    from app.main import app
    print("   ✓ Aplicação FastAPI criada")
    print(f"   - Título: {app.title}")
    print(f"   - Versão: {app.version}")
    print(f"   - Rotas registradas: {len(app.routes)}")
except Exception as e:
    print(f"   ✗ Erro ao criar aplicação: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n=== DIAGNÓSTICO CONCLUÍDO COM SUCESSO ===")
print("\nSe o diagnóstico passou, o problema pode estar no Uvicorn.")
print("Tente iniciar manualmente com:")
print("  python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8061")
