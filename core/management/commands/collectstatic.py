"""
Shadows django-cloudinary-storage's own `collectstatic` command.

`cloudinary_storage` is in INSTALLED_APPS (needed for its
MediaCloudinaryStorage backend, used for user-uploaded media — avatars,
resumes), and Django's app-command precedence means any app defining a
`collectstatic` command overrides the built-in one from
django.contrib.staticfiles. cloudinary_storage's version is meant for
projects that *also* push their static assets to Cloudinary
(STATICFILES_STORAGE == 'cloudinary_storage.storage.StaticCloudinaryStorage')
— we don't do that, we use Django's own StaticFilesStorage for static files.
In our configuration, cloudinary_storage's collectstatic override runs
without error but silently fails to actually copy any files (confirmed via
Vercel's deployment "Static Assets" summary showing nothing collected, even
though the command exits cleanly) — a bug/gap in that package's non-Cloudinary
code path, not something in our own settings.

Since `core` is listed after `cloudinary_storage` in INSTALLED_APPS, Django
picks this file's Command over cloudinary_storage's for `manage.py
collectstatic`, while cloudinary_storage's app registration (and whatever
else it needs INSTALLED_APPS for) stays untouched.
"""

from django.contrib.staticfiles.management.commands.collectstatic import (
    Command as StaticfilesCollectstaticCommand,
)


class Command(StaticfilesCollectstaticCommand):
    pass
