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

# Python 2.7.3 has a bug requiring this work-around
# See http://bugs.python.org/issue15881#msg170215
try:
    import multiprocessing
except ImportError:
    pass

from setuptools import setup, find_packages


def parse_requirements():
    """
    Read requirements from the requirements.txt file.
    """
    with open("requirements.txt", "rb") as filehandle:
        return filehandle.readlines()


setup(
    name="osstrends",
    author="David Rusk",
    author_email="drusk@uvic.ca",
    version="0.1",
    long_description=("Open Source Software development activity by "
                      "geographical location."),
    packages=find_packages(),
    include_package_data=True,  # Include data specified in MANIFEST.in
    zip_safe=False,
    install_requires=parse_requirements()
)
