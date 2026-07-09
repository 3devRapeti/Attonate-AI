from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from .managers import UserManager

OTP_CHANNEL_CHOICES = [
    ("email", "Email"),
    ("phone", "Phone"),
]

VISA_CHOICES = [
    ("us_citizen", "U.S. Citizen"),
    ("green_card", "Permanent Resident (Green Card)"),
    ("h1b", "H-1B"),
    ("opt", "OPT / STEM OPT"),
    ("tn", "TN Visa"),
    ("other_visa", "Other work visa"),
    ("not_authorized", "Not authorized to work in the U.S."),
    ("outside_us", "Outside the U.S. — no visa needed"),
]

DAY_CHOICES = [
    ("Mon", "Mon"),
    ("Tue", "Tue"),
    ("Wed", "Wed"),
    ("Thu", "Thu"),
    ("Fri", "Fri"),
    ("Sat", "Sat"),
    ("Sun", "Sun"),
]

SECTOR_CHOICES = [
    ("healthcare", "Healthcare"),
    ("finance", "Finance"),
    ("legal", "Legal"),
    ("technology", "Technology / Software"),
    ("automotive", "Automotive"),
    ("retail_ecommerce", "Retail / E-commerce"),
    ("education", "Education"),
    ("government", "Government / Public Sector"),
    ("research_academia", "Research / Academia"),
    ("other", "Other"),
]

COMPANY_SIZE_CHOICES = [
    ("1-10", "1–10 employees"),
    ("11-50", "11–50 employees"),
    ("51-200", "51–200 employees"),
    ("201-1000", "201–1,000 employees"),
    ("1000+", "1,000+ employees"),
]

ACCOUNT_TYPE_CHOICES = [
    ("user", "User"),
    ("client", "Client"),
]


class User(AbstractUser):
    """
    Email-based user. Username is dropped in favor of email as the login
    field. Phone number is also required and unique — per an explicit
    product decision, email and phone both act as primary lookup keys for
    an account (see accounts.backends.EmailOrPhoneBackend, which lets
    someone log in with either one).
    """

    username = None
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, unique=True)

    # Which side of the site this account belongs to. Determines which
    # profile model (Profile vs ClientProfile) and which account page/signup
    # flow applies — set once at signup and not changed afterward.
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES, default="user")

    # OTP verification status (see accounts.otp + the send/verify views in
    # accounts.views). Non-blocking today — nothing gates on these being
    # True — currently only surfaced on the client account page.
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone_number"]

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def is_client(self):
        return self.account_type == "client"


class Profile(models.Model):
    """
    Annotator/contributor profile (User-mode account management). Client-side
    account pages are a separate, later effort.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    # Photo & name
    display_name = models.CharField(max_length=150, blank=True)
    photo = models.ImageField(upload_to="avatars/", blank=True, null=True)

    # Citizenship & work authorization
    citizenship = models.CharField(max_length=100, blank=True)
    visa_status = models.CharField(max_length=30, choices=VISA_CHOICES, blank=True)
    work_auth_expiry = models.DateField(blank=True, null=True)

    # Work info & resume
    job_title = models.CharField(max_length=150, blank=True)
    years_experience = models.PositiveIntegerField(blank=True, null=True)
    skills = models.CharField(max_length=500, blank=True, help_text="Comma-separated")
    resume = models.FileField(upload_to="resumes/", blank=True, null=True)

    # Availability
    availability_hours = models.PositiveIntegerField(blank=True, null=True, help_text="Hours per week")
    timezone = models.CharField(max_length=100, blank=True)
    available_days = models.JSONField(default=list, blank=True)

    # Rating — set by Taxon, not user-editable
    rating = models.FloatField(blank=True, null=True)

    # Pay preference
    min_pay = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    # Notification preferences
    notify_email = models.BooleanField(default=True)
    notify_sms = models.BooleanField(default=True)
    notify_project_digest = models.BooleanField(default=True)
    notifications_paused = models.BooleanField(default=False)
    muted_projects = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name or self.user.email

    @property
    def rating_label(self):
        if self.rating is None:
            return None
        if self.rating >= 90:
            return "A+"
        if self.rating >= 80:
            return "A"
        if self.rating >= 70:
            return "B+"
        if self.rating >= 60:
            return "B"
        return "C"


class ClientProfile(models.Model):
    """
    Company/client account details (Client-mode account management).
    Unlike Profile (annotators), all the required fields here are collected
    up front at signup — see accounts.forms.ClientSignupForm — so there's no
    "finish your account" nudge flow for clients like there is for users.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="client_profile")

    full_name = models.CharField(max_length=150, blank=True)
    company_name = models.CharField(max_length=150, blank=True)
    position = models.CharField(max_length=100, blank=True, help_text="Their role/title at the company")
    sector = models.CharField(max_length=30, choices=SECTOR_CHOICES, blank=True)
    country = models.CharField(max_length=100, blank=True)

    # Extra qualifying details for the sales team — optional.
    company_size = models.CharField(max_length=20, choices=COMPANY_SIZE_CHOICES, blank=True)
    company_website = models.URLField(blank=True)
    use_case = models.TextField(blank=True, help_text="What kind of annotation/labeling work are they looking for?")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name or self.user.email


class OTPCode(models.Model):
    """
    A one-time verification code for either the email or phone channel.

    Always used for email (Resend is a plain send-API, not a verification
    service, so we generate/store/check the code ourselves). For phone,
    this is only used as a *local fallback* when Twilio isn't configured
    (see accounts.otp) — once TWILIO_ACCOUNT_SID/AUTH_TOKEN/
    VERIFY_SERVICE_SID are set, Twilio Verify manages phone codes itself
    and rows here are never created for that channel.

    code_hash, never the raw code, is what's stored — see accounts.otp
    for the hashing/generation/checking logic.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otp_codes")
    channel = models.CharField(max_length=10, choices=OTP_CHANNEL_CHOICES)
    code_hash = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)
    consumed = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=["user", "channel", "consumed"])]

    def __str__(self):
        return f"{self.channel} OTP for {self.user.email}"

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at
