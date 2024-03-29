import os
import re

from flask import Flask
import time

from flask_login import LoginManager
from jinja2 import evalcontextfilter
from markupsafe import Markup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.utils import secure_filename

from tables import Base
from flask_sqlalchemy_session import flask_scoped_session

import configparser

from user import User

conf = configparser.ConfigParser({  }) # pass default values in dictionary
conf.read("clapps.conf")

clapps_contact = "%s <%s>" % (conf.get("contact", "name"), conf.get("contact", "email"))


# set up Flask
app = Flask(__name__, static_url_path='')
app.secret_key = conf.get("server", "secret")
start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

app.config['UPLOAD_FOLDER'] = conf.get("server", "upload_dir")

# set up database connection
db_url = conf.get("database", "url")
engine = create_engine(db_url, pool_recycle=3600)

# flask-mysqlalchemy integration
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = flask_scoped_session(DBSession, app)

# set up logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Started at %s" % str(start_time))

# initialize list of users who can log in
users = {}
for id, value in conf.items("users"):
    name, passwd = re.split("\s*,\s*", value)
    users[id] = User(id, name, passwd)


# retrieve list of countries
from tables import Country
countries = {country.id: country for country in session.query(Country).all()}
country_list = [(c.code, c.name_en) for id, c in sorted(countries.items(), key=lambda x:x[0])]

# retrieve statuses
status_items = conf.items("status")
status_colors = {}
status_labels = {}
for id, value in status_items:
    id = int(id)
    label, color = re.split("\s*,\s*", value)
    status_colors[id] = color
    status_labels[id] = label

# initialize file upload path
upload_dir = conf.get("server", "upload_dir")

if os.path.isabs(upload_dir):
    fs_upload_dir = upload_dir
else:
    fs_upload_dir = os.path.abspath(upload_dir)



status_choices = [(str(id), "%d - %s" % (id, status_labels[id])) for id in sorted(status_labels.keys())]

@app.template_filter("ft")
@evalcontextfilter
def ft(eval_ctx, value):
    t = value.timetuple()
    return time.strftime("%d/%m/%y", t)


def cv_filename_from_data(id, lastname):
    dir = app.config['UPLOAD_FOLDER']

    # create CVs directory if it doesn't exist
    if not os.path.exists(dir):
        os.makedirs(dir)
    
    filename = secure_filename("%d-%s.pdf" % (id, lastname))
    file_path = os.path.join(dir, filename)
    return file_path

@app.template_filter("cv_filename")
@evalcontextfilter
def cv_filename(eval_ctx, application):
    return cv_filename_from_data(application.id, application.lastname)


@app.template_filter("flaglink")
@evalcontextfilter
def flaglink(eval_ctx, countrycode):
    url = "img/famfamfam_flags/%s.gif" % countrycode.lower()
    return Markup('<img src="%s" alt="%s"/>' % (url, countrycode))

@app.template_filter("emlink")
@evalcontextfilter
def emlink(eval_ctx, address):
    return Markup("<img src='img/envelope.png' height='12px' /> <a href='mailto:%s'>%s</a>" % (address, address))

@app.template_filter("statuscolor")
@evalcontextfilter
def statuscolor(eval_ctx, status):
    return status_colors.get(status, "white")

@app.template_filter("statuslabel")
@evalcontextfilter
def statuslabel(eval_ctx, status):
    return status_labels.get(status, "(undef)")
