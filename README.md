OSS Trends
==============

Open Source Software development activity by geographical location.

Design
======

Data pipeline:
 -periodic process
 -input is list of locations
 -for each location find all users
 -for each user find all repositories
 -build link between locations and repositories people are working on
 -extract stats about projects, and technologies people in a location
  are working on

Web UI:
 -input location: select from map or autocompleting textbox?
   -choice of location is controlled to something that can be mapped to a
    database entry (due to variations in natural language)

Database:
 -key-value store: compare performance vs relational database?

Technologies:
 -requests for Github API access.
 -flask for lightweight web UI
 -MongoDB for key-value store, PostgreSQL for relational


Problems Encountered:
 -rate limiting on search could be a problem.  Need a back-off mechanism.

  Could also look into data from from http://www.githubarchive.org/ instead
  ex: download activity for April 2012:
    wget http://data.githubarchive.org/2012-04-{01..31}-{0..23}.json.gz