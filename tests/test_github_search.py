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

import unittest

from hamcrest import assert_that, equal_to, has_length, contains_inanyorder
import httpretty

from osstrends import data_pipeline
from tests import testutil


class GitHubSearcherTest(unittest.TestCase):
    def setUp(self):
        self.searcher = data_pipeline.GitHubSearcher()

    @httpretty.activate
    def test_search_users_by_location_in_single_call(self):
        response_data = testutil.read("victoria_search_page1.json")

        httpretty.register_uri(httpretty.GET,
                               "https://api.github.com/search/users",
                               responses=[
                                   httpretty.Response(
                                       body=response_data,
                                       status=200)
                               ])

        users = self.searcher.search_users_by_location("victoria")

        assert_that(users, has_length(100))

    @httpretty.activate
    def test_search_repos_by_user(self):
        response_data = testutil.read("user_repos.json")

        httpretty.register_uri(httpretty.GET,
                               "https://api.github.com/users/drusk/repos",
                               responses=[
                                   httpretty.Response(
                                       body=response_data,
                                       status=200
                                   )
                               ])

        repos = self.searcher.search_repos_by_user("drusk")

        assert_that(repos, has_length(16))
        assert_that(repos, contains_inanyorder(
            "MOP",
            "scratch",
            "fishcounter",
            "config-files",
            "WeightRep",
            "drusk.github.com",
            "algorithms",
            "cadcVOFS",
            "query-gateway",
            "query-composer",
            "pml",
            "pml-applications",
            "uvic-transcript-parser",
            "archive",
            "investment-tracker",
            "drusk-gwt-oracle-example"
        ))

    @httpretty.activate
    def test_resolve_forked_repo_to_source(self):
        response_data = testutil.read("repo_is_fork.json")

        httpretty.register_uri(httpretty.GET,
                               "https://api.github.com/repos/drusk/MOP",
                               responses=[
                                   httpretty.Response(
                                       body=response_data,
                                       status=200
                                   )
                               ])

        owner, repo_name = self.searcher.resolve_repo_to_source("drusk", "MOP")

        assert_that(owner, equal_to("ijiraq"))
        assert_that(repo_name, equal_to("MOP"))

    @httpretty.activate
    def test_resolve_source_repo_to_source(self):
        response_data = testutil.read("repo_is_source.json")

        httpretty.register_uri(httpretty.GET,
                               "https://api.github.com/repos/drusk/algorithms",
                               responses=[
                                   httpretty.Response(
                                       body=response_data,
                                       status=200
                                   )
                               ])

        owner, repo_name = self.searcher.resolve_repo_to_source("drusk", "algorithms")

        assert_that(owner, equal_to("drusk"))
        assert_that(repo_name, equal_to("algorithms"))


if __name__ == '__main__':
    unittest.main()
