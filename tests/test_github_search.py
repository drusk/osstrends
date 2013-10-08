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
from mock import Mock

from osstrends import data_pipeline
from tests import testutil


class GitHubSearcherTest(unittest.TestCase):
    def setUp(self):
        self.searcher = data_pipeline.GitHubSearcher()

    @httpretty.activate
    def test_search_users_by_location_in_single_call(self):
        self.mock_uri("https://api.github.com/search/users",
                      testutil.read("victoria_search_page1.json"))

        users = self.searcher.search_users_by_location("victoria")

        assert_that(users, has_length(100))

    @httpretty.activate
    def test_search_repos_by_user(self):
        self.mock_uri("https://api.github.com/users/drusk/repos",
                      testutil.read("user_repos.json"))

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
        self.mock_uri("https://api.github.com/repos/drusk/MOP",
                      testutil.read("repo_is_fork.json"))

        owner, repo_name = self.searcher.resolve_repo_to_source("drusk", "MOP")

        assert_that(owner, equal_to("ijiraq"))
        assert_that(repo_name, equal_to("MOP"))

    @httpretty.activate
    def test_resolve_source_repo_to_source(self):
        self.mock_uri("https://api.github.com/repos/drusk/algorithms",
                      testutil.read("repo_is_source.json"))

        owner, repo_name = self.searcher.resolve_repo_to_source("drusk", "algorithms")

        assert_that(owner, equal_to("drusk"))
        assert_that(repo_name, equal_to("algorithms"))

    @httpretty.activate
    def test_get_repo_language_stats(self):
        self.mock_uri("https://api.github.com/repos/drusk/algorithms/languages",
                      testutil.read("language_stats_algorithms.json"))

        language_stats = self.searcher.get_repo_language_stats("drusk", "algorithms")

        assert_that(language_stats, equal_to(
            {
                "Java": 150390,
                "Python": 4713
            }
        ))

    @httpretty.activate
    def test_get_user_language_stats(self):
        self.searcher.search_repos_by_user = Mock(return_value=["algorithms", "pml"])

        self.mock_uri("https://api.github.com/repos/drusk/algorithms/languages",
                      testutil.read("language_stats_algorithms.json"))
        self.mock_uri("https://api.github.com/repos/drusk/pml/languages",
                      testutil.read("language_stats_pml.json"))

        language_stats = self.searcher.get_user_language_stats("drusk")

        assert_that(language_stats, equal_to(
            {
                "Java": 150390,
                "Python": 273059,
                "Shell": 5407
            }
        ))

    def mock_uri(self, uri, response_data, status=200):
        httpretty.register_uri(httpretty.GET,
                               uri,
                               responses=[
                                   httpretty.Response(
                                       body=response_data,
                                       status=status
                                   )
                               ])


if __name__ == '__main__':
    unittest.main()
