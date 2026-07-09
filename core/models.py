from django.conf import settings
from django.db import models


class ContactSalesLead(models.Model):
    """
    "Looking for annotators?" lead capture — lives on the user-facing
    homepage (see templates/core/home.html) since that's aimed at labs/
    companies who land there rather than on the client marketing page.
    No email notifications are wired up yet — visible via Django admin.
    """

    name = models.CharField(max_length=150)
    lab_name = models.CharField(max_length=150, verbose_name="Lab / company name")
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.lab_name} ({self.email})"


class SupportRequest(models.Model):
    REASON_CHOICES = [
        ("account", "Account issue"),
        ("payment", "Payment / payout issue"),
        ("technical", "Technical problem"),
        ("general", "General question"),
        ("other", "Other"),
    ]

    MODE_CHOICES = [
        ("user", "User"),
        ("client", "Client"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="support_requests",
    )
    name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)

    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    message = models.TextField(blank=True)

    submitted_mode = models.CharField(max_length=10, choices=MODE_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        who = self.user.email if self.user_id else (self.email or "anonymous")
        return f"{who} — {self.get_reason_display()}"
