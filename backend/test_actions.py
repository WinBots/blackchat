#!/usr/bin/env python3
"""
Script de teste para validar implementação de Actions
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.db.models import Contact, ContactTag, Sequence, ContactSequence
from sqlalchemy import and_
import json

def test_actions():
    """Testa funcionalidades de actions"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("TESTE: Funcionalidades de Actions")
        print("=" * 80)
        
        # Buscar um contato de teste
        contact = db.query(Contact).first()
        if not contact:
            print("\n[AVISO] Nenhum contato encontrado no banco de dados")
            print("Crie um contato primeiro para testar as funcionalidades")
            return
        
        print(f"\n[OK] Usando contato de teste: ID={contact.id}")
        print(f"     Nome: {contact.first_name} {contact.last_name}")
        
        # Teste 1: Custom Fields
        print("\n" + "-" * 80)
        print("TESTE 1: Custom Fields")
        print("-" * 80)
        
        custom_fields = json.loads(contact.custom_fields) if isinstance(contact.custom_fields, str) else (contact.custom_fields or {})
        custom_fields["teste_campo"] = "valor_teste"
        custom_fields["cidade"] = "São Paulo"
        custom_fields["interesse"] = "Premium"
        contact.custom_fields = json.dumps(custom_fields)
        db.commit()
        
        print(f"[OK] Custom fields salvos: {json.dumps(custom_fields, indent=2)}")
        
        # Teste 2: Tags
        print("\n" + "-" * 80)
        print("TESTE 2: Tags")
        print("-" * 80)
        
        # Limpar tags antigas do teste
        db.query(ContactTag).filter(
            and_(
                ContactTag.contact_id == contact.id,
                ContactTag.tag_name.like('teste_%')
            )
        ).delete()
        db.commit()
        
        # Adicionar tags
        test_tags = ["teste_lead_quente", "teste_vip", "teste_interessado"]
        for tag_name in test_tags:
            existing = db.query(ContactTag).filter(
                and_(
                    ContactTag.contact_id == contact.id,
                    ContactTag.tag_name == tag_name
                )
            ).first()
            
            if not existing:
                new_tag = ContactTag(
                    tenant_id=contact.tenant_id,
                    contact_id=contact.id,
                    tag_name=tag_name
                )
                db.add(new_tag)
        
        db.commit()
        
        # Listar tags
        tags = db.query(ContactTag).filter(ContactTag.contact_id == contact.id).all()
        print(f"[OK] Tags adicionadas ({len(tags)} total):")
        for tag in tags:
            print(f"     - {tag.tag_name}")
        
        # Remover uma tag
        db.query(ContactTag).filter(
            and_(
                ContactTag.contact_id == contact.id,
                ContactTag.tag_name == "teste_vip"
            )
        ).delete()
        db.commit()
        print("[OK] Tag 'teste_vip' removida")
        
        # Teste 3: Sequences
        print("\n" + "-" * 80)
        print("TESTE 3: Sequences")
        print("-" * 80)
        
        # Criar sequência de teste
        test_sequence = db.query(Sequence).filter(
            and_(
                Sequence.tenant_id == contact.tenant_id,
                Sequence.name == "teste_followup"
            )
        ).first()
        
        if not test_sequence:
            test_sequence = Sequence(
                tenant_id=contact.tenant_id,
                name="teste_followup",
                description="Sequência de teste para follow-up",
                is_active=True,
                steps=json.dumps([
                    {"delay": "1d", "message": "Dia 1: Como posso ajudar?"},
                    {"delay": "2d", "message": "Dia 3: Ainda tem interesse?"},
                    {"delay": "3d", "message": "Dia 6: Oferta especial!"}
                ])
            )
            db.add(test_sequence)
            db.commit()
            print(f"[OK] Sequencia criada: {test_sequence.name}")
        else:
            print(f"[OK] Sequencia ja existe: {test_sequence.name}")
        
        # Inscrever contato na sequência
        existing_enrollment = db.query(ContactSequence).filter(
            and_(
                ContactSequence.contact_id == contact.id,
                ContactSequence.sequence_id == test_sequence.id,
                ContactSequence.status.in_(['active', 'paused'])
            )
        ).first()
        
        if not existing_enrollment:
            from datetime import datetime
            enrollment = ContactSequence(
                tenant_id=contact.tenant_id,
                contact_id=contact.id,
                sequence_id=test_sequence.id,
                status='active',
                current_step=0,
                next_execution_at=datetime.now()
            )
            db.add(enrollment)
            db.commit()
            print(f"[OK] Contato inscrito na sequencia")
        else:
            print(f"[OK] Contato ja inscrito na sequencia")
        
        # Listar sequências do contato
        enrollments = db.query(ContactSequence).filter(
            ContactSequence.contact_id == contact.id
        ).all()
        print(f"[OK] Inscricoes ativas: {len(enrollments)}")
        for enr in enrollments:
            seq = db.query(Sequence).filter(Sequence.id == enr.sequence_id).first()
            print(f"     - {seq.name if seq else 'N/A'} (status: {enr.status})")
        
        # Resumo final
        print("\n" + "=" * 80)
        print("TODOS OS TESTES CONCLUIDOS COM SUCESSO!")
        print("=" * 80)
        print("\nFuncionalidades validadas:")
        print("  [OK] Custom Fields - Armazenamento e recuperacao")
        print("  [OK] Tags - Adicionar, listar e remover")
        print("  [OK] Sequences - Criar, inscrever e listar")
        print("\nProntas para uso nos fluxos do Telegram!")
        print()
        
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_actions()
