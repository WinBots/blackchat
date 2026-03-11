from app.db.session import SessionLocal
from app.db.models.user import User
from app.db.models.tenant import Tenant
from app.db.models.subscription import Subscription

db = SessionLocal()
users = db.query(User).all()
for u in users:
    t = db.query(Tenant).filter(Tenant.id == u.tenant_id).first()
    s = db.query(Subscription).filter(Subscription.tenant_id == u.tenant_id).first()
    print(f"user_id={u.id} | email={u.email} | full_name={u.full_name}")
    print(f"         tenant={t.name if t else '?'} | stripe_cid={t.stripe_customer_id if t else '?'}")
    print(f"         sub_id={s.id if s else '?'} | status={s.status if s else '?'} | plan_id={s.plan_id if s else '?'} | stripe_sub={s.stripe_subscription_id if s else '?'}")
    print()
db.close()
