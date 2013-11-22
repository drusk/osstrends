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

from flask import Flask, render_template, request

from osstrends.database import MongoDatabase
from osstrends.locations import load_locations


app = Flask(__name__)

db = MongoDatabase()
locations = load_locations()


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
                           language_stats=language_stats)


@app.route("/location/<location_normalized>")
def location_languages(location_normalized):
    language_stats = db.get_location_language_stats(location_normalized)
    return render_template("location_languages.html",
                           location=location_normalized,
                           language_stats=language_stats)


@app.route("/users/location_language")
def users_by_location_and_language():
    location = request.args["location"]
    language = request.args["language"]

    users = db.get_users(location=location, language=language)
    return render_template("users_by_location_and_language.html",
                           users=users,
                           location=location,
                           language=language)


if __name__ == "__main__":
    app.run()