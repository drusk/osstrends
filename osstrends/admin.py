# Copyright (C) 2014 David Rusk
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

from flask_wtf import Form
from wtforms import PasswordField, StringField
from wtforms.validators import Length


class LoginForm(Form):
    username = StringField("username", validators=[
        Length(min=1, message="Please provide your username.")])
    password = PasswordField("password")


class Admin(object):
    """
    Implements the interface required by flask-login for site users that
    need authentication.
    """

    DEFAULT_USERNAME = "admin"
    DEFAULT_PASSWORD = "admin"

    def __init__(self, db):
        self._db = db

        if not db.is_admin_initialized():
            db.set_admin(self.DEFAULT_USERNAME, self.DEFAULT_PASSWORD)

    @property
    def username(self):
        return self.DEFAULT_USERNAME

    def validate_credentials(self, provided_username, provided_password):
        """
        Returns True if the provided credentials match what's in the
        database, and False if they do not match.
        """
        return self._db.validate_admin(provided_username, provided_password)

    def change_password(self, new_password):
        """
        Update the administrator's password.
        Returns void.
        """
        self._db.set_admin(self.DEFAULT_USERNAME, new_password)

    def is_authenticated(self):
        """
        Required by flask-login.
        Misleading name.  Just means that this user should be allowed
        to authenticate.
        """
        return True

    def is_active(self):
        """
        Required by flask-login.
        Should return True unless the user has been banned, etc.
        """
        return True

    def is_anonymous(self):
        """
        Required by flask-login.
        """
        return False

    def get_id(self):
        """
        Required by flask-login.
        """
        return self.DEFAULT_USERNAME
