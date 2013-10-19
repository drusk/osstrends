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

# Modified from http://flask.pocoo.org/docs/patterns/fabric/

from fabric.api import *


# the user to use for the remote commands
env.user = "drusk"

# the servers where the commands are executed
env.hosts = ["rusk.dlinkddns.com"]


def package():
    # create a new source distribution as tarball
    local("python setup.py sdist --formats=gztar", capture=False)


def deploy():
    # figure out the release name and version
    dist = local("python setup.py --fullname", capture=True).strip()

    # upload the source tarball to the temporary folder on the server
    put("dist/%s.tar.gz" % dist, "/tmp/osstrends.tar.gz")

    # create a place where we can unzip the tarball, then enter
    # that directory and unzip it
    run("mkdir /tmp/osstrends")

    run("tar xzf /tmp/osstrends.tar.gz --directory /tmp/osstrends")

    with cd("/tmp/osstrends/%s" % dist):
        # now setup the package with our virtual environment's
        # python interpreter
        run("/var/www/osstrends/venv/bin/python setup.py install")

        # now that all is set up, delete the folder again
        run("rm -rf /tmp/osstrends /tmp/osstrends.tar.gz")

        # and finally copy up the .wsgi file
        put("osstrends.wsgi", "/var/www/osstrends")