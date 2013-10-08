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

import json
import unittest

from hamcrest import assert_that, equal_to, has_length
import pymongo

from osstrends import data_pipeline
from tests import testutil

TEST_DB_NAME = "test-osstrends"


class MongoDatabaseIntegrationTest(unittest.TestCase):
    def setUp(self):
        pymongo.MongoClient().drop_database(TEST_DB_NAME)

        self.db = data_pipeline.MongoDatabase(db_name=TEST_DB_NAME)

    def test_save_and_retrieve_users_by_location(self):
        location = "victoria"
        retrieved_users = self.db.get_users_by_location(location)
        assert_that(retrieved_users, has_length(0))

        users = json.loads(testutil.read("victoria_users.json"))
        assert_that(users, has_length(649))

        self.db.insert_users_by_location(location, users)
        retrieved_users = self.db.get_users_by_location(location)
        assert_that(retrieved_users, has_length(649))

    def test_save_and_retrieve_user_language_stats(self):
        userid = "drusk"
        language_stats = {
            "Python": 12345,
            "Java": 6789
        }

        self.db.insert_user_language_stats(userid, language_stats)

        assert_that(self.db.get_user_language_stats(userid),
                    equal_to(language_stats))


if __name__ == '__main__':
    unittest.main()
