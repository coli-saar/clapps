# coding: utf-8

from sqlalchemy import Column, DateTime, Float, Integer, SmallInteger, String, Table, text, ForeignKey, Unicode, Date, \
    Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()
metadata = Base.metadata



class Application(Base):
    __tablename__ = 'applications'

    id = Column(Integer, primary_key=True)
    code = Column(String(100))
    firstname = Column(String(200))
    lastname = Column(String(200))
    birthday = Column(DateTime)
    application_time = Column(DateTime)
    level = Column(String(200))
    # disability = Column(Integer)
    nationality = Column(String(2), ForeignKey('countries.code'))
    email = Column(String(200))
    affiliation = Column(String(200))
    aff_city = Column(String(200))
    aff_country = Column(String(2), ForeignKey('countries.code'))
    status = Column(Integer)
    comments = Column(Text)
    source = Column(Text)

    s_nationality = relationship("Country", foreign_keys=[nationality])
    s_aff_country = relationship("Country", foreign_keys=[aff_country])


class Country(Base):
    __tablename__ = 'countries'

    id = Column(Integer, primary_key=True)
    code = Column(String(2))
    name_en = Column(String(100))
    name_fr = Column(String(100))


class Degree(Base):
    __tablename__ = 'degrees'

    id = Column(Integer, primary_key=True)
    app_id = Column(Integer, ForeignKey('applications.id'))
    university = Column(String(200))
    city = Column(String(200))
    country = Column(String(2), ForeignKey('countries.code'))
    degree = Column(String(200))
    subject = Column(String(200))
    year = Column(Integer)

    application = relationship("Application", backref=backref("degrees"))


class Letter(Base):
    __tablename__ = 'letters'

    id = Column(Integer, primary_key=True)
    app_id = Column(Integer, ForeignKey('applications.id'))
    name = Column(String(200))
    email = Column(String(200))
    affiliation = Column(String(200))

    application = relationship("Application", backref=backref("letters"))
