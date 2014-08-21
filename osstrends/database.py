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

import collections

import pymongo
from werkzeug.security import generate_password_hash, check_password_hash


class MongoDatabase(object):
    """
    Performs database insertions and queries.
    """

    DEFAULT_DB_NAME = "osstrends"

    USERS_COLLECTION = "users"
    ADMIN_COLLECTION = "admins"

    ADMIN_USERNAME_KEY = "username"
    ADMIN_PASSWORD_KEY = "password"

    USERID_KEY = "login"
    NORMALIZED_LOCATION_KEY = "location_normalized"
    LANGUAGES_KEY = "languages"
    TOTAL_CODE_SIZE_KEY = "total_code_size"

    def __init__(self, db_name=DEFAULT_DB_NAME, host="localhost", port=27017):
        self._client = pymongo.MongoClient(
            "mongodb://{host}:{port}".format(host=host, port=port)
        )
        self._db = self._client[db_name]

    def _get_users_collection(self):
        return self._db[self.USERS_COLLECTION]

    def _get_admin_collection(self):
        return self._db[self.ADMIN_COLLECTION]

    def delete_users(self):
        self._get_users_collection().drop()

    def get_user(self, userid):
        """
        Retrieve user information object for the specified user.

        Args:
          userid: str
            The user's login id.

        Returns:
            user: http://developer.github.com/v3/users/
        """
        return self._get_users_collection().find_one(
            {self.USERID_KEY: userid}
        )

    def insert_user(self, user, normalized_location):
        """
        Adds a user to the database, or updates the existing entry with
        updated or new fields.

        Args:
          user: dict-like
            Contains the user data.
          normalized_location: str
            Normalized version of the user's location which will be used
            in database lookups.

        Returns: void
        """
        user[self.NORMALIZED_LOCATION_KEY] = normalized_location

        self._get_users_collection().update(
            {self.USERID_KEY: user[self.USERID_KEY]},
            {"$set": user},
            upsert=True
        )

    def get_users(self, location=None, language=None):
        """
        Lookup users by location and/or language from the database.

        Args:
          location: str
            Find users from this location.  Must be normalized.
          language: str
            Only return users who have code in this programming language.

        Returns:
          users: list(dict)
            A list of user information objects
            (http://developer.github.com/v3/users/).
            Returns an empty list if there are no users for that
            location/language.
        """
        query = {}

        if location is not None:
            query[self.NORMALIZED_LOCATION_KEY] = location

        if language is not None:
            key = "%s.%s" % (self.LANGUAGES_KEY, language)
            query[key] = {"$exists": True}

        return list(self._get_users_collection().find(query))

    def get_user_language_stats(self, userid):
        """
        Retrieve a user's programming language statistics.

        Args:
          userid: str
            The login id of the user for whom the statistics are being gathered.

        Returns:
          language_stats: dict
            Keys are the language names, values are the number of bytes
            written in that language.
        """
        return self.get_user(userid)[self.LANGUAGES_KEY]

    def insert_user_language_stats(self, userid, language_stats):
        """
        Insert language statistics data for a user into the database.

        Args:
          userid: str
            The login id of the user for whom the statistics are being gathered.
          language_stats: dict
            Keys are the language names, values are the number of bytes
            written in that language.

        Returns: void
        """
        self._get_users_collection().update(
            {self.USERID_KEY: userid},
            {"$set": {self.LANGUAGES_KEY: language_stats,
                      self.TOTAL_CODE_SIZE_KEY: sum(language_stats.values())}},
            upsert=True
        )

    def get_location_language_stats(self, location_normalized):
        """
        Retrieves programming language statistics for a location which are
        aggregated from all the individual users in that location.

        Args:
          location_normalized: str

        Returns:
          language_bytes: dict
            Keys are the language names, values are the number of bytes
            written in that language.
          developer_counts: dict
            Keys are the language name, values are the number of developers
            in the location with code in that language.
        """
        language_bytes = collections.defaultdict(int)
        developer_counts = collections.defaultdict(int)

        for user in self.get_users(location=location_normalized):
            for language, count in user[self.LANGUAGES_KEY].iteritems():
                language_bytes[language] += count
                developer_counts[language] += 1

        return language_bytes, developer_counts

    def is_admin_initialized(self):
        """
        Checks if the administrator account has been created.

        Returns: bool
          True if the administrator account has been created.
        """
        return self._get_admin_collection().count() > 0

    def set_admin(self, username, password):
        """
        Sets the administrator username and password.

        Args:
          username: str
            The administrator's username.
          password: str
            The administrator's password, which will be hashed for
            security.

        Returns: void
        """
        hashed_password = generate_password_hash(password)

        self._get_admin_collection().update(
            {self.ADMIN_USERNAME_KEY: username},
            {
                self.ADMIN_USERNAME_KEY: username,
                self.ADMIN_PASSWORD_KEY: hashed_password
            },
            upsert=True
        )

    def validate_admin(self, username, password):
        """
        Checks if the username and password match the admin credentials
        in the database.

        Args:
          username: str
          password: str
            The plain-text password

        Returns: bool
          True if the provided credentials match the database, false if
          they do not.
        """
        admin = self._get_admin_collection().find_one()

        return (admin[self.ADMIN_USERNAME_KEY] == username and
                check_password_hash(admin[self.ADMIN_PASSWORD_KEY], password))
