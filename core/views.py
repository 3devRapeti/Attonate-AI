from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from accounts.forms import profile_is_complete
from accounts.models import Profile

from .forms import ContactSalesForm, SupportRequestForm
from .utils import get_current_mode


def _is_ajax(request):
    # The contact forms progressively enhance into fetch()-based submissions
    # (see static/js/site.js initContactForms) so the "sent" animation can
    # play without a full page reload. This header is how the JS marks
    # those requests; anything else (JS disabled, fetch failed) falls back
    # to a normal POST and gets the classic redirect/messages flow below.
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def _handle_contact_forms(request):
    """
    Shared POST handling for the two embedded lead-capture forms that live
    on core/home.html (Contact Sales + Contact Support). Both forms post
    back to the same URL they're rendered on (/ or /client/), distinguished
    by a hidden `form_name` field. Returns a redirect/JsonResponse on
    success (POST/redirect/GET, so a refresh doesn't resubmit), or the two
    unbound/bound forms to render otherwise.
    """
    contact_sales_form = ContactSalesForm()
    support_form = SupportRequestForm(authenticated=request.user.is_authenticated)
    ajax = _is_ajax(request)

    if request.method == "POST" and request.POST.get("form_name") == "contact_sales":
        contact_sales_form = ContactSalesForm(request.POST)
        if contact_sales_form.is_valid():
            contact_sales_form.save()
            if ajax:
                return JsonResponse({"ok": True, "message": "Thanks — we'll be in touch shortly."})
            messages.success(request, "Thanks — we'll be in touch shortly.")
            return redirect(request.path + "#contact-sales")
        if ajax:
            return JsonResponse(
                {"ok": False, "errors": contact_sales_form.errors.get_json_data()}, status=400
            )

    elif request.method == "POST" and request.POST.get("form_name") == "support":
        support_form = SupportRequestForm(request.POST, authenticated=request.user.is_authenticated)
        if support_form.is_valid():
            support_request = support_form.save(commit=False)
            support_request.submitted_mode = get_current_mode(request)
            if request.user.is_authenticated:
                support_request.user = request.user
                support_request.name = ""
                support_request.email = request.user.email
            support_request.save()
            if ajax:
                return JsonResponse({"ok": True, "message": "Support request sent — we'll follow up by email."})
            messages.success(request, "Support request sent — we'll follow up by email.")
            return redirect(request.path + "#contact-support")
        if ajax:
            return JsonResponse({"ok": False, "errors": support_form.errors.get_json_data()}, status=400)

    return contact_sales_form, support_form


def home(request):
    # One-time bounce to the account page right after a Google sign-up (see
    # accounts.signals.populate_profile_from_google) — mirrors what our own
    # email/password signup_view already does directly.
    if request.session.pop("just_signed_up", False):
        return redirect(f"{reverse('accounts:account')}#profile")

    result = _handle_contact_forms(request)
    if not isinstance(result, tuple):
        return result
    contact_sales_form, support_form = result
    return render(request, "core/home.html", {
        "contact_sales_form": contact_sales_form,
        "support_form": support_form,
    })


def client_home(request):
    # Client-mode marketing page, served at /client/. current_mode/mode_data
    # are supplied by core.context_processors.site_content, which derives
    # the mode from request.path — no separate context needed here, and no
    # separate template either (core/home.html branches on current_mode for
    # the couple of spots that differ, e.g. the Apply CTA).
    result = _handle_contact_forms(request)
    if not isinstance(result, tuple):
        return result
    contact_sales_form, support_form = result
    return render(request, "core/home.html", {
        "contact_sales_form": contact_sales_form,
        "support_form": support_form,
    })


def coming_soon_view(request):
    """
    Shared landing spot for every not-yet-built feature (client dashboard,
    footer links, secondary CTAs, etc). Open to everyone — no reason to
    gate a placeholder page — and points people at Contact Sales so
    interested visitors/clients still turn into a real lead instead of a
    dead end.
    """
    return render(request, "core/coming_soon.html")


@login_required
def apply_view(request):
    """
    Entry point for "Apply" CTAs. Browsing the site (including job/task
    details, once those exist) stays open to everyone — this is the one
    place that actually requires a finished profile, since applying is the
    action that matters.
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if not profile_is_complete(profile):
        messages.warning(request, "Finish your account before applying.")
        return redirect(f"{reverse('accounts:account')}#profile")
    return render(request, "core/apply_placeholder.html")
