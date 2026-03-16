"""
Chaves de cache centralizadas.
Todas as chaves seguem o padrão:  domínio:tenant_id:recurso:id
TTLs definidos aqui para fácil ajuste.
"""


class CacheKeys:
    """Gerador de chaves e TTLs."""

    # ── Planos (raramente mudam) ──
    PLANS_ALL = "plans:all"
    PLANS_TTL = 600  # 10 min

    @staticmethod
    def plan(plan_id: int) -> str:
        return f"plan:{plan_id}"

    PLAN_TTL = 600

    # ── Configuração Stripe (raramente muda) ──
    STRIPE_CONFIG = "stripe:config"
    STRIPE_CONFIG_TTL = 300  # 5 min

    # ── Tenant / Subscription (muda ao trocar plano) ──
    @staticmethod
    def subscription(tenant_id: int) -> str:
        return f"tenant:{tenant_id}:subscription"

    SUBSCRIPTION_TTL = 300

    # ── Fluxos e steps (mudam ao editar) ──
    @staticmethod
    def flow(flow_id: int) -> str:
        return f"flow:{flow_id}"

    FLOW_TTL = 120  # 2 min

    @staticmethod
    def flow_steps(flow_id: int) -> str:
        return f"flow:{flow_id}:steps"

    FLOW_STEPS_TTL = 120

    # ── Canal/Bot config (muda raramente) ──
    @staticmethod
    def channel(channel_id: int) -> str:
        return f"channel:{channel_id}"

    CHANNEL_TTL = 300
