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
import os


def path(filename):
    """
    Performs path resolution to the data file.
    """
    return os.path.join(os.path.dirname(__file__), filename)


class Location(object):
    def __init__(self, normalized, valid_variations, search_term):
        self.normalized = normalized
        self.valid_variations = valid_variations
        self.search_term = search_term

    def __repr__(self):
        return self.normalized


def load_locations(filename="locations.json"):
    locations = []

    with open(path(filename), "rb") as filehandle:
        for json_object in json.load(filehandle):
            if json_object["include"]:
                locations.append(
                    Location(
                        json_object["normalized"],
                        json_object["valid_variations"],
                        json_object["search_term"]
                    )
                )

    return locations
