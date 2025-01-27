from flask import Blueprint, render_template
from CTFd.models import db, Challenges, Solves
from CTFd.constants.config import ChallengeVisibilityTypes, Configs
from CTFd.utils.config import is_teams_mode
from CTFd.utils.dates import ctf_ended, ctf_paused, ctf_started
from CTFd.utils.decorators import (
    during_ctf_time_only,
    require_complete_profile,
    require_verified_emails,
)
from CTFd.utils.decorators.visibility import check_challenge_visibility
from CTFd.utils.helpers import get_errors, get_infos
from CTFd.utils.user import get_current_user, get_current_team, authed

blueprint = Blueprint('modules',
                      __name__,
                      template_folder='templates',
                      static_folder='assets')


def load_bp():

    # module listing
    @blueprint.route('/modules', methods=['GET'])
    @require_complete_profile
    @during_ctf_time_only
    @require_verified_emails
    @check_challenge_visibility
    def listing():
        """Render the module listing page."""

        # get current user
        if is_teams_mode():
            account = get_current_team()
            filter_column = Solves.team_id
        else:
            account = get_current_user()
            filter_column = Solves.user_id

        # get list of modules
        modules = db.session.query(Challenges.module).filter(Challenges.state == "visible").distinct().all()
        module_list = [m[0] if m[0] is not None else 'uncategorized' for m in modules]
        module_list.sort()

        # Get stats for each module
        module_stats = {}
        for module in module_list:
            # Get total challenges in module
            total = Challenges.query.filter_by(module=module, state="visible").count()

            # Get solved challenges for current user in this module
            if account:
                solved = db.session.query(Solves)\
                    .join(Challenges)\
                    .filter(Challenges.module == module)\
                    .filter(Challenges.state == "visible")\
                    .filter(filter_column == account.id)\
                    .count()
            else:
                solved = 0

            module_stats[module] = {
                'total': total,
                'solved': solved
            }
        return render_template('modules.html', modules=module_list, stats=module_stats)

    # module listing
    # we have to rewrite a huge chunk of this instead of reusing challenges.html
    # since challenges.html relies on info returned by the API and the API does not return
    # the module value of a challenge. there is also no support for editing the API through a plugins
    #
    # we will reuse a bunch of challenges.html code anyways
    #
    # if we do not need assets/js, remember to delete it
    @blueprint.route('/modules/<module_name>', methods=['GET'])
    @require_complete_profile
    @during_ctf_time_only
    @require_verified_emails
    @check_challenge_visibility
    def module_challenges(module_name):
        infos = get_infos()
        errors = get_errors()

        # Check visibility and CTF state
        if Configs.challenge_visibility == ChallengeVisibilityTypes.ADMINS:
            infos.append("Challenge Visibility is set to Admins Only")
        if ctf_started() is False:
            errors.append(f"{Configs.ctf_name} has not started yet")
        if ctf_paused() is True:
            infos.append(f"{Configs.ctf_name} is paused")
        if ctf_ended() is True:
            infos.append(f"{Configs.ctf_name} has ended")

        # Get all challenges for this module
        challenges = Challenges.query\
            .filter_by(state='visible', module=module_name)\
            .order_by(Challenges.value)\
            .all()

        if not challenges:
            errors.append(f"No challenges found for module {module_name}")

        # Get solved challenges
        solved_ids = set()
        if authed():
            user = get_current_user()
            if user:
                # Check if team mode
                if is_teams_mode():
                    team = get_current_team()
                    if team:
                        solved = Solves.query\
                            .filter_by(team_id=team.id)\
                            .join(Challenges)\
                            .filter(Challenges.module == module_name)\
                            .all()
                        solved_ids = {s.challenge_id for s in solved}
                else:
                    # User mode
                    solved = Solves.query\
                        .filter_by(user_id=user.id)\
                        .join(Challenges)\
                        .filter(Challenges.module == module_name)\
                        .all()
                    solved_ids = {s.challenge_id for s in solved}

        # Organize challenges by category
        categories = {}
        for challenge in challenges:
            if challenge.category not in categories:
                categories[challenge.category] = []

            categories[challenge.category].append({
                'id': challenge.id,
                'name': challenge.name,
                'value': challenge.value,
                'category': challenge.category,
                'solved': challenge.id in solved_ids
            })

        # Sort categories if theme setting exists
        try:
            category_sort = Configs.ctf_theme_settings.get('challenge_category_order')
            if category_sort:
                categories = dict(sorted(categories.items(), key=eval(category_sort)))
        except Exception as e:
            print(f"Error sorting categories: {e}")

        return render_template(
            'module_challenge_listing.html',
            module_name=module_name,
            categories=categories,
            infos=infos,
            errors=errors
        )

    return blueprint
