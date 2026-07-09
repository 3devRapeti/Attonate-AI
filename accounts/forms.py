from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import (
    COMPANY_SIZE_CHOICES,
    DAY_CHOICES,
    SECTOR_CHOICES,
    ClientProfile,
    Profile,
    User,
)


class SignupForm(UserCreationForm):
    """User (annotator) signup — kept minimal on purpose. The rest of the
    profile (citizenship, work info, etc.) is filled in after signup on the
    account page. Email and phone are both required and unique — see
    accounts.backends.EmailOrPhoneBackend."""

    class Meta:
        model = User
        fields = ("email", "phone_number")
        widgets = {
            "phone_number": forms.TextInput(attrs={"placeholder": "+1 555 000 0000"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "field-input"


class ClientSignupForm(UserCreationForm):
    """
    Client (enterprise) signup — a fuller form than the user side, since
    this is a higher-intent B2B action and we want the basics up front
    rather than deferring to a later "finish your account" step. No visa/
    work-eligibility questions here — those are user-only.
    """

    full_name = forms.CharField(max_length=150, label="Your name")
    company_name = forms.CharField(max_length=150, label="Company")
    position = forms.CharField(max_length=100, label="Your position at the company")
    sector = forms.ChoiceField(choices=SECTOR_CHOICES, label="Sector")
    country = forms.CharField(max_length=100, label="Country")
    company_size = forms.ChoiceField(choices=COMPANY_SIZE_CHOICES, label="Company size", required=False)
    company_website = forms.URLField(label="Company website", required=False)

    class Meta:
        model = User
        fields = ("email", "phone_number")
        widgets = {
            "phone_number": forms.TextInput(attrs={"placeholder": "+1 555 000 0000"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "field-input"

    def save(self, commit=True):
        user = super().save(commit=False)
        user.account_type = "client"
        if commit:
            user.save()
            ClientProfile.objects.create(
                user=user,
                full_name=self.cleaned_data["full_name"],
                company_name=self.cleaned_data["company_name"],
                position=self.cleaned_data["position"],
                sector=self.cleaned_data["sector"],
                country=self.cleaned_data["country"],
                company_size=self.cleaned_data.get("company_size", ""),
                company_website=self.cleaned_data.get("company_website", ""),
            )
        return user


class LoginForm(forms.Form):
    """Accepts either an email or a phone number — see
    accounts.backends.EmailOrPhoneBackend, which looks up whichever one was
    entered."""

    identifier = forms.CharField(
        label="Email or phone",
        widget=forms.TextInput(attrs={"class": "field-input", "autofocus": True}),
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "field-input"}))


# ---------------------------------------------------------------------------
# The account page is split into independently-saveable sections (own <form>,
# own Save button, own pane). Each of these is a partial ModelForm bound to
# the same Profile instance — saving one doesn't touch the others' fields.
# `section_id` is used by the template (tabs) and the view (routing which
# form a POST belongs to).
# ---------------------------------------------------------------------------


class ProfilePhotoNameForm(forms.ModelForm):
    section_id = "profile"
    section_label = "Profile"

    class Meta:
        model = Profile
        fields = ["display_name", "photo"]
        widgets = {
            "display_name": forms.TextInput(attrs={"class": "field-input"}),
        }
        labels = {"display_name": "Full name"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["display_name"].required = True


class WorkEligibilityForm(forms.ModelForm):
    section_id = "eligibility"
    section_label = "Work Eligibility"

    class Meta:
        model = Profile
        fields = ["citizenship", "visa_status", "work_auth_expiry"]
        widgets = {
            "citizenship": forms.TextInput(attrs={"class": "field-input"}),
            "visa_status": forms.Select(attrs={"class": "field-input"}),
            "work_auth_expiry": forms.DateInput(attrs={"class": "field-input", "type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["citizenship"].required = True
        self.fields["visa_status"].required = True


class WorkInfoForm(forms.ModelForm):
    section_id = "work"
    section_label = "Work Info"

    class Meta:
        model = Profile
        fields = ["job_title", "years_experience", "skills", "resume"]
        widgets = {
            "job_title": forms.TextInput(attrs={"class": "field-input"}),
            "years_experience": forms.NumberInput(attrs={"class": "field-input", "min": 0}),
            "skills": forms.TextInput(attrs={"class": "field-input", "placeholder": "Legal review, Spanish, Python"}),
        }


class AvailabilityForm(forms.ModelForm):
    section_id = "availability"
    section_label = "Availability"

    available_days = forms.MultipleChoiceField(
        choices=DAY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Profile
        fields = ["availability_hours", "timezone"]
        widgets = {
            "availability_hours": forms.NumberInput(attrs={"class": "field-input", "min": 0, "max": 168}),
            "timezone": forms.TextInput(attrs={"class": "field-input", "placeholder": "America/Los_Angeles"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["available_days"].initial = self.instance.available_days

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.available_days = self.cleaned_data.get("available_days", [])
        if commit:
            profile.save()
        return profile


class PayForm(forms.ModelForm):
    section_id = "pay"
    section_label = "Pay"

    class Meta:
        model = Profile
        fields = ["min_pay"]
        widgets = {
            "min_pay": forms.NumberInput(attrs={"class": "field-input", "min": 0, "step": "0.5"}),
        }


class NotificationsForm(forms.ModelForm):
    section_id = "notifications"
    section_label = "Notifications"

    muted_projects = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "field-input", "placeholder": "Project A, Project B"}),
        help_text="Comma-separated project names to mute notifications for.",
    )

    class Meta:
        model = Profile
        fields = ["notify_email", "notify_sms", "notify_project_digest", "notifications_paused"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["muted_projects"].initial = ", ".join(self.instance.muted_projects or [])

    def clean_muted_projects(self):
        raw = self.cleaned_data.get("muted_projects", "")
        return [p.strip() for p in raw.split(",") if p.strip()]

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.muted_projects = self.cleaned_data.get("muted_projects", [])
        if commit:
            profile.save()
        return profile


# Ordered list the view/template iterate over to build the tabs.
PROFILE_SECTION_FORMS = [
    ProfilePhotoNameForm,
    WorkEligibilityForm,
    WorkInfoForm,
    AvailabilityForm,
    PayForm,
    NotificationsForm,
]

REQUIRED_PROFILE_FIELDS = ["display_name", "citizenship", "visa_status"]


def profile_is_complete(profile):
    return all(getattr(profile, field) for field in REQUIRED_PROFILE_FIELDS)


# ---------------------------------------------------------------------------
# Client account page. Unlike the user side, everything required is already
# collected at signup (ClientSignupForm), so this is a single simple form —
# no tabs, no "finish your account" nudging.
# ---------------------------------------------------------------------------


class ClientProfileForm(forms.ModelForm):
    class Meta:
        model = ClientProfile
        fields = [
            "full_name",
            "company_name",
            "position",
            "sector",
            "country",
            "company_size",
            "company_website",
            "use_case",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "field-input"}),
            "company_name": forms.TextInput(attrs={"class": "field-input"}),
            "position": forms.TextInput(attrs={"class": "field-input"}),
            "sector": forms.Select(attrs={"class": "field-input"}),
            "country": forms.TextInput(attrs={"class": "field-input"}),
            "company_size": forms.Select(attrs={"class": "field-input"}),
            "company_website": forms.URLInput(attrs={"class": "field-input"}),
            "use_case": forms.Textarea(attrs={"class": "field-input", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("full_name", "company_name", "position", "sector", "country"):
            self.fields[name].required = True
