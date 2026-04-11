"""
Insere 300 contatos fictícios no tenant 3 para testes de envio em massa.
Contatos são marcados com a tag "teste-massa" para fácil remoção posterior.

Uso:
    cd backend
    python seed_contacts.py
    python seed_contacts.py --delete   # remove os contatos criados por este script
"""
import argparse
import random
import string
from app.db.session import SessionLocal
from app.db.models.contact import Contact
from app.db.models.tag import ContactTag

TENANT_ID = 3
TOTAL = 300
TAG = "teste-massa"

FIRST_NAMES = [
    "Ana", "Bruno", "Carlos", "Daniela", "Eduardo", "Fernanda", "Gabriel",
    "Helena", "Igor", "Juliana", "Kevin", "Larissa", "Marcos", "Natalia",
    "Otavio", "Patricia", "Rafael", "Sabrina", "Thiago", "Vanessa",
    "Anderson", "Beatriz", "Cesar", "Debora", "Elias", "Flavia", "Gustavo",
    "Heloisa", "Ivan", "Jessica", "Leonardo", "Mariana", "Nicolas", "Olivia",
    "Paulo", "Raquel", "Sergio", "Tatiane", "Ulisses", "Viviane",
]

LAST_NAMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Lima", "Pereira", "Costa",
    "Ferreira", "Rodrigues", "Almeida", "Nascimento", "Carvalho", "Araújo",
    "Gomes", "Martins", "Ribeiro", "Barbosa", "Rocha", "Cardoso", "Mendes",
]

def rand_telegram_id():
    return str(random.randint(100_000_000, 999_999_999))

def rand_username(first, last):
    suffix = ''.join(random.choices(string.digits, k=4))
    return f"{first.lower()}{last.lower()}{suffix}"

def seed(db):
    created = 0
    for i in range(TOTAL):
        first = random.choice(FIRST_NAMES)
        last  = random.choice(LAST_NAMES)
        contact = Contact(
            tenant_id=TENANT_ID,
            first_name=first,
            last_name=last,
            username=rand_username(first, last),
            telegram_user_id=rand_telegram_id(),
            custom_fields={},
        )
        db.add(contact)
        db.flush()  # gera o id

        tag = ContactTag(contact_id=contact.id, tag_name=TAG)
        db.add(tag)
        created += 1

    db.commit()
    print(f"✅ {created} contatos fictícios criados no tenant {TENANT_ID} com tag '{TAG}'")

def delete_seeds(db):
    tags = db.query(ContactTag).filter(ContactTag.tag_name == TAG).all()
    ids  = [t.contact_id for t in tags]
    if not ids:
        print("Nenhum contato de teste encontrado.")
        return
    db.query(ContactTag).filter(ContactTag.contact_id.in_(ids)).delete(synchronize_session=False)
    db.query(Contact).filter(Contact.id.in_(ids), Contact.tenant_id == TENANT_ID).delete(synchronize_session=False)
    db.commit()
    print(f"🗑️  {len(ids)} contatos de teste removidos.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--delete", action="store_true", help="Remove contatos de teste")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.delete:
            delete_seeds(db)
        else:
            seed(db)
    finally:
        db.close()
