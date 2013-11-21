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

from hamcrest import assert_that, contains, equal_to
from mock import Mock, MagicMock, call

from osstrends.database import MongoDatabase
from osstrends.github import GitHubSearcher
from osstrends.locations import Location, load_locations
from osstrends.pipeline import DataPipeline
import testutil


class DataPipelineTest(unittest.TestCase):
    def setUp(self):
        self.db = Mock(spec=MongoDatabase)
        self.searcher = Mock(spec=GitHubSearcher)
        self.locations = load_locations(testutil.path("test_locations.json"))

        self.pipeline = DataPipeline(self.db, self.searcher, self.locations)
        self.pipeline._initialize_workers = Mock()

    def test_execute_pipeline(self):
        self.pipeline.process_location = Mock()

        self.pipeline.execute()

        self.db.delete_users.assert_called_once_with()

        assert_that(self.pipeline.process_location.call_args_list,
                    contains(*[call(location) for location in self.locations]))

    def test_process_location(self):
        self.pipeline.queue_user = Mock()

        num_users = 10
        users = [MagicMock() for _ in xrange(num_users)]
        self.searcher.search_users_by_location.return_value = users

        location = self.locations[0]
        self.pipeline.process_location(location)

        self.searcher.search_users_by_location.assert_called_once_with(
            location.search_term
        )

        assert_that(self.pipeline.queue_user.call_count, equal_to(num_users))

    def test_process_user(self):
        full_user_details = {"location": "Victoria, BC"}
        language_stats = Mock()
        self.searcher.search_user.return_value = full_user_details
        self.searcher.get_user_language_stats.return_value = language_stats

        user = {"login": "drusk"}
        location = self.locations[0]

        self.pipeline.process_user(user, location)

        self.searcher.search_user.assert_called_once_with("drusk")
        self.db.insert_user.assert_called_once_with(full_user_details,
                                                    location.normalized)

        self.searcher.get_user_language_stats.assert_called_once_with("drusk")
        self.db.insert_user_language_stats.assert_called_once_with(
            "drusk", language_stats)

    def test_user_filtered_due_to_stopword(self):
        location = Location("Victoria, BC, Canada",
                            ["Australia", "Melbourne"],
                            "victoria")

        def get_full_details(userid):
            full_details = {"login": userid}

            if userid == "Bob":
                full_details["location"] = "Victoria, australia"
            elif userid == "drusk":
                full_details["location"] = "VICTORIA"
            else:
                raise ValueError("Unknown userid: %s" % userid)

            return full_details

        self.searcher.search_user = Mock(side_effect=get_full_details)

        user1 = {"login": "Bob"}
        self.pipeline.process_user(user1, location)

        self.searcher.search_user.assert_called_once_with("Bob")
        assert_that(self.db.insert_user.called, equal_to(False))

        user2 = {"login": "drusk"}
        self.pipeline.process_user(user2, location)

        assert_that(self.searcher.search_user.call_count, equal_to(2))
        self.db.insert_user.assert_called_once_with(
            {"login": "drusk", "location": "VICTORIA"}, location.normalized)


if __name__ == '__main__':
    unittest.main()
