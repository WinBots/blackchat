import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()  # carrega variáveis do arquivo .env

# ---------------------------------------------------------------------------
# Configurações — preencha aqui ou defina variáveis de ambiente:
#   TITAN_USER  e  TITAN_PASS
# ---------------------------------------------------------------------------
SMTP_SERVER = "smtp.titan.email"
SMTP_PORT   = 587                          # TLS; use 465 para SSL

USERNAME    = os.getenv("TITAN_USER", "seu.usuario@seudominio.com")
PASSWORD    = os.getenv("TITAN_PASS", "sua_senha")
DESTINATARIO = "windson3433@gmail.com"


def enviar_email(destinatario: str, assunto: str, corpo: str) -> None:
    """Envia um e-mail via Titan SMTP usando STARTTLS (porta 587)."""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = assunto
    msg["From"]    = USERNAME
    msg["To"]      = destinatario
    msg.attach(MIMEText(corpo, "plain", "utf-8"))

    print(f"[+] Conectando a {SMTP_SERVER}:{SMTP_PORT} ...")
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()          # inicia TLS
            server.ehlo()
            server.login(USERNAME, PASSWORD)
            server.sendmail(USERNAME, [destinatario], msg.as_string())
            print(f"[✓] E-mail enviado com sucesso para {destinatario}")

    except smtplib.SMTPAuthenticationError:
        print("[✗] Falha de autenticação — verifique usuário e senha.")
    except smtplib.SMTPConnectError as e:
        print(f"[✗] Não foi possível conectar ao servidor: {e}")
    except smtplib.SMTPException as e:
        print(f"[✗] Erro SMTP: {e}")
    except OSError as e:
        print(f"[✗] Erro de rede/timeout: {e}")


if __name__ == "__main__":
    enviar_email(
        destinatario=DESTINATARIO,
        assunto="Teste de envio — Titan SMTP",
        corpo="Olá!\n\nEste é um e-mail de teste enviado via Titan SMTP com Python.\n",
    )
