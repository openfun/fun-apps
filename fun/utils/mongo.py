import pymongo

from django.conf import settings

MONGO = settings.CONTENTSTORE['DOC_STORE_CONFIG']


def connect_to_mongo():
    """Connect to FUN Mongo database."""
    db = pymongo.database.Database(
            pymongo.MongoClient(host=MONGO['host']),
            MONGO['db'])
    if 'user' in MONGO:
        db.authenticate(MONGO['user'], MONGO['password'])
    return db
