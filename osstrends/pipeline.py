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

import logging

from osstrends.database import MongoDatabase
from osstrends.github import GitHubSearcher
from osstrends.locations import load_locations

logger = logging.getLogger(__name__)


class DataPipeline(object):
    """
    The main pipeline for acquiring the application's data.
    """

    def __init__(self, db, searcher, locations):
        """
        Constructor.

        Args:
          db: interface for the database that will store the data retrieved.
          searcher: interface for the search service that will retrieve the
            data.
          locations: list(str)
            The locations to be included in the data retrieval.
        """
        self.db = db
        self.searcher = searcher
        self.locations = locations

    def execute(self):
        """
        Runs the pipeline.
        """
        # Remove the old data
        self.db.delete_users()

        for location in self.locations:
            self.process_location(location)

    def process_location(self, location):
        """
        Searches for users in a location and then processes them.

        Args:
          location: osstrends.locations.Location
        """
        logger.info("Starting to process location: {}".format(location))

        users = self.searcher.search_users_by_location(location.search_term)

        logger.info("Got users for location: {}".format(
            location.search_term))

        for user in users:
            self.process_user(user, location)

    def process_user(self, user, location):
        """
        The location-based search does not return very much information
        about the user.  This method gets the full details about the user
        and saves them to the database.
        """
        userid = user["login"]

        full_user_details = self.searcher.search_user(userid)

        if full_user_details["location"] not in location.valid_variations:
            # This is needed because searching for "Victoria" will return users from
            # Victoria BC, but also from Victoria the Australian state.
            return

        self.db.insert_user(full_user_details, location.normalized)

        logger.info("Retrieved user info for {}".format(userid))

        logger.info(
            "Starting collection of language stats for user: {}".format(
                userid))

        language_stats = self.searcher.get_user_language_stats(userid)
        self.db.insert_user_language_stats(userid, language_stats)

        logger.info(
            "Finished collecting language stats for user: {}".format(
                userid))


def execute():
    """
    Executes the data pipeline with default parameters.
    """
    DataPipeline(MongoDatabase(), GitHubSearcher(), load_locations()).execute()
