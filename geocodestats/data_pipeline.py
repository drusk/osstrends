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
import requests

from geocodestats import auth

GH_API_URL_BASE = "https://api.github.com"
GH_SEARCH_HEADERS = {"Accept": "application/vnd.github.preview"}

# The locations to lookup users from
LOCATIONS = ["victoria", "vancouver"]


class MongoDatabase(object):
    """
    Performs database insertions and queries.
    """

    DEFAULT_DB_NAME = "geocodestats"
    USERS_LOCATIONS = "users_locations"
    LOCATION_KEY = "location"
    USERS_KEY = "users"

    def __init__(self, db_name=DEFAULT_DB_NAME, host="localhost", port=27017):
        self._client = pymongo.MongoClient(
            "mongodb://{host}:{port}".format(host=host, port=port)
        )
        self._db = self._client[db_name]

    def _get_collection(self, collection_name):
        """
        Returns a handle to the specified MongoDB database collection.
        """
        return self._db[collection_name]

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
        result = self._get_collection(self.USERS_LOCATIONS).find_one(
            {self.LOCATION_KEY: location}
        )

        if result is None:
            return []

        return result[self.USERS_KEY]

    def insert_users_by_location(self, location, users):
        """
        Associate a collection of users with a location in the database.

        Args:
          location: str
            The location which the users are from.
          users: list(dict)
            A list of user information objects (http://developer.github.com/v3/users/)
        """
        self._get_collection(self.USERS_LOCATIONS).insert(
            {self.LOCATION_KEY: location, self.USERS_KEY: users}
        )


def search_github_users_by_location(location):
    """
    Search for GitHub users who list their location.

    Args:
      location: str
        The location value to look for.

    Returns:
      users: list of JSON objects with user data
             (see http://developer.github.com/v3/users/)
        A list of users who matched the location.
    """

    def http_get(url, params=None):
        return requests.get(url,
                            params=params,
                            headers=GH_SEARCH_HEADERS,
                            auth=(auth.GH_AUTH_USERNAME, auth.GH_AUTH_TOKEN))

    response = http_get("{}/search/users".format(GH_API_URL_BASE),
                        params={
                            "q": "location:{}".format(location),
                            # use max page size to reduce API calls needed
                            "per_page": 100
                        }
    )

    def parse_users(response):
        try:
            return response.json()["items"]
        except KeyError:
            print response.json()

    users = parse_users(response)

    while True:
        try:
            next_url = response.links["next"]["url"]
        except KeyError:
            # No more pages to read
            break

        response = http_get(next_url)
        users.extend(parse_users(response))

    return users


def download_users():
    """
    Downloads users for each location.
    """
    db = MongoDatabase()
    for location in LOCATIONS:
        users = search_github_users_by_location(location)
        db.insert_users_by_location(location, users)
