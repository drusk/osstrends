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

from osstrends.database import MongoDatabase
from tests import testutil

TEST_DB_NAME = "test-osstrends"


class MongoDatabaseIntegrationTest(unittest.TestCase):
    def setUp(self):
        pymongo.MongoClient().drop_database(TEST_DB_NAME)

        self.db = MongoDatabase(db_name=TEST_DB_NAME)

    def test_save_and_retrieve_users_by_location(self):
        location = "victoria"
        retrieved_users = self.db.get_users_by_location(location)
        assert_that(retrieved_users, has_length(0))

        users = json.loads(testutil.read("victoria_users.json"))
        assert_that(users, has_length(649))

        unique_userids = {user["login"] for user in users}
        assert_that(unique_userids, has_length(554))

        for user in users:
            self.db.insert_user(user, location)

        retrieved_users = self.db.get_users_by_location(location)
        assert_that(retrieved_users, has_length(554))

    def test_get_user(self):
        for user in json.loads(testutil.read("victoria_users.json")):
            self.db.insert_user(user, "victoria")

        user = self.db.get_user("drusk")

        assert_that(user["login"], equal_to("drusk"))
        assert_that(user["html_url"], equal_to("https://github.com/drusk"))

    def test_save_and_retrieve_user_language_stats(self):
        userid = "drusk"
        language_stats = {
            "Python": 12345,
            "Java": 6789
        }

        self.db.insert_user_language_stats(userid, language_stats)

        assert_that(self.db.get_user_language_stats(userid),
                    equal_to(language_stats))
        assert_that(self.db.get_user(userid)["total_code_size"],
                    equal_to(19134))

    def test_save_and_retrieve_user_who_was_not_already_in_database(self):
        user = json.loads(testutil.read("user_drusk.json"))

        self.db.insert_user(user, "victoria")

        retrieved_user = self.db.get_user("drusk")
        assert_that(retrieved_user["login"], equal_to("drusk"))
        assert_that(retrieved_user["name"], equal_to("David Rusk"))
        assert_that(retrieved_user["public_repos"], equal_to(16))

    def test_save_and_retrieve_user_already_in_database(self):
        userid = "drusk"
        language_stats = {
            "Python": 12345,
            "Java": 6789
        }

        self.db.insert_user_language_stats(userid, language_stats)

        user = json.loads(testutil.read("user_drusk.json"))

        self.db.insert_user(user, "victoria")

        # Make sure language data is still there
        assert_that(self.db.get_user_language_stats(userid),
                    equal_to(language_stats))


if __name__ == '__main__':
    unittest.main()
