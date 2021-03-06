# Copyright (C) 2013 David Rusk
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

__author__ = "David Rusk <drusk@uvic.ca>"

from flask import Flask, redirect, render_template, request
from flask.ext.login import (LoginManager, login_required, login_user,
                             logout_user)

from osstrends import auth
from osstrends.admin import Admin, LoginForm, ChangePasswordForm
from osstrends.database import MongoDatabase
from osstrends.locations import load_locations


app = Flask(__name__)
app.secret_key = auth.APP_SECRET_KEY

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/login"

db = MongoDatabase()
locations = load_locations()
admin = Admin(db)


@app.route("/")
def location_selection():
    return render_template("location_selection.html", locations=locations)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/users")
def users_by_location():
    location = request.args["location"]
    users = db.get_users(location=location)
    return render_template("users.html", location=location, users=users)


@app.route("/user/languages/<userid>")
def user_languages(userid):
    user = db.get_user(userid)
    language_stats = db.get_user_language_stats(userid)
    return render_template("user_languages.html",
                           userid=userid,
                           github_page=user["html_url"],
                           language_stats=language_stats,
                           location=user["location_normalized"])


@app.route("/location/<location_normalized>")
def location_languages(location_normalized):
    language_bytes, developer_counts = db.get_location_language_stats(
        location_normalized)

    return render_template("location_languages.html",
                           location=location_normalized,
                           language_bytes=language_bytes,
                           developer_counts=developer_counts)


@app.route("/users/location_language")
def users_by_location_and_language():
    location = request.args["location"]
    language = request.args["language"]

    users = db.get_users(location=location, language=language)
    return render_template("users_by_location_and_language.html",
                           users=users,
                           location=location,
                           language=language)


@login_manager.user_loader
def load_admin_user(userid):
    """
    This callback is required by flask-login to reload the user object.
    """
    return admin


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    login_form = LoginForm()

    if login_form.validate_on_submit():
        if admin.validate_credentials(
                login_form.username.data, login_form.password.data):
            login_user(admin)
            return redirect("/admin")
        else:
            error = "Username or password incorrect."

    return render_template("admin/login.html", form=login_form, error=error)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/admin")
@login_required
def admin_main():
    return render_template("admin/main.html")


@app.route("/admin/password", methods=["GET", "POST"])
@login_required
def admin_change_password():
    error = None
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if form.new_password.data == form.repeat_password.data:
            admin.change_password(form.new_password.data)
            # TODO notification of successfully changed password
            return redirect("/admin")
        else:
            error = "New password and repeat don't match."

    return render_template("admin/password.html", form=form, error=error)


if __name__ == "__main__":
    app.run()