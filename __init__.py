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
import os

def load(app):

    # TODO: patch!
    # from flask import redirect, url_for
    # # we hook flask redirect to always redirect any challenges to modules
    # # this allows /challenges endpoint to still exist without patching CTFd code
    # def custom_redirect(location, *args, **kwargs):
    #     if location == url_for('challenges.listing'):
    #         return redirect(url_for('modules.listing'), *args, **kwargs)
    #     return redirect(location, *args, **kwargs)
    #
    # import flask
    # flask.redirect = custom_redirect

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
