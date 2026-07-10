"""
Admin email notifications — pings a real inbox whenever a lead comes in
(Contact Sales / Support) or a new account is created, instead of that
only being visible by checking /admin/ manually.

Reuses the same Resend setup as accounts.otp (RESEND_API_KEY — no second
account/service needed), and degrades to a console print when it's not
configured, same dev-without-credentials pattern as accounts.otp.

Add to .env / Vercel env vars:
  ADMIN_NOTIFY_EMAIL   - where these notifications get sent. Supports
                         multiple recipients as a comma-separated list,
                         e.g. "tridevrapeti@gmail.com,bhuwansaik@gmail.com".
                         Notifications are silently skipped (not even
                         printed) if this isn't set.

Note: on Resend's shared onboarding@resend.dev domain (the OTP_FROM_EMAIL
default), Resend only allows delivery to the email address you signed up
to Resend with — a second recipient on a different address will likely
get rejected/silently dropped even though the API call itself succeeds.
Verifying your own domain in Resend (e.g. so mail sends from
notifications@attonate.com) removes that restriction and lets you send to
any recipient, including a cofounder's inbox.
"""

import os


def notify_admin(subject, fields):
    """
    fields: list of (label, value) tuples, rendered as a simple HTML body.
    No-op if ADMIN_NOTIFY_EMAIL isn't set — everything past that first
    check is skipped, including the dev-console fallback, so this is safe
    to call unconditionally from views without extra guards.
    """
    raw_to = os.environ.get("ADMIN_NOTIFY_EMAIL", "")
    if not raw_to:
        return
    to_emails = [addr.strip() for addr in raw_to.split(",") if addr.strip()]
    if not to_emails:
        return

    body_html = "".join(
        f"<p><strong>{label}:</strong> {value}</p>" for label, value in fields
    )
    api_key = os.environ.get("RESEND_API_KEY", "")

    if not api_key:
        # Dev fallback: no Resend key configured yet — print instead of
        # sending, mirroring accounts.otp.send_email_otp.
        plain = "\n".join(f"{label}: {value}" for label, value in fields)
        print(f"[dev-notify] {subject} -> {', '.join(to_emails)}\n{plain}")
        return

    import resend  # imported lazily so the package is only required once configured

    resend.api_key = api_key
    from_email = os.environ.get("OTP_FROM_EMAIL", "Attonate <onboarding@resend.dev>")
    try:
        resend.Emails.send(
            {
                "from": from_email,
                "to": to_emails,
                "subject": subject,
                "html": body_html,
            }
        )
    except Exception as exc:  # Resend's SDK raises plain Exception subclasses
        # Never let a notification failure break the actual form
        # submission / signup — just log it.
        print(f"[notify] failed to send admin notification: {exc}")
