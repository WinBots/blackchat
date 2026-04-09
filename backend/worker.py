"""
Ponto de entrada do worker ARQ.

Uso (a partir do diretório backend/):

  Desenvolvimento (todas as filas):
    arq worker.WorkerSettings

  Produção (workers especializados por domínio):
    arq worker.WebhookWorkerSettings   # Webhooks Telegram/Instagram
    arq worker.FlowWorkerSettings      # Execução de fluxos
    arq worker.BulkWorkerSettings      # Disparos em massa
    arq worker.SequenceWorkerSettings  # Sequências, e-mail, IA

Cada comando acima deve ser iniciado como processo separado.
Em produção, use supervisord, systemd ou PM2 para gerenciar os processos.
"""
# Re-exporta tudo do pacote workers para facilitar o import pelo CLI do ARQ
from app.workers.worker_settings import (
    WorkerSettings,
    WebhookWorkerSettings,
    FlowWorkerSettings,
    BulkWorkerSettings,
    SequenceWorkerSettings,
)

__all__ = [
    "WorkerSettings",
    "WebhookWorkerSettings",
    "FlowWorkerSettings",
    "BulkWorkerSettings",
    "SequenceWorkerSettings",
]
