#!/usr/bin/env python3
"""
Script para criar tabelas do sistema SaaS e popular planos iniciais
"""
from app.db.session import engine, get_db, Base
from app.db.models import Plan, Tenant, User, Subscription
from datetime import datetime, timedelta
from passlib.context import CryptContext

# Contexto para hash de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_tables():
    """Cria todas as tabelas"""
    print("Criando tabelas...")
    Base.metadata.create_all(bind=engine)
    print("OK - Tabelas criadas")


def seed_plans():
    """Popula planos iniciais"""
    db = next(get_db())
    
    # Verificar se já existem planos
    existing = db.query(Plan).first()
    if existing:
        print("Planos ja existem, pulando...")
        return
    
    plans = [
        Plan(
            name="free",
            display_name="Gratuito",
            description="Teste gratis por 14 dias",
            price_monthly=0,
            max_bots=1,
            max_contacts=100,
            max_messages_per_month=1000,
            max_flows=5,
            has_advanced_flows=False,
            has_api_access=False,
            has_webhooks=False,
            has_priority_support=False,
            has_whitelabel=False,
        ),
        Plan(
            name="basic",
            display_name="Basico",
            description="Para pequenos negocios",
            price_monthly=49.00,
            max_bots=3,
            max_contacts=1000,
            max_messages_per_month=10000,
            max_flows=20,
            has_advanced_flows=True,
            has_api_access=False,
            has_webhooks=False,
            has_priority_support=False,
            has_whitelabel=False,
        ),
        Plan(
            name="professional",
            display_name="Profissional",
            description="Para empresas em crescimento",
            price_monthly=149.00,
            max_bots=10,
            max_contacts=10000,
            max_messages_per_month=100000,
            max_flows=100,
            has_advanced_flows=True,
            has_api_access=True,
            has_webhooks=True,
            has_priority_support=True,
            has_whitelabel=False,
        ),
        Plan(
            name="enterprise",
            display_name="Enterprise",
            description="Para grandes empresas",
            price_monthly=499.00,
            max_bots=None,  # Ilimitado
            max_contacts=None,
            max_messages_per_month=None,
            max_flows=None,
            has_advanced_flows=True,
            has_api_access=True,
            has_webhooks=True,
            has_priority_support=True,
            has_whitelabel=True,
        ),
    ]
    
    for plan in plans:
        db.add(plan)
    
    db.commit()
    print(f"OK - {len(plans)} planos criados")


def create_demo_tenant():
    """Cria um tenant de demonstração com usuário admin"""
    db = next(get_db())
    
    # Verificar se já existe
    existing = db.query(Tenant).filter(Tenant.email == "demo@blackchatpro.com").first()
    if existing:
        print("Tenant demo ja existe, pulando...")
        return
    
    # Criar tenant
    tenant = Tenant(
        name="Empresa Demo",
        email="demo@blackchatpro.com",
        is_active=True
    )
    db.add(tenant)
    db.flush()  # Para pegar o ID
    
    # Criar usuário admin
    user = User(
        tenant_id=tenant.id,
        email="admin@blackchatpro.com",
        password_hash=pwd_context.hash("admin123"),
        full_name="Admin Demo",
        is_active=True,
        is_admin=True
    )
    db.add(user)
    db.flush()
    
    # Criar assinatura trial (14 dias)
    free_plan = db.query(Plan).filter(Plan.name == "free").first()
    subscription = Subscription(
        tenant_id=tenant.id,
        plan_id=free_plan.id,
        status="trial",
        started_at=datetime.utcnow(),
        trial_ends_at=datetime.utcnow() + timedelta(days=14),
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow() + timedelta(days=14)
    )
    db.add(subscription)
    
    db.commit()
    
    print("OK - Tenant demo criado")
    print(f"   Email: admin@blackchatpro.com")
    print(f"   Senha: admin123")
    print(f"   Plano: Trial (14 dias)")


if __name__ == "__main__":
    print("="*60)
    print("CRIACAO DO SISTEMA SAAS")
    print("="*60)
    
    create_tables()
    seed_plans()
    create_demo_tenant()
    
    print("="*60)
    print("CONCLUIDO!")
    print("="*60)

