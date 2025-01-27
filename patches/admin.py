from CTFd.plugins import override_template
import re

def patch_update_challenge(app):
    """
    Patch admin/challenges/update.html
    """

    # retrieve create.html / overriden create.html
    if 'admin/challenges/update.html' in app.overridden_templates:
        original = app.override_templates['admin/challenges/update.html']
    else:
        with open('/opt/CTFd/CTFd/themes/admin/templates/challenges/update.html', 'r') as f:
            original = f.read()

    match = re.search(r'{% block category %}', original)
    if match:
        pos = match.start()
        original = original[:pos] + """
    {% block module %}
    <div class="form-group">
        <label>
            Module<br>
            <small class="form-text text-muted">Challenge Module</small>
        </label>
        <input type="text" class="form-control chal-module" name="module" value="{{ challenge.module }}" required>
    </div>
    {% endblock %}
    """ + original[pos:]
    if match:
        override_template('admin/challenges/update.html', original)
    else:
        raise Exception("failed to patch challenge update form fields")

def patch_create_new_challenge(app):
    """
    Patch admin/challenges/create.html
    """

    # retrieve create.html / overriden create.html
    if 'admin/challenges/create.html' in app.overridden_templates:
        original = app.override_templates['admin/challenges/create.html']
    else:
        with open('/opt/CTFd/CTFd/themes/admin/templates/challenges/create.html', 'r') as f:
            original = f.read()

    match = re.search(r'{% block category %}', original)
    if match:
        pos = match.start()
        original = original[:pos] + """
    {% block module %}
    <div class="form-group">
        <label>
            Module:<br>
            <small class="form-text text-muted">
                Module to classify your challenge under
            </small>
        </label>
        <input type="text" class="form-control" name="module" placeholder="Enter challenge module" required>
    </div>
    {% endblock %}
    """ + original[pos:]

    if match:
        override_template('admin/challenges/create.html', original)
    else:
        raise Exception("failed to patch challenge creation form fields")

def patch_admin_challenges_listing(app):
    """
    Patch admin/challenges/challenges.html
    """

    # retrieve challenges.html / overriden challenge.html
    if 'admin/challenges/challenges.html' in app.overridden_templates:
        original = app.override_templates['admin/challenges/challenges.html']
    else:
        with open('/opt/CTFd/CTFd/themes/admin/templates/challenges/challenges.html', 'r') as f:
            original = f.read()

    # we want to insert module before category
    # we patch the table header here
    match = re.search(r'<th class="sort-col"><b>Category</b></th>', original)
    if match:
        pos = match.start()
        original = original[:pos] + r'<th class="sort-col"><b>Module</b></th>' + original[pos:]

    # we patch the table column here
    match2 = re.search(r'<td>{{ challenge.category }}</td>', original)
    if match2:
        pos = match2.start()
        original = original[:pos] + r'<td>{{ challenge.module }}</td>' + original[pos:]

    # if we patched both successfully, we can override the template
    if match and match2:
        override_template('admin/challenges/challenges.html', original)
    else:
        raise Exception("failed to patch admin challenge listing")

