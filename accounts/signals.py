import urllib.request
from urllib.error import URLError

from allauth.account.signals import user_signed_up
from django.core.files.base import ContentFile
from django.dispatch import receiver

from .models import Profile


@receiver(user_signed_up)
def populate_profile_from_google(sender, request, user, **kwargs):
    """
    When someone signs up via Google (not plain email/password), pull their
    name and profile photo from the Google account instead of leaving those
    fields blank for them to fill in manually.
    """
    sociallogin = kwargs.get("sociallogin")
    if not sociallogin or sociallogin.account.provider != "google":
        return

    # Google sign-up doesn't go through our own signup_view (which redirects
    # straight to the account page), so it lands on LOGIN_REDIRECT_URL
    # (the homepage) instead. This flag makes the very next page load bounce
    # to the account page one time, matching the email-signup flow.
    if request is not None:
        request.session["just_signed_up"] = True

    profile, _ = Profile.objects.get_or_create(user=user)
    data = sociallogin.account.extra_data
    changed = False

    name = data.get("name")
    if name and not profile.display_name:
        profile.display_name = name
        changed = True

    picture_url = data.get("picture")
    if picture_url and not profile.photo:
        try:
            with urllib.request.urlopen(picture_url, timeout=5) as resp:
                image_data = resp.read()
            profile.photo.save(f"{user.pk}_google.jpg", ContentFile(image_data), save=False)
            changed = True
        except (URLError, OSError, ValueError):
            # Non-fatal — worst case they just upload a photo manually later.
            pass

    if changed:
        profile.save()
