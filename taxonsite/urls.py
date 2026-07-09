from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from accounts.views import client_account_view

urlpatterns = [
    path("admin/", admin.site.urls),
    # Our own accounts.urls is listed first, so its login/signup/logout/
    # account paths win for any path both apps define. allauth.urls only
    # actually gets used for the paths we don't define ourselves — the
    # google/login/ and google/login/callback/ ones.
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("allauth.urls")),
    # Client account management lives under /client/ (not /accounts/) so
    # its URL matches the site's single-mode-per-URL convention (core.utils
    # .get_current_mode derives mode from the path prefix) — this keeps a
    # client's account page feeling like part of /client/, not a detour
    # back into the user-facing /accounts/ namespace. See accounts.views
    # .account_view, which redirects here for any client user regardless
    # of which URL they land on.
    path("client/account/", client_account_view, name="client_account"),
    path("", include("core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
