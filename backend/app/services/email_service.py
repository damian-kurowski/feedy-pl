import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings


def send_email(to_email: str, subject: str, html_body: str) -> bool:
    """Send email via SMTP. Returns False if SMTP not configured."""
    if not settings.smtp_host or not settings.smtp_user:
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(msg)

    return True


def send_password_reset_email(to_email: str, reset_token: str) -> bool:
    """Send password reset email with link."""
    reset_url = f"{settings.app_url}/reset-password?token={reset_token}"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #4F46E5;">Feedy — Resetowanie hasła</h2>
        <p>Otrzymaliśmy prośbę o reset hasła do Twojego konta.</p>
        <p>Kliknij poniższy link, aby ustawić nowe hasło:</p>
        <p style="margin: 24px 0;">
            <a href="{reset_url}"
               style="background-color: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                Resetuj hasło
            </a>
        </p>
        <p style="color: #6B7280; font-size: 14px;">Link jest ważny przez 30 minut.</p>
        <p style="color: #6B7280; font-size: 14px;">Jeśli nie prosiłeś o reset hasła, zignoruj tę wiadomość.</p>
        <hr style="border: none; border-top: 1px solid #E5E7EB; margin: 24px 0;" />
        <p style="color: #9CA3AF; font-size: 12px;">Feedy — Zarządzanie feedami produktowymi</p>
    </div>
    """
    return send_email(to_email, "Resetowanie hasła — Feedy", html)


def send_feed_error_notification(to_email: str, feed_name: str, error: str) -> bool:
    """Notify user when their feed fails to refresh."""
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #4F46E5;">Feedy — Problem z feedem</h2>
        <p>Feed <strong>{feed_name}</strong> napotkał błąd podczas odświeżania:</p>
        <div style="background-color: #FEF2F2; border: 1px solid #FCA5A5; border-radius: 6px; padding: 12px; margin: 16px 0;">
            <p style="color: #991B1B; margin: 0; font-size: 14px;">{error}</p>
        </div>
        <p>Sprawdź konfigurację feeda w panelu Feedy.</p>
        <p style="margin: 24px 0;">
            <a href="{settings.app_url}/dashboard"
               style="background-color: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                Przejdź do panelu
            </a>
        </p>
    </div>
    """
    return send_email(to_email, f"Problem z feedem: {feed_name} — Feedy", html)
