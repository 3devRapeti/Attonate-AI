from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

from .forms import profile_is_complete
from .models import Profile

# Paths a logged-in user with an incomplete profile can still reach —
# otherwise they'd never be able to get to the account page to fix it, or to
# log out, or hit Django admin/static/media.
EXEMPT_PATH_PREFIXES = ("/accounts/", "/admin/", "/static/", "/media/")


class RequireCompleteProfileMiddleware:
    """
    Enforces that signed-in users fill in the required profile fields
    (full name, citizenship, work authorization — see
    accounts.forms.REQUIRED_PROFILE_FIELDS) before using the rest of the
    site. Redirects to the account page until they do.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if (
            user is not None
            and user.is_authenticated
            and not request.path.startswith(EXEMPT_PATH_PREFIXES)
        ):
            profile, _ = Profile.objects.get_or_create(user=user)
            if not profile_is_complete(profile):
                messages.info(request, "Finish setting up your profile to continue.")
                return redirect(f"{reverse('accounts:account')}#profile")
        return self.get_response(request)
