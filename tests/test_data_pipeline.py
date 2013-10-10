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

from hamcrest import assert_that, contains
from mock import Mock, call

from osstrends import data_pipeline


class DataPipelineTest(unittest.TestCase):
    def setUp(self):
        self.db = Mock(spec=data_pipeline.MongoDatabase)
        self.searcher = Mock(spec=data_pipeline.GitHubSearcher)

    def test_execute_pipeline(self):
        location1 = "victoria"
        location2 = "vancouver"

        def create_user(login):
            return {"login": login}

        location1_user1_login = "drusk"
        location1_user1 = create_user(location1_user1_login)
        location1_user1_stats = {"Python": 10, "Java": 5}

        location1_user2_login = "rrusk"
        location1_user2 = create_user(location1_user2_login)
        location1_user2_stats = {"C": 15, "Java": 8}

        location2_user1_login = "brian"
        location2_user1 = create_user(location2_user1_login)
        location2_user1_stats = {"C#": 9, "Shell": 2}

        # Mock user-location search
        def get_users_by_location(location):
            lookup = {
                location1: [location1_user1,
                            location1_user2],
                location2: [location2_user1]
            }
            try:
                return lookup[location]
            except KeyError:
                raise ValueError("Invalid location: %s" % location)

        self.searcher.search_users_by_location = Mock(side_effect=get_users_by_location)

        # Mock user search.  In reality additional information is returned.
        def get_user(userid):
            lookup = {
                location1_user1_login: location1_user1,
                location1_user2_login: location1_user2,
                location2_user1_login: location2_user1
            }
            try:
                return lookup[userid]
            except KeyError:
                raise ValueError("Invalid user: %s" % userid)

        self.searcher.search_user = Mock(side_effect=get_user)

        # Mock user-language searches
        def get_language_stats(user):
            lookup = {
                location1_user1_login: location1_user1_stats,
                location1_user2_login: location1_user2_stats,
                location2_user1_login: location2_user1_stats
            }
            try:
                return lookup[user]
            except KeyError:
                raise ValueError("Invalid user: %s" % user)

        self.searcher.get_user_language_stats = Mock(side_effect=get_language_stats)

        pipeline = data_pipeline.DataPipeline(self.db, self.searcher,
                                              [location1, location2])
        pipeline.execute()

        assert_that(self.searcher.search_users_by_location.call_args_list,
                    contains(
                        call(location1),
                        call(location2)
                    )
        )

        assert_that(self.db.insert_users_by_location.call_args_list,
                    contains(
                        call(location1, [location1_user1, location1_user2]),
                        call(location2, [location2_user1])
                    )
        )

        assert_that(self.searcher.search_user.call_args_list,
                    contains(
                        call(location1_user1_login),
                        call(location1_user2_login),
                        call(location2_user1_login)
                    ))

        assert_that(self.db.insert_user.call_args_list,
                    contains(
                        call(location1_user1),
                        call(location1_user2),
                        call(location2_user1)
                    ))

        assert_that(self.searcher.get_user_language_stats.call_args_list,
                    contains(
                        call(location1_user1_login),
                        call(location1_user2_login),
                        call(location2_user1_login)
                    )
        )

        assert_that(self.db.insert_user_language_stats.call_args_list,
                    contains(
                        call(location1_user1_login, location1_user1_stats),
                        call(location1_user2_login, location1_user2_stats),
                        call(location2_user1_login, location2_user1_stats)
                    ))


if __name__ == '__main__':
    unittest.main()
