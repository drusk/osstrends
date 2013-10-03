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

from hamcrest import assert_that, has_length
import pymongo

from osstrends import data_pipeline
from tests import testutil

TEST_DB_NAME = "test-osstrends"


class MongoDatabaseIntegrationTest(unittest.TestCase):
    def setUp(self):
        pymongo.MongoClient().drop_database(TEST_DB_NAME)

    def test_save_and_retrieve_users_by_location(self):
        db = data_pipeline.MongoDatabase(db_name=TEST_DB_NAME)

        location = "victoria"
        retrieved_users = db.get_users_by_location(location)
        assert_that(retrieved_users, has_length(0))

        users = json.loads(testutil.read("victoria_users.json"))
        assert_that(users, has_length(649))

        db.insert_users_by_location(location, users)
        retrieved_users = db.get_users_by_location(location)
        assert_that(retrieved_users, has_length(649))


if __name__ == '__main__':
    unittest.main()
