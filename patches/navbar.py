from CTFd.plugins import override_template
from CTFd.utils.config import ctf_theme

def patch_navbar(app):
    """
    Patch challenge listing to list module challenges instead
    """
    theme = ctf_theme()

    if 'components/navbar.html' in app.overridden_templates:
        original = app.override_templates['components/navbar.html']
    else:
        with open(f'/opt/CTFd/CTFd/themes/{theme}/templates/components/navbar.html', 'r') as f:
            original = f.read()

    original = original.replace("Challenges", "Modules")
    original = original.replace("challenges.listing", "modules.listing")

    override_template('components/navbar.html', original)
