"""
OTP generation, delivery, and verification for email + phone.

Email always goes through this module's own generate/hash/check logic —
Resend is a plain send-API, not a verification service, so there's no
provider-side "check this code" call to defer to.

Phone prefers Twilio Verify (which manages code generation/expiry/checking
entirely on Twilio's side) when TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN /
TWILIO_VERIFY_SERVICE_SID are all set. When they're not set — e.g. local
dev, before a Twilio account exists — phone falls back to the same local
OTPCode flow as email, with the code printed to the console instead of
actually being texted. This means the whole feature is testable end-to-end
with zero credentials, and switches to real SMS the moment those three
env vars are added — no other code changes needed.

Required env vars (add to .env — see taxonsite/settings.py for how it's
loaded):
  RESEND_API_KEY          - from https://resend.com (free tier: 3k/mo)
  OTP_FROM_EMAIL          - e.g. "Taxon AI <onboarding@resend.dev>" (Resend's
                            shared test domain works until you verify your
                            own domain with them)
  TWILIO_ACCOUNT_SID      - from the Twilio console
  TWILIO_AUTH_TOKEN       - from the Twilio console
  TWILIO_VERIFY_SERVICE_SID - create a "Verify Service" in the Twilio
                            console (Verify > Services) and paste its SID
"""

import hashlib
import os
import random
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from .models import OTPCode

OTP_TTL_MINUTES = 10
MAX_ATTEMPTS = 5
RESEND_COOLDOWN_SECONDS = 60


class OTPSendError(Exception):
    """Raised when a code couldn't be generated/sent — message is user-safe."""


class OTPCheckResult:
    def __init__(self, ok, error=None):
        self.ok = ok
        self.error = error


def _hash_code(code, user_id, channel):
    # Not a password — a short-lived, single-use, rate-limited code — but
    # hashing it is nearly free and means a DB read/leak doesn't expose
    # live codes. Salted with SECRET_KEY so it isn't a bare SHA256(code).
    raw = f"{channel}:{user_id}:{code}:{settings.SECRET_KEY}"
    return hashlib.sha256(raw.encode()).hexdigest()


def _generate_local_code(user, channel):
    """Create+store a fresh local OTPCode row, invalidating older ones for
    this user/channel. Returns the plaintext code (never stored as-is)."""
    code = f"{random.randint(0, 999999):06d}"
    OTPCode.objects.filter(user=user, channel=channel, consumed=False).delete()
    OTPCode.objects.create(
        user=user,
        channel=channel,
        code_hash=_hash_code(code, user.pk, channel),
        expires_at=timezone.now() + timedelta(minutes=OTP_TTL_MINUTES),
    )
    return code


def _check_local_code(user, channel, submitted_code):
    otp = (
        OTPCode.objects.filter(user=user, channel=channel, consumed=False)
        .order_by("-created_at")
        .first()
    )
    if otp is None:
        return OTPCheckResult(False, "No code found — request a new one.")
    if otp.is_expired:
        return OTPCheckResult(False, "That code expired — request a new one.")
    if otp.attempts >= MAX_ATTEMPTS:
        return OTPCheckResult(False, "Too many attempts — request a new one.")

    otp.attempts += 1
    otp.save(update_fields=["attempts"])

    if otp.code_hash != _hash_code(submitted_code.strip(), user.pk, channel):
        return OTPCheckResult(False, "Incorrect code.")

    otp.consumed = True
    otp.save(update_fields=["consumed"])
    return OTPCheckResult(True)


def _recent_send_exists(user, channel):
    cutoff = timezone.now() - timedelta(seconds=RESEND_COOLDOWN_SECONDS)
    return OTPCode.objects.filter(
        user=user, channel=channel, created_at__gte=cutoff
    ).exists()


# --------------------------------------------------------------------- #
# Email (always local generation + Resend delivery, console fallback)
# --------------------------------------------------------------------- #

def send_email_otp(user):
    if _recent_send_exists(user, "email"):
        raise OTPSendError("Please wait a bit before requesting another code.")

    code = _generate_local_code(user, "email")
    api_key = os.environ.get("RESEND_API_KEY", "")

    if not api_key:
        # Dev fallback: no Resend key configured yet — print instead of
        # sending, so the feature is fully testable without credentials.
        print(f"[dev-otp] Email verification code for {user.email}: {code}")
        return

    import resend  # imported lazily so the package is only required once configured

    resend.api_key = api_key
    from_email = os.environ.get("OTP_FROM_EMAIL", "Taxon AI <onboarding@resend.dev>")
    try:
        resend.Emails.send(
            {
                "from": from_email,
                "to": user.email,
                "subject": "Your Taxon AI verification code",
                "html": (
                    f"<p>Your verification code is <strong>{code}</strong>.</p>"
                    f"<p>It expires in {OTP_TTL_MINUTES} minutes.</p>"
                ),
            }
        )
    except Exception as exc:  # Resend's SDK raises plain Exception subclasses
        raise OTPSendError("Couldn't send the email — please try again shortly.") from exc


def check_email_otp(user, submitted_code):
    return _check_local_code(user, "email", submitted_code)


# --------------------------------------------------------------------- #
# Phone (Twilio Verify when configured, local fallback otherwise)
# --------------------------------------------------------------------- #

def _twilio_configured():
    return all(
        os.environ.get(k)
        for k in ("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_VERIFY_SERVICE_SID")
    )


def _twilio_verify_service():
    from twilio.rest import Client  # imported lazily, same reasoning as resend above

    client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
    return client.verify.v2.services(os.environ["TWILIO_VERIFY_SERVICE_SID"])


def send_phone_otp(user):
    if not _twilio_configured():
        if _recent_send_exists(user, "phone"):
            raise OTPSendError("Please wait a bit before requesting another code.")
        code = _generate_local_code(user, "phone")
        print(f"[dev-otp] Phone verification code for {user.phone_number}: {code}")
        return

    try:
        _twilio_verify_service().verifications.create(to=user.phone_number, channel="sms")
    except Exception as exc:  # twilio.base.exceptions.TwilioRestException et al.
        raise OTPSendError("Couldn't send the text — check the phone number and try again.") from exc


def check_phone_otp(user, submitted_code):
    if not _twilio_configured():
        return _check_local_code(user, "phone", submitted_code)

    try:
        check = _twilio_verify_service().verification_checks.create(
            to=user.phone_number, code=submitted_code.strip()
        )
    except Exception:
        return OTPCheckResult(False, "Incorrect or expired code.")

    if check.status == "approved":
        return OTPCheckResult(True)
    return OTPCheckResult(False, "Incorrect or expired code.")
