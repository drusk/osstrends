# Use virtual environment to manage dependencies:
# http://flask.pocoo.org/docs/deploying/mod_wsgi/#working-with-virtual-environments
activate_this = "/var/www/osstrends/venv/bin/activate_this.py"
execfile(activate_this, dict=(__file__=activate_this))

from osstrends.web import app as application