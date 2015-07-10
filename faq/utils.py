# -*- coding: utf-8 -*-

import pymongo

from django.conf import settings

MONGO = settings.CONTENTSTORE['OPTIONS']
COLLECTION = 'zendesk_student_faq_articles'


def connect_to_mongo():
    """Connect to FUN Mongo database."""
    db = pymongo.database.Database(
            pymongo.MongoClient(host=MONGO['host'][0]),
            MONGO['db'])
    db.authenticate(MONGO['user'], MONGO['password'])
    return db


def connect_and_drop_collection(collection):
    """Connect to databse, and drop given collection."""
    db = connect_to_mongo()
    db.connection[MONGO['db']].drop_collection(collection)
    return db[collection]


def get_fun_faq_collection():
    db = connect_to_mongo()
    return db[COLLECTION]
