from flask import session, flash, redirect, url_for
from functools import wraps


def login_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            session.permanent = True
            if "loggedin" not in session:
                print("Please log in to access this page.")
                return redirect(url_for("general.login_general"))

            if session.get("role") != role:
                flash("You don't have access to this page.")
                role_dashboard = {
                    "user": "user.user_dashboard",
                    "company": "company.company_dashboard",
                    "admin": "admin.admin_dashboard",
                }
                user_role = session.get("role")
                if user_role in role_dashboard:
                    return redirect(url_for(role_dashboard[user_role]))
                else:
                    return redirect(url_for("general.login_general"))
            return f(*args, **kwargs)

        return decorated_function

    return decorator
