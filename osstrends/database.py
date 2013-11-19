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

import pymongo


class MongoDatabase(object):
    """
    Performs database insertions and queries.
    """

    DEFAULT_DB_NAME = "osstrends"

    USERS_COLLECTION = "users"
    USERID_KEY = "login"
    NORMALIZED_LOCATION_KEY = "location_normalized"
    LANGUAGES_KEY = "languages"

    def __init__(self, db_name=DEFAULT_DB_NAME, host="localhost", port=27017):
        self._client = pymongo.MongoClient(
            "mongodb://{host}:{port}".format(host=host, port=port)
        )
        self._db = self._client[db_name]

    def _get_users_collection(self):
        return self._db[self.USERS_COLLECTION]

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

    def insert_user(self, user):
        """
        Adds a user to the database, or updates the existing entry with
        updated or new fields.

        Args:
          user: dict-like
            Contains the user data.

        Returns: void
        """
        self._get_users_collection().update(
            {self.USERID_KEY: user[self.USERID_KEY]},
            {"$set": user},
            upsert=True
        )

    def get_users_by_location(self, location):
        """
        Lookup users by location from the database.

        Args:
          location: str
            Find users from this location (ex: Victoria).

        Returns:
          users: list(dict)
            A list of user information objects
            (http://developer.github.com/v3/users/).
            Returns an empty list if there are no users for that location.
        """
        return list(self._get_users_collection().find(
            {self.NORMALIZED_LOCATION_KEY: location})
        )

    def insert_users_by_location(self, location, users):
        """
        Associate a collection of users with a location in the database.

        Args:
          location: str
            The location which the users are from.
          users: list(dict)
            A list of user information objects (http://developer.github.com/v3/users/)

        Returns: void
        """
        users_collection = self._get_users_collection()

        for user in users:
            user[self.NORMALIZED_LOCATION_KEY] = location
            users_collection.insert(user)

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
            {"$set": {self.LANGUAGES_KEY: language_stats}},
            upsert=True
        )
