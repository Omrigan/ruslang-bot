from flask import Flask
from pymongo import MongoClient
import secret_settings, study_settings
import telegram
#import my_correction
from nltk.stem import WordNetLemmatizer
import traceback, sys
import train, remainder
import random, re, os
from enum import Enum

import time, datetime
import logging, argparse
from xml.etree import ElementTree
from bs4 import BeautifulSoup
import requests
import my_import
env = os.getenv('BOT_ENV', 'staging')

class States():
    idle = 1
    translates_proposed = 2



logger = logging.getLogger("bot")
help_text = open('docs/help.txt').read()
changelog_text = open('docs/changelog.txt').read()
wnl = WordNetLemmatizer()



params = {}







def eraseLastWord(user, text):
    if(len(user['words'])>0):
        str_out = "%s - %s" % (user['words'][-1]['en'], user['words'][-1]['ru'])
        user['words'] = user['words'][:-1]
        telegram.sendMessage(user['chat_id'], "Last word erased\n" + str_out)

def getListWord(user, text):
    str_out = "\n".join(["%s" % (w['correct'], ) for w in user['words']])
    telegram.sendMessage(user['chat_id'], str_out)

def start(user, text):
    telegram.sendMessage(user['chat_id'], """
    Welcome
    I am an EnglishWordRepeater bot.
    To learn how to use me, print /help
    """)
def help(user, text):
    telegram.sendMessage(user['chat_id'], help_text)

def startTrain(user, text):
    user['train']['type'] = 0
    train.doTrain(user, text)

def addReamainder(user, text):
    remainder.remove_job(user)
    tokens = text.split(' ')
    delta = datetime.timedelta()
    if len(tokens)>=2:
        tokens=tokens[1].replace(' ', '').split(':')
        hours = int(tokens[0])
        minutes = int(tokens[1])
        delta = datetime.timedelta(hours=hours, minutes=minutes)
    remainder.add_job(user, datetime.datetime.utcnow()+delta)
    telegram.sendMessage(user['chat_id'], "Successfully set. Nearest at  %s" % (datetime.datetime.now()+delta,))

def removeRemainder(user, text):
    remainder.remove_job(user)
    telegram.sendMessage(user['chat_id'], "Removed")

comands = {
    'eraselast': eraseLastWord,
    'getlist': getListWord,
    'starttrain': startTrain,
    'endtrain': train.endTrain,
    'start': start,
    'help': help,
    'setremainder': addReamainder,
    'removeremainder': removeRemainder
}

def parseAction(chat_id, text):
    logger.warning("%s - %s" %(chat_id, text))
    user = users.find_one({'chat_id': chat_id})
    if user is None:

        user = {'chat_id': chat_id,
                'state': States.idle,
                'words': list(db.wordlist.find()),
                'train': {
                    'type': 0,
                    'word': 0,
                    'correct': 0,
                }}
    if 'train' not in user:
        user['train'] = {
                    'type': 0,
                    'word': 0,
                    'correct': 0,

                }
    if text[0]=='/': #Command
        cmd = text[1:].lower().split(' ')[0]
        if cmd in comands:
            comands[cmd](user, text)
    else:
        if user['train']['type']!=0:
            train.doTrain(user, text)
    users.save(user)





def getUpdates():
    messeges = telegram.getUpdates(params['offset'])
    for u in messeges:
        if 'message' in u:
            if u['update_id'] < params['offset']:
                print('Error')
            else:
                chat_id = u['message']['chat']['id']
                text = u['message']['text']
                params['offset'] = max(params['offset'], u['update_id']+1)
                try:
                    parseAction(chat_id, text)
                except Exception:
                    logging.error('Error! (%s, %s)' %(chat_id, text))
                    logging.error(traceback.print_exc())
                    telegram.sendMessage(chat_id, 'Parse error! Try again')

    db.meta.save(params)

if __name__ == "__main__":
    global client
    global words


    ###LOGGING
    access = logging.FileHandler('access.log')
    access.setLevel(logging.INFO)
    access.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    error = logging.FileHandler('error.log')
    error.setLevel(logging.ERROR)
    error.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(access)
    logger.addHandler(error)
    if env=='debug':
        logging.basicConfig(level=logging.DEBUG)
        logging.debug("Debug mode")


    db = MongoClient(secret_settings.mongo['uri']).ruslang
    overwrite = False
    if overwrite:
        db.users.drop()
        db.wordlist.drop()
    cols = db.collection_names()
    if 'users' not in cols:
        db.create_collection('users')
    if 'wordlist' not in cols:
        db.create_collection('wordlist')
        my_import.doImport()
    users = db.users
    wordlist = db.wordlist



    params['offset'] = 0
    logging.warning('Started')
    while True:
        getUpdates()
        time.sleep(0.1)
    #app.run()
