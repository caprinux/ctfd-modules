from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.migrations import upgrade
from CTFd.models import Challenges
from sqlalchemy import Column, String
from .blueprint import load_bp
from .patches.admin import (
    patch_admin_challenges_listing,
    patch_create_new_challenge,
    patch_update_challenge
)
from .patches.navbar import patch_navbar
from flask import request, redirect, url_for
import os


def load(app):

    # we hook challenge listing to list modules instead
    @app.before_request
    def check_challenges_endpoint():
        if request.endpoint == 'challenges.listing':
            return redirect(url_for('modules.listing'))

    # register assets directory
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_name = os.path.basename(dir_path)
    register_plugin_assets_directory(app,
                                     base_path="/plugins/"+dir_name+"/assets/",
                                     endpoint="module_assets")

    # upgrade our model
    if not hasattr(Challenges, 'module'):
        setattr(Challenges, 'module', Column(String(80)))
    upgrade(plugin_name="challenge_modules")

    # hotfix admin configuration
    patch_admin_challenges_listing(app)
    patch_create_new_challenge(app)
    patch_update_challenge(app)

    # hotfix navbar
    patch_navbar(app)

    bp = load_bp()
    app.register_blueprint(bp)
