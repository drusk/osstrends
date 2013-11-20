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

from hamcrest import assert_that, has_length, equal_to, contains_inanyorder

from osstrends.locations import load_locations
import testutil


class LocationTest(unittest.TestCase):
    def test_load_locations(self):
        locations = load_locations(testutil.path("test_locations.json"))

        assert_that(locations, has_length(2))
        location1 = locations[0]
        location2 = locations[1]

        assert_that(location1.normalized, equal_to("Victoria, BC, Canada"))
        assert_that(location1.stopwords,
                    contains_inanyorder(
                        "Melbourne",
                        "Australia"
                    ))
        assert_that(location1.search_term, equal_to("victoria"))

        assert_that(location2.normalized, equal_to("Seattle, WA, USA"))


if __name__ == '__main__':
    unittest.main()
