from .content import CONTENT
from .utils import get_current_mode


def site_content(request):
    """Makes the site content available in every template (navbar/footer
    need it too, not just the home page).

    The site no longer has a client-side user/client toggle — instead, mode
    is determined by URL: anything under /client/ is the client-facing
    marketing site, everything else is the user (annotator) side. This is
    computed here so every view/template gets the right mode_data without
    each view having to set it individually.
    """
    current_mode = get_current_mode(request)
    return {
        "content": CONTENT,
        "current_mode": current_mode,
        "mode_data": CONTENT[current_mode],
    }
