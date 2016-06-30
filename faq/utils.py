# -*- coding: utf-8 -*-

from django.conf import settings
from fun.utils.mongo import connect_to_mongo

MONGO = settings.CONTENTSTORE['DOC_STORE_CONFIG']

COLLECTION = 'zendesk_student_faq_articles'


def connect_and_drop_collection(collection):
    """Connect to databse, and drop given collection."""
    db = connect_to_mongo()
    db.connection[MONGO['db']].drop_collection(collection)
    return db[collection]


def get_fun_faq_collection():
    db = connect_to_mongo()
    return db[COLLECTION]
