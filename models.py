
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import mapper, sessionmaker
from main import main_app
from flask import session
from constants import JWT_PAYLOAD

class User(object):
    pass

def get_user_id():
    return session[JWT_PAYLOAD]['sub']

def loadSession():
    engine = create_engine(main_app.config['SQLALCHEMY_DATABASE_URI'], echo=True)
    metadata = MetaData(engine)
    users = Table('User', metadata, autoload=True)
    mapper(User, users)
    Session = sessionmaker(bind=engine)
    dbsession = Session()
    return dbsession

dbsession = loadSession()
#res = dbsession.query(User).all()