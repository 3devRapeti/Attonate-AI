import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from . import otp
from .forms import (
    PROFILE_SECTION_FORMS,
    ClientProfileForm,
    ClientSignupForm,
    LoginForm,
    SignupForm,
    profile_is_complete,
)
from .models import ClientProfile, Profile

SECTION_FORM_MAP = {cls.section_id: cls for cls in PROFILE_SECTION_FORMS}

# Backend to credit explicitly when logging someone in right after
# form.save() (i.e. not via authenticate()) — needed now that
# AUTHENTICATION_BACKENDS has more than one entry (email/phone login +
# Google), so Django can't infer which one to use on its own.
_LOGIN_BACKEND = "accounts.backends.EmailOrPhoneBackend"


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("core:home")
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.account_type = "user"
            user.save(update_fields=["account_type"])
            Profile.objects.create(user=user, display_name="")
            login(request, user, backend=_LOGIN_BACKEND)
            messages.success(request, "Welcome to Taxon AI — let's finish setting up your profile.")
            return redirect("accounts:account")
    else:
        form = SignupForm()
    return render(request, "accounts/signup.html", {"form": form})


def client_signup_view(request):
    """Client (enterprise) signup — separate, fuller form than the user
    side. See accounts.forms.ClientSignupForm for why."""
    if request.user.is_authenticated:
        return redirect("core:home")
    if request.method == "POST":
        form = ClientSignupForm(request.POST)
        if form.is_valid():
            user = form.save()  # also creates the ClientProfile — see the form's save()
            login(request, user, backend=_LOGIN_BACKEND)
            messages.success(request, "Welcome to Taxon AI — our team will be in touch shortly.")
            return redirect("core:client_home")
    else:
        form = ClientSignupForm()
    return render(request, "accounts/client_signup.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("core:home")
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data["identifier"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=identifier, password=password)
            if user is not None:
                login(request, user)
                return redirect("core:home")
            form.add_error(None, "Incorrect email/phone or password.")
    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("core:home")


@login_required
def account_view(request):
    # Client accounts get their own URL (/client/account/, see taxonsite.
    # urls) so the page stays under the site's single-mode-per-URL scheme
    # instead of rendering client content at a /accounts/... URL. Redirect
    # rather than calling client_account_view directly, so this also
    # canonicalizes any old bookmark/link straight to the right place.
    if request.user.is_client:
        return redirect("client_account")

    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        section_id = request.POST.get("section")
        form_cls = SECTION_FORM_MAP.get(section_id)
        if form_cls is None:
            messages.error(request, "Something went wrong — unrecognized section.")
            return redirect("accounts:account")

        submitted_form = form_cls(request.POST, request.FILES, instance=profile)
        if submitted_form.is_valid():
            submitted_form.save()
            messages.success(request, f"{form_cls.section_label} saved.")
            return redirect(f"{reverse('accounts:account')}#{section_id}")

        # Invalid: re-render with this section's errors, everything else fresh.
        forms_by_section = {
            cls.section_id: (submitted_form if cls is form_cls else cls(instance=profile))
            for cls in PROFILE_SECTION_FORMS
        }
    else:
        forms_by_section = {cls.section_id: cls(instance=profile) for cls in PROFILE_SECTION_FORMS}

    return render(
        request,
        "accounts/account.html",
        {
            "profile": profile,
            "sections": PROFILE_SECTION_FORMS,
            "forms_by_section": forms_by_section,
            "profile_complete": profile_is_complete(profile),
        },
    )


@login_required
def client_account_view(request):
    """Client account page — a single simple form (company info + contact),
    since everything required was already collected at signup. Lives at its
    own URL (/client/account/, see taxonsite.urls) so it stays under the
    site's single-mode-per-URL scheme; account_view also redirects here for
    any client user who lands on /accounts/account/ instead."""
    if not request.user.is_client:
        return redirect("accounts:account")

    client_profile, _ = ClientProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ClientProfileForm(request.POST, instance=client_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Company details saved.")
            return redirect("client_account")
    else:
        form = ClientProfileForm(instance=client_profile)

    return render(
        request,
        "accounts/client_account.html",
        {"client_profile": client_profile, "form": form},
    )


@login_required
def export_data_view(request):
    account = {"email": request.user.email, "phone_number": request.user.phone_number}

    if request.user.is_client:
        profile = get_object_or_404(ClientProfile, user=request.user)
        data = {
            "account": account,
            "client_profile": {
                "full_name": profile.full_name,
                "company_name": profile.company_name,
                "position": profile.position,
                "sector": profile.get_sector_display() if profile.sector else "",
                "country": profile.country,
                "company_size": profile.company_size,
                "company_website": profile.company_website,
                "use_case": profile.use_case,
            },
        }
    else:
        profile = get_object_or_404(Profile, user=request.user)
        data = {
            "account": account,
            "profile": {
                "display_name": profile.display_name,
                "citizenship": profile.citizenship,
                "visa_status": profile.get_visa_status_display() if profile.visa_status else "",
                "work_auth_expiry": str(profile.work_auth_expiry) if profile.work_auth_expiry else None,
                "job_title": profile.job_title,
                "years_experience": profile.years_experience,
                "skills": profile.skills,
                "availability_hours": profile.availability_hours,
                "timezone": profile.timezone,
                "available_days": profile.available_days,
                "rating": profile.rating,
                "min_pay": str(profile.min_pay) if profile.min_pay is not None else None,
                "notify_email": profile.notify_email,
                "notify_sms": profile.notify_sms,
                "notify_project_digest": profile.notify_project_digest,
                "notifications_paused": profile.notifications_paused,
                "muted_projects": profile.muted_projects,
            },
        }

    response = HttpResponse(json.dumps(data, indent=2), content_type="application/json")
    response["Content-Disposition"] = 'attachment; filename="taxon-account-data.json"'
    return response


@login_required
def delete_account_view(request):
    if request.method == "POST":
        user = request.user
        was_client = user.is_client
        logout(request)
        user.delete()  # cascades to Profile/ClientProfile, and Django clears the uploaded files' DB rows
        # (Photo/resume files on disk aren't auto-deleted by Django — fine for
        # local dev; worth adding a signal/cleanup job before real deployment.)
        messages.success(request, "Your account has been deleted.")
        return redirect("core:client_home" if was_client else "core:home")
    return render(request, "accounts/delete_confirm.html")


def _account_url_with_fragment(request, fragment):
    """Wherever this user's account page lives (client vs user — see
    account_view/client_account_view), with #fragment appended so the
    browser scrolls straight back to the verification card."""
    name = "client_account" if request.user.is_client else "accounts:account"
    return f"{reverse(name)}#{fragment}"


# ---------------------------------------------------------------------
# Email + phone OTP verification (see accounts.otp for the actual send/
# check logic). Non-blocking by design — nothing gates on email_verified
# or phone_verified being True yet; these just flip status badges on the
# account page. Currently only surfaced in templates/accounts/
# client_account.html, but the views themselves aren't client-only, so
# the same UI can be added to the user account page later with no
# backend changes.
# ---------------------------------------------------------------------

@login_required
def send_email_otp_view(request):
    if request.method == "POST":
        if request.user.email_verified:
            messages.info(request, "Your email is already verified.")
        else:
            try:
                otp.send_email_otp(request.user)
                messages.success(request, f"Verification code sent to {request.user.email}.")
            except otp.OTPSendError as exc:
                messages.error(request, str(exc))
    return redirect(_account_url_with_fragment(request, "verify"))


@login_required
def verify_email_otp_view(request):
    if request.method == "POST":
        result = otp.check_email_otp(request.user, request.POST.get("code", ""))
        if result.ok:
            request.user.email_verified = True
            request.user.save(update_fields=["email_verified"])
            messages.success(request, "Email verified.")
        else:
            messages.error(request, result.error or "Verification failed.")
    return redirect(_account_url_with_fragment(request, "verify"))


@login_required
def send_phone_otp_view(request):
    if request.method == "POST":
        if request.user.phone_verified:
            messages.info(request, "Your phone number is already verified.")
        else:
            try:
                otp.send_phone_otp(request.user)
                messages.success(request, f"Verification code sent to {request.user.phone_number}.")
            except otp.OTPSendError as exc:
                messages.error(request, str(exc))
    return redirect(_account_url_with_fragment(request, "verify"))


@login_required
def verify_phone_otp_view(request):
    if request.method == "POST":
        result = otp.check_phone_otp(request.user, request.POST.get("code", ""))
        if result.ok:
            request.user.phone_verified = True
            request.user.save(update_fields=["phone_verified"])
            messages.success(request, "Phone number verified.")
        else:
            messages.error(request, result.error or "Verification failed.")
    return redirect(_account_url_with_fragment(request, "verify"))
