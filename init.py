from flask import Flask
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tables import Base
from flask_sqlalchemy_session import flask_scoped_session

import configparser


conf = configparser.ConfigParser({  }) # pass default values in dictionary
conf.read("clapps.conf")


# set up Flask
app = Flask(__name__, static_url_path='')
app.secret_key = conf.get("application", "secret")
start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

# set up database connection
db_url = conf.get("database", "url")
engine = create_engine(db_url)

# flask-mysqlalchemy integration
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = flask_scoped_session(DBSession, app)

# set up logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Started at %s" % str(start_time))

# retrieve list of countries
from tables import Country
countries = {country.id: country for country in session.query(Country).all()}
country_list = [(c.code, c.name_en) for id, c in sorted(countries.items(), key=lambda x:x[0])]