from pymongo import MongoClient
import secret_settings
import datetime


def doImport():
    db = MongoClient(secret_settings.mongo['uri']).ruslang
    wordlist = db.wordlist
    wordlist.remove()
    for l in open('data/doc.txt'):
        l = l[:-1]
        wordlist.save({'word': l.lower(), 'correct': l, 'expiration_date': datetime.datetime.utcnow(), 'stage': 1})