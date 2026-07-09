from .forms import profile_is_complete
from .models import Profile


def profile_status(request):
    """
    Makes `profile_incomplete` available to every template, so base.html can
    show a persistent (but non-blocking) reminder banner site-wide instead of
    hard-redirecting people away from pages they're just trying to browse.

    Client accounts don't get this nudge — everything required is already
    collected up front at signup (see accounts.forms.ClientSignupForm), so
    there's nothing to finish.
    """
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated or user.is_client:
        return {"profile_incomplete": False}
    profile, _ = Profile.objects.get_or_create(user=user)
    return {"profile_incomplete": not profile_is_complete(profile)}
