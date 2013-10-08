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

from hamcrest import assert_that, has_length, contains_inanyorder
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


if __name__ == '__main__':
    unittest.main()
