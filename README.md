# Flask-Fixtures

A simple library that allows you to add database fixtures for your unit tests
using nothing but JSON or YAML.

## Installation

Installing Flask-Fixtures is simple, just do a typical pip install like so:

```
pip install flask-fixtures
```

To install the library from source simply download the source code, or check
it out if you have git installed on your system, then just run the install
command.

```
git clone https://github.com/croach/Flask-Fixtures.git
cd /path/to/flask-fixtures
python setup.py install
```

## Setup

To setup the library, you simply need to tell Flask-Fixtures where it can find
the fixtures files for your tests. Fixtures can reside anywhere on the file
system, but by default, Flask-Fixtures looks for these files in a directory
called `fixtures` in your app's root directory. To add more directories to the
list to be searched, just add an attribute called `FIXTURES_DIRS` to your
app's config object. This attribute should be a list of strings, where each
string is a path to a fixtures directory. Absolute paths are added as is, but
reltative paths will be relative to your app's root directory.

Once you have configured the extension, you can begin adding fixtures for your
tests.

## Adding Fixtures

To add a set of fixtures, you simply add any number of JSON or YAML files
describing the individual fixtures to be added to your test database into one
of the directories you specified in the `FIXTURES_DIRS` attribute, or into the
default fixtures directory. As an example, I'm going to assume we have a Flask
application with the following directory structure.

```
/myapp
    __init__.py
    config.py
    models.py
    /fixtures
        authors.json
```

The `__init__.py` file will be responsible for creating our Flask application
object.

```python
# myapp/__init__.py

from flask import Flask

app = Flask(__name__)
```

The `config.py` object holds our test configuration file.

```python
# myapp/config.py

class TestConfig(object):
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    testing = True
    debug = True
```

And, finally, inside of the `models.py` files we have the following database
models.

```python
# myapp/models.py

from flask.ext.sqlalchemy import SQLAlchemy

from myapp import app

db = SQLAlchemy(app)

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    author = db.relationship('Author', backref='books')
```

Given the model classes above, if we wanted to mock up some data for our
database, we could do so in single file, or we could even split our fixtures
into multiple files each corresponding to a single model class. For this
simple example, we'll go with one file that we'll call `authors.json`.

A fixtures file contains a list of objects. Each object contains a key called
`records` that holds another list of objects each representing either a row in
a table, or an instance of a model. If you wish to work with tables, you'll
need to specify the name of the table with the `table` key. If you'd prefer to
work with models, specify the fully-qualified class name of the model using
the `model` key. Once you've specified the table or model you want to work
with, you'll need to specify the data associated with each table row, or model
instance. Each object in the `records` list will hold the data for a single
row or model. The example below is the JSON for a single author record and a
few books associated with that author. Create a file called
`myapp/fixtures/authors.json` and copy and paste the fixtures JSON below into
that file.

```json
[
    {
        "table": "author",
        "records": [{
            "id": 1,
            "first_name": "William",
            "last_name": "Gibson",
        }]
    },
    {
        "model": "myapp.models.Book",
        "records": [{
            "title": "Neuromancer",
            "author_id": 1
        },
        {
            "title": "Count Zero",
            "author_id": 1
        },
        {
            "title": "Mona Lisa Overdrive",
            "author_id": 1
        }]
    }
]
```

After reading over the previous section, you might be asking yourself why the
library supports two methods for adding records to the database. There are a
few good reasons for supporting both tables and models when creating fixtures.
Using tables is faster, since we can take advantage of SQLAlchemy's bulk
insert to add several records at once. However, to do so, you must first make
sure that the records list is homegenous. **In other words, every object in
the `records` list must have the same set of key/value pairs, otherwise the
bulk insert will not work.** Using models, however, allows you to have a
heterogenous list of record objects.

The other reason you may want to use models instead of tables is that you'll
be able to take advantage of any python-level defaults, checks, etc. that you
have setup on the model. Using a table, bypasses the model completely and
inserts the data directly into the database, which means you'll need to think
on a lower level when creating table-based fixtures.

## Usage

To use Flask-Fixtures in your unit tests, you'll need to make sure your test
class inherits from `FixturesMixin` and that you've specified a list of
fixtures files to load. The sample code below shows how to do each these
steps.

First, make sure the app that you're testing is initialized with the proper
configuration. Then import and initialize the `FixturesMixin` class, create a
new test class, and inherit from `FixturesMixin`. Now you just need to tell
Flask-Fixtures which fixtures files to use for your tests. You can do so by
setting either the `fixtures` or `class_fixtures` class variable. The former
will setup and tear down fixtures between each test while the latter will
setup fixtures only when the class is first created and tear them down after
all tests have finished executing (in other words, changes to the database
will persist between tests). The `fixtures` and `class_fixtures` variables
should be set to a list of strings, each of which is the name of a fixtures
file to load. Flask-Fixtures will then search the default fixtures directory
followed by each directory in the `FIXTURES_DIRS` config variable, in order,
for a file matching each name in the list and load each into the test
database.

```python
# myapp/fixtures/test_fixtures.py

import unittest

from myapp import app
from myapp.models import db, Book, Author

from flask.ext.fixtures import FixturesMixin

# Configure the app with the testing configuration
app.config.from_object('myapp.config.TestConfig')

# Initialize the Flask-Fixtures mixin class
FixturesMixin.init_app(app, db)

# Make sure to inherit from the FixturesMixin class
class TestFoo(unittest.TestCase, FixturesMixin):

    # Specify the fixtures file you want to load
    fixtures = ['authors.json']

    # Your tests go here

    def test_authors(self):
        authors = Author.query.all()
        assert len(authors) == Author.query.count() == 1
        assert len(authors[0].books) == 3

    def test_books(self):
        books = Book.query.all()
        assert len(books) == Book.query.count() == 3
        gibson = Author.query.filter(Author.last_name=='Gibson').one()
        for book in books:
            assert book.author == gibson
```

## Examples

To see the library in action, you can find a simple Flask application and set
of unit tests matching the ones in the example above in the `tests/myapp`
directory. To run these examples yourself, just follow the directions below
for "Contributing to Flask-Fixtures".

## Contributing to Flask-Fixtures

Currently, Flask-Fixtures supports the py.test, nose, and unittest (included
in the python standard library) libraries. To contribute bug fixes and
features to Flask-Fixtures, you'll need to make sure that any code you
contribute does not break any of the existing unit tests in any of these three
environments.

To run the unit tests in each environment, you'll first need to checkout the
source code and install it in develop mode. I suggest using virtualenv to
create a virtual development environment, so you're not polluting your normal
Python environment with a development version of Flask-Fixtures. Once you have
your virtual environment created, just `cd` into the directory where you
checked out the Flask-Fixtures source code and install it with pip using the
`-e` (editable mode) option.

```
cd /path/to/flask_fixtures
pip install -e .
```

Then, you'll need to install the py.test and nose libraries. Once you have
those installed, you can run the tests with the commands in the table below.

| Library  | Command                                             |
|:---------|:----------------------------------------------------|
| py.test  | py.test                                             |
| nose     | nosetests                                           |
| unittest | python -m unittest discover --start-directory tests |

