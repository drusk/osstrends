OSS Trends
==============

A webapp for exploring Open Source Software development activity by
geographical location.

Currently all data is collected from
[GitHub's public API](http://developer.github.com/v3/).

Features
========
* Find developers by location, including information such as company and
  real name if provided.
* Visualize a developer's programming language usage.
* Visualize the popular languages in a location, based on either number of
  developers or size of code.
* Find developers who use a specific language in a specified location.
* Sortable and filterable data table view of data.

Technologies Used
=================
* Python and JavaScript
* [Flask](http://flask.pocoo.org/)
* [MongoDB](http://www.mongodb.org/) and
  [PyMongo](https://github.com/mongodb/mongo-python-driver)
* [Requests](http://requests.readthedocs.org/en/latest/)
* [Bootstrap](http://getbootstrap.com/)
* [jQuery](http://jquery.com/)
* [DataTables](http://datatables.net/)
* [Chart.js](http://www.chartjs.org/)
* [Select2](http://ivaynberg.github.io/select2/)

Future Improvements
===================
* Find similar developers
* Work in LinkedIn data?
* Full repo analysis for tools, libraries and frameworks usage
* Easy deployment and setup procedure for other locations.  Include admin
  web interface for making configuration changes.