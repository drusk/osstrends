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
import urlparse

import requests

from osstrends import auth


class GitHubSearcher(object):
    """
    Performs searches on the GitHub API.
    """

    GH_API_URL_BASE = "https://api.github.com"
    GH_SEARCH_HEADERS = {"Accept": "application/vnd.github.preview"}

    def search_user(self, userid):
        """
        Retrieve the GitHub user object for the user with the specified userid.

        Args:
          userid: str
            The user's login id.

        Returns:
          user: User object described at http://developer.github.com/v3/users/
        """
        return self._gh_http_get("/users/{}".format(userid)).json()

    def search_users_by_location(self, location):
        """
        Search for GitHub users who list their location.

        Args:
          location: str
            The location value to look for.

        Returns:
          users: list of JSON objects with data for users who matched the
          location.  Note that this does NOT contain all the user
          information available with a direct user lookup.
        """
        response = self._gh_http_get("/search/users",
                                     params={
                                         "q": "location:{}".format(location),
                                         # use max page size to reduce API calls needed
                                         "per_page": 100
                                     }
        )

        def parse_users(response):
            return response.json()["items"]

        users = parse_users(response)

        while True:
            try:
                next_url = response.links["next"]["url"]
            except KeyError:
                # No more pages to read
                break

            response = self._gh_http_get(next_url)
            users.extend(parse_users(response))

        return users

    def search_repos_by_user(self, userid):
        """
        Obtain the list of repositories owned by a user.

        Args:
          userid: str
            The user's login id.

        Returns:
          repo_names: list(str)
            A list of the repository names, not the full name.  That is, not
            prepended with "userid/"
        """
        response = self._gh_http_get("/users/{}/repos".format(userid))

        return [repo["name"] for repo in response.json()]

    def get_repo_language_stats(self, owner, repo_name):
        """
        Looks up statistics of the languages used in a repository.

        Args:
          owner: str
            The login id for the user who owns the repository being looked
            up.
          repo_name: str
            The repository name, not the full name.  That is, not
            prepended with "userid/"

        Returns:
          language_stats: dict
            Keys are the language names, values are the number of bytes
            written in that language.
        """
        return self._gh_http_get(
            "/repos/{}/{}/languages".format(owner, repo_name)
        ).json()

    def get_user_language_stats(self, userid):
        """
        Looks up a user's programming languages based on their public repositories.

        Args:
          userid: str
            The login id of the user for whom the statistics are being gathered.

        Returns:
          language_stats: dict
            Keys are the language names, values are the number of bytes
            written in that language.
        """
        user_stats = collections.defaultdict(int)

        for repo in self.search_repos_by_user(userid):
            repo_stats = self.get_repo_language_stats(userid, repo)

            for language, size in repo_stats.iteritems():
                user_stats[language] += size

        return user_stats

    def resolve_repo_to_source(self, owner, repo_name):
        """
        Determines the "source" repository of a repository; that is, the
        top-level parent of a fork.  If the repository is not a fork then
        it is its own source.

        Args:
          owner: str
            The login id for the user who owns the repository being looked
            up.
          repo_name: str
            The repository name, not the full name.  That is, not
            prepended with "userid/"

        Returns:
          source_owner: str
            The owner of the source repository.
          source_repo_name: str
            The name of the source repository (should ordinarily be the same
            as the input repo_name).
        """
        response = self._gh_http_get("/repos/{}/{}".format(owner, repo_name))
        data = response.json()

        try:
            return data["source"]["full_name"].split("/")
        except KeyError:
            # This repo is not a fork, it is its own source
            return owner, repo_name

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
