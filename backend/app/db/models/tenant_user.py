import json

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


# ─── Permissões disponíveis no sistema ────────────────────────────────────────
# Cada chave mapeia para uma área/recurso do sistema.
# Owner SEMPRE tem todas as permissões, independente deste campo.
AVAILABLE_PERMISSIONS = [
    "dashboard",    # Dashboard – ver métricas
    "contacts",     # Contatos – ver, enviar mensagens, tags, fluxos
    "flows",        # Automações – criar, editar, deletar fluxos
    "broadcasts",   # Mensagens em massa – envio em lote
    "channels",     # Canais – Telegram, Instagram, configuração
    "settings",     # Configurações gerais do workspace
    "billing",      # Cobrança, planos e assinatura
]

# Labels para exibição no frontend
PERMISSION_LABELS = {
    "dashboard":  "Dashboard",
    "contacts":   "Contatos",
    "flows":      "Automações",
    "broadcasts": "Mensagens em massa",
    "channels":   "Canais",
    "settings":   "Configurações",
    "billing":    "Cobrança e Planos",
}


class TenantUser(Base):
    """
    Tabela de vínculo N:N entre Users e Tenants (workspaces).
    Cada registro conecta um usuário a um workspace com um papel (role).
    """
    __tablename__ = "tenant_users"
    __table_args__ = (UniqueConstraint("tenant_id", "user_id", name="uq_tenant_user"),)

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String(50), default="owner", nullable=False)  # owner | admin | member
    is_default = Column(Boolean, default=False, nullable=False)  # workspace padrão ao logar
    permissions = Column(Text, nullable=True)  # JSON array ex: ["dashboard","contacts","flows"]  (null = ALL)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="workspace_members")
    user = relationship("User", back_populates="workspaces")

    # ── helpers ────────────────────────────────────────────────────────

    def get_permissions(self) -> list[str]:
        """Retorna a lista de permissões. Owner sempre recebe ALL."""
        if self.role == "owner":
            return list(AVAILABLE_PERMISSIONS)
        if not self.permissions:
            return list(AVAILABLE_PERMISSIONS)  # null = all (backward compat)
        try:
            perms = json.loads(self.permissions)
            return [p for p in perms if p in AVAILABLE_PERMISSIONS]
        except (json.JSONDecodeError, TypeError):
            return list(AVAILABLE_PERMISSIONS)

    def set_permissions(self, perms: list[str]) -> None:
        """Define as permissões. Filtra apenas as válidas."""
        valid = [p for p in perms if p in AVAILABLE_PERMISSIONS]
        self.permissions = json.dumps(valid)

    def has_permission(self, perm: str) -> bool:
        """Verifica se o membro tem uma permissão específica."""
        if self.role == "owner":
            return True
        return perm in self.get_permissions()
