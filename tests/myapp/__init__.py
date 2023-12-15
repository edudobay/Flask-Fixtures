from __future__ import absolute_import
# myapp/__init__.py

from flask import Flask

app = Flask(__name__)

# Configure the app with the testing configuration
app.config.from_object('myapp.config.TestConfig')
