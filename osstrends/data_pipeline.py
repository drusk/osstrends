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

import urlparse

import pymongo
import requests

from osstrends import auth

# The locations to lookup users from
LOCATIONS = ["victoria", "vancouver"]


class MongoDatabase(object):
    """
    Performs database insertions and queries.
    """

    DEFAULT_DB_NAME = "osstrends"
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


class GitHubSearcher(object):
    """
    Performs searches on the GitHub API.
    """

    GH_API_URL_BASE = "https://api.github.com"
    GH_SEARCH_HEADERS = {"Accept": "application/vnd.github.preview"}

    def search_users_by_location(self, location):
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
        response = self._gh_http_get("/search/users",
                                     params={
                                         "q": "location:{}".format(location),
                                         # use max page size to reduce API calls needed
                                         "per_page": 100
                                     }
        )

        users = self._parse_users(response)

        while True:
            try:
                next_url = response.links["next"]["url"]
            except KeyError:
                # No more pages to read
                break

            response = self._gh_http_get(next_url)
            users.extend(self._parse_users(response))

        return users

    def _gh_http_get(self, url, params=None, headers=None):
        """
        Performs an HTTP request for the specified GitHub API endpoint.

        Args:
          url: str
            Can be either the full URL or just the endpoint being queried.
            An example of an endpoint would be "/search/users"
          params: dict
            Any HTTP get parameters.
          headers: dict
            Any HTTP headers.

        Returns:
          A requests response object.
        """
        if not url.startswith(self.GH_API_URL_BASE):
            url = self.GH_API_URL_BASE + url

        parsed_url = urlparse.urlparse(url)

        if parsed_url.path.startswith("/search"):
            if headers is None:
                headers = {}
            headers.update(self.GH_SEARCH_HEADERS)

        return requests.get(url,
                            params=params,
                            headers=self.GH_SEARCH_HEADERS,
                            auth=(auth.GH_AUTH_USERNAME, auth.GH_AUTH_TOKEN))

    def _parse_users(self, response):
        try:
            return response.json()["items"]
        except KeyError:
            print response.json()


def download_users():
    """
    Downloads users for each location.
    """
    db = MongoDatabase()
    searcher = GitHubSearcher()
    for location in LOCATIONS:
        users = searcher.search_users_by_location(location)
        db.insert_users_by_location(location, users)
