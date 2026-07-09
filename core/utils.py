def get_current_mode(request):
    """
    Single source of truth for "which side of the site is this request on" —
    mirrors the logic in core.context_processors.site_content. Pulled out
    here so views (which need the plain string, not a template context
    dict) don't have to duplicate the path check.
    """
    return "client" if request.path.startswith("/client") else "user"
